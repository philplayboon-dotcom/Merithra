"""Core Game State Machine for Merithra.

Deterministic state machine managing game phases and events for replay capability.
"""

from __future__ import annotations

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class GamePhase(Enum):
    """Phasen des Spielzuges."""
    MULLIGAN = auto()         # Start-Mulligan vor erstem Zug
    TURN_START = auto()       # Beginn des Zuges
    DRAW = auto()             # Karte ziehen
    MAIN_PHASE = auto()       # Hauptphase: Karten spielen, angreifen
    COMBAT = auto()           # Expliziter Kampfphase (optional)
    TURN_END = auto()         # Zug beenden
    NEXT_TURN = auto()        # Übergang zum nächsten Spieler


class GameEvent(Enum):
    """Events, die während des Spiels feuern."""
    CARD_PLAYED = "on_card_played"
    MINION_SUMMONED = "on_minion_summoned"
    MINION_DIED = "on_minion_died"
    DAMAGE_DEALT = "on_damage_dealt"
    HERO_POWER_USED = "on_hero_power_used"
    TURN_START = "on_turn_start"
    TURN_END = "on_turn_end"
    DRAW = "on_draw"
    GAME_END = "on_game_end"


@dataclass
class GameState:
    """Der gesamte Spielzustand (deterministisch für Replays)."""

    game_id: str
    player_id: str
    opponent_id: str

    phase: GamePhase = GamePhase.MULLIGAN
    turn_number: int = 0
    mana: int = 1
    max_mana: int = 1

    # Für deterministisches Random (Shuffling, etc.)
    seed: int = field(default_factory=lambda: __import__("random").getrandbits(64))
    event_log: List[str] = field(default_factory=list)

    # Zusätzliche Spielzustände können hier hinzugefügt werden
    # z.B. held_health, board, hand, deck etc.

    def advance_turn(self) -> None:
        """Nächsten Turn vorbereiten (Mana erhöhen, Phase wechseln)."""
        self.turn_number += 1
        self.mana = min(self.max_mana, self.mana + 1)
        self.event_log.append(GameEvent.TURN_END.value)

    def to_dict(self) -> Dict[str, Any]:
        """Serialisierung nach JSON/Dict."""
        return {
            "game_id": self.game_id,
            "player_id": self.player_id,
            "opponent_id": self.opponent_id,
            "phase": self.phase.name,
            "turn_number": self.turn_number,
            "mana": self.mana,
            "max_mana": self.max_mana,
            "seed": self.seed,
            "event_log": self.event_log,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameState":
        """Deserialisierung aus Dict."""
        from .state_machine import GamePhase  # Avoid circular import in some contexts

        return cls(
            game_id=data["game_id"],
            player_id=data["player_id"],
            opponent_id=data["opponent_id"],
            phase=GamePhase[data["phase"]],
            turn_number=data.get("turn_number", 0),
            mana=data.get("mana", 1),
            max_mana=data.get("max_mana", 1),
            seed=data.get("seed", __import__("random").getrandbits(64)),
            event_log=data.get("event_log", []),
        )


class StateMachine:
    """Deterministische Game State Machine mit Event-Handling."""

    # Phase transitions: current_phase -> [mögliche_next_phasen]
    _TRANSITIONS: dict[GamePhase, list[GamePhase]] = {
        GamePhase.MULLIGAN: [GamePhase.TURN_START],
        GamePhase.TURN_START: [GamePhase.DRAW],
        GamePhase.DRAW: [GamePhase.MAIN_PHASE],
        GamePhase.MAIN_PHASE: [GamePhase.COMBAT, GamePhase.TURN_END],
        GamePhase.COMBAT: [GamePhase.TURN_END],
        GamePhase.TURN_END: [GamePhase.NEXT_TURN],
        GamePhase.NEXT_TURN: [GamePhase.TURN_START],  # Neue Runde beginnt
    }

    def __init__(self, initial_state: GameState, event_handlers: Optional[Dict[GameEvent, list]] = None):
        self.state: GameState = initial_state
        self.event_handlers: dict[GameEvent, list] = event_handlers or {}
        # Ensure every known event has an empty list if not provided
        for ev in GameEvent:
            if ev not in self.event_handlers:
                self.event_handlers[ev] = []

    def can_transition(self, target: GamePhase) -> bool:
        """Prüfen, ob Transition von current phase nach target möglich."""
        allowed = self._TRANSITIONS.get(self.state.phase, [])
        return target in allowed

    def advance_turn(self) -> None:
        """Wechsel zum nächsten Zug: MULLIGAN -> TURN_START -> DRAW.

        Führt die Phasenübergänge durch und erhöht Turn/Mana.
        """
        if self.state.phase == GamePhase.MULLIGAN:
            self.transition(GamePhase.TURN_START)
        if self.state.phase == GamePhase.TURN_START:
            self.transition(GamePhase.DRAW)
        # Mana erhöhen (wie von GameState.advance_turn)
        self.state.turn_number += 1
        self.state.mana = min(self.state.max_mana, self.state.mana + 1)
        self.state.event_log.append(GameEvent.TURN_END.value)

    def transition(self, target: GamePhase) -> bool:
        """Transition zur Ziel-Phase durchführen wenn erlaubt.

        Returns True wenn erfolgreich, False wenn Transition verboten.
        """
        if not self.can_transition(target):
            return False

        # Event vor Phase wechseln feuern (optional)
        # self.emit(GameEvent(f"transition_to_{target.name}"), ...)

        self.state.phase = target
        return True

    def emit(self, event: GameEvent, **data: Any) -> bool:
        """Event feuern und alle registrierten Handler aufrufen.

        Returns True wenn mind. ein Handler aufgerufen wurde.
        """
        self.state.event_log.append(event.value)

        handlers = self.event_handlers.get(event, [])
        if not handlers:
            return False

        results = []
        for handler in handlers:
            try:
                result = handler(event=self, **data)
                results.append(result)
            except Exception as exc:  # pragma: no cover
                # Log error but don't crash the game
                print(f"[StateMachine] Error in event handler {handler}: {exc}")
                results.append(False)

        return all(results) if results else True

    def replay_from_log(self, events: list[GameEvent]) -> GameState:
        """Deterministisches Replay aus Event-Log.

        Wichtig: muss bei gleichem Seed gleiche Ergebnisse liefern.
        """
        # Save current state
        old_state = self.state.to_dict()
        old_handlers = {k: list(v) for k, v in self.event_handlers.items()}

        try:
            # Reset to initial-ish state and replay
            # (Vereinfacht: wir gehen davon aus, dass der Caller den Zustand zurücksetzt)
            for ev in events:
                self.emit(ev)
            return self.state
        finally:
            # Restore original state (good practice if caller wants to continue)
            self.state = GameState.from_dict(old_state)
            self.event_handlers = old_handlers

    def __repr__(self) -> str:
        return f"<StateMachine phase={self.state.phase.name} turn={self.state.turn_number}>"


# Convenience factory for initial state
def create_initial_state(game_id: str, player_id: str, opponent_id: str) -> GameState:
    """Erstelle einen initialen GameState für den Start."""
    return GameState(
        game_id=game_id,
        player_id=player_id,
        opponent_id=opponent_id,
        phase=GamePhase.MULLIGAN,
        mana=1,
        max_mana=1,
    )