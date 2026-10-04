"""Unit tests for Match Lifecycle Manager and PvE Match flows."""

import pytest
from core.cards import Card, CardType, Rarity, get_card_registry
from core.entities import Player, Hero, Minion
from core.engine.match import MatchManager, MatchConfig, MatchStatus
from core.pve.encounters import get_encounter, DEFAULT_ENCOUNTERS


def test_match_initialization():
    """Test match manager boots with correct player decks and state."""
    config = MatchConfig(
        player_hero_name="Jaina",
        player_hero_class="MAGE",
        player_max_health=30,
        encounter=get_encounter("enc_wild_wolf"),
    )

    manager = MatchManager(config)

    assert manager.status == MatchStatus.IN_PROGRESS
    assert manager.player.hero.name == "Jaina"
    assert manager.player.hero.current_health == 30
    assert len(manager.player.hand) == 3
    assert manager.opponent.hero.name == "Leitwolf"
    assert len(manager.opponent.hand) == 3
    assert len(manager.combat_log) > 0


def test_match_player_actions():
    """Test playing cards and attacking."""
    config = MatchConfig(
        player_hero_name="Hero",
        player_hero_class="MAGE",
        encounter=get_encounter("enc_wild_wolf"),
    )
    manager = MatchManager(config)

    # Give player 5 mana and a cheap minion card
    c = Card(id="c_test", name="Fast Wolf", cost=1, card_type=CardType.MINION, class_type="NEUTRAL", rarity=Rarity.COMMON, text="", attack=3, health=2, keywords=["CHARGE"])
    manager.player.hand.append(c)
    manager.player.mana = 5

    # Play card
    success = manager.play_card("c_test")
    assert success is True
    assert len(manager.player.board) == 1
    assert manager.player.mana == 4

    # Attack enemy hero with charge minion
    opp_hp_before = manager.opponent.hero.current_health
    atk_success = manager.attack_hero(0)
    assert atk_success is True
    assert manager.opponent.hero.current_health == opp_hp_before - 3


def test_match_victory_and_rewards():
    """Test victory detection and claiming rewards."""
    config = MatchConfig(
        player_hero_name="Hero",
        encounter=get_encounter("enc_wild_wolf"),
    )
    manager = MatchManager(config)

    # Set opponent health to 2 and attack for 3 damage
    manager.opponent.hero.current_health = 2
    c = Card(id="c_finisher", name="Finisher", cost=1, card_type=CardType.MINION, class_type="NEUTRAL", rarity=Rarity.COMMON, text="", attack=3, health=2, keywords=["CHARGE"])
    manager.player.board.append(Minion(card=c, owner=manager.player, can_attack=True))

    manager.attack_hero(0)

    assert manager.status == MatchStatus.VICTORY
    rewards = manager.claim_rewards()
    assert rewards is not None
    assert rewards.gold == 25
    assert rewards.experience == 50
    assert "card_001" in rewards.guaranteed_cards

    # Multiple claims should return None (prevents reward duplication)
    second_claim = manager.claim_rewards()
    assert second_claim is None


def test_match_defeat_and_retry():
    """Test defeat condition and non-destructive retry flow."""
    config = MatchConfig(
        player_hero_name="Hero",
        encounter=get_encounter("enc_wild_wolf"),
    )
    manager = MatchManager(config)

    # Defeat player hero
    manager.player.hero.current_health = 0
    status = manager.check_match_status()

    assert status == MatchStatus.DEFEAT
    assert manager.claim_rewards() is None

    # Retry match cleanly
    manager.retry_match()

    assert manager.status == MatchStatus.IN_PROGRESS
    assert manager.player.hero.current_health == 30
    assert manager.opponent.hero.current_health == 15
    assert len(manager.player.hand) == 3
    assert len(manager.opponent.hand) == 3
    assert manager.combat_log
    assert "Kampf gestartet." in manager.combat_log[0]


def test_match_full_turn_cycle():
    """Test ending player turn runs AI turn and returns to player."""
    config = MatchConfig(
        player_hero_name="Hero",
        encounter=get_encounter("enc_wild_wolf"),
    )
    manager = MatchManager(config)

    # End player turn
    manager.end_player_turn()

    # Now it should be player turn again with increased mana
    assert manager.player.max_mana == 2
    assert manager.player.mana == 2
    assert manager.player.turn_number >= 1
