"""Effects System for Merithra.

Composition-based effects that can be applied to targets during game play.

Effects are simple dataclasses with a `type` string and `value`.
The Engine interprets these types and applies the appropriate logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Effect:
    """Basis-Effect-Klasse.

    Attributes:
        type: Der Effect-Typ (z.B. "DAMAGE", "HEAL", "DRAW_CARDS").
        target_filter: Wer betroffen ist ("ANY", "MINION", "HERO", "SELF").
        value: Der numerische Wert (Schaden, Heilung, Kartenanzahl etc.).
        target_id: Optional spezifisches Target (falls mehrere Kandidaten existieren).
        permanent: Ob der Effekt dauerhaft ist (z.B. Buff) oder einmalig.
    """

    type: str
    target_filter: str = "ANY"
    value: int = 0
    target_id: str | None = None
    permanent: bool = False

    def apply(self, target: Any, game_state: Any) -> None:
        """Wende den Effect auf ein Target an.

        Ruft entsprechende Methoden des Targets auf, falls vorhanden,
        und passt bei fehlender API direkte Attribute an.
        """
        # Normalisieren für einfachen Match
        eff_type = self.type.upper().strip()

        try:
            if eff_type == "DAMAGE":
                if hasattr(target, "take_damage"):
                    target.take_damage(self.value or 0, game_state)
                elif hasattr(target, "current_health"):
                    target.current_health = max(0, (target.current_health or 0) - (self.value or 0))

            elif eff_type == "HEAL":
                if hasattr(target, "heal"):
                    target.heal(self.value or 0)
                elif hasattr(target, "current_health"):
                    max_health = getattr(target, "max_health", 30)
                    target.current_health = min(max_health, (target.current_health or 0) + (self.value or 0))

            elif eff_type == "SET_ATTACK":
                if hasattr(target, "attack"):
                    target.attack = self.value or 0

            elif eff_type == "SET_HEALTH":
                if hasattr(target, "current_health"):
                    target.current_health = self.value or 0

            elif eff_type == "DRAW_CARDS":
                if hasattr(game_state, "draw_cards"):
                    game_state.draw_cards(self.value or 0)

            elif eff_type == "SET_MAX_MANA":
                if hasattr(game_state, "max_mana"):
                    game_state.max_mana = self.value or 0

            elif eff_type == "ARMOR":
                if hasattr(target, "armor"):
                    target.armor = getattr(target, "armor", 0) + (self.value or 0)

            elif eff_type == "POISONOUS":
                pass  # Wird von der Engine bei Kampfabschluss verarbeitet

            elif eff_type == "WINDFURY":
                pass  # Wird von der Engine bei Angriffen verarbeitet

            elif eff_type == "LIFESTEAL":
                pass  # Wird von der Engine bei Schadensverteilung verarbeitet

            else:
                # Unbekannter Typ - stilvoll ignorieren oder loggen
                pass
        except Exception:
            # Fehler im Effekt sollten das Spiel nicht abstürzen lassen
            pass

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Effect":
        """Effect aus einer serialisierten Darstellung erstellen."""
        return cls(
            type=data.get("type", ""),
            target_filter=data.get("target_filter", "ANY"),
            value=data.get("value", 0),
            target_id=data.get("target_id"),
            permanent=data.get("permanent", False),
        )


# Convenience-Factory-Funktionen für gängige Effects


def damage(value: int, target_filter: str = "ANY") -> Effect:
    return Effect(type="DAMAGE", target_filter=target_filter, value=value)


def heal(value: int) -> Effect:
    return Effect(type="HEAL", value=value)


def set_attack(value: int) -> Effect:
    return Effect(type="SET_ATTACK", value=value)


def set_health(value: int) -> Effect:
    return Effect(type="SET_HEALTH", value=value)


def draw_cards(count: int) -> Effect:
    return Effect(type="DRAW_CARDS", value=count)


def set_max_mana(value: int) -> Effect:
    return Effect(type="SET_MAX_MANA", value=value)


def armor(value: int) -> Effect:
    return Effect(type="ARMOR", value=value)


# ---------------------------------------------------------------------------
# Effect Collection (für Karten)


@dataclass
class EffectBundle:
    """Sammlung von Effects, die auf einer Karte definiert sind.

    Ermöglicht es, mehrere Effects pro Karte zu haben und sie
    nacheinander anzuwenden.
    """

    effects: list[Effect] = field(default_factory=list)

    def add(self, effect: Effect) -> None:
        self.effects.append(effect)

    def apply_all(self, target: Any, game_state: Any) -> None:
        """Wende alle Effects nacheinander an."""
        for eff in self.effects:
            eff.apply(target, game_state)