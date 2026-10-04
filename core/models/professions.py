"""Data models for Professions, Recipes, and Crafting in Merithra."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional
from .economy import Inventory


class ProfessionType(Enum):
    """Available crafting and gathering professions."""
    ALCHEMIST = "alchemist"       # Potions, elixirs, coatings
    BLACKSMITH = "blacksmith"     # Weapons, armor, reinforcement
    INSCRIBER = "inscriber"       # Card creation, enchantment scrolls, deck seals
    LEATHERWORKER = "leatherworker" # Bags, armor, grips


@dataclass
class RecipeIngredient:
    """An ingredient required to craft a recipe."""
    item_id: str
    quantity: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {"item_id": self.item_id, "quantity": self.quantity}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RecipeIngredient":
        return cls(item_id=data["item_id"], quantity=data.get("quantity", 1))


@dataclass
class Recipe:
    """A crafting recipe definition."""
    id: str
    name: str
    profession: ProfessionType
    required_level: int
    ingredients: List[RecipeIngredient] = field(default_factory=list)
    output_item_id: Optional[str] = None
    output_card_id: Optional[str] = None
    output_quantity: int = 1
    xp_reward: int = 10
    required_station: Optional[str] = None  # e.g. "alchemy_lab", "forge"

    def can_craft(self, inventory: Inventory, profession_level: int) -> bool:
        """Check if player has required level and ingredients."""
        if profession_level < self.required_level:
            return False
        reqs = {ing.item_id: ing.quantity for ing in self.ingredients}
        return inventory.has_items(reqs)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "profession": self.profession.value,
            "required_level": self.required_level,
            "ingredients": [i.to_dict() for i in self.ingredients],
            "output_item_id": self.output_item_id,
            "output_card_id": self.output_card_id,
            "output_quantity": self.output_quantity,
            "xp_reward": self.xp_reward,
            "required_station": self.required_station,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Recipe":
        return cls(
            id=data["id"],
            name=data["name"],
            profession=ProfessionType(data["profession"]),
            required_level=data.get("required_level", 1),
            ingredients=[RecipeIngredient.from_dict(i) for i in data.get("ingredients", [])],
            output_item_id=data.get("output_item_id"),
            output_card_id=data.get("output_card_id"),
            output_quantity=data.get("output_quantity", 1),
            xp_reward=data.get("xp_reward", 10),
            required_station=data.get("required_station"),
        )


@dataclass
class ProfessionState:
    """Player's progression in a specific profession."""
    profession: ProfessionType
    level: int = 1
    experience: int = 0
    unlocked_recipe_ids: List[str] = field(default_factory=list)

    def add_experience(self, xp: int) -> bool:
        """Add XP and level up if threshold reached. Returns True on level up."""
        if xp <= 0:
            return False

        self.experience += xp
        leveled_up = False
        # Simple curve: Level N requires N * 100 XP
        while self.experience >= self.level * 100 and self.level < 100:
            self.experience -= self.level * 100
            self.level += 1
            leveled_up = True
        return leveled_up

    def unlock_recipe(self, recipe_id: str) -> bool:
        """Unlock a recipe if not already learned."""
        if recipe_id not in self.unlocked_recipe_ids:
            self.unlocked_recipe_ids.append(recipe_id)
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profession": self.profession.value,
            "level": self.level,
            "experience": self.experience,
            "unlocked_recipe_ids": list(self.unlocked_recipe_ids),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProfessionState":
        return cls(
            profession=ProfessionType(data["profession"]),
            level=data.get("level", 1),
            experience=data.get("experience", 0),
            unlocked_recipe_ids=list(data.get("unlocked_recipe_ids", [])),
        )


# Default starter recipes
DEFAULT_RECIPES: Dict[str, Recipe] = {
    "rec_healing_salve": Recipe(
        id="rec_healing_salve",
        name="Heilsalbe herstellen",
        profession=ProfessionType.ALCHEMIST,
        required_level=1,
        ingredients=[RecipeIngredient("wolf_pelt", 1)],
        output_item_id="healing_salve",
        output_quantity=2,
        xp_reward=20,
    ),
}


def get_recipe(recipe_id: str) -> Optional[Recipe]:
    return DEFAULT_RECIPES.get(recipe_id)
