from __future__ import annotations

import asyncio

from client.game_board import GameBoard
from core.cards import Card, CardType, Rarity
from core.entities import Hero, Minion, Player
from core.engine.state_machine import (
    GameEvent,
    GamePhase,
    StateMachine,
    create_initial_state,
)
from core.engine.match import MatchConfig, MatchManager, MatchStatus
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
    assert board._end_turn_button in board.controls[-1].controls[0].controls
    assert board._end_turn_button.content == "Zug beenden"
    assert len(board._opponent_board_row.controls) == 7
    assert len(board._hand_row.controls) == 5
    assert len(board.hand_cards) == 1
    assert len(board._board_row.controls) == 7
    assert len(board._mana_crystals) == 3
    assert [crystal.is_current for crystal in board._mana_crystals] == [True, True, False]
    assert board._mana_text.value == "2/3"


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

    board._on_enemy_minion_select(taunt_minion)
    assert board._attack_button.disabled is False
    assert board._attack_button.content == "Angreifen · enemy-guard"
    board._on_attack_button_click(None)

    assert taunt_minion not in manager.opponent.board
    assert manager.opponent.hero.current_health == opponent_hp
    assert attacker.can_attack is False


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
