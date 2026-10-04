"""Card definitions and registry for Merithra.

Cards are data-driven (JSON/YAML) and loaded at runtime into Python objects.
Effects are composition-based, not inheritance-heavy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from .effects import EffectBundle


class CardType(Enum):
    """Typen von Karten."""
    MINION = auto()
    SPELL = auto()
    WEAPON = auto()
    HERO_POWER = auto()
    LOCATION = auto()  # For future PvE scenarios


class Rarity(Enum):
    """Seltenheitsgrade."""
    FREE = auto()
    COMMON = auto()
    RARE = auto()
    EPIC = auto()
    LEGENDARY = auto()


@dataclass
class Effect:
    """Ein Effekt, der auf ein Target angewendet wird.

    Composition-basiert: Effects werden kombiniert, nicht vererbt.
    """

    type: str  # z.B. "DAMAGE", "HEAL", "SET_ATTACK", "DRAW_CARDS"
    target_filter: str = "ANY"  # "ANY", "MINION", "HERO", "SELF"
    value: Optional[int] = None
    target_id: Optional[str] = None  # Spezifisches Target via ID
    permanent: bool = False  # Dauereffekt vs. einmalig anwenden

    def apply(self, target: Any, game_state: Any) -> None:
        """Wende diesen Effect auf ein Target an.

        Subclasses oder externe Logic können diesen Method override/extend.
        """
        pass


@dataclass
class Card:
    """Repräsentiert eine Spielkarte.

    Alle Daten kommen zur Laufzeit aus JSON/YAML Definitionen.
    """

    id: str
    name: str
    cost: int
    card_type: CardType
    class_type: str  # "NEUTRAL", "WARRIOR", "MAGE", etc.
    rarity: Rarity
    text: str  # Anzeigetext (Tooltip)

    # Basiskarten-Statistiken
    attack: int = 0
    health: int = 0
    durability: Optional[int] = None  # Für Waffen

    # Keywords (kompositorial)
    keywords: List[str] = field(default_factory=list)  # ["TAUNT", "CHARGE", ...]
    windfury: int = 0  # Anzahl verbleibender Angriffe dieses Zuges

    # Strukturierte Effects (für Engine)
    effects: List[Effect] = field(default_factory=list)

    # Metadaten
    set_id: str = ""  # Erweiterung-Set Identifikator
    collectible: bool = True  # Kann in Sammlungen verwendet werden

    def can_play(self, game_state: Any) -> bool:
        """Prüfen, ob die Karte im aktuellen Spielzustand gespielt werden kann.

        Basis-Validierung: Mana prüfen, etc.
        """
        # Wird von der Engine überschrieben/calliert
        return self.cost <= getattr(game_state, "mana", 0)

    def to_dict(self) -> Dict[str, Any]:
        """Nach JSON/Dict für Speicherung/Übertragung."""
        return {
            "id": self.id,
            "name": self.name,
            "cost": self.cost,
            "card_type": self.card_type.name,
            "class_type": self.class_type,
            "rarity": self.rarity.name,
            "text": self.text,
            "attack": self.attack,
            "health": self.health,
            "durability": self.durability,
            "keywords": self.keywords,
            "windfury": self.windfury,
            "effects": [
                e.__dict__ if isinstance(e, Effect) else (e if isinstance(e, dict) else str(e))
                for e in self.effects
            ],
            "set_id": self.set_id,
            "collectible": self.collectible,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Card":
        """Aus Dict erstellen."""
        from .effects import Effect  # Lazy import

        kwargs = {
            "id": data["id"],
            "name": data["name"],
            "cost": data["cost"],
            "card_type": CardType[data["card_type"]],
            "class_type": data["class_type"],
            "rarity": Rarity[data["rarity"]],
            "text": data.get("text", ""),
            "attack": data.get("attack", 0),
            "health": data.get("health", 0),
            "durability": data.get("durability"),
            "keywords": data.get("keywords", []),
            "windfury": data.get("windfury", 0),
            "effects": [Effect.from_dict(ef) if isinstance(ef, dict) else ef for ef in data.get("effects", [])],
            "set_id": data.get("set_id", ""),
            "collectible": data.get("collectible", True),
        }
        return cls(**kwargs)


# ---------------------------------------------------------------------------
# Effect Implementation (simple, extendable)
# ---------------------------------------------------------------------------


@dataclass
class SimpleEffect(Effect):
    """Basis-Implementation eines Effects.

    Die apply-Methode sollte von der Engine aufgerufen werden
    und den Target zustandsverändernd beeinflussen.
    """

    def apply(self, target: Any, game_state: Any) -> None:
        """Standard-Apply-Logik (überschreibbar in Engine)."""
        etype = self.type.lower()

        if etype == "damage":
            if hasattr(target, "take_damage"):
                target.take_damage(self.value, game_state)
            elif hasattr(target, "current_health"):
                max_health = getattr(target, "max_health", 30)
                target.current_health = max(0, min(max_health, (target.current_health or 0) - self.value))

        elif etype == "heal":
            if hasattr(target, "heal"):
                target.heal(self.value)
            elif hasattr(target, "current_health"):
                max_health = getattr(target, "max_health", 30)
                target.current_health = min(max_health, (target.current_health or 0) + self.value)

        elif etype == "set_attack":
            if hasattr(target, "attack"):
                target.attack = self.value

        elif etype == "set_health":
            if hasattr(target, "current_health"):
                target.current_health = self.value

        elif etype == "draw_cards":
            if hasattr(game_state, "draw_cards"):
                game_state.draw_cards(self.value)

        elif etype == "set_max_mana":
            if hasattr(game_state, "max_mana"):
                game_state.max_mana = self.value

        elif etype == "armor":
            if hasattr(target, "armor"):
                target.armor = getattr(target, "armor", 0) + self.value

        elif etype == "unknown":
            pass  # Unbekannter Typ - stilvoll ignorieren

        else:
            # Unbekannter Typ - stilvoll ignorieren
            pass


# Convenience factory for common effects
def create_damage_effect(value: int, target_filter: str = "ANY") -> SimpleEffect:
    return SimpleEffect(type="DAMAGE", target_filter=target_filter, value=value)


def create_heal_effect(value: int) -> SimpleEffect:
    return SimpleEffect(type="HEAL", value=value)


def create_draw_effect(count: int) -> SimpleEffect:
    return SimpleEffect(type="DRAW_CARDS", value=count)


def create_set_max_mana_effect(value: int) -> SimpleEffect:
    return SimpleEffect(type="SET_MAX_MANA", value=value)


# ---------------------------------------------------------------------------
# Card Registry (lädt JSON zur Laufzeit)
# ---------------------------------------------------------------------------


class CardRegistry:
    """Registry für Card-Definitionen.

    Lädt Cards aus JSON-Dateien und verwaltet Lookups per ID/Class/Rarity.
    """

    def __init__(self, paths: Optional[list[str]] = None):
        self._cards: dict[str, Card] = {}  # id -> Card
        self._by_class: dict[str, list[Card]] = {}  # class_type -> [Card]
        self._by_rarity: dict[Rarity, list[Card]] = {}  # Rarity -> [Card]
        self._loaded_from: list[str] = []

        # Default-Pfade suchen
        default_paths = [
            "cards/default.json",
            "data/cards.json",
            "./cards.json",
        ]
        search_paths = paths or default_paths

        for path in search_paths:
            self._load_from_path(path)

    def _load_from_path(self, path: str) -> None:
        """Lade Cards aus einer JSON-Datei."""
        import json
        import os

        if not os.path.exists(path):
            # Try relative to package (optional fallback)
            # NOTE: 'merithra' package import optional; skip if not available
            try:
                import merithra  # type: ignore
                alt = os.path.join(os.path.dirname(merithra.__file__), path)
                if os.path.exists(alt):
                    path = alt
            except ModuleNotFoundError:
                # Package not installed yet - continue without it
                pass

        if not os.path.exists(path):
            return  # File not found, skip silently

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            print(f"[CardRegistry] Failed to load {path}: {exc}")
            return

        self._loaded_from.append(path)

        # JSON kann entweder ein List von Cards oder ein Dict mit "cards" Key sein
        cards_data = data.get("cards", data) if isinstance(data, dict) else data

        if isinstance(cards_data, list):
            for card_data in cards_data:
                try:
                    card = Card.from_dict(card_data)
                    self._add_card(card)
                except Exception as exc:
                    print(f"[CardRegistry] Failed to parse card {card_data.get('id', '?')}: {exc}")

    def _add_card(self, card: Card) -> None:
        """Füge Karte Registry hinzu und aktualisiere Indizes."""
        self._cards[card.id] = card

        # Index nach Klasse
        ct = card.class_type
        self._by_class.setdefault(ct, []).append(card)

        # Index nach Seltenheit
        r = card.rarity
        self._by_rarity.setdefault(r, []).append(card)

    # -------------------------------------------------------------------
    # Lookup-Methoden
    # -------------------------------------------------------------------

    def get(self, card_id: str) -> Optional[Card]:
        """Card per ID abrufen."""
        return self._cards.get(card_id)

    def get_by_class(self, class_type: str) -> list[Card]:
        """Alle Karten einer Klasse zurückgeben."""
        return self._by_class.get(class_type, [])

    def get_by_rarity(self, rarity: Rarity) -> list[Card]:
        """Alle Karten einer Seltenheit zurückgeben."""
        return self._by_rarity.get(rarity, [])

    def get_random(self, rarity: Optional[Rarity] = None, count: int = 1, class_type: Optional[str] = None) -> list[Card]:
        """Zufällige Karten auswählen."""
        import random

        pool = self._cards.values()
        if rarity is not None:
            pool = [c for c in pool if c.rarity is rarity]
        if class_type is not None:
            pool = [c for c in pool if c.class_type == class_type or c.class_type == "NEUTRAL"]

        # Shuffle deterministisch via Seed (aus GameState)
        # hier vereinfacht:
        random.shuffle(list(pool))

        return pool[:count]

    def get_random_starting_deck(self, class_type: str, count: int = 30) -> list[Card]:
        """Erstelle ein Start-Deck für eine Klasse.

        MVP: Einfache Auswahl von Neutral + Class Cards.
        """
        class_cards = self.get_by_class(class_type)
        neutral_cards = self.get_by_class("NEUTRAL")

        deck: list[Card] = []
        # Füge Class Cards hinzu (begrenzte Anzahl)
        deck.extend(class_cards[:count // 2])
        # Rest mit Neutral Cards füllen
        deck.extend(neutral_cards[: (count - len(deck))])

        return deck[:count]


# ---------------------------------------------------------------------------
# Default Card Definitions (MVP - 20 Karten)
# ---------------------------------------------------------------------------
# Diese werden standardmäßig geladen wenn keine externen JSON-Dateien gefunden werden.

DEFAULT_CARDS_JSON = [
    {
        "id": "card_001",
        "name": "Großer Wolf",
        "cost": 3,
        "card_type": "MINION",
        "class_type": "NEUTRAL",
        "rarity": "COMMON",
        "text": "Ein kräftiger Wolf mit Charge.",
        "attack": 3,
        "health": 3,
        "keywords": ["CHARGE"],
        "effects": [
            {"type": "BUFF", "target": "SELF", "value": "+1 Attack this turn"}
        ]
    },
    {
        "id": "card_002",
        "name": "Feuerball",
        "cost": 3,
        "card_type": "SPELL",
        "class_type": "NEUTRAL",
        "rarity": "COMMON",
        "text": "Verursache 6 Schaden einem beliebigen Ziel.",
        "attack": 0,
        "health": 0,
        "effects": [
            {"type": "DAMAGE", "target_filter": "ANY", "value": 6}
        ]
    },
    {
        "id": "card_003",
        "name": "Schildwache",
        "cost": 1,
        "card_type": "MINION",
        "class_type": "NEUTRAL",
        "rarity": "FREE",
        "text": "Schützt den Helden. (Taunt)",
        "attack": 1,
        "health": 1,
        "keywords": ["TAUNT"],
        "effects": []
    },
    {
        "id": "card_004",
        "name": "Pferdebestien",
        "cost": 6,
        "card_type": "MINION",
        "class_type": "NEUTRAL",
        "rarity": "RARE",
        "text": "Sturmpferd mit 6/6 Stats.",
        "attack": 6,
        "health": 6,
        "keywords": [],
        "effects": []
    },
    {
        "id": "card_005",
        "name": "BeschwöreDämon",
        "cost": 5,
        "card_type": "MINION",
        "class_type": "NEUTRAL",
        "rarity": "RARE",
        "text": "Ein mächtiger Dämon mit Lifesteal.",
        "attack": 4,
        "health": 5,
        "keywords": ["LIFESTEAL"],
        "effects": []
    },
    {
        "id": "card_006",
        "name": "Eislanze",
        "cost": 2,
        "card_type": "SPELL",
        "class_type": "NEUTRAL",
        "rarity": "COMMON",
        "text": "Verursache 3 Schaden und Gefrier-ein Ziel.",
        "attack": 0,
        "health": 0,
        "effects": [
            {"type": "DAMAGE", "target_filter": "ANY", "value": 3},
            {"type": "SET_DEFENSE", "target": "SELF", "value": -1}  # Simple placeholder
        ]
    },
    {
        "id": "card_007",
        "name": "Herr der Dinge",
        "cost": 5,
        "card_type": "MINION",
        "class_type": "NEUTRAL",
        "rarity": "EPIC",
        "text": "Edelsteinkämpfer mit Taunt und Divine Shield.",
        "attack": 3,
        "health": 5,
        "keywords": ["TAUNT", "DIVINE_SHIELD"],
        "effects": []
    },
    {
        "id": "card_008",
        "name": "Axt des Kriegers",
        "cost": 2,
        "card_type": "WEAPON",
        "class_type": "NEUTRAL",
        "rarity": "COMMON",
        "durability": 2,
        "text": "Waffe mit 2 Haltbarkeit und 2+ Angriff.",
        "attack": 2,
        "durability": 2,
        "keywords": [],
        "effects": []
    },
    {
        "id": "card_009",
        "name": "Heilung",
        "cost": 2,
        "card_type": "SPELL",
        "class_type": "NEUTRAL",
        "rarity": "COMMON",
        "text": "Stelle 5 Leben wieder her.",
        "attack": 0,
        "health": 0,
        "effects": [
            {"type": "HEAL", "value": 5}
        ]
    },
    {
        "id": "card_010",
        "name": "Drachenfrost",
        "cost": 7,
        "card_type": "SPELL",
        "class_type": "NEUTRAL",
        "rarity": "EPIC",
        "text": "Verursache 5 Schaden. Wenn ein Diener stirbt, zieh eine Karte.",
        "attack": 0,
        "health": 0,
        "effects": [
            {"type": "DAMAGE", "target_filter": "ANY", "value": 5},
            {"type": "DRAW_CARDS", "value": 1}  # Trigger condition simplified
        ]
    },
    {
        "id": "card_011",
        "name": "Sturmgeborener",
        "cost": 2,
        "card_type": "MINION",
        "class_type": "NEUTRAL",
        "rarity": "COMMON",
        "text": "Ist schneller als alle anderen. (Charge)",
        "attack": 2,
        "health": 1,
        "keywords": ["CHARGE"],
        "effects": []
    },
    {
        "id": "card_012",
        "name": "Scharlachroter Priester",
        "cost": 3,
        "card_type": "MINION",
        "class_type": "NEUTRAL",
        "rarity": "RARE",
        "text": "Heilt alle Diener um 1 Leben.",
        "attack": 2,
        "health": 3,
        "keywords": [],
        "effects": [
            {"type": "HEAL", "value": 1, "target_filter": "ALLY"}  # simplified
        ]
    },
    {
        "id": "card_013",
        "name": "Polarm",
        "cost": 4,
        "card_type": "WEAPON",
        "class_type": "NEUTRAL",
        "rarity": "RARE",
        "durability": 3,
        "text": "Eine mächtige Polhammer-Waffe.",
        "attack": 3,
        "durability": 3,
        "keywords": [],
        "effects": []
    },
    {
        "id": "card_014",
        "name": "Zyklon",
        "cost": 10,
        "card_type": "SPELL",
        "class_type": "NEUTRAL",
        "rarity": "LEGENDARY",
        "text": "Verursache 10 Schaden und zieht 2 Karten.",
        "attack": 0,
        "health": 0,
        "effects": [
            {"type": "DAMAGE", "target_filter": "ANY", "value": 10},
            {"type": "DRAW_CARDS", "value": 2}
        ]
    },
    {
        "id": "card_015",
        "name": "Aasgeier",
        "cost": 3,
        "card_type": "MINION",
        "class_type": "NEUTRAL",
        "rarity": "COMMON",
        "text": "Wenn ein Diener stirbt, zieht eine Karte.",
        "attack": 2,
        "health": 3,
        "keywords": ["DEATHRATTLE"],  # For future expansion
        "effects": []
    },
    {
        "id": "card_016",
        "name": "Schwert der Sieges",
        "cost": 5,
        "card_type": "WEAPON",
        "class_type": "NEUTRAL",
        "rarity": "EPIC",
        "durability": 4,
        "text": "+4 Angriff und Lebensraub.",
        "attack": 4,
        "durability": 4,
        "keywords": ["LIFESTEAL"],
        "effects": []
    },
    {
        "id": "card_017",
        "name": "Erdbebenschock",
        "cost": 3,
        "card_type": "SPELL",
        "class_type": "NEUTRAL",
        "rarity": "COMMON",
        "text": "Verursache 4 Schaden allen Dienern.",
        "attack": 0,
        "health": 0,
        "effects": [
            {"type": "DAMAGE", "target_filter": "ALL_ENEMY", "value": 4}
        ]
    },
    {
        "id": "card_018",
        "name": "Arkanes Intelligenz",
        "cost": 2,
        "card_type": "SPELL",
        "class_type": "NEUTRAL",
        "rarity": "COMMON",
        "text": "Ziehe 2 Karten. Wenn ihr ein kostspieligen Zauber spielt, reduziert sich dessen Kosten um (1).",
        "attack": 0,
        "health": 0,
        "effects": [
            {"type": "DRAW_CARDS", "value": 2}
        ]
    },
    {
        "id": "card_019",
        "name": "Wächter des Konzils",
        "cost": 4,
        "card_type": "MINION",
        "class_type": "NEUTRAL",
        "rarity": "RARE",
        "text": "Hat Zauberschutz. Kann nicht von-Zauber getroffen werden.",
        "attack": 3,
        "health": 4,
        "keywords": ["DIVINE_SHIELD"],  # Using as placeholder for Spell Shield
        "effects": []
    },
    {
        "id": "card_020",
        "name": "Großer Dragon",
        "cost": 8,
        "card_type": "MINION",
        "class_type": "NEUTRAL",
        "rarity": "LEGENDARY",
        "text": "Ein uralter Dragon mit 8/8 Stats und Flügelschlag.",
        "attack": 8,
        "health": 8,
        "keywords": ["WINDFURY"],  # For future
        "effects": []
    }
]


# Auto-load defaults on module import (if no external files found)
import os

_default_registry = None


def get_default_registry() -> CardRegistry:
    """Gibt das Standard-Card-Registry zurück (lädt Defaults)."""
    global _default_registry
    if _default_registry is None:
        _default_registry = CardRegistry()
        # Load default JSON cards embedded in this module
        from . import Card, DEFAULT_CARDS_JSON as _default_cards
        for card_data in _default_cards:
            try:
                card = Card.from_dict(card_data)
                _default_registry._add_card(card)
            except Exception as exc:
                print(f"[DefaultRegistry] Failed card {card_data.get('id')}: {exc}")
        # Mark that default data was loaded (for test tracking)
        _default_registry._loaded_from.append("DEFAULT_CARDS_JSON (embedded module data)")
    return _default_registry


# Module-level convenience - lazily initialized
_card_registry: CardRegistry | None = None


def get_card_registry() -> CardRegistry:
    """Gibt das Card-Registry zurück, bei Bedarf initialisiert es Defaults."""
    global _card_registry
    if _card_registry is None:
        _card_registry = get_default_registry()
    return _card_registry


# Modul-level convenience (wird bei Bedarf genutzt)
card_registry = None  # Wird später via init_card_registry() gesetzt

# Export häufig genutzt Klassen
__all__ = [
    "CardType", "Rarity", "Card", "Effect", "SimpleEffect", "EffectBundle",
    "create_damage_effect", "create_heal_effect", "create_draw_effect",
    "create_set_max_mana_effect", "CardRegistry", "get_card_registry",
    "init_card_registry", "get_default_registry"
]