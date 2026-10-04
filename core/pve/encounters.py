"""Encounter Definitions and Boss Mechanics for Merithra PvE.

Encounters define opponent deck presets, health, special abilities,
dialogues, and guaranteed/repeatable rewards.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.cards import Card, get_card_registry
from core.entities import Hero, Player
from .ai import AIArchetype


@dataclass
class EncounterReward:
    """Rewards granted upon victory."""
    gold: int = 0
    experience: int = 0
    guaranteed_cards: List[str] = field(default_factory=list)
    possible_materials: Dict[str, int] = field(default_factory=dict)
    is_first_clear_only: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gold": self.gold,
            "experience": self.experience,
            "guaranteed_cards": list(self.guaranteed_cards),
            "possible_materials": dict(self.possible_materials),
            "is_first_clear_only": self.is_first_clear_only,
        }


@dataclass
class Encounter:
    """A PvE encounter configuration."""
    id: str
    name: str
    description: str
    hero_name: str
    hero_class: str
    max_health: int
    archetype: AIArchetype = AIArchetype.MIDRANGE
    deck_card_ids: List[str] = field(default_factory=list)
    rewards: EncounterReward = field(default_factory=EncounterReward)
    intro_dialogue: str = ""
    victory_dialogue: str = ""
    defeat_dialogue: str = ""

    def create_opponent_player(self) -> Player:
        """Instantiate a ready-to-play Player instance for this encounter."""
        registry = get_card_registry()
        hero = Hero(
            name=self.hero_name,
            max_health=self.max_health,
            current_health=self.max_health,
            class_type=self.hero_class,
        )

        deck: List[Card] = []
        for card_id in self.deck_card_ids:
            card = registry.get(card_id)
            if card:
                deck.append(card)

        # Fallback if deck is empty: provide standard class deck
        if not deck:
            deck = registry.get_random_starting_deck(self.hero_class, count=20)

        player = Player(hero=hero, deck=deck, mana=1, max_mana=1)
        # Draw initial hand (3 cards for opponent)
        for _ in range(3):
            player.draw_card()
        return player

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "hero_name": self.hero_name,
            "hero_class": self.hero_class,
            "max_health": self.max_health,
            "archetype": self.archetype.value,
            "deck_card_ids": self.deck_card_ids,
            "rewards": self.rewards.to_dict(),
            "intro_dialogue": self.intro_dialogue,
            "victory_dialogue": self.victory_dialogue,
            "defeat_dialogue": self.defeat_dialogue,
        }


# Standard Starter Encounters for Campaign / Testing
DEFAULT_ENCOUNTERS: Dict[str, Encounter] = {
    "enc_wild_wolf": Encounter(
        id="enc_wild_wolf",
        name="Wildes Wolfsrudel",
        description="Ein Rudel hungriger Wölfe greift aus dem Dickicht an.",
        hero_name="Leitwolf",
        hero_class="NEUTRAL",
        max_health=15,
        archetype=AIArchetype.AGGRESSIVE,
        deck_card_ids=["card_001", "card_001", "card_002", "card_002", "card_003"],
        rewards=EncounterReward(
            gold=25,
            experience=50,
            guaranteed_cards=["card_001"],
            possible_materials={"wolf_pelt": 1},
        ),
        intro_dialogue="Ein tiefes Knurren hallt durch den Wald...",
        victory_dialogue="Das Rudel zieht sich jaulend zurück.",
        defeat_dialogue="Die Wölfe überwältigen dich. Sammle deine Kräfte und versuche es erneut.",
    ),
    "enc_bandit_leader": Encounter(
        id="enc_bandit_leader",
        name="Banditenanführer Goran",
        description="Ein gerissener Wegelagerer, der den Pass nach Oakhaven blockiert.",
        hero_name="Goran der Schlächter",
        hero_class="WARRIOR",
        max_health=25,
        archetype=AIArchetype.MIDRANGE,
        deck_card_ids=[
            "card_001", "card_002", "card_003", "card_008",
            "card_009", "card_010", "card_011", "card_012",
        ],
        rewards=EncounterReward(
            gold=60,
            experience=120,
            guaranteed_cards=["card_008"],
            possible_materials={"iron_scrap": 2, "bandit_coin": 1},
        ),
        intro_dialogue="Zoll oder dein Leben, Reisender!",
        victory_dialogue="Goran lässt seine Axt fallen und flieht.",
        defeat_dialogue="Goran triumphiert. Doch dein Wille bleibt ungebrochen.",
    ),
}


def get_encounter(encounter_id: str) -> Optional[Encounter]:
    """Retrieve an encounter by ID."""
    return DEFAULT_ENCOUNTERS.get(encounter_id)
