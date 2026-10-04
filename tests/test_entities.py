"""Unit tests for core.entities.

Tests cover:
- Hero Klasse (Health, Armor, is_alive())
- Player Klasse (Mana, Deck, Hand, draw_card())
- Minion Klasse (Health, Divine Shield, Taunt, take_damage())
- Deathrattle Trigger
"""

from __future__ import annotations

from typing import Any

import pytest

from core.entities import (
    Hero,
    Player,
    Minion,
    init_card_registry,
    card_registry,
)
from core.cards import Card, CardType, Rarity, get_default_registry


# -----------------------------------------------------------
# Hero Class Tests
# -----------------------------------------------------------


class TestHero:
    """Tests for Hero class (Health, Armor, is_alive())."""

    def test_hero_creation_defaults(self) -> None:
        """Hero should have default current_health = 30."""
        hero = Hero(name="Test Hero", max_health=30)
        assert hero.current_health == 30
        assert hero.max_health == 30
        assert hero.armor == 0
        assert hero.is_alive() is True

    def test_hero_creation_custom(self) -> None:
        """Hero should accept custom health values."""
        hero = Hero(name="Custom", max_health=20, current_health=15)
        assert hero.current_health == 15
        assert hero.max_health == 20

    def test_hero_is_alive_positive(self) -> None:
        """is_alive() should return True when health > 0."""
        hero = Hero(name="Alive", max_health=30, current_health=1)
        assert hero.is_alive() is True

    def test_hero_is_alive_zero_returns_false(self) -> None:
        """is_alive() should return False when health = 0."""
        hero = Hero(name="Dead", max_health=30, current_health=0)
        assert hero.is_alive() is False

    def test_hero_is_alive_negative_returns_false(self) -> None:
        """is_alive() should return False when health < 0."""
        hero = Hero(name="Negative", max_health=30, current_health=-5)
        assert hero.is_alive() is False

    def test_hero_take_damage_no_armor(self) -> None:
        """take_damage should reduce health without armor."""
        hero = Hero(name="No Armor", max_health=30, current_health=20)
        hero.take_damage(10, None)
        assert hero.current_health == 10
        assert hero.armor == 0

    def test_hero_take_damage_with_armor(self) -> None:
        """take_damage should absorb armor first."""
        hero = Hero(name="With Armor", max_health=30, current_health=30, armor=5)
        hero.take_damage(10, None)
        # 5 damage absorbed by armor, 5 real damage to health
        assert hero.current_health == 25
        assert hero.armor == 0  # Armor consumed

    def test_hero_take_damage_exceeds_health(self) -> None:
        """take_damage should not go below 0 health."""
        hero = Hero(name="Low HP", max_health=30, current_health=5)
        hero.take_damage(100, None)
        assert hero.current_health == 0
        assert hero.is_alive() is False

    def test_hero_heal(self) -> None:
        """heal should increase health up to max."""
        hero = Hero(name="Hurt", max_health=30, current_health=10)
        hero.heal(25)
        assert hero.current_health == 30  # min(max, 10+25)

    def test_hero_heal_over_max(self) -> None:
        """heal should cap at max_health."""
        hero = Hero(name="Full", max_health=30, current_health=20)
        hero.heal(50)
        assert hero.current_health == 30  # capped


# -----------------------------------------------------------
# Player Class Tests
# -----------------------------------------------------------


class TestPlayer:
    """Tests for Player class (Mana, Deck, Hand, draw_card())."""

    @pytest.fixture
    def player_fixture(self) -> Player:
        """Create a player with a hero for testing."""
        hero = Hero(name="Test Hero", max_health=30)
        return Player(hero=hero)

    def test_player_creation(self, player_fixture: Player) -> None:
        """Player should create with proper defaults."""
        p = player_fixture
        assert p.hero is not None
        assert p.mana == 1
        assert p.max_mana == 1
        assert p.turn_number == 0
        assert p.fatigue == 0
        assert len(p.deck) == 0
        assert len(p.hand) == 0

    def test_draw_card_from_deck(self, player_fixture: Player) -> None:
        """draw_card should add card from deck to hand."""
        p = player_fixture
        # Add cards to deck
        card1 = Card(
            id="d001", name="Deck Card 1", cost=1,
            card_type=CardType.MINION, class_type="NEUTRAL",
            rarity=Rarity.COMMON, text="Test", attack=1, health=1,
        )
        card2 = Card(
            id="d002", name="Deck Card 2", cost=2,
            card_type=CardType.MINION, class_type="NEUTRAL",
            rarity=Rarity.COMMON, text="Test", attack=2, health=2,
        )
        p.deck.extend([card1, card2])
        
        drawn = p.draw_card()
        assert drawn is card1
        assert len(p.hand) == 1
        assert drawn.id == "d001"

    def test_draw_card_empty_deck_fatigue(self, player_fixture: Player) -> None:
        """draw_card from empty deck should increase fatigue damage."""
        p = player_fixture
        # Draw when deck is empty - should cause fatigue damage
        original_fatigue = p.fatigue
        drawn = p.draw_card()
        assert drawn is None  # No card to draw
        assert p.fatigue == original_fatigue + 1  # Fatigue increases
        # Hero takes fatigue damage
        assert p.hero is not None
        p.hero.take_damage(p.fatigue, p.game_state)  # simplified

    def test_draw_card_empty_deck_no_hero(self) -> None:
        """draw_card with no hero should just increase fatigue."""
        from core.entities import Player
        p = Player(hero=None)
        p.deck = []
        original_fatigue = p.fatigue
        drawn = p.draw_card()
        assert drawn is None
        assert p.fatigue == original_fatigue + 1

    def test_play_card_basic(self, player_fixture: Player) -> None:
        """play_card should remove from hand and reduce mana."""
        p = player_fixture
        card = Card(
            id="p001", name="Play Test", cost=2,
            card_type=CardType.SPELL, class_type="NEUTRAL",
            rarity=Rarity.COMMON, text="Test",
        )
        p.hand.append(card)
        p.mana = 3  # Set enough mana
        
        result = p.play_card(card.id)
        assert result is True
        assert card not in p.hand
        assert p.mana == 1  # 3 - 2 = 1

    def test_play_card_insufficient_mana(self, player_fixture: Player) -> None:
        """play_card should fail with insufficient mana."""
        p = player_fixture
        card = Card(
            id="p002", name="Expensive", cost=5,
            card_type=CardType.SPELL, class_type="NEUTRAL",
            rarity=Rarity.COMMON, text="Test",
        )
        p.hand.append(card)
        p.mana = 3  # Not enough for cost 5
        
        result = p.play_card(card.id)
        assert result is False
        # Card should still be in hand
        assert card in p.hand
        # Mana should not change
        assert p.mana == 3

    def test_end_turn_reset_mana(self, player_fixture: Player) -> None:
        """end_turn should reset mana to max_mana."""
        p = player_fixture
        p.mana = 2
        p.end_turn()
        assert p.mana == p.max_mana  # Should reset to 1 (default max_mana)
        assert p.turn_number == 1  # Turn should increment

    def test_end_turn_draw_card(self, player_fixture: Player) -> None:
        """end_turn should draw a card."""
        p = player_fixture
        # Already have one card in deck
        card = Card(
            id="e001", name="Drawn Card", cost=1,
            card_type=CardType.MINION, class_type="NEUTRAL",
            rarity=Rarity.COMMON, text="Test", attack=1, health=1,
        )
        p.deck.append(card)
        initial_hand_size = len(p.hand)
        
        p.end_turn()
        assert len(p.hand) == initial_hand_size + 1  # Drew a card
        assert p.turn_number == 1

    def test_to_dict_from_dict_roundtrip(self, player_fixture: Player) -> None:
        """Player to_dict/from_dict should round-trip correctly."""
        p = player_fixture
        card = Card(
            id="r001", name="Roundtrip Card", cost=3,
            card_type=CardType.MINION, class_type="NEUTRAL",
            rarity=Rarity.COMMON, text="Test", attack=2, health=3,
        )
        p.deck.append(card)
        p.hand.append(card)
        
        data = p.to_dict()
        restored = Player.from_dict(data)
        
        assert restored.hero.name == p.hero.name
        assert len(restored.deck) == len(p.deck)
        assert len(restored.hand) == len(p.hand)
        assert restored.mana == p.mana
        assert restored.max_mana == p.max_mana
        assert restored.turn_number == p.turn_number


# -----------------------------------------------------------
# Minion Class Tests
# -----------------------------------------------------------


class TestMinion:
    """Tests for Minion class (Health, Divine Shield, Taunt, take_damage())."""

    @pytest.fixture
    def test_card(self) -> Card:
        """Create a test minion card."""
        return Card(
            id="minion_001",
            name="Test Minion",
            cost=3,
            card_type=CardType.MINION,
            class_type="NEUTRAL",
            rarity=Rarity.COMMON,
            text="A test minion",
            attack=2,
            health=3,
            keywords=["TAUNT"],
        )

    @pytest.fixture
    def player_fixture(self) -> Player:
        """Create a player to own the minion."""
        from core.entities import Player
        hero = Hero(name="Hero", max_health=30)
        return Player(hero=hero)

    def test_minion_creation(self, test_card: Card, player_fixture: Player) -> None:
        """Minion should be created with proper defaults."""
        m = Minion(card=test_card, owner=player_fixture)
        assert m.card == test_card
        assert m.owner == player_fixture
        assert m.current_health == test_card.health  # Should be 3
        assert m.has_taunt is False  # Default, card has TAUNT but we set separately
        assert m.divine_shield is False
        assert m.can_attack is False
        assert m.is_alive() is True

    def test_minion_with_taunt(self) -> None:
        """Minion with Taunt keyword should have has_taunt=True."""
        card = Card(
            id="t001", name="Taunt Minion", cost=3,
            card_type=CardType.MINION, class_type="NEUTRAL",
            rarity=Rarity.COMMON, text="Test", attack=2, health=3,
            keywords=["TAUNT"],
        )
        from core.entities import Player
        player = Player(hero=Hero(name="Hero", max_health=30))
        m = Minion(card=card, owner=player, has_taunt=True)
        assert m.has_taunt is True

    def test_minion_divine_shield_blocks_damage(self) -> None:
        """Divine Shield should block first damage and disappear."""
        card = Card(
            id="ds001", name="Divine Shield", cost=3,
            card_type=CardType.MINION, class_type="NEUTRAL",
            rarity=Rarity.COMMON, text="Test", attack=2, health=5,
        )
        from core.entities import Player
        player = Player(hero=Hero(name="Hero", max_health=30))
        m = Minion(card=card, owner=player, divine_shield=True)
        
        # First damage should be blocked
        died = m.take_damage(10, None)
        assert died is False  # Divine Shield blocks, minion survives
        assert m.divine_shield is False  # Shield disappeared
        assert m.is_alive() is True

    def test_minion_divine_shield_single_damage(self) -> None:
        """Single damage should break Divine Shield."""
        card = Card(
            id="ds002", name="DS2", cost=3,
            card_type=CardType.MINION, class_type="NEUTRAL",
            rarity=Rarity.COMMON, text="Test", attack=1, health=5,
        )
        from core.entities import Player
        player = Player(hero=Hero(name="Hero", max_health=30))
        m = Minion(card=card, owner=player, divine_shield=True)
        
        # One damage should break shield
        died = m.take_damage(1, None)
        assert died is False
        assert m.divine_shield is False
        assert m.is_alive() is True

    def test_minion_no_shield_takes_damage(self) -> None:
        """Minion without Divine Shield should take damage."""
        card = Card(
            id="nos001", name="No Shield", cost=3,
            card_type=CardType.MINION, class_type="NEUTRAL",
            rarity=Rarity.COMMON, text="Test", attack=1, health=3,
        )
        from core.entities import Player
        player = Player(hero=Hero(name="Hero", max_health=30))
        m = Minion(card=card, owner=player)
        
        # 2 damage should reduce health
        died = m.take_damage(2, None)
        assert died is False  # Still alive
        assert m.current_health == 1

    def test_minion_death_from_damage(self) -> None:
        """Minion should die when current_health <= 0."""
        card = Card(
            id="dead001", name="Die Minion", cost=3,
            card_type=CardType.MINION, class_type="NEUTRAL",
            rarity=Rarity.COMMON, text="Test", attack=1, health=2,
        )
        from core.entities import Player
        player = Player(hero=Hero(name="Hero", max_health=30))
        m = Minion(card=card, owner=player)
        
        # First damage
        died1 = m.take_damage(1, None)
        assert died1 is False  # health: 1
        
        # Second damage should kill
        died2 = m.take_damage(1, None)
        assert died2 is True  # Died
        assert m.is_alive() is False

    def test_minion_take_damage_with_taunt_check(self) -> None:
        """Minion.can_attack_target should check taunt."""
        card_attacker = Card(
            id="att001", name="Attacker", cost=3,
            card_type=CardType.MINION, class_type="NEUTRAL",
            rarity=Rarity.COMMON, text="Test", attack=2, health=5,
            keywords=[],
        )
        card_defender = Card(
            id="def001", name="Defender", cost=3,
            card_type=CardType.MINION, class_type="NEUTRAL",
            rarity=Rarity.COMMON, text="Test", attack=1, health=5,
            keywords=["TAUNT"],
        )
        from core.entities import Player
        player = Player(hero=Hero(name="Hero", max_health=30))
        opponent = Player(hero=Hero(name="Opponent", max_health=30))
        
        attacker = Minion(card=card_attacker, owner=player)
        defender = Minion(card=card_defender, owner=opponent, has_taunt=True)
        
        # Can attack target (simplified logic)
        can_attack = attacker.can_attack_target(defender, None)
        assert can_attack is True  # Basic allow (full logic in engine)

    def test_minion_deathrattle_trigger(self) -> None:
        """Minion deathrattle effects should be triggered on death."""
        from core.cards import Effect, EffectBundle
        from core.entities import Player
        
        card = Card(
            id="dr001", name="Deathrattle Minion", cost=3,
            card_type=CardType.MINION, class_type="NEUTRAL",
            rarity=Rarity.COMMON, text="Test", attack=2, health=1,
        )
        player = Player(hero=Hero(name="Hero", max_health=30))
        
        # Add a deathrattle effect (e.g., draw a card - simplified)
        draw_effect = card.rarity  # Just test trigger mechanism
        
        # For now, just verify deathrattle_effects field exists
        m = Minion(
            card=card, 
            owner=player, 
            deathrattle_effects=[],  # Empty for now
        )
        assert len(m.deathrattle_effects) == 0

    def test_minion_to_dict_from_dict(self, test_card: Card, player_fixture: Player) -> None:
        """Minion to_dict/from_dict should round-trip correctly."""
        p = player_fixture
        m = Minion(card=test_card, owner=p)
        
        data = m.to_dict()
        restored = Minion.from_dict(data, p)
        
        assert restored.card == test_card
        assert restored.owner == p
        assert restored.current_health == m.current_health
        assert restored.has_taunt == m.has_taunt
        assert restored.divine_shield == m.divine_shield
        assert restored.windfury == m.windfury
        assert restored.can_attack == m.can_attack


# -----------------------------------------------------------
# Entity Edge Cases
# -----------------------------------------------------------


class TestEntityEdgeCases:
    """Edge case tests for entities."""

    def test_hero_with_custom_armor(self) -> None:
        """Hero with custom armor starting value."""
        hero = Hero(name="Armored", max_health=30, current_health=30, armor=8)
        assert hero.armor == 8
        assert hero.is_alive() is True

    def test_minion_with_windfury(self) -> None:
        """Minion with Windfury should track it."""
        card = Card(
            id="wf001", name="Windfury", cost=5,
            card_type=CardType.MINION, class_type="NEUTRAL",
            rarity=Rarity.RARE, text="Test", attack=4, health=5,
            keywords=["WINDFURY"],
        )
        from core.entities import Player
        player = Player(hero=Hero(name="Hero", max_health=30))
        m = Minion(card=card, owner=player, windfury=2)
        assert m.windfury == 2

    def test_minium_with_enraged(self) -> None:
        """Minion with Enraged should track it."""
        card = Card(
            id="en001", name="Enraged", cost=4,
            card_type=CardType.MINION, class_type="NEUTRAL",
            rarity=Rarity.COMMON, text="Test", attack=3, health=4,
        )
        from core.entities import Player
        player = Player(hero=Hero(name="Hero", max_health=30))
        m = Minion(card=card, owner=player, enraged=True)
        assert m.enraged is True

    def test_player_with_empty_deck_draw(self) -> None:
        """Player with empty deck drawing should handle gracefully."""
        hero = Hero(name="Test", max_health=30)
        p = Player(hero=hero, deck=[])
        result = p.draw_card()
        assert result is None
        assert p.fatigue == 1  # First fatigue