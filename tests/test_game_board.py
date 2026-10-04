from __future__ import annotations

import asyncio

from client.game_board import GameBoard
from core.cards import Card, CardType, Rarity
from core.engine.match import MatchConfig, MatchManager, MatchStatus
from core.engine.state_machine import (
    GameEvent,
    GamePhase,
    StateMachine,
    create_initial_state,
)
from core.entities import Hero, Minion, Player
from core.pve.encounters import get_encounter


def _main_phase_machine() -> StateMachine:
    machine = StateMachine(create_initial_state("ui-test", "player", "opponent"))
    for phase in (GamePhase.TURN_START, GamePhase.DRAW, GamePhase.MAIN_PHASE):
        assert machine.transition(phase)
    return machine


def _card(
    card_id: str,
    card_type: CardType,
    cost: int = 1,
    attack: int = 2,
    health: int = 2,
) -> Card:
    return Card(
        id=card_id,
        name=card_id,
        cost=cost,
        card_type=card_type,
        class_type="NEUTRAL",
        rarity=Rarity.COMMON,
        text="",
        attack=attack,
        health=health,
    )


def test_game_board_builds_hand_board_and_mana_controls() -> None:
    player = Player(
        hero=Hero(name="Player", max_health=30),
        hand=[_card("hand-minion", CardType.MINION)],
        mana=2,
        max_mana=3,
    )
    board = GameBoard(player, state_machine=_main_phase_machine())

    board.build()

    assert board.hand_container in board.controls[-2].controls
    assert board._end_turn_button is board._battlefield_row.controls[1].content
    assert board._end_turn_button not in board.controls[-1].controls[0].controls
    assert board._end_turn_button.content == "Zug beenden"
    assert len(board._opponent_board_row.controls) == 7
    assert len(board._hand_row.controls) == 5
    assert len(board.hand_cards) == 1
    assert len(board._board_row.controls) == 7
    assert len(board._mana_crystals) == 3
    assert [crystal.is_current for crystal in board._mana_crystals] == [True, True, False]
    assert board._mana_text.value == "2/3"


def test_hand_displays_all_cards_beyond_five_in_a_scrollable_row() -> None:
    cards = [_card(f"hand-{index}", CardType.MINION) for index in range(6)]
    player = Player(hero=Hero(name="Player", max_health=30), hand=cards, mana=6)
    board = GameBoard(player, state_machine=_main_phase_machine())

    board.build()

    assert len(board.hand_cards) == 6
    assert [widget.card for widget in board.hand_cards] == cards
    assert len(board._hand_row.controls) == 6
    assert board._hand_row.wrap is False
    assert board._hand_row.scroll is not None


def test_hand_card_click_only_plays_affordable_cards() -> None:
    playable = _card("playable", CardType.MINION, cost=1)
    unaffordable = _card("unaffordable", CardType.MINION, cost=3)
    player = Player(
        hero=Hero(name="Player", max_health=30),
        hand=[playable, unaffordable],
        mana=1,
        max_mana=3,
    )
    board = GameBoard(player, state_machine=_main_phase_machine())
    board.build()

    playable_widget, unaffordable_widget = board.hand_cards
    assert playable_widget.is_playable is True
    assert playable_widget.opacity == 1
    assert unaffordable_widget.is_playable is False
    assert unaffordable_widget.opacity < playable_widget.opacity

    unaffordable_widget._handle_click(None)
    assert unaffordable in player.hand
    assert player.mana == 1
    assert player.board == []

    playable_widget._handle_click(None)

    assert playable not in player.hand
    assert unaffordable in player.hand
    assert player.mana == 0
    assert len(player.board) == 1
    assert [widget.card for widget in board.hand_cards] == [unaffordable]
    assert board.hand_cards[0].is_playable is False


def test_affordable_hand_card_is_subdued_outside_main_phase() -> None:
    card = _card("inactive-card", CardType.MINION, cost=0)
    player = Player(hero=Hero(name="Player", max_health=30), hand=[card], mana=1)
    board = GameBoard(
        player,
        state_machine=StateMachine(
            create_initial_state("inactive-test", "player", "opponent")
        ),
    )
    board.build()

    widget = board.hand_cards[0]
    assert widget.is_playable is False
    assert widget.opacity < 1
    widget._handle_click(None)
    assert card in player.hand
    assert player.board == []
    assert player.mana == 1


def test_playing_minion_updates_player_and_engine_state() -> None:
    card = _card("test-minion", CardType.MINION, cost=2)
    player = Player(
        hero=Hero(name="Player", max_health=30),
        hand=[card],
        mana=3,
        max_mana=3,
    )
    machine = _main_phase_machine()
    board = GameBoard(player, state_machine=machine)
    board.build()

    board._on_card_play_from_hand(card)

    assert card not in player.hand
    assert player.mana == 1
    assert len(player.board) == 1
    assert player.board[0].owner is player
    assert machine.state.mana == 1
    assert [crystal.is_current for crystal in board._mana_crystals] == [True, False, False]
    assert GameEvent.CARD_PLAYED.value in machine.state.event_log
    assert GameEvent.MINION_SUMMONED.value in machine.state.event_log


def test_ready_minion_attacks_opposing_hero() -> None:
    player = Player(hero=Hero(name="Player", max_health=30))
    opponent = Player(hero=Hero(name="Opponent", max_health=30))
    minion = _card("attacker", CardType.MINION, attack=4)
    player.board.append(Minion(card=minion, owner=player, can_attack=True))
    machine = _main_phase_machine()
    board = GameBoard(player, opponent, machine)
    board.build()

    board._on_minion_attack_select(player.board[0])
    board._on_attack_button_click(None)

    assert opponent.hero.current_health == 26
    assert player.board[0].can_attack is False
    assert GameEvent.DAMAGE_DEALT.value in machine.state.event_log


def test_attack_ready_minions_are_highlighted_and_clickable() -> None:
    player = Player(hero=Hero(name="Player", max_health=30))
    opponent = Player(hero=Hero(name="Opponent", max_health=30))
    ready = Minion(
        card=_card("ready", CardType.MINION, attack=3),
        owner=player,
        can_attack=True,
    )
    exhausted = Minion(
        card=_card("exhausted", CardType.MINION, attack=3),
        owner=player,
        can_attack=False,
    )
    player.board.extend([ready, exhausted])
    board = GameBoard(player, opponent, _main_phase_machine())
    board.build()

    ready_widget, exhausted_widget = board.minion_slots[:2]
    assert ready_widget.can_attack is True
    assert exhausted_widget.can_attack is False
    assert (
        ready_widget._get_attack_border_color()
        != exhausted_widget._get_attack_border_color()
    )
    ready_widget._on_click(None)
    assert board._selected_minion is ready
    exhausted_widget._on_click(None)
    assert board._selected_minion is ready


def test_clicking_enemy_minion_executes_selected_attack_immediately() -> None:
    player = Player(hero=Hero(name="Player", max_health=30))
    opponent = Player(hero=Hero(name="Opponent", max_health=30))
    attacker = Minion(
        card=_card("attacker", CardType.MINION, attack=3, health=4),
        owner=player,
        can_attack=True,
    )
    target = Minion(
        card=_card("target", CardType.MINION, attack=1, health=2),
        owner=opponent,
    )
    player.board.append(attacker)
    opponent.board.append(target)
    machine = _main_phase_machine()
    board = GameBoard(player, opponent, machine)
    board.build()

    board.minion_slots[0]._on_click(None)
    board.opponent_minion_slots[0]._on_click(None)

    assert target not in opponent.board
    assert attacker.can_attack is False
    assert board._selected_minion is None
    assert GameEvent.DAMAGE_DEALT.value in machine.state.event_log


def test_clicking_enemy_hero_executes_attack_without_taunt() -> None:
    player = Player(hero=Hero(name="Player", max_health=30))
    opponent = Player(hero=Hero(name="Opponent", max_health=30))
    attacker = Minion(
        card=_card("attacker", CardType.MINION, attack=4),
        owner=player,
        can_attack=True,
    )
    player.board.append(attacker)
    board = GameBoard(player, opponent, _main_phase_machine())
    board.build()

    board.minion_slots[0]._on_click(None)
    board._opponent_hero_widget.on_click(None)

    assert opponent.hero.current_health == 26
    assert attacker.can_attack is False
    assert board._selected_minion is None


def test_lethal_board_attack_resolves_victory_through_match_manager() -> None:
    manager = MatchManager(MatchConfig(encounter=get_encounter("enc_wild_wolf")))
    attacker = Minion(
        card=_card("finisher", CardType.MINION, attack=4),
        owner=manager.player,
        can_attack=True,
    )
    manager.player.board.append(attacker)
    manager.opponent.hero.current_health = 3
    board = GameBoard(
        manager.player,
        manager.opponent,
        manager.state_machine,
        match_manager=manager,
    )
    board.build()

    board._on_minion_attack_select(attacker)
    board._on_attack_button_click(None)

    assert manager.opponent.hero.current_health == 0
    assert manager.status == MatchStatus.VICTORY
    assert board.match_status == MatchStatus.VICTORY
    assert board._result_banner.visible is True
    assert board._result_text.value == "Sieg! Leitwolf wurde besiegt."


def test_selected_attacker_is_explicitly_highlighted_in_board_ui() -> None:
    player = Player(hero=Hero(name="Player", max_health=30))
    minion = Minion(
        card=_card("selected-attacker", CardType.MINION, attack=4, health=5),
        owner=player,
        can_attack=True,
    )
    player.board.append(minion)
    board = GameBoard(player, Player(hero=Hero(name="Opponent", max_health=30)), _main_phase_machine())
    board.build()

    board._on_minion_attack_select(minion)

    assert board.minion_slots[0].selected_for_attack is True
    assert board._selected_attacker_text.value == (
        "selected-attacker (4/5) — Ziel: gegnerischer Held oder Diener"
    )
    assert board._attack_button.disabled is False
    assert board._attack_button.content == "Angreifen · Gegnerheld"


def test_opponent_minion_cards_are_visible_and_taunt_must_be_targeted() -> None:
    manager = MatchManager(MatchConfig(encounter=get_encounter("enc_wild_wolf")))
    attacker = Minion(
        card=_card("friendly-attacker", CardType.MINION, attack=4, health=5),
        owner=manager.player,
        can_attack=True,
    )
    taunt_minion = Minion(
        card=_card("enemy-guard", CardType.MINION, attack=1, health=2),
        owner=manager.opponent,
        has_taunt=True,
    )
    ordinary_minion = Minion(
        card=_card("enemy-scout", CardType.MINION, attack=1, health=2),
        owner=manager.opponent,
    )
    manager.player.board.append(attacker)
    manager.opponent.board.append(ordinary_minion)
    manager.opponent.board.append(taunt_minion)
    opponent_hp = manager.opponent.hero.current_health
    board = GameBoard(
        manager.player,
        manager.opponent,
        manager.state_machine,
        match_manager=manager,
    )
    board.build()

    enemy_widget = board.opponent_minion_slots[1]
    assert board.opponent_minion_slots[0].minion is ordinary_minion
    assert enemy_widget.minion is taunt_minion
    assert enemy_widget.is_enemy is True
    assert enemy_widget.minion.has_taunt is True
    assert enemy_widget.content.controls[0].controls[0].value == "enemy-guard"
    assert enemy_widget.content.controls[1].controls[0].value == "SPOTT"

    board._on_minion_attack_select(attacker)
    assert board.opponent_minion_slots[0].target_selectable is False
    assert board.opponent_minion_slots[1].target_selectable is True
    assert board._attack_button.disabled is True

    board._on_attack_button_click(None)
    assert manager.opponent.hero.current_health == opponent_hp
    board._on_enemy_minion_select(ordinary_minion)
    assert board._attack_target is None

    board._opponent_hero_widget.on_click(None)
    assert manager.opponent.hero.current_health == opponent_hp
    assert attacker.can_attack is True

    board.opponent_minion_slots[1]._on_click(None)

    assert taunt_minion not in manager.opponent.board
    assert manager.opponent.hero.current_health == opponent_hp
    assert attacker.can_attack is False
    assert board._selected_minion is None


def test_end_turn_button_is_at_battlefield_right_and_advances_turn() -> None:
    next_card = _card("drawn-next-turn", CardType.SPELL)
    player = Player(
        hero=Hero(name="Player", max_health=30),
        deck=[next_card],
        mana=1,
        max_mana=1,
    )
    opponent = Player(hero=Hero(name="Opponent", max_health=30), mana=1, max_mana=1)
    machine = _main_phase_machine()
    board = GameBoard(player, opponent, machine)
    board.build()

    assert board._battlefield_row.controls[1].content is board._end_turn_button
    board._end_turn_button.on_click(None)

    assert board._is_opponent_turn is True
    assert board._end_turn_button.disabled is True
    assert player.turn_number == 1
    assert next_card in player.hand
    assert machine.state.phase == GamePhase.MAIN_PHASE


def test_combat_log_keeps_only_six_recent_readable_events() -> None:
    board = GameBoard(Player(hero=Hero(name="Player", max_health=30)))
    board.build()

    for index in range(7):
        board._add_log(f"Ereignis {index}")

    assert len(board._combat_log_entries) == 6
    assert board._game_log.value.count("\n") == 5
    assert "Ereignis 6" in board._game_log.value
    assert "Ereignis 0" not in board._game_log.value


def test_ai_plays_one_affordable_card_and_returns_to_player_turn() -> None:
    player = Player(hero=Hero(name="Player", max_health=30), max_mana=3)
    played_card = _card("ai-played", CardType.SPELL, cost=1)
    remaining_card = _card("ai-remains", CardType.SPELL, cost=4)
    opponent = Player(
        hero=Hero(name="Opponent", max_health=30),
        hand=[played_card, remaining_card],
        mana=3,
        max_mana=3,
    )
    machine = _main_phase_machine()
    board = GameBoard(player, opponent, machine)
    board.build()

    board._on_end_turn()
    assert board._is_opponent_turn is True
    asyncio.run(board._ai_turn())

    assert opponent.graveyard == [played_card]
    assert opponent.hand == [remaining_card]
    assert board._is_opponent_turn is False
    assert machine.state.phase == GamePhase.MAIN_PHASE
    assert GameEvent.CARD_PLAYED.value in machine.state.event_log
