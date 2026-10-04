"""Data models for Economy, Inventory, Wallets, and Transactions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .items import Item, get_item


@dataclass
class ItemStack:
    """A quantity of a specific item."""
    item_id: str
    quantity: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "quantity": self.quantity,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ItemStack":
        return cls(
            item_id=data["item_id"],
            quantity=data.get("quantity", 1),
        )


@dataclass
class CurrencyWallet:
    """Player currency balances."""
    gold: int = 0

    def add_gold(self, amount: int) -> None:
        if amount > 0:
            self.gold += amount

    def spend_gold(self, amount: int) -> bool:
        """Attempt to deduct gold. Returns True if successful, False if insufficient."""
        if amount < 0 or self.gold < amount:
            return False
        self.gold -= amount
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {"gold": self.gold}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CurrencyWallet":
        return cls(gold=data.get("gold", 0))


@dataclass
class Inventory:
    """Player inventory containing item stacks."""
    stacks: Dict[str, ItemStack] = field(default_factory=dict)
    max_slots: int = 40

    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """Add item(s) to inventory. Stacks automatically."""
        if quantity <= 0:
            return False

        item_def = get_item(item_id)
        max_stack = item_def.max_stack if item_def else 99

        if item_id in self.stacks:
            current = self.stacks[item_id]
            current.quantity += quantity
            return True
        else:
            if len(self.stacks) >= self.max_slots:
                return False  # Inventory full
            self.stacks[item_id] = ItemStack(item_id=item_id, quantity=quantity)
            return True

    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Remove item(s) from inventory. Returns True if successfully removed."""
        if quantity <= 0 or item_id not in self.stacks:
            return False

        stack = self.stacks[item_id]
        if stack.quantity < quantity:
            return False

        stack.quantity -= quantity
        if stack.quantity <= 0:
            del self.stacks[item_id]
        return True

    def get_quantity(self, item_id: str) -> int:
        """Get the current count of an item in inventory."""
        stack = self.stacks.get(item_id)
        return stack.quantity if stack else 0

    def has_items(self, requirements: Dict[str, int]) -> bool:
        """Check if all required items and quantities are present."""
        for item_id, count in requirements.items():
            if self.get_quantity(item_id) < count:
                return False
        return True

    def consume_items(self, requirements: Dict[str, int]) -> bool:
        """Atomically consume multiple items. Fails completely if any item is missing."""
        if not self.has_items(requirements):
            return False

        for item_id, count in requirements.items():
            self.remove_item(item_id, count)
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stacks": {k: v.to_dict() for k, v in self.stacks.items()},
            "max_slots": self.max_slots,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Inventory":
        stacks_data = data.get("stacks", {})
        stacks = {k: ItemStack.from_dict(v) for k, v in stacks_data.items()}
        return cls(
            stacks=stacks,
            max_slots=data.get("max_slots", 40),
        )
