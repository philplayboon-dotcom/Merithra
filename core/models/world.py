"""Data models for World Map, Regions, Cities, Routes, and Shops."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional
from .economy import Inventory, CurrencyWallet


@dataclass
class ShopItem:
    """An item offered by a merchant."""
    item_id: str
    price: int
    stock: int = -1       # -1 for unlimited stock

    def to_dict(self) -> Dict[str, Any]:
        return {"item_id": self.item_id, "price": self.price, "stock": self.stock}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShopItem":
        return cls(
            item_id=data["item_id"],
            price=data["price"],
            stock=data.get("stock", -1),
        )


@dataclass
class Shop:
    """A city merchant or market stall."""
    id: str
    name: str
    description: str
    items: List[ShopItem] = field(default_factory=list)
    buy_multiplier: float = 0.5   # Player sells items at base_value * buy_multiplier

    def buy_item(self, item_id: str, quantity: int, wallet: CurrencyWallet, inventory: Inventory) -> bool:
        """Player buys an item from the shop."""
        shop_item = next((i for i in self.items if i.item_id == item_id), None)
        if not shop_item:
            return False

        if shop_item.stock != -1 and shop_item.stock < quantity:
            return False

        total_cost = shop_item.price * quantity
        if not wallet.spend_gold(total_cost):
            return False

        if not inventory.add_item(item_id, quantity):
            # Rollback wallet
            wallet.add_gold(total_cost)
            return False

        if shop_item.stock != -1:
            shop_item.stock -= quantity
        return True

    def sell_item(self, item_id: str, quantity: int, wallet: CurrencyWallet, inventory: Inventory) -> bool:
        """Player sells an item to the shop."""
        from .items import get_item
        item_def = get_item(item_id)
        if not item_def:
            return False

        if inventory.get_quantity(item_id) < quantity:
            return False

        unit_payout = max(1, int(item_def.base_value * self.buy_multiplier))
        total_payout = unit_payout * quantity

        if not inventory.remove_item(item_id, quantity):
            return False

        wallet.add_gold(total_payout)
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "items": [i.to_dict() for i in self.items],
            "buy_multiplier": self.buy_multiplier,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Shop":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            items=[ShopItem.from_dict(i) for i in data.get("items", [])],
            buy_multiplier=data.get("buy_multiplier", 0.5),
        )


@dataclass
class City:
    """A city or town acting as a hub for trading, quests, and crafting."""
    id: str
    name: str
    description: str
    region_id: str
    shops: List[Shop] = field(default_factory=list)
    available_crafting_stations: List[str] = field(default_factory=list)
    available_quest_ids: List[str] = field(default_factory=list)
    connected_city_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "region_id": self.region_id,
            "shops": [s.to_dict() for s in self.shops],
            "available_crafting_stations": list(self.available_crafting_stations),
            "available_quest_ids": list(self.available_quest_ids),
            "connected_city_ids": list(self.connected_city_ids),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "City":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            region_id=data.get("region_id", ""),
            shops=[Shop.from_dict(s) for s in data.get("shops", [])],
            available_crafting_stations=list(data.get("available_crafting_stations", [])),
            available_quest_ids=list(data.get("available_quest_ids", [])),
            connected_city_ids=list(data.get("connected_city_ids", [])),
        )


@dataclass
class Region:
    """A geographic territory containing cities and routes."""
    id: str
    name: str
    description: str
    required_story_chapter: int = 1
    cities: List[City] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "required_story_chapter": self.required_story_chapter,
            "cities": [c.to_dict() for c in self.cities],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Region":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            required_story_chapter=data.get("required_story_chapter", 1),
            cities=[City.from_dict(c) for c in data.get("cities", [])],
        )


# Default Starter World Setup: Oakhaven & Silverport
DEFAULT_CITIES: Dict[str, City] = {
    "city_oakhaven": City(
        id="city_oakhaven",
        name="Oakhaven",
        description="Eine ruhige Waldstadt im Herzen von Merithra.",
        region_id="region_heartland",
        shops=[
            Shop(
                id="shop_oakhaven_general",
                name="Waldmarkt Oakhaven",
                description="Händler für Kräuter, Pelze und Handelswaren.",
                items=[
                    ShopItem("healing_salve", price=12, stock=5),
                    ShopItem("spices_oakhaven", price=25, stock=10),
                ],
            )
        ],
        available_crafting_stations=["alchemy_lab", "leather_rack"],
        connected_city_ids=["city_silverport"],
    ),
    "city_silverport": City(
        id="city_silverport",
        name="Silverport",
        description="Eine geschäftige Hafenstadt mit reichem Erzhandel.",
        region_id="region_heartland",
        shops=[
            Shop(
                id="shop_silverport_smith",
                name="Hafenschmiede",
                description="Waffen, Rüstungen und Roherze.",
                items=[
                    ShopItem("iron_scrap", price=5, stock=20),
                    ShopItem("silver_ore", price=20, stock=8),
                ],
            )
        ],
        available_crafting_stations=["forge"],
        connected_city_ids=["city_oakhaven"],
    ),
}


def get_city(city_id: str) -> Optional[City]:
    return DEFAULT_CITIES.get(city_id)
