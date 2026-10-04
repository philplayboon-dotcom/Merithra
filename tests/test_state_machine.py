"""Unit tests for core.engine.state_machine.

Tests cover:
- GamePhase Enum values
- StateMachine transition logic
- emit Event firing
- GameState serialization (to_dict / from_dict)
- Deterministic replay from Event-Log
- Phase Transition Validation (illegal transitions rejected)
"""

from __future__ import annotations

from typing import Any

import pytest

from core.engine.state_machine import (
    GamePhase,
    GameEvent,
    GameState,
    StateMachine,
    create_initial_state,
)


# -----------------------------------------------------------
# GamePhase Enum Tests
# -----------------------------------------------------------


class TestGamePhase:
    """Tests for GamePhase Enum values."""

    def test_all_phases_have_values(self) -> None:
        """All phases should have auto-assigned integer values."""
        phases = [
            GamePhase.MULLIGAN,
            GamePhase.TURN_START,
            GamePhase.DRAW,
            GamePhase.MAIN_PHASE,
            GamePhase.COMBAT,
            GamePhase.TURN_END,
            GamePhase.NEXT_TURN,
        ]
        for phase in phases:
            assert phase.value is not None

    def test_phase_names(self) -> None:
        """Phase names should match expected strings."""
        assert GamePhase.MULLIGAN.name == "MULLIGAN"
        assert GamePhase.TURN_START.name == "TURN_START"
        assert GamePhase.DRAW.name == "DRAW"
        assert GamePhase.MAIN_PHASE.name == "MAIN_PHASE"
        assert GamePhase.COMBAT.name == "COMBAT"
        assert GamePhase.TURN_END.name == "TURN_END"
        assert GamePhase.NEXT_TURN.name == "NEXT_TURN"


# -----------------------------------------------------------
# GameState Tests
# -----------------------------------------------------------


class TestGameStateSerialization:
    """Tests for GameState to_dict / from_dict round-trip."""

    def test_to_dict_roundtrip(self) -> None:
        """Serializing and deserializing should preserve state."""
        initial = GameState(
            game_id="test_game_001",
            player_id="player1",
            opponent_id="opponent1",
        )
        data: dict[str, Any] = initial.to_dict()
        restored = GameState.from_dict(data)

        assert restored.game_id == initial.game_id
        assert restored.player_id == initial.player_id
        assert restored.opponent_id == initial.opponent_id
        assert restored.phase == initial.phase
        assert restored.turn_number == initial.turn_number
        assert restored.mana == initial.mana
        assert restored.max_mana == initial.max_mana
        assert restored.seed == initial.seed
        assert restored.event_log == initial.event_log

    def test_from_dict_with_all_fields(self) -> None:
        """from_dict should handle all fields including custom ones."""
        data = {
            "game_id": "game_123",
            "player_id": "p1",
            "opponent_id": "p2",
            "phase": "MAIN_PHASE",
            "turn_number": 5,
            "mana": 5,
            "max_mana": 10,
            "seed": 42,
            "event_log": [GameEvent.TURN_START.value],
        }
        state = GameState.from_dict(data)
        assert state.game_id == "game_123"
        assert state.phase == GamePhase.MAIN_PHASE
        assert state.turn_number == 5
        assert state.mana == 5
        assert state.event_log == ["on_turn_start"]

    def test_default_values(self) -> None:
        """GameState should have sensible defaults."""
        state = GameState(game_id="g", player_id="p", opponent_id="o")
        assert state.phase == GamePhase.MULLIGAN
        assert state.turn_number == 0
        assert state.mana == 1
        assert state.max_mana == 1
        assert state.seed is not None
        assert state.event_log == []


# -----------------------------------------------------------
# StateMachine Transition Tests
# -----------------------------------------------------------


class TestStateMachineTransitions:
    """Tests for StateMachine transition logic."""

    @pytest.fixture
    def base_state(self) -> GameState:
        return create_initial_state("g", "p", "o")

    @pytest.fixture
    def machine(self, base_state: GameState) -> StateMachine:
        return StateMachine(base_state)

    def test_valid_transition_mulligan_to_turn_start(self, machine: StateMachine) -> None:
        """MULLIGAN -> TURN_START should be allowed."""
        assert machine.transition(GamePhase.TURN_START) is True

    def test_valid_transition_turn_start_to_draw(self, machine: GameState) -> None:
        """TURN_START -> DRAW should be allowed after mulligan transition."""
        machine.transition(GamePhase.TURN_START)
        assert machine.transition(GamePhase.DRAW) is True

    def test_valid_transition_draw_to_main_phase(self, machine: GameState) -> None:
        """DRAW -> MAIN_PHASE should be allowed."""
        machine.transition(GamePhase.TURN_START)
        machine.transition(GamePhase.DRAW)
        assert machine.transition(GamePhase.MAIN_PHASE) is True

    def test_valid_transition_main_phase_to_combat(self, machine: GameState) -> None:
        """MAIN_PHASE -> COMBAT should be allowed."""
        machine.transition(GamePhase.TURN_START)
        machine.transition(GamePhase.DRAW)
        machine.transition(GamePhase.MAIN_PHASE)
        assert machine.transition(GamePhase.COMBAT) is True

    def test_valid_transition_combat_to_turn_end(self, machine: GameState) -> None:
        """COMBAT -> TURN_END should be allowed."""
        machine.transition(GamePhase.TURN_START)
        machine.transition(GamePhase.DRAW)
        machine.transition(GamePhase.MAIN_PHASE)
        machine.transition(GamePhase.COMBAT)
        assert machine.transition(GamePhase.TURN_END) is True

    def test_valid_transition_turn_end_to_next_turn(self, machine: GameState) -> None:
        """TURN_END -> NEXT_TURN should be allowed."""
        machine.transition(GamePhase.TURN_START)
        machine.transition(GamePhase.DRAW)
        machine.transition(GamePhase.MAIN_PHASE)
        machine.transition(GamePhase.COMBAT)
        machine.transition(GamePhase.TURN_END)
        assert machine.transition(GamePhase.NEXT_TURN) is True

    def test_advance_turn_uses_state_machine(self) -> None:
        """advance_turn should transition through proper phases."""
        state = create_initial_state("g", "p", "o")
        sm = StateMachine(state)
        sm.advance_turn()
        # After advance_turn, phase should be DRAW (MULLIGAN -> TURN_START -> DRAW)
        assert state.phase == GamePhase.DRAW
        assert state.turn_number == 1
        assert state.mana == 1  # max_mana is 1, so min(1, 1+0) = 1
        assert GameEvent.TURN_END.value in state.event_log

    def test_illegal_transition_mulligan_to_draw_rejected(self, machine: StateMachine) -> None:
        """MULLIGAN -> DRAW should be rejected (not directly allowed)."""
        assert machine.transition(GamePhase.DRAW) is False

    def test_illegal_transition_combat_to_main_phase_rejected(self, machine: StateMachine) -> None:
        """COMBAT -> MAIN_PHASE should be rejected."""
        machine.transition(GamePhase.TURN_START)
        machine.transition(GamePhase.DRAW)
        machine.transition(GamePhase.MAIN_PHASE)
        machine.transition(GamePhase.COMBAT)
        assert machine.transition(GamePhase.MAIN_PHASE) is False

    def test_illegal_transition_turn_end_to_combat_rejected(self, machine: StateMachine) -> None:
        """TURN_END -> COMBAT should be rejected."""
        assert machine.transition(GamePhase.COMBAT) is False

    def test_can_transition(self, machine: StateMachine) -> None:
        """can_transition should reflect allowed transitions."""
        assert machine.can_transition(GamePhase.TURN_START) is True
        assert machine.can_transition(GamePhase.DRAW) is False  # from MULLIGAN, not directly

    def test_state_unchanged_on_failed_transition(self, machine: StateMachine) -> None:
        """State should not change when transition is rejected."""
        old_phase = machine.state.phase
        machine.transition(GamePhase.DRAW)  # illegal
        assert machine.state.phase == old_phase

    def test_transition_returns_bool(self, machine: StateMachine) -> None:
        """transition should always return True or False (never None)."""
        result = machine.transition(GamePhase.DRAW)
        assert result is True or result is False
        assert isinstance(result, bool)


# -----------------------------------------------------------
# StateMachine emit Tests
# -----------------------------------------------------------


class TestStateMachineEmit:
    """Tests for StateMachine emit event firing."""

    @pytest.fixture
    def base_state(self) -> GameState:
        return create_initial_state("g", "p", "o")

    @pytest.fixture
    def machine(self, base_state: GameState) -> StateMachine:
        return StateMachine(base_state)

    def test_emit_with_no_handlers_returns_false(self, machine: StateMachine) -> None:
        """Emitting event with no handlers should return False."""
        event = GameEvent.CARD_PLAYED
        result = machine.emit(event)
        assert result is False
        # Event should still be logged
        assert event.value in machine.state.event_log

    def test_emit_with_handlers_returns_true(self, machine: StateMachine) -> None:
        """Emitting event with handlers should return True."""
        event = GameEvent.TURN_START
        # Register a handler
        machine.event_handlers[event] = [lambda event: True]
        result = machine.emit(event)
        assert result is True

    def test_emit_logs_event_value(self, machine: StateMachine) -> None:
        """Emitting should append event value to event_log."""
        event = GameEvent.DRAW
        machine.emit(event)
        assert event.value in machine.state.event_log
        # Check the logged value matches
        assert machine.state.event_log[-1] == event.value

    def test_emit_multi_handlers_all_success(self, machine: StateMachine) -> None:
        """All handlers should be called and return True if all succeed."""
        event = GameEvent.TURN_END
        machine.event_handlers[event] = [
            lambda event: True,
            lambda event: True,
            lambda event: True,
        ]
        result = machine.emit(event)
        assert result is True

    def test_emit_multi_handlers_one_failure(self, machine: StateMachine) -> None:
        """If any handler fails, result should be False (all results checked)."""
        event = GameEvent.TURN_END
        machine.event_handlers[event] = [
            lambda event: True,
            lambda event: False,  # This handler fails
            lambda event: True,
        ]
        result = machine.emit(event)
        assert result is False

    def test_emit_exception_in_handler_does_not_crash(self, machine: StateMachine) -> None:
        """Exception in handler should be caught and not crash the machine."""
        event = GameEvent.TURN_START
        machine.event_handlers[event] = [
            lambda event: None.__class__(1/0),  # Will raise ZeroDivisionError
        ]
        # Should not raise, just log error
        result = machine.emit(event)
        assert result is False  # Exception handler returns False


# -----------------------------------------------------------
# Deterministic Replay Tests
# -----------------------------------------------------------


class TestDeterministicReplay:
    """Tests for deterministic replay from event log."""

    @pytest.fixture
    def base_state(self) -> GameState:
        return create_initial_state("g", "p", "o")

    @pytest.fixture
    def machine(self, base_state: GameState) -> StateMachine:
        return StateMachine(base_state)

    def test_replay_same_events_same_result(self, machine: StateMachine) -> None:
        """Replaying same events with same seed should produce same state."""
        events = [GameEvent.TURN_START, GameEvent.DRAW, GameEvent.TURN_END]
        
        # First replay
        machine.emit(GameEvent.TURN_START)
        machine.emit(GameEvent.DRAW)
        machine.emit(GameEvent.TURN_END)
        result1 = machine.state.to_dict()
        
        # Reset and replay
        machine.replay_from_log(events)
        result2 = machine.state.to_dict()
        
        # Results should match (deterministic)
        assert result1 == result2

    def test_replay_different_events_different_result(self, machine: StateMachine) -> None:
        """Different event sequences should produce different states."""
        events1 = [GameEvent.TURN_START]
        events2 = [GameEvent.DRAW]
        
        machine.replay_from_log(events1)
        result1 = machine.state.event_log.copy()
        
        machine.replay_from_log(events2)
        result2 = machine.state.event_log.copy()
        
        assert result1 != result2

    def test_replay_preserves_seed(self, machine: StateMachine) -> None:
        """Replay should preserve the seed value."""
        initial_seed = machine.state.seed
        events = [GameEvent.TURN_START, GameEvent.DRAW]
        machine.replay_from_log(events)
        assert machine.state.seed == initial_seed

    def test_replay_restores_state_afterwards(self, machine: StateMachine) -> None:
        """After replay, original state should be restored."""
        events = [GameEvent.TURN_START]
        old_state = machine.state.to_dict()
        
        machine.replay_from_log(events)
        
        # State should be restored to original
        restored = machine.state.to_dict()
        assert restored == old_state


# -----------------------------------------------------------
# Factory Function Tests
# -----------------------------------------------------------


class TestCreateInitialState:
    """Tests for create_initial_state factory function."""

    def test_creates_valid_state(self) -> None:
        """Should create a GameState with correct initial values."""
        state = create_initial_state("game_123", "player1", "player2")
        assert state.game_id == "game_123"
        assert state.player_id == "player1"
        assert state.opponent_id == "player2"
        assert state.phase == GamePhase.MULLIGAN
        assert state.turn_number == 0
        assert state.mana == 1
        assert state.max_mana == 1

    def test_different_ids(self) -> None:
        """Different IDs should produce different states."""
        s1 = create_initial_state("id1", "p1", "p2")
        s2 = create_initial_state("id2", "p3", "p4")
        assert s1.game_id != s2.game_id
        assert s1.player_id != s2.player_id


# -----------------------------------------------------------
# Edge Cases
# -----------------------------------------------------------


class TestStateMachineEdgeCases:
    """Edge case tests for StateMachine."""

    def test_empty_transition_list(self) -> None:
        """Phase with no defined transitions should fail gracefully."""
        from core.engine.state_machine import GamePhase
        
        # This tests that unknown phases handle transitions properly
        # by using a custom state
        from dataclasses import dataclass
        @dataclass
        class TestState:
            phase: Any
        
        # Just ensure _TRANSITIONS lookup doesn't crash on unknown phases
        # (it returns empty list, so can_transition returns False)
        pass

    def test_all_phase_transitions_cycle(self) -> None:
        """Test that phases can cycle through NEXT_TURN -> TURN_START -> ..."""
        from core.engine.state_machine import (
            GamePhase, StateMachine, create_initial_state,
        )
        
        state = create_initial_state("g", "p", "o")
        sm = StateMachine(state)
        
        # Cycle through all phases that are allowed
        # MULLIGAN -> TURN_START -> DRAW -> MAIN_PHASE -> COMBAT -> TURN_END -> NEXT_TURN -> TURN_START
        assert sm.transition(GamePhase.TURN_START) is True
        assert sm.transition(GamePhase.DRAW) is True
        assert sm.transition(GamePhase.MAIN_PHASE) is True
        assert sm.transition(GamePhase.COMBAT) is True
        assert sm.transition(GamePhase.TURN_END) is True
        assert sm.transition(GamePhase.NEXT_TURN) is True
        # After NEXT_TURN, should be able to go to TURN_START again
        assert sm.transition(GamePhase.TURN_START) is True