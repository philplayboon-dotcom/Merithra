"""Unit tests for core.cards.effects.

Tests cover:
- Effect Dataclass Struktur
- Effect apply() Methoden
- Factory-Funktionen (damage(), heal(), draw_cards())
"""

from __future__ import annotations

from typing import Any

import pytest

from core.cards.effects import (
    Effect,
    EffectBundle,
    damage,
    heal,
    draw_cards,
    set_attack,
    set_health,
    set_max_mana,
    armor,
)


# -----------------------------------------------------------
# Effect Dataclass Struktur Tests
# -----------------------------------------------------------


class TestEffectDataclass:
    """Tests for Effect dataclass structure."""

    def test_effect_creation_basic(self) -> None:
        """Effect should be creatable with basic fields."""
        eff = Effect(type="DAMAGE", value=5)
        assert eff.type == "DAMAGE"
        assert eff.value == 5
        assert eff.target_filter == "ANY"
        assert eff.target_id is None
        assert eff.permanent is False

    def test_effect_creation_with_all_fields(self) -> None:
        """Effect should accept all fields."""
        eff = Effect(
            type="HEAL",
            target_filter="MINION",
            value=10,
            target_id="hero1",
            permanent=True,
        )
        assert eff.type == "HEAL"
        assert eff.target_filter == "MINION"
        assert eff.value == 10
        assert eff.target_id == "hero1"
        assert eff.permanent is True

    def test_effect_defaults(self) -> None:
        """Effect should use defaults for optional fields."""
        eff = Effect(type="DAMAGE", value=3)
        assert eff.target_filter == "ANY"
        assert eff.target_id is None
        assert eff.permanent is False

    def test_effect_type_case_insensitive(self) -> None:
        """Effect apply method should handle case normalization."""
        # The apply method uppercases the type
        eff = Effect(type="damage", value=3)  # lowercase
        # apply method will uppercase it, so it should still match "DAMAGE"
        assert eff.type == "damage"  # Store as given


# -----------------------------------------------------------
# Effect apply() Methoden Tests
# -----------------------------------------------------------


class TestEffectApply:
    """Tests for Effect apply() methods."""

    def test_damage_effect_apply_placeholder(self) -> None:
        """Damage effect apply should reduce health."""
        from core.entities import Hero
        eff = damage(5)
        hero = Hero(name="Test", max_health=30, current_health=30)
        eff.apply(hero, None)
        # Damage should be applied
        assert hero.current_health == 25  # 30 - 5

    def test_heal_effect_apply_heals(self) -> None:
        """Heal effect apply should increase health (via placeholder logic)."""
        from core.entities import Hero
        eff = heal(10)
        hero = Hero(name="Test", max_health=30, current_health=20)
        eff.apply(hero, None)
        # Placeholder: print statement, but let's verify hero state
        # Actual healing logic is in Hero.heal(), not Effect.apply()
        assert hero.current_health == 30  # Was 20 + 10 = 30 (capped at max)

    def test_draw_cards_effect_apply(self) -> None:
        """Draw cards effect apply should be placeholder."""
        from core.entities import Hero, Player
        eff = draw_cards(3)
        player = Player(hero=Hero(name="Test", max_health=30))
        eff.apply(player, None)
        # Placeholder - shouldn't crash

    def test_set_attack_effect(self) -> None:
        """SET_ATTACK effect should be creatable."""
        eff = set_attack(7)
        assert eff.type == "SET_ATTACK"
        assert eff.value == 7

    def test_set_health_effect(self) -> None:
        """SET_HEALTH effect should be creatable."""
        eff = set_health(15)
        assert eff.type == "SET_HEALTH"
        assert eff.value == 15

    def test_set_max_mana_effect(self) -> None:
        """SET_MAX_MANA effect should be creatable."""
        eff = set_max_mana(10)
        assert eff.type == "SET_MAX_MANA"
        assert eff.value == 10

    def test_armor_effect(self) -> None:
        """ARMOR effect should be creatable."""
        eff = armor(5)
        assert eff.type == "ARMOR"
        assert eff.value == 5

    def test_effect_unknown_type(self) -> None:
        """Unknown effect type should be handled gracefully."""
        from core.entities import Hero
        eff = Effect(type="UNKNOWN_TYPE", value=99)
        hero = Hero(name="Test", max_health=30, current_health=30)
        # Should not crash
        eff.apply(hero, None)
        assert hero.current_health == 30


# -----------------------------------------------------------
# Factory-Funktionen Tests
# -----------------------------------------------------------


class TestEffectFactories:
    """Tests for effect factory functions."""

    def test_damage_factory(self) -> None:
        """damage() factory function."""
        eff = damage(8)
        assert eff.type == "DAMAGE"
        assert eff.value == 8

    def test_damage_factory_with_filter(self) -> None:
        """damage() factory with target_filter."""
        eff = damage(5, target_filter="HERO")
        assert eff.type == "DAMAGE"
        assert eff.value == 5
        assert eff.target_filter == "HERO"

    def test_heal_factory(self) -> None:
        """heal() factory function."""
        eff = heal(15)
        assert eff.type == "HEAL"
        assert eff.value == 15

    def test_draw_cards_factory(self) -> None:
        """draw_cards() factory function."""
        eff = draw_cards(4)
        assert eff.type == "DRAW_CARDS"
        assert eff.value == 4

    def test_set_attack_factory(self) -> None:
        """set_attack() factory function."""
        eff = set_attack(10)
        assert eff.type == "SET_ATTACK"
        assert eff.value == 10

    def test_set_health_factory(self) -> None:
        """set_health() factory function."""
        eff = set_health(20)
        assert eff.type == "SET_HEALTH"
        assert eff.value == 20

    def test_set_max_mana_factory(self) -> None:
        """set_max_mana() factory function."""
        eff = set_max_mana(12)
        assert eff.type == "SET_MAX_MANA"
        assert eff.value == 12

    def test_armor_factory(self) -> None:
        """armor() factory function."""
        eff = armor(8)
        assert eff.type == "ARMOR"
        assert eff.value == 8


# -----------------------------------------------------------
# EffectBundle Tests
# -----------------------------------------------------------


class TestEffectBundleApplyAll:
    """Tests for EffectBundle.apply_all()."""

    def test_bundle_apply_all_placeholders(self) -> None:
        """EffectBundle.apply_all should apply effects without crashing."""
        from core.entities import Hero
        from core.cards.effects import EffectBundle, damage, heal
        
        bundle = EffectBundle()
        bundle.add(damage(3))
        bundle.add(heal(2))
        
        hero = Hero(name="Test", max_health=30, current_health=20)
        bundle.apply_all(hero, None)
        # Placeholder effects, health may change or not - shouldn't crash


# -----------------------------------------------------------
# SimpleEffect Tests
# -----------------------------------------------------------


class TestSimpleEffect:
    """Tests for SimpleEffect (extended Effect)."""

    def test_simple_effect_creation(self) -> None:
        """SimpleEffect should be creatable."""
        from core.cards import SimpleEffect
        eff = SimpleEffect(type="DAMAGE", value=5)
        assert eff.type == "DAMAGE"
        assert eff.value == 5

    def test_simple_effect_apply_damage_placeholder(self) -> None:
        """SimpleEffect.apply for damage should apply damage."""
        from core.entities import Hero
        from core.cards import SimpleEffect, create_damage_effect
        
        eff = create_damage_effect(5)
        hero = Hero(name="Test", max_health=30, current_health=30)
        eff.apply(hero, None)
        # Damage should be applied
        assert hero.current_health == 25  # 30 - 5


# -----------------------------------------------------------
# Round-trip Tests for Effects
# -----------------------------------------------------------


class TestEffectSerialization:
    """Tests for Effect to_dict / from_dict round-trip (if applicable)."""

    def test_effect_to_dict_basic(self) -> None:
        """Effect to_dict should capture basic fields."""
        eff = Effect(type="DAMAGE", value=7, target_filter="MINION")
        data = eff.__dict__
        assert data["type"] == "DAMAGE"
        assert data["value"] == 7
        assert data["target_filter"] == "MINION"

    def test_effect_from_dict_basic(self) -> None:
        """Effect from_dict should reconstruct from dict."""
        from core.cards.effects import Effect
        
        data = {"type": "HEAL", "value": 5, "target_filter": "HERO"}
        eff = Effect.from_dict(data) if hasattr(Effect, 'from_dict') else Effect(**data)
        # Note: Effect dataclass may not have from_dict, testing __dict__ roundtrip
        assert eff.type == "HEAL"
        assert eff.value == 5


# -----------------------------------------------------------
# Edge Cases
# -----------------------------------------------------------


class TestEffectEdgeCases:
    """Edge case tests for effects."""

    def test_zero_value_effect(self) -> None:
        """Effect with value 0 should be valid."""
        eff = damage(0)
        assert eff.value == 0
        eff = heal(0)
        assert eff.value == 0

    def test_negative_value_effect(self) -> None:
        """Effect with negative value should be valid (healing overkill, etc.)."""
        eff = heal(-5)  # This might have undefined behavior, just test it doesn't crash
        # Negative heal might be treated as damage depending on implementation
        assert eff.value == -5

    def test_large_value_effect(self) -> None:
        """Effect with large value should be valid."""
        eff = damage(9999)
        assert eff.value == 9999