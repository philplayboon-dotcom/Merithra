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

    assert board.hand_container in board.controls
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
