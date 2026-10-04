"""Entity System for Merithra.

Player, Hero, Minion und verwandte Klassen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .cards import Card, CardType, Rarity, Effect, EffectBundle


# ---------------------------------------------------------------------------
# Hero Class
# ---------------------------------------------------------------------------


@dataclass
class Hero:
    """Ein Held/Heldenmacht-Inhaber.

    Attributes:
        name: Held-Name (z.B. "Jaina", "Thrall").
        max_health: Maximale Lebenspunkte.
        current_health: Aktuelle Lebenspunkte.
        armor: Aktuelle Rüstung.
        hero_power: Die unique Heldenmacht-Karte.
        class_type: Klassen-Typ (WARRIOR, MAGE, etc.).
    """

    name: str
    max_health: int
    current_health: int = field(default_factory=lambda: 30)  # Start-HP
    armor: int = 0
    class_type: str = "NEUTRAL"  # z.B. "WARRIOR", "MAGE", "PALADIN"
    hero_power: Optional[Card] = None  # Die Heldenmacht-Karte

    # Metadata
    title: str = ""  # Optional: "the Lich King", etc.

    def is_alive(self) -> bool:
        return self.current_health > 0

    def take_damage(self, amount: int, game_state: Any) -> None:
        """Nimm Schaden (inkl. Rüstung reduzieren)."""
        # Rüstung absorbiert zuerst
        actual_damage = max(0, amount - self.armor)
        self.current_health = max(0, self.current_health - actual_damage)
        # Überschüssige Rüstung wird nicht "gespeichert", sie wird verbraucht
        # (Alternative: Rüstung bleibt, Schaden trifft zuerst Rüstung)
        if actual_damage > 0:
            self.armor = max(0, self.armor - (amount - actual_damage))  # Simplified

    def heal(self, amount: int) -> None:
        """Heile den Helden."""
        self.current_health = min(self.max_health, self.current_health + amount)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "max_health": self.max_health,
            "current_health": self.current_health,
            "armor": self.armor,
            "class_type": self.class_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Hero":
        return cls(
            name=data["name"],
            max_health=data["max_health"],
            current_health=data.get("current_health", 30),
            armor=data.get("armor", 0),
            class_type=data.get("class_type", "NEUTRAL"),
        )


# ---------------------------------------------------------------------------
# Player Class
# ---------------------------------------------------------------------------


@dataclass
class Player:
    """Ein Spieler im Spiel.

    Attributes:
        hero: Der Held des Spielers.
        deck: Das Deck (Liste von Card-Objekten).
        hand: Aktive Karten in der Hand.
        board: Gefeldete Minionen (max. 7 Slots).
        graveyard: Verbrauchte/kardierte Karten.
        mana: Aktuelles Mana.
        max_mana: Maximales Mana pro Zug.
        turn_number: Aktuelle Turn-Nummer.
        fatigue: Fatigue-Schaden counter (später).
    """

    hero: Hero
    deck: list[Card] = field(default_factory=list)
    hand: list[Card] = field(default_factory=list)
    board: list[Any] = field(default_factory=list)  # Minion-Objekte
    graveyard: list[Card] = field(default_factory=list)
    mana: int = 1
    max_mana: int = 1
    turn_number: int = 0
    fatigue: int = 0

    # Referenz zum Spiel-Engine-State (optional)
    game_state: Optional[Any] = None

    def draw_card(self) -> Optional[Card]:
        """Ziehe eine Karte aus dem Deck.

        Returns die gezogene Karte oder None wenn Deck leer.
        """
        if not self.deck:
            # Fatigue damage
            self.fatigue += 1
            self.hero.take_damage(self.fatigue, self.game_state) if self.hero else None
            return None

        card = self.deck.pop(0)  # Einfaches Ziehen von oben
        self.hand.append(card)
        return card

    def play_card(self, card_id: str, target: Optional[Any] = None) -> bool:
        """Spiele eine Karte aus der Hand.

        Returns True wenn erfolgreich.
        """
        # Karte in Hand finden
        card = next((c for c in self.hand if c.id == card_id), None)
        if not card:
            return False

        # Basic Cost Check
        if card.cost > self.mana:
            return False  # Not enough mana

        # Remove from hand
        self.hand.remove(card)

        # Reduce mana
        self.mana -= card.cost

        # Eventuell Effects anwenden (temporär, bis Engine full Integration)
        # For now, just return True (UI/Engine handles the rest)
        return True

    def end_turn(self) -> None:
        """Ende des Zuges: Mana resetzen, Karte ziehen, Phase wechseln."""
        self.mana = self.max_mana  # Reset auf Max (oder +1 "Mana curve" Logic)
        self.draw_card()
        self.turn_number += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hero": self.hero.to_dict() if self.hero else {},
            "deck": [c.to_dict() for c in self.deck],
            "hand": [c.to_dict() for c in self.hand],
            "board": [m.to_dict() if hasattr(m, "to_dict") else str(m) for m in self.board],
            "graveyard": [c.to_dict() for c in self.graveyard],
            "mana": self.mana,
            "max_mana": self.max_mana,
            "turn_number": self.turn_number,
            "fatigue": self.fatigue,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        from .cards import Card

        hero_data = data.get("hero", {})
        hero = Hero.from_dict(hero_data) if hero_data else Hero(name="Hero", max_health=30)

        deck_data = data.get("deck", [])
        deck = [Card.from_dict(c) for c in deck_data if c]

        hand_data = data.get("hand", [])
        hand = [Card.from_dict(c) for c in hand_data if c]

        board_data = data.get("board", [])
        # Board enthält Minions - simplified hier
        board = board_data  # In Vollversion: Minion-Objekte rehydrieren

        return cls(
            hero=hero,
            deck=deck,
            hand=hand,
            board=board,
            mana=data.get("mana", 1),
            max_mana=data.get("max_mana", 1),
            turn_number=data.get("turn_number", 0),
            fatigue=data.get("fatigue", 0),
        )


# ---------------------------------------------------------------------------
# Minion Class (Diener auf dem Board)
# ---------------------------------------------------------------------------


@dataclass
class Minion:
    """Ein Diener, der auf dem Board steht.

    Attributes:
        card: Die Card-Definition (statisch).
        owner: Der Spieler, der diesen Diener kontrolliert.
        current_health: Aktuelle Lebenspunkte (startet bei card.health).
        has_taunt: Ob dieser Diener Taunt hat.
        divine_shield: Ob dieser Diener Divine Shield hat.
        enraged: Ob dieser Diener "Enrage" ist (schneller/schlager).
        windfury: Ob dieser Diener Windfury hat (zweimal angreifen).
        can_attack: Ob dieser Diener in diesem Zug angreifen darf.
        die_die_this_turn: Flag für Deathrattle-Trigger.
    """

    card: Card
    owner: Player
    current_health: Optional[int] = None  # Wird auf card.health initialisiert
    has_taunt: bool = False
    divine_shield: bool = False
    enraged: bool = False
    windfury: int = 0  # Anzahl verbleibender Angriffe dieses Zuges (meist 1 oder 2)
    can_attack: bool = False  # Wird am Zugbeginn auf True gesetzt
    _has_attacked_this_turn: bool = False  # Tracking für Attack Limit

    # Deathrattle & Triggers
    deathrattle_effects: list[Effect] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialisierung nach Erstellung."""
        if self.current_health is None:
            self.current_health = self.card.health
        # can_attack Logic: Nur wenn Diener schon auf Board war oder Zug begann
        # Einfaches Regel: can_attack = True nach TURN_START

    @property
    def attack(self) -> int:
        """Attack-Wert, inkl. möglicher Buffs/Keywords."""

        # Basis-Attack aus Card
        base = self.card.attack

        # Keyword-Modifikatoren (vereinfacht)
        # Windfury & Enrage etc. würden hier addiert werden
        return base

    def is_alive(self) -> bool:
        return self.current_health > 0

    def take_damage(self, amount: int, game_state: Any) -> bool:
        """Nimm Schaden. Returns True wenn Diener gestorben ist.

        Berücksichtigt Divine Shield und Taunt-Logik (vom Engine aufgerufen).
        """
        # Divine Shield blockiert ersten Schaden und verschwindet
        if self.divine_shield:
            self.divine_shield = False
            # Schaden wird komplett abgefedert, aber Shield verschwindet
            return False

        self.current_health -= amount

        # Check death
        if self.current_health <= 0:
            # Trigger Deathrattle
            self._trigger_deathrattle(game_state)
            return True  # Diener gestorben

        return False

    def _trigger_deathrattle(self, game_state: Any) -> None:
        """Aktiviere Deathrattle Effects."""
        for effect in self.deathrattle_effects:
            # Einfaches Anwenden (Target hängt von Effekt ab)
            # game_state oder Owner könnten Target sein
            try:
                effect.apply(self, game_state)
            except Exception:
                pass  # Fehler ignorieren fürs MVP

    def can_attack_target(self, target: Any, game_state: Any) -> bool:
        """Prüfe, ob dieser Minion dieses Ziel angreifen kann.

        Prüft: Taunt des Ziels, Divine Shield etc.
        """
        # Vereinfacht: Wenn Ziel Taunt hat, muss dieser Minion nicht angreifen
        # oder nur Minions mit Taunt angreifen.
        if hasattr(target, "has_taunt") and target.has_taunt:
            # In einem vollen System würde hier geprüft, ob ein anderer Minion
            # mit Taunt vorhanden ist. Hier: Erlaube trotzdem (oder blockiere).
            pass

        # Windfury: Erlaubt zusätzlichen Angriff
        # kann_attack tracking happens elsewhere

        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "card_id": self.card.id if self.card else None,
            "card_name": self.card.name if self.card else None,
            "card_cost": self.card.cost if self.card else None,
            "card_text": self.card.text if self.card else None,
            "card_keywords": self.card.keywords if self.card else [],
            "owner_name": self.owner.hero.name if self.owner else None,
            "current_health": self.current_health,
            "has_taunt": self.has_taunt,
            "divine_shield": self.divine_shield,
            "windfury": self.windfury,
            "can_attack": self.can_attack,
            "attack": self.attack,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], owner: Player) -> "Minion":
        from .cards import Card

        card_id = data.get("card_id")
        card_name = data.get("card_name")
        card_cost = data.get("card_cost")
        card_text = data.get("card_text")
        card_keywords = data.get("card_keywords", [])

        card = card_registry.get(card_id) if card_registry and card_id else None  # Module-level ref

        # Fallback: Card neu erstellen wenn nicht in Registry (vereinfacht)
        if not card:
            # Einfache Fallback-Card erzeugen
            card = Card(
                id=card_id or "unknown",
                name=card_name or "Minion",
                cost=card_cost if card_cost is not None else 0,
                card_type=CardType.MINION,
                class_type=data.get("class_type", "NEUTRAL"),
                rarity=data.get("rarity", Rarity.COMMON),
                text=card_text if card_text is not None else "",
                attack=data.get("attack", 1),
                health=data.get("health", 3),
                keywords=card_keywords if card_keywords is not None else [],
            )

        return cls(
            card=card,
            owner=owner,
            current_health=data.get("current_health", card.health if card else 3),
            has_taunt=data.get("has_taunt", False),
            divine_shield=data.get("divine_shield", False),
            enraged=data.get("enraged", False),
            windfury=data.get("windfury", 0),
            can_attack=data.get("can_attack", False),
            deathrattle_effects=[Effect.from_dict(e) if isinstance(e, dict) else e for e in data.get("deathrattle_effects", [])],
        )


# Module-level Registry Reference (wird initialisiert bei Game Setup)
card_registry = None  # Wird im Game Setup gesetzt


def init_card_registry(registry) -> None:
    """Setze das Modul-level Registry nach dem Laden."""
    global card_registry
    card_registry = registry