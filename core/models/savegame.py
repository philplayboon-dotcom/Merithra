"""Unified Save Game Data Model for persistent campaign progress."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import json

from .economy import Inventory, CurrencyWallet
from .professions import ProfessionState, ProfessionType
from .quests import Quest, QuestStatus


@dataclass
class DeckRecord:
    """A saved deck definition."""
    id: str
    name: str
    hero_class: str
    card_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "hero_class": self.hero_class,
            "card_ids": list(self.card_ids),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeckRecord":
        return cls(
            id=data["id"],
            name=data["name"],
            hero_class=data.get("hero_class", "NEUTRAL"),
            card_ids=list(data.get("card_ids", [])),
        )


@dataclass
class SaveGameData:
    """Comprehensive save file structure representing player's complete state."""
    version: int = 1
    save_id: str = "slot_1"
    player_name: str = "Reisender"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    play_time_seconds: int = 0

    # Campaign & Location
    current_chapter: int = 1
    current_city_id: str = "city_oakhaven"
    unlocked_city_ids: List[str] = field(default_factory=lambda: ["city_oakhaven"])

    # Economy & Items
    wallet: CurrencyWallet = field(default_factory=CurrencyWallet)
    inventory: Inventory = field(default_factory=Inventory)

    # Cards & Decks
    collection_card_ids: List[str] = field(default_factory=list)  # Owned card pool
    decks: List[DeckRecord] = field(default_factory=list)
    active_deck_id: Optional[str] = None

    # Quests & Encounters
    quests: Dict[str, Quest] = field(default_factory=dict)
    completed_encounter_ids: List[str] = field(default_factory=list)
    claimed_one_time_rewards: List[str] = field(default_factory=list)

    # Professions
    professions: Dict[str, ProfessionState] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "save_id": self.save_id,
            "player_name": self.player_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "play_time_seconds": self.play_time_seconds,
            "current_chapter": self.current_chapter,
            "current_city_id": self.current_city_id,
            "unlocked_city_ids": list(self.unlocked_city_ids),
            "wallet": self.wallet.to_dict(),
            "inventory": self.inventory.to_dict(),
            "collection_card_ids": list(self.collection_card_ids),
            "decks": [d.to_dict() for d in self.decks],
            "active_deck_id": self.active_deck_id,
            "quests": {k: q.to_dict() for k, q in self.quests.items()},
            "completed_encounter_ids": list(self.completed_encounter_ids),
            "claimed_one_time_rewards": list(self.claimed_one_time_rewards),
            "professions": {k: p.to_dict() for k, p in self.professions.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SaveGameData":
        decks_data = data.get("decks", [])
        decks = [DeckRecord.from_dict(d) for d in decks_data]

        quests_data = data.get("quests", {})
        quests = {k: Quest.from_dict(v) for k, v in quests_data.items()}

        profs_data = data.get("professions", {})
        professions = {k: ProfessionState.from_dict(v) for k, v in profs_data.items()}

        return cls(
            version=data.get("version", 1),
            save_id=data.get("save_id", "slot_1"),
            player_name=data.get("player_name", "Reisender"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            play_time_seconds=data.get("play_time_seconds", 0),
            current_chapter=data.get("current_chapter", 1),
            current_city_id=data.get("current_city_id", "city_oakhaven"),
            unlocked_city_ids=list(data.get("unlocked_city_ids", ["city_oakhaven"])),
            wallet=CurrencyWallet.from_dict(data.get("wallet", {})),
            inventory=Inventory.from_dict(data.get("inventory", {})),
            collection_card_ids=list(data.get("collection_card_ids", [])),
            decks=decks,
            active_deck_id=data.get("active_deck_id"),
            quests=quests,
            completed_encounter_ids=list(data.get("completed_encounter_ids", [])),
            claimed_one_time_rewards=list(data.get("claimed_one_time_rewards", [])),
            professions=professions,
        )


def create_new_savegame(player_name: str = "Reisender", starting_class: str = "MAGE") -> SaveGameData:
    """Factory creating a fully initialized starting savegame."""
    from core.cards import get_card_registry
    registry = get_card_registry()

    # Initial starter cards
    starting_deck_cards = registry.get_random_starting_deck(starting_class, count=20)
    card_ids = [c.id for c in starting_deck_cards]

    default_deck = DeckRecord(
        id="starter_deck",
        name=f"Startdeck ({starting_class})",
        hero_class=starting_class,
        card_ids=card_ids,
    )

    save = SaveGameData(
        player_name=player_name,
        wallet=CurrencyWallet(gold=50),
        collection_card_ids=list(card_ids),
        decks=[default_deck],
        active_deck_id="starter_deck",
    )

    # Initial starter professions
    save.professions[ProfessionType.ALCHEMIST.value] = ProfessionState(
        profession=ProfessionType.ALCHEMIST,
        level=1,
        unlocked_recipe_ids=["rec_healing_salve"],
    )

    # Initial starter items
    save.inventory.add_item("wolf_pelt", 3)
    save.inventory.add_item("healing_salve", 2)

    return save
