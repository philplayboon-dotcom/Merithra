"""Unit tests for RPG and persistent World/Economy models."""

import pytest
from core.models import (
    Item,
    ItemType,
    Inventory,
    CurrencyWallet,
    ProfessionState,
    ProfessionType,
    Recipe,
    RecipeIngredient,
    Shop,
    ShopItem,
    City,
    Quest,
    QuestObjective,
    ObjectiveType,
    QuestReward,
    QuestStatus,
    SaveGameData,
    create_new_savegame,
    get_item,
    get_city,
    get_quest,
)


def test_inventory_and_stacking():
    """Test adding, stacking, and removing items from inventory."""
    inv = Inventory(max_slots=5)

    assert inv.add_item("wolf_pelt", 2) is True
    assert inv.get_quantity("wolf_pelt") == 2

    # Stacking
    assert inv.add_item("wolf_pelt", 3) is True
    assert inv.get_quantity("wolf_pelt") == 5

    # Partial remove
    assert inv.remove_item("wolf_pelt", 2) is True
    assert inv.get_quantity("wolf_pelt") == 3

    # Total remove
    assert inv.remove_item("wolf_pelt", 3) is True
    assert inv.get_quantity("wolf_pelt") == 0
    assert "wolf_pelt" not in inv.stacks


def test_inventory_atomic_consumption():
    """Test that consume_items is atomic (either all consumed or none)."""
    inv = Inventory()
    inv.add_item("iron_scrap", 5)
    inv.add_item("silver_ore", 2)

    # Valid consumption
    reqs = {"iron_scrap": 3, "silver_ore": 1}
    assert inv.has_items(reqs) is True
    assert inv.consume_items(reqs) is True
    assert inv.get_quantity("iron_scrap") == 2
    assert inv.get_quantity("silver_ore") == 1

    # Insufficient consumption
    too_much = {"iron_scrap": 5, "silver_ore": 1}
    assert inv.has_items(too_much) is False
    assert inv.consume_items(too_much) is False
    # State remained untouched
    assert inv.get_quantity("iron_scrap") == 2
    assert inv.get_quantity("silver_ore") == 1


def test_currency_wallet():
    """Test wallet balance additions and spending."""
    wallet = CurrencyWallet(gold=100)

    assert wallet.spend_gold(30) is True
    assert wallet.gold == 70

    assert wallet.spend_gold(100) is False  # Not enough gold
    assert wallet.gold == 70

    wallet.add_gold(50)
    assert wallet.gold == 120


def test_crafting_and_profession_progression():
    """Test crafting recipe checks and XP gain."""
    prof = ProfessionState(profession=ProfessionType.ALCHEMIST, level=1, experience=0)
    inv = Inventory()
    inv.add_item("wolf_pelt", 2)

    recipe = Recipe(
        id="rec_salve",
        name="Salve",
        profession=ProfessionType.ALCHEMIST,
        required_level=1,
        ingredients=[RecipeIngredient("wolf_pelt", 2)],
        output_item_id="healing_salve",
        output_quantity=2,
        xp_reward=150,
    )

    assert recipe.can_craft(inv, prof.level) is True

    # Crafting execution
    reqs = {i.item_id: i.quantity for i in recipe.ingredients}
    assert inv.consume_items(reqs) is True
    assert inv.add_item(recipe.output_item_id, recipe.output_quantity) is True

    # Experience & Level up
    leveled_up = prof.add_experience(recipe.xp_reward)
    assert leveled_up is True
    assert prof.level == 2
    assert prof.experience == 50  # 150 - 100 for level 1 -> 2


def test_shop_trading():
    """Test buying and selling items with a merchant."""
    shop = Shop(
        id="test_shop",
        name="Market",
        description="",
        items=[ShopItem("healing_salve", price=10, stock=3)],
        buy_multiplier=0.5,
    )

    wallet = CurrencyWallet(gold=50)
    inv = Inventory()

    # Buy item
    assert shop.buy_item("healing_salve", 2, wallet, inv) is True
    assert wallet.gold == 30
    assert inv.get_quantity("healing_salve") == 2
    assert shop.items[0].stock == 1

    # Sell item (healing_salve base_value = 10, payout = 5 each)
    assert shop.sell_item("healing_salve", 1, wallet, inv) is True
    assert wallet.gold == 35
    assert inv.get_quantity("healing_salve") == 1


def test_quest_progress_and_completion():
    """Test quest objective progression."""
    quest = Quest(
        id="q_test",
        title="Test Quest",
        description="",
        objectives=[
            QuestObjective(
                id="obj_1",
                description="",
                objective_type=ObjectiveType.WIN_ENCOUNTER,
                target_id="enc_wolf",
                required_count=2,
            )
        ],
        rewards=QuestReward(gold=50),
    )

    assert quest.is_all_objectives_met() is False

    quest.objectives[0].update_progress(1)
    assert quest.is_all_objectives_met() is False

    quest.objectives[0].update_progress(1)
    assert quest.is_all_objectives_met() is True
    assert quest.objectives[0].is_complete() is True


def test_savegame_serialization():
    """Test full SaveGameData serialization to and from dictionary."""
    save = create_new_savegame("HeroName", "WARRIOR")
    save.wallet.add_gold(150)
    save.unlocked_city_ids.append("city_silverport")

    d = save.to_dict()
    rehydrated = SaveGameData.from_dict(d)

    assert rehydrated.player_name == "HeroName"
    assert rehydrated.wallet.gold == 200  # 50 starter + 150
    assert "city_silverport" in rehydrated.unlocked_city_ids
    assert len(rehydrated.decks) == 1
    assert rehydrated.decks[0].hero_class == "WARRIOR"
    assert rehydrated.inventory.get_quantity("wolf_pelt") == 3
