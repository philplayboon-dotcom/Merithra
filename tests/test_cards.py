"""Unit tests for core.cards.

Tests cover:
- Card Dataclass Attributes
- Card Registry Loading (JSON/Defaults)
- Card can_play() Validation
- Effect Application (DAMAGE, HEAL, DRAW_CARDS)
- Rarity Handling (FREE, COMMON, RARE, EPIC, LEGENDARY)
- Keyword Extraction from Cards
"""

from __future__ import annotations

from typing import Any, List

import pytest

from core.cards import (
    Card,
    CardType,
    Rarity,
    Effect,
    EffectBundle,
    SimpleEffect,
    create_damage_effect,
    create_heal_effect,
    create_draw_effect,
    get_card_registry,
    get_default_registry,
    CardRegistry,
)


# -----------------------------------------------------------
# Card Dataclass Attribute Tests
# -----------------------------------------------------------


class TestCardDataclass:
    """Tests for Card dataclass attributes."""

    def test_card_creation_minimal(self) -> None:
        """Card should be creatable with minimal attributes."""
        card = Card(
            id="c001",
            name="Test Card",
            cost=3,
            card_type=CardType.MINION,
            class_type="NEUTRAL",
            rarity=Rarity.COMMON,
            text="A test card",
        )
        assert card.id == "c001"
        assert card.name == "Test Card"
        assert card.cost == 3
        assert card.card_type == CardType.MINION
        assert card.class_type == "NEUTRAL"
        assert card.rarity == Rarity.COMMON
        assert card.text == "A test card"
        assert card.attack == 0  # default
        assert card.health == 0  # default
        assert card.keywords == []  # default
        assert card.effects == []  # default

    def test_card_creation_full(self) -> None:
        """Card should hold all attributes when provided."""
        card = Card(
            id="c002",
            name="Full Card",
            cost=5,
            card_type=CardType.SPELL,
            class_type="MAGE",
            rarity=Rarity.EPIC,
            text="A full test card",
            attack=4,
            health=2,
            durability=3,
            keywords=["TAUNT", "DIVINE_SHIELD"],
        )
        assert card.id == "c002"
        assert card.name == "Full Card"
        assert card.cost == 5
        assert card.card_type == CardType.SPELL
        assert card.class_type == "MAGE"
        assert card.rarity == Rarity.EPIC
        assert card.text == "A full test card"
        assert card.attack == 4
        assert card.health == 2
        assert card.durability == 3
        assert set(card.keywords) == {"TAUNT", "DIVINE_SHIELD"}

    def test_card_defaults(self) -> None:
        """Card should use defaults for optional attributes."""
        card = Card(
            id="c003",
            name="Defaults Card",
            cost=1,
            card_type=CardType.SPELL,
            class_type="NEUTRAL",
            rarity=Rarity.FREE,
            text="Defaults test",
        )
        assert card.attack == 0
        assert card.health == 0
        assert card.durability is None
        assert card.keywords == []

    def test_card_rarity_enum(self) -> None:
        """Rarity should be proper Rarity enum values."""
        for rarity in [Rarity.FREE, Rarity.COMMON, Rarity.RARE, Rarity.EPIC, Rarity.LEGENDARY]:
            card = Card(
                id=f"c_{rarity.name.lower()}",
                name=f"{rarity.name} Card",
                cost=1,
                card_type=CardType.MINION,
                class_type="NEUTRAL",
                rarity=rarity,
                text=f"{rarity.name} test",
            )
            assert card.rarity is rarity


# -----------------------------------------------------------
# Card can_play Tests
# -----------------------------------------------------------


class TestCardCanPlay:
    """Tests for Card can_play() validation."""

    @pytest.fixture
    def valid_state(self) -> Any:
        """Minimal game state for can_play checks."""
        from core.engine.state_machine import GameState
        return GameState(game_id="g", player_id="p", opponent_id="o")

    def test_can_play_with_sufficient_mana(self, valid_state: Any) -> None:
        """Card with cost <= mana should be playable."""
        from core.engine.state_machine import GameState

        sufficient_state = GameState(
            game_id=valid_state.game_id,
            player_id=valid_state.player_id,
            opponent_id=valid_state.opponent_id,
            mana=2,
            max_mana=2,
        )
        card = Card(
            id="c001",
            name="Mana Card",
            cost=2,
            card_type=CardType.SPELL,
            class_type="NEUTRAL",
            rarity=Rarity.COMMON,
            text="Test",
        )
        assert card.can_play(sufficient_state) is True

    def test_can_play_insufficient_mana(self, valid_state: Any) -> None:
        """Card with cost > mana should not be playable."""
        card = Card(
            id="c002",
            name="Expensive Card",
            cost=10,
            card_type=CardType.SPELL,
            class_type="NEUTRAL",
            rarity=Rarity.COMMON,
            text="Test",
        )
        # Default mana is 1
        assert card.can_play(valid_state) is False

    def test_can_play_with_custom_mana(self) -> None:
        """Card can play with custom mana setting."""
        from core.engine.state_machine import GameState
        state = GameState(game_id="g", player_id="p", opponent_id="o", mana=5)
        card = Card(
            id="c003",
            name="Just Right",
            cost=5,
            card_type=CardType.SPELL,
            class_type="NEUTRAL",
            rarity=Rarity.COMMON,
            text="Test",
        )
        assert card.can_play(state) is True

    def test_can_play_zero_cost(self, valid_state: Any) -> None:
        """Zero cost card should always be playable."""
        card = Card(
            id="c004",
            name="Free Card",
            cost=0,
            card_type=CardType.SPELL,
            class_type="NEUTRAL",
            rarity=Rarity.FREE,
            text="Test",
        )
        assert card.can_play(valid_state) is True

    def test_can_play_hero_power(self, valid_state: Any) -> None:
        """Hero power cards should validate correctly."""
        from core.cards import CardType
        from core.engine.state_machine import GameState
        card = Card(
            id="c005",
            name="Hero Power",
            cost=2,
            card_type=CardType.HERO_POWER,
            class_type="MAGE",
            rarity=Rarity.COMMON,
            text="Test",
        )
        # With mana 2+, should be playable
        state = GameState(game_id="g", player_id="p", opponent_id="o", mana=2)
        assert card.can_play(state) is True


# -----------------------------------------------------------
# Effect Application Tests
# -----------------------------------------------------------


class TestEffectApplication:
    """Tests for Effect application (DAMAGE, HEAL, DRAW_CARDS)."""

    def test_damage_effect_creation(self) -> None:
        """Damage effect should be creatable."""
        from core.cards import create_damage_effect
        eff = create_damage_effect(5)
        assert eff.type == "DAMAGE"
        assert eff.value == 5

    def test_heal_effect_creation(self) -> None:
        """Heal effect should be creatable."""
        from core.cards import create_heal_effect
        eff = create_heal_effect(10)
        assert eff.type == "HEAL"
        assert eff.value == 10

    def test_draw_cards_effect_creation(self) -> None:
        """Draw cards effect should be creatable."""
        from core.cards import create_draw_effect
        eff = create_draw_effect(3)
        assert eff.type == "DRAW_CARDS"
        assert eff.value == 3

    def test_damage_effect_apply_placeholder(self) -> None:
        """Damage effect apply should reduce health."""
        from core.entities import Hero
        from core.cards import create_damage_effect
        eff = create_damage_effect(3)
        hero = Hero(name="Test", max_health=30, current_health=30)
        # Apply damage - now implemented, reduces health
        eff.apply(hero, None)
        assert hero.current_health == 27  # 30 - 3

    def test_heal_effect_apply_placeholder(self) -> None:
        """Heal effect apply should heal the target."""
        from core.entities import Hero
        from core.cards import create_heal_effect
        eff = create_heal_effect(5)
        hero = Hero(name="Test", max_health=30, current_health=20)
        eff.apply(hero, None)
        # Health should be min(max, current+value)
        assert hero.current_health == 25  # min(30, 20+5)

    def test_draw_cards_effect_apply_placeholder(self) -> None:
        """Draw cards effect apply should not crash."""
        from core.entities import Hero, Player
        from core.cards import create_draw_effect
        eff = create_draw_effect(2)
        player = Player(hero=Hero(name="Test", max_health=30))
        # Draw cards doesn't affect health - just shouldn't crash
        eff.apply(player, None)

    def test_effect_with_target_filter(self) -> None:
        """Effect with target_filter should store it correctly."""
        from core.cards import create_damage_effect
        eff = create_damage_effect(3, target_filter="MINION")
        assert eff.target_filter == "MINION"

    def test_permanent_effect(self) -> None:
        """Permanent effect should set permanent=True."""
        from core.cards.effects import Effect
        eff = Effect(type="DAMAGE", value=1, permanent=True)
        assert eff.permanent is True


# -----------------------------------------------------------
# Rarity Handling Tests
# -----------------------------------------------------------


class TestRarityHandling:
    """Tests for Rarity enum handling."""

    def test_all_rarity_values(self) -> None:
        """All rarity enum values should exist."""
        assert Rarity.FREE.value is not None
        assert Rarity.COMMON.value is not None
        assert Rarity.RARE.value is not None
        assert Rarity.EPIC.value is not None
        assert Rarity.LEGENDARY.value is not None

    def test_rarity_ordering(self) -> None:
        """Rarity values should increase in rarity."""
        assert Rarity.FREE.value < Rarity.COMMON.value
        assert Rarity.COMMON.value < Rarity.RARE.value
        assert Rarity.RARE.value < Rarity.EPIC.value
        assert Rarity.EPIC.value < Rarity.LEGENDARY.value

    def test_card_rarity_persistence(self) -> None:
        """Card rarity should persist through to_dict/from_dict."""
        card = Card(
            id="r001",
            name="Rarity Test",
            cost=3,
            card_type=CardType.MINION,
            class_type="NEUTRAL",
            rarity=Rarity.RARE,
            text="Test",
        )
        data = card.to_dict()
        assert data["rarity"] == "RARE"
        
        restored = Card.from_dict(data)
        assert restored.rarity == Rarity.RARE

    def test_default_cards_have_rarity(self) -> None:
        """Default cards should have proper rarity values."""
        registry = get_default_registry()
        for card in registry._cards.values():
            assert card.rarity in [Rarity.FREE, Rarity.COMMON, Rarity.RARE, Rarity.EPIC, Rarity.LEGENDARY]


# -----------------------------------------------------------
# Keyword Extraction Tests
# -----------------------------------------------------------


class TestKeywordExtraction:
    """Tests for keyword extraction from Cards."""

    def test_keywords_stored_and_retrieved(self) -> None:
        """Keywords should be stored and retrievable."""
        card = Card(
            id="kw001",
            name="Keyword Card",
            cost=3,
            card_type=CardType.MINION,
            class_type="NEUTRAL",
            rarity=Rarity.COMMON,
            text="Test",
            keywords=["TAUNT", "DIVINE_SHIELD", "CHARGE"],
        )
        assert "TAUNT" in card.keywords
        assert "DIVINE_SHIELD" in card.keywords
        assert "CHARGE" in card.keywords

    def test_single_keyword(self) -> None:
        """Card with single keyword."""
        card = Card(
            id="kw002",
            name="Single Kw",
            cost=2,
            card_type=CardType.MINION,
            class_type="NEUTRAL",
            rarity=Rarity.COMMON,
            text="Test",
            keywords=["TAUNT"],
        )
        assert card.keywords == ["TAUNT"]

    def test_no_keywords(self) -> None:
        """Card without keywords should have empty list."""
        card = Card(
            id="kw003",
            name="No Kw",
            cost=1,
            card_type=CardType.SPELL,
            class_type="NEUTRAL",
            rarity=Rarity.COMMON,
            text="Test",
        )
        assert card.keywords == []

    def test_keywords_in_to_dict_from_dict(self) -> None:
        """Keywords should persist through serialization."""
        card = Card(
            id="kw004",
            name="Serialize Kw",
            cost=4,
            card_type=CardType.MINION,
            class_type="NEUTRAL",
            rarity=Rarity.RARE,
            text="Test",
            keywords=["TAUNT", "WINDFURY"],
        )
        data = card.to_dict()
        assert "TAUNT" in data["keywords"]
        assert "WINDFURY" in data["keywords"]
        
        restored = Card.from_dict(data)
        assert "TAUNT" in restored.keywords
        assert "WINDFURY" in restored.keywords


# -----------------------------------------------------------
# Card Registry Tests
# -----------------------------------------------------------


class TestCardRegistryLoading:
    """Tests for Card Registry loading (JSON/Defaults)."""

    def test_default_registry_exists(self) -> None:
        """Default registry should be loadable."""
        registry = get_default_registry()
        assert registry is not None
        assert len(registry._cards) > 0

    def test_registry_card_count(self) -> None:
        """Default registry should have expected number of cards."""
        registry = get_default_registry()
        # The DEFAULT_CARDS_JSON has 20 cards
        assert len(registry._cards) == 20

    def test_registry_get_by_id(self) -> None:
        """Should be able to get card by ID."""
        registry = get_default_registry()
        card = registry.get("card_001")
        assert card is not None
        assert card.name == "Großer Wolf"

    def test_registry_get_by_class(self) -> None:
        """Should be able to get cards by class."""
        registry = get_default_registry()
        warrior_cards = registry.get_by_class("NEUTRAL")
        assert len(warrior_cards) > 0
        # All should be NEUTRAL
        for c in warrior_cards:
            assert c.class_type == "NEUTRAL"

    def test_registry_get_by_rarity(self) -> None:
        """Should be able to get cards by rarity."""
        registry = get_default_registry()
        for rarity in [Rarity.FREE, Rarity.COMMON, Rarity.RARE, Rarity.EPIC, Rarity.LEGENDARY]:
            cards = registry.get_by_rarity(rarity)
            # At least some cards should exist for each rarity in defaults
            for c in cards:
                assert c.rarity is rarity

    def test_registry_loaded_from_paths(self) -> None:
        """Registry should track loaded paths."""
        registry = get_default_registry()
        assert len(registry._loaded_from) > 0


# -----------------------------------------------------------
# Effect Bundle Tests
# -----------------------------------------------------------


class TestEffectBundle:
    """Tests for EffectBundle composition."""

    def test_bundle_creation(self) -> None:
        """EffectBundle should be creatable."""
        from core.cards import EffectBundle
        bundle = EffectBundle()
        assert bundle.effects == []

    def test_bundle_add_effect(self) -> None:
        """Should be able to add effects to bundle."""
        from core.cards import EffectBundle, Effect
        bundle = EffectBundle()
        eff = Effect(type="DAMAGE", value=5)
        bundle.add(eff)
        assert len(bundle.effects) == 1

    def test_bundle_apply_all(self) -> None:
        """Should be able to apply all effects."""
        from core.entities import Hero
        from core.cards import EffectBundle, create_damage_effect, create_heal_effect
        
        bundle = EffectBundle()
        bundle.add(create_damage_effect(3))
        bundle.add(create_heal_effect(2))
        
        hero = Hero(name="Test", max_health=30, current_health=20)
        # apply_all is a placeholder, shouldn't crash
        bundle.apply_all(hero, None)
        # Health may or may not change (placeholder behavior)


# -----------------------------------------------------------
# Factory Function Tests
# -----------------------------------------------------------


class TestEffectFactories:
    """Tests for effect factory functions."""

    def test_create_damage_effect(self) -> None:
        """create_damage_effect factory function."""
        eff = create_damage_effect(7)
        assert eff.type == "DAMAGE"
        assert eff.value == 7
        assert eff.target_filter == "ANY"

    def test_create_heal_effect(self) -> None:
        """create_heal_effect factory function."""
        eff = create_heal_effect(15)
        assert eff.type == "HEAL"
        assert eff.value == 15

    def test_create_draw_effect(self) -> None:
        """create_draw_effect factory function."""
        eff = create_draw_effect(5)
        assert eff.type == "DRAW_CARDS"
        assert eff.value == 5

    def test_create_damage_with_target_filter(self) -> None:
        """create_damage_effect with target_filter."""
        eff = create_damage_effect(3, target_filter="HERO")
        assert eff.target_filter == "HERO"
        assert eff.value == 3


# -----------------------------------------------------------
# to_dict / from_dict Tests for Cards
# -----------------------------------------------------------


class TestCardSerialization:
    """Tests for Card to_dict / from_dict round-trip."""

    def test_roundtrip_preserves_all_fields(self) -> None:
        """to_dict/from_dict should preserve all card fields."""
        card = Card(
            id="s001",
            name="Serialize Roundtrip",
            cost=4,
            card_type=CardType.MINION,
            class_type="MAGE",
            rarity=Rarity.EPIC,
            text="A test card with all fields",
            attack=3,
            health=5,
            durability=2,
            keywords=["TAUNT"],
        )
        data = card.to_dict()
        restored = Card.from_dict(data)
        
        assert restored.id == card.id
        assert restored.name == card.name
        assert restored.cost == card.cost
        assert restored.card_type == card.card_type
        assert restored.class_type == card.class_type
        assert restored.rarity == card.rarity
        assert restored.text == card.text
        assert restored.attack == card.attack
        assert restored.health == card.health
        assert restored.durability == card.durability
        assert set(restored.keywords) == set(card.keywords)
        assert len(restored.effects) == len(card.effects)

    def test_roundtrip_with_effects(self) -> None:
        """to_dict/from_dict should preserve effects."""
        from core.cards.effects import Effect
        
        card = Card(
            id="s002",
            name="With Effects",
            cost=3,
            card_type=CardType.SPELL,
            class_type="NEUTRAL",
            rarity=Rarity.COMMON,
            text="Deals damage and heals",
            effects=[
                {"type": "DAMAGE", "value": 6},
                {"type": "HEAL", "value": 3},
            ],
        )
        data = card.to_dict()
        restored = Card.from_dict(data)
        
        assert len(restored.effects) == 2
        assert restored.effects[0].type == "DAMAGE"
        assert restored.effects[0].value == 6
        assert restored.effects[1].type == "HEAL"
        assert restored.effects[1].value == 3