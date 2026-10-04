"""Unit tests for PvE AI Decision Engine."""

import pytest
from core.cards import Card, CardType, Rarity, get_card_registry
from core.entities import Player, Hero, Minion
from core.engine.state_machine import StateMachine, create_initial_state, GamePhase
from core.pve.ai import PvEAI, AIArchetype, AIAction, ActionType
from core.pve.encounters import Encounter, DEFAULT_ENCOUNTERS, get_encounter


@pytest.fixture
def base_game_setup():
    """Create basic two-player setup with state machine."""
    hero_ai = Hero(name="Boss", max_health=20, current_health=20, class_type="NEUTRAL")
    hero_player = Hero(name="Player", max_health=30, current_health=30, class_type="MAGE")

    ai_player = Player(hero=hero_ai, mana=3, max_mana=3)
    human_player = Player(hero=hero_player, mana=3, max_mana=3)

    state = create_initial_state("test_ai_game", "ai", "human")
    sm = StateMachine(state)
    sm.transition(GamePhase.TURN_START)
    sm.transition(GamePhase.DRAW)
    sm.transition(GamePhase.MAIN_PHASE)

    return ai_player, human_player, sm


def test_ai_collects_legal_actions(base_game_setup):
    """Test that AI accurately enumerates playable cards and board attacks."""
    ai_player, human_player, sm = base_game_setup

    card1 = Card(id="c1", name="Wolf", cost=1, card_type=CardType.MINION, class_type="NEUTRAL", rarity=Rarity.COMMON, text="", attack=1, health=1)
    card2 = Card(id="c2", name="Bear", cost=4, card_type=CardType.MINION, class_type="NEUTRAL", rarity=Rarity.COMMON, text="", attack=4, health=4)

    ai_player.hand = [card1, card2]

    minion = Minion(card=card1, owner=ai_player, can_attack=True)
    ai_player.board = [minion]

    ai = PvEAI(archetype=AIArchetype.MIDRANGE)
    legal = ai.get_legal_actions(ai_player, human_player, sm)

    action_types = [a.action_type for a in legal]
    assert ActionType.PLAY_CARD in action_types  # card1 is playable (cost 1 <= 3)
    assert ActionType.ATTACK_HERO in action_types  # ready minion can attack hero
    assert ActionType.END_TURN in action_types  # always legal


def test_ai_respects_enemy_taunt(base_game_setup):
    """Test that AI must attack enemy minions with Taunt and cannot attack face."""
    ai_player, human_player, sm = base_game_setup

    card_atk = Card(id="c1", name="Attacker", cost=1, card_type=CardType.MINION, class_type="NEUTRAL", rarity=Rarity.COMMON, text="", attack=2, health=2)
    card_taunt = Card(id="c2", name="Defender", cost=2, card_type=CardType.MINION, class_type="NEUTRAL", rarity=Rarity.COMMON, text="", attack=1, health=3, keywords=["TAUNT"])

    ai_minion = Minion(card=card_atk, owner=ai_player, can_attack=True)
    ai_player.board = [ai_minion]

    player_taunt = Minion(card=card_taunt, owner=human_player, has_taunt=True, current_health=3)
    human_player.board = [player_taunt]

    ai = PvEAI()
    legal = ai.get_legal_actions(ai_player, human_player, sm)

    # Face attack should NOT be legal when enemy has taunt
    hero_attacks = [a for a in legal if a.action_type == ActionType.ATTACK_HERO]
    assert len(hero_attacks) == 0

    # Taunt attack MUST be legal
    minion_attacks = [a for a in legal if a.action_type == ActionType.ATTACK_MINION]
    assert len(minion_attacks) == 1
    assert minion_attacks[0].target_minion == player_taunt


def test_ai_detects_lethal(base_game_setup):
    """Test that AI prioritizes lethal face attack above all else."""
    ai_player, human_player, sm = base_game_setup
    human_player.hero.current_health = 5

    big_card = Card(id="c_big", name="Golem", cost=6, card_type=CardType.MINION, class_type="NEUTRAL", rarity=Rarity.RARE, text="", attack=6, health=6)
    ai_minion = Minion(card=big_card, owner=ai_player, can_attack=True)
    ai_player.board = [ai_minion]

    ai = PvEAI(archetype=AIArchetype.CONTROL)  # Even control archetype should execute lethal!
    best = ai.choose_best_action(ai_player, human_player, sm)

    assert best.action_type == ActionType.ATTACK_HERO
    assert best.score >= 1000.0


def test_ai_archetypes_prioritization(base_game_setup):
    """Test aggressive vs control scoring differences."""
    ai_player, human_player, sm = base_game_setup

    atk_card = Card(id="c1", name="Wolf", cost=1, card_type=CardType.MINION, class_type="NEUTRAL", rarity=Rarity.COMMON, text="", attack=2, health=2)
    tgt_card = Card(id="c2", name="Enemy Minion", cost=1, card_type=CardType.MINION, class_type="NEUTRAL", rarity=Rarity.COMMON, text="", attack=1, health=2)

    ai_minion = Minion(card=atk_card, owner=ai_player, can_attack=True)
    enemy_minion = Minion(card=tgt_card, owner=human_player, current_health=2)

    ai_player.board = [ai_minion]
    human_player.board = [enemy_minion]

    ai_aggro = PvEAI(archetype=AIArchetype.AGGRESSIVE)
    ai_control = PvEAI(archetype=AIArchetype.CONTROL)

    act_face = AIAction(action_type=ActionType.ATTACK_HERO, attacker=ai_minion, target_hero=human_player.hero)
    act_trade = AIAction(action_type=ActionType.ATTACK_MINION, attacker=ai_minion, target_minion=enemy_minion)

    aggro_face_score = ai_aggro.evaluate_action(act_face, ai_player, human_player)
    aggro_trade_score = ai_aggro.evaluate_action(act_trade, ai_player, human_player)
    assert aggro_face_score > aggro_trade_score

    control_face_score = ai_control.evaluate_action(act_face, ai_player, human_player)
    control_trade_score = ai_control.evaluate_action(act_trade, ai_player, human_player)
    assert control_trade_score > control_face_score


def test_ai_plays_full_turn(base_game_setup):
    """Test that play_full_turn executes playable actions until ending turn."""
    ai_player, human_player, sm = base_game_setup

    c1 = Card(id="c1", name="Wolf 1", cost=1, card_type=CardType.MINION, class_type="NEUTRAL", rarity=Rarity.COMMON, text="", attack=1, health=1)
    c2 = Card(id="c2", name="Wolf 2", cost=1, card_type=CardType.MINION, class_type="NEUTRAL", rarity=Rarity.COMMON, text="", attack=1, health=1)

    ai_player.hand = [c1, c2]
    ai_player.mana = 2

    ai = PvEAI(archetype=AIArchetype.AGGRESSIVE)
    actions = ai.play_full_turn(ai_player, human_player, sm)

    assert len(actions) >= 2
    assert len(ai_player.board) == 2
    assert ai_player.mana == 0
    assert actions[-1].action_type == ActionType.END_TURN


def test_encounters_creation():
    """Test encounter setup from defaults."""
    enc = get_encounter("enc_wild_wolf")
    assert enc is not None
    assert enc.max_health == 15
    assert enc.archetype == AIArchetype.AGGRESSIVE

    opponent = enc.create_opponent_player()
    assert opponent.hero.name == "Leitwolf"
    assert opponent.hero.current_health == 15
    assert len(opponent.hand) == 3
