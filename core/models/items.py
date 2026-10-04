"""Data models for Items, Materials, and Trade Goods in Merithra."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, Optional


class ItemType(Enum):
    """Categorization of items."""
    MATERIAL = "material"            # Crafting ingredients (ores, herbs, pelt, etc.)
    CONSUMABLE = "consumable"        # Potions, rations, buffs
    TRADE_GOOD = "trade_good"        # Regional trade commodities (spices, silk, timber)
    EQUIPMENT = "equipment"          # Artifacts, hero accessories
    RECIPE_SCROLL = "recipe_scroll"  # Teaches new crafting recipes


class ItemRarity(Enum):
    """Item quality tiers."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class Item:
    """Base data definition for any item or material."""
    id: str
    name: str
    description: str
    item_type: ItemType
    rarity: ItemRarity = ItemRarity.COMMON
    base_value: int = 1              # Base sell/buy value in Gold
    max_stack: int = 99              # Maximum quantity per inventory stack
    is_quest_item: bool = False
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type.value,
            "rarity": self.rarity.value,
            "base_value": self.base_value,
            "max_stack": self.max_stack,
            "is_quest_item": self.is_quest_item,
            "attributes": dict(self.attributes),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Item":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            item_type=ItemType(data.get("item_type", "material")),
            rarity=ItemRarity(data.get("rarity", "common")),
            base_value=data.get("base_value", 1),
            max_stack=data.get("max_stack", 99),
            is_quest_item=data.get("is_quest_item", False),
            attributes=data.get("attributes", {}),
        )


# Standard Item Definitions
DEFAULT_ITEMS: Dict[str, Item] = {
    "wolf_pelt": Item(
        id="wolf_pelt",
        name="Wolfsfell",
        description="Ein dichtes, warmes Fell eines Waldwolfs. Beliebt bei Gerbern.",
        item_type=ItemType.MATERIAL,
        base_value=5,
    ),
    "iron_scrap": Item(
        id="iron_scrap",
        name="Alteisen",
        description="Rostige Metallstücke, die von Schmieden wieder eingeschmolzen werden können.",
        item_type=ItemType.MATERIAL,
        base_value=3,
    ),
    "silver_ore": Item(
        id="silver_ore",
        name="Silbererz",
        description="Glänzendes Erz aus den Tiefen von Oakhaven.",
        item_type=ItemType.MATERIAL,
        rarity=ItemRarity.UNCOMMON,
        base_value=15,
    ),
    "healing_salve": Item(
        id="healing_salve",
        name="Heilsalbe",
        description="Eine kühlende Kräutersalbe, die im Kampf oder auf Reisen heilt.",
        item_type=ItemType.CONSUMABLE,
        base_value=10,
    ),
    "spices_oakhaven": Item(
        id="spices_oakhaven",
        name="Oakhaven-Gewürze",
        description="Aromatische Waldkräuter und Gewürze. Sehr begehrt in Küstenstädten.",
        item_type=ItemType.TRADE_GOOD,
        base_value=25,
    ),
}


def get_item(item_id: str) -> Optional[Item]:
    """Retrieve item definition by ID."""
    return DEFAULT_ITEMS.get(item_id)
