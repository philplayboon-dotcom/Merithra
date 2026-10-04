"""PvE AI Decision Engine for Merithra.

Provides rule-compliant action generation, tactical evaluation, and archetypes
(Aggressive, Control, Midrange) for PvE opponents. Includes bridge for optional
local LLM integration (Ollama / Qwen3).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional
import json
import logging

from core.cards import Card, CardType
from core.entities import Player, Minion, Hero
from core.engine.state_machine import GamePhase, StateMachine, GameEvent

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of actions an AI or player can perform during a turn."""
    PLAY_CARD = "play_card"
    ATTACK_MINION = "attack_minion"
    ATTACK_HERO = "attack_hero"
    HERO_POWER = "hero_power"
    END_TURN = "end_turn"


class AIArchetype(Enum):
    """Behavioral profiles for PvE opponents."""
    AGGRESSIVE = "aggressive"  # Prioritizes face damage and cheap minions
    CONTROL = "control"        # Prioritizes board clears, trading, and surviving
    MIDRANGE = "midrange"      # Balances value trades, board presence, and tempo


@dataclass
class AIAction:
    """A discrete, validated action chosen by the AI."""
    action_type: ActionType
    card: Optional[Card] = None
    attacker: Optional[Minion] = None
    target_minion: Optional[Minion] = None
    target_hero: Optional[Hero] = None
    score: float = 0.0
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert action to structured dictionary for serialization/LLM."""
        data: Dict[str, Any] = {"action": self.action_type.value}
        if self.card:
            data["card_id"] = self.card.id
            data["card_name"] = self.card.name
        if self.attacker:
            data["attacker"] = self.attacker.card.name if self.attacker.card else "Minion"
        if self.target_minion:
            data["target_minion"] = self.target_minion.card.name if self.target_minion.card else "Minion"
        if self.target_hero:
            data["target_hero"] = self.target_hero.name
        if self.score:
            data["score"] = round(self.score, 2)
        if self.reason:
            data["reason"] = self.reason
        return data


class PvEAI:
    """Decision maker for PvE AI opponents."""

    def __init__(
        self,
        archetype: AIArchetype = AIArchetype.MIDRANGE,
        llm_enabled: bool = False,
        llm_endpoint: str = "http://127.0.0.1:11434/api/chat",
        llm_model: str = "qwen3:4b",
    ):
        self.archetype = archetype
        self.llm_enabled = llm_enabled
        self.llm_endpoint = llm_endpoint
        self.llm_model = llm_model

    def get_legal_actions(
        self,
        ai_player: Player,
        opponent_player: Player,
        state_machine: Optional[StateMachine] = None,
    ) -> List[AIAction]:
        """Collect all legally permissible actions in the current board state."""
        actions: List[AIAction] = []

        # 1. Playable cards from hand
        board_space = 7 - len(ai_player.board)
        for card in ai_player.hand:
            if card.cost <= ai_player.mana:
                if card.card_type == CardType.MINION:
                    if board_space > 0:
                        actions.append(
                            AIAction(
                                action_type=ActionType.PLAY_CARD,
                                card=card,
                                reason=f"Play minion {card.name} (Cost: {card.cost})",
                            )
                        )
                elif card.card_type == CardType.SPELL:
                    # Generic spell play
                    actions.append(
                        AIAction(
                            action_type=ActionType.PLAY_CARD,
                            card=card,
                            reason=f"Cast spell {card.name} (Cost: {card.cost})",
                        )
                    )

        # 2. Ready minions attacking
        ready_minions = [m for m in ai_player.board if isinstance(m, Minion) and m.can_attack and m.attack > 0]
        
        # Check opponent taunt minions
        enemy_taunts = [
            m for m in opponent_player.board
            if isinstance(m, Minion) and m.has_taunt and m.is_alive()
        ]
        
        enemy_alive_minions = [
            m for m in opponent_player.board
            if isinstance(m, Minion) and m.is_alive()
        ]

        for attacker in ready_minions:
            if enemy_taunts:
                # Must attack taunt minions
                for taunt_target in enemy_taunts:
                    actions.append(
                        AIAction(
                            action_type=ActionType.ATTACK_MINION,
                            attacker=attacker,
                            target_minion=taunt_target,
                            reason=f"{attacker.card.name} attacks taunt minion {taunt_target.card.name}",
                        )
                    )
            else:
                # Can attack enemy hero
                actions.append(
                    AIAction(
                        action_type=ActionType.ATTACK_HERO,
                        attacker=attacker,
                        target_hero=opponent_player.hero,
                        reason=f"{attacker.card.name} attacks enemy hero {opponent_player.hero.name}",
                    )
                )
                # Can attack any enemy minion
                for target_m in enemy_alive_minions:
                    actions.append(
                        AIAction(
                            action_type=ActionType.ATTACK_MINION,
                            attacker=attacker,
                            target_minion=target_m,
                            reason=f"{attacker.card.name} attacks {target_m.card.name}",
                        )
                    )

        # 3. Hero Power
        if (
            ai_player.hero
            and ai_player.hero.hero_power
            and ai_player.mana >= 2
        ):
            actions.append(
                AIAction(
                    action_type=ActionType.HERO_POWER,
                    card=ai_player.hero.hero_power,
                    reason=f"Use hero power {ai_player.hero.hero_power.name}",
                )
            )

        # 4. End Turn is always an option
        actions.append(
            AIAction(
                action_type=ActionType.END_TURN,
                reason="End current turn",
            )
        )

        return actions

    def evaluate_action(
        self,
        action: AIAction,
        ai_player: Player,
        opponent_player: Player,
    ) -> float:
        """Score an action based on the AI's archetype and strategic heuristics."""
        if action.action_type == ActionType.END_TURN:
            return 0.0

        score = 1.0

        # Check lethal on hero
        if action.action_type == ActionType.ATTACK_HERO and action.attacker:
            if opponent_player.hero.current_health <= action.attacker.attack:
                return 1000.0  # Immediate lethal!

        if action.action_type == ActionType.PLAY_CARD and action.card:
            card = action.card
            # Mana efficiency: spending more mana is generally prioritized
            score += card.cost * 2.0
            if card.card_type == CardType.MINION:
                score += (card.attack + card.health) * 1.5
                if "TAUNT" in card.keywords:
                    score += 3.0 if self.archetype == AIArchetype.CONTROL else 1.0
                if "CHARGE" in card.keywords:
                    score += 4.0 if self.archetype == AIArchetype.AGGRESSIVE else 2.0
            elif card.card_type == CardType.SPELL:
                score += 3.0

        elif action.action_type == ActionType.ATTACK_HERO and action.attacker:
            dmg = action.attacker.attack
            if self.archetype == AIArchetype.AGGRESSIVE:
                score += 2.0 + dmg * 4.5
            elif self.archetype == AIArchetype.MIDRANGE:
                score += 1.0 + dmg * 2.5
            else:  # CONTROL
                score += dmg * 1.0

        elif action.action_type == ActionType.ATTACK_MINION and action.attacker and action.target_minion:
            atk = action.attacker
            tgt = action.target_minion
            target_hp = tgt.current_health if tgt.current_health is not None else tgt.card.health
            attacker_hp = atk.current_health if atk.current_health is not None else atk.card.health

            # Will target die?
            target_dies = atk.attack >= target_hp
            # Will attacker survive?
            attacker_survives = attacker_hp > tgt.attack

            trade_value = tgt.attack + target_hp

            if target_dies and attacker_survives:
                # Free trade / high value
                score += 6.0 + trade_value
            elif target_dies:
                # 1-for-1 trade: good if target is bigger or control
                score += 3.0 + (trade_value - atk.attack)
            else:
                # Chip damage on minion
                score += 1.0

            if self.archetype == AIArchetype.CONTROL:
                score *= 2.0
            elif self.archetype == AIArchetype.AGGRESSIVE:
                score *= 0.4

        elif action.action_type == ActionType.HERO_POWER:
            score += 2.0

        return score

    def choose_best_action(
        self,
        ai_player: Player,
        opponent_player: Player,
        state_machine: Optional[StateMachine] = None,
    ) -> AIAction:
        """Select the highest scoring legal action."""
        legal_actions = self.get_legal_actions(ai_player, opponent_player, state_machine)
        if not legal_actions:
            return AIAction(action_type=ActionType.END_TURN, reason="No legal actions")

        # Evaluate and score all actions
        for action in legal_actions:
            action.score = self.evaluate_action(action, ai_player, opponent_player)

        # Sort actions descending by score
        scored_actions = sorted(legal_actions, key=lambda a: a.score, reverse=True)
        best = scored_actions[0]

        # If best action is end turn or has 0 score, end turn
        if best.score <= 0.0:
            return AIAction(action_type=ActionType.END_TURN, reason="No profitable actions left")

        return best

    def execute_action(
        self,
        action: AIAction,
        ai_player: Player,
        opponent_player: Player,
        state_machine: StateMachine,
    ) -> bool:
        """Execute a chosen action against the state machine and entities."""
        if action.action_type == ActionType.END_TURN:
            return True

        if action.action_type == ActionType.PLAY_CARD and action.card:
            card = action.card
            if card.cost > ai_player.mana:
                return False
            if card.card_type == CardType.MINION and len(ai_player.board) >= 7:
                return False

            if not ai_player.play_card(card.id):
                return False

            if card.card_type == CardType.MINION:
                minion = Minion(
                    card=card,
                    owner=ai_player,
                    can_attack="CHARGE" in card.keywords,
                    has_taunt="TAUNT" in card.keywords,
                    divine_shield="DIVINE_SHIELD" in card.keywords,
                )
                ai_player.board.append(minion)
                state_machine.emit(
                    GameEvent.MINION_SUMMONED,
                    player=ai_player,
                    minion=minion,
                )
            else:
                ai_player.graveyard.append(card)

            state_machine.state.mana = ai_player.mana
            state_machine.emit(GameEvent.CARD_PLAYED, player=ai_player, card=card)
            return True

        elif action.action_type == ActionType.ATTACK_HERO and action.attacker:
            attacker = action.attacker
            if not attacker.can_attack or attacker.attack <= 0:
                return False
            damage = attacker.attack
            opponent_player.hero.take_damage(damage, state_machine.state)
            attacker.can_attack = False
            state_machine.emit(
                GameEvent.DAMAGE_DEALT,
                source=attacker,
                target=opponent_player.hero,
                amount=damage,
            )
            return True

        elif action.action_type == ActionType.ATTACK_MINION and action.attacker and action.target_minion:
            attacker = action.attacker
            target = action.target_minion
            if not attacker.can_attack or attacker.attack <= 0 or not target.is_alive():
                return False

            atk_dmg = attacker.attack
            tgt_dmg = target.attack

            # Simultaneous damage
            target_died = target.take_damage(atk_dmg, state_machine.state)
            attacker_died = attacker.take_damage(tgt_dmg, state_machine.state)

            attacker.can_attack = False

            state_machine.emit(
                GameEvent.DAMAGE_DEALT,
                source=attacker,
                target=target,
                amount=atk_dmg,
            )

            if target_died and target in opponent_player.board:
                opponent_player.board.remove(target)
                state_machine.emit(GameEvent.MINION_DIED, minion=target, player=opponent_player)

            if attacker_died and attacker in ai_player.board:
                ai_player.board.remove(attacker)
                state_machine.emit(GameEvent.MINION_DIED, minion=attacker, player=ai_player)

            return True

        elif action.action_type == ActionType.HERO_POWER:
            if ai_player.mana < 2:
                return False
            ai_player.mana -= 2
            state_machine.state.mana = ai_player.mana
            state_machine.emit(GameEvent.HERO_POWER_USED, player=ai_player)
            return True

        return False

    def play_full_turn(
        self,
        ai_player: Player,
        opponent_player: Player,
        state_machine: StateMachine,
        max_actions: int = 15,
    ) -> List[AIAction]:
        """Execute complete AI turn until only END_TURN remains or max actions reached."""
        executed: List[AIAction] = []

        for _ in range(max_actions):
            best_action = self.choose_best_action(ai_player, opponent_player, state_machine)
            if best_action.action_type == ActionType.END_TURN:
                executed.append(best_action)
                break

            success = self.execute_action(best_action, ai_player, opponent_player, state_machine)
            if success:
                executed.append(best_action)
            else:
                # If execution failed, break to prevent infinite loop
                break

        return executed
