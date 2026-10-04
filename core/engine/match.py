"""Match Lifecycle Manager for Merithra PvE.

Manages complete game lifecycle: Setup, Turn Management, Win/Loss Resolution,
Rewards Payout on Victory, and Non-destructive Retry on Defeat.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional
import copy

from core.cards import Card, CardType, get_card_registry
from core.entities import Player, Hero, Minion
from core.engine.state_machine import (
    GamePhase,
    GameEvent,
    GameState,
    StateMachine,
    create_initial_state,
)
from core.pve.ai import PvEAI, AIArchetype, AIAction, ActionType
from core.pve.encounters import Encounter, EncounterReward


class MatchStatus(Enum):
    """Current state of a match."""
    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    VICTORY = auto()
    DEFEAT = auto()


@dataclass
class MatchConfig:
    """Configuration for starting a match."""
    player_hero_name: str = "Held"
    player_hero_class: str = "MAGE"
    player_max_health: int = 30
    player_deck_ids: List[str] = field(default_factory=list)
    encounter: Optional[Encounter] = None
    ai_archetype: AIArchetype = AIArchetype.MIDRANGE


class MatchManager:
    """Manages the full lifecycle of a PvE card match."""

    def __init__(
        self,
        config: MatchConfig,
        event_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ):
        self.config = config
        self.event_callback = event_callback
        self.status = MatchStatus.NOT_STARTED

        self.player: Player
        self.opponent: Player
        self.state_machine: StateMachine
        self.ai: PvEAI
        self.combat_log: List[str] = []
        self.rewards_claimed: bool = False

        self._initialize_match()

    def _initialize_match(self) -> None:
        """Set up players, decks, hand, and state machine."""
        self.combat_log = []
        self.rewards_claimed = False
        registry = get_card_registry()

        # 1. Setup Human Player
        player_hero = Hero(
            name=self.config.player_hero_name,
            max_health=self.config.player_max_health,
            current_health=self.config.player_max_health,
            class_type=self.config.player_hero_class,
        )

        player_deck: List[Card] = []
        if self.config.player_deck_ids:
            for cid in self.config.player_deck_ids:
                c = registry.get(cid)
                if c:
                    player_deck.append(c)
        else:
            player_deck = registry.get_random_starting_deck(
                self.config.player_hero_class, count=20
            )

        self.player = Player(
            hero=player_hero,
            deck=player_deck,
            mana=1,
            max_mana=1,
        )

        # Draw starting hand (3 cards)
        for _ in range(3):
            self.player.draw_card()

        # 2. Setup Opponent Player
        if self.config.encounter:
            self.opponent = self.config.encounter.create_opponent_player()
            self.ai = PvEAI(archetype=self.config.encounter.archetype)
        else:
            opp_hero = Hero(
                name="Trainings-Gegner",
                max_health=20,
                current_health=20,
                class_type="NEUTRAL",
            )
            opp_deck = registry.get_random_starting_deck("NEUTRAL", count=20)
            self.opponent = Player(hero=opp_hero, deck=opp_deck, mana=1, max_mana=1)
            for _ in range(3):
                self.opponent.draw_card()
            self.ai = PvEAI(archetype=self.config.ai_archetype)

        # 3. Setup State Machine
        initial_state = create_initial_state("match_001", "player", "opponent")
        self.state_machine = StateMachine(initial_state)

        self.status = MatchStatus.IN_PROGRESS
        self.rewards_claimed = False
        self._log("Kampf gestartet.")

        # Transition to Player's first turn
        self.state_machine.transition(GamePhase.TURN_START)
        self.state_machine.transition(GamePhase.DRAW)
        self.state_machine.transition(GamePhase.MAIN_PHASE)
        self.state_machine.emit(GameEvent.TURN_START, player=self.player)

    def _log(self, message: str) -> None:
        """Append to internal log and trigger external callback if registered."""
        self.combat_log.append(message)
        if self.event_callback:
            self.event_callback(message, {"status": self.status.name})

    def check_match_status(self) -> MatchStatus:
        """Verify win/loss conditions."""
        if self.status in (MatchStatus.VICTORY, MatchStatus.DEFEAT):
            return self.status

        if not self.player.hero.is_alive():
            self.status = MatchStatus.DEFEAT
            self.state_machine.emit(GameEvent.GAME_END, winner=self.opponent, loser=self.player)
            self._log(f"Niederlage! {self.player.hero.name} wurde besiegt.")
            return self.status

        if not self.opponent.hero.is_alive():
            self.status = MatchStatus.VICTORY
            self.state_machine.emit(GameEvent.GAME_END, winner=self.player, loser=self.opponent)
            self._log(f"Sieg! {self.opponent.hero.name} wurde bezwungen.")
            return self.status

        return MatchStatus.IN_PROGRESS

    def play_card(self, card_id: str) -> bool:
        """Human player plays a card from hand."""
        if self.status != MatchStatus.IN_PROGRESS:
            return False
        if self.state_machine.state.phase != GamePhase.MAIN_PHASE:
            return False

        card = next((c for c in self.player.hand if c.id == card_id), None)
        if not card or card.cost > self.player.mana:
            return False

        if card.card_type == CardType.MINION and len(self.player.board) >= 7:
            return False

        if not self.player.play_card(card_id):
            return False

        if card.card_type == CardType.MINION:
            minion = Minion(
                card=card,
                owner=self.player,
                can_attack="CHARGE" in card.keywords,
                has_taunt="TAUNT" in card.keywords,
                divine_shield="DIVINE_SHIELD" in card.keywords,
            )
            self.player.board.append(minion)
            self.state_machine.emit(GameEvent.MINION_SUMMONED, player=self.player, minion=minion)
        else:
            self.player.graveyard.append(card)

        self.state_machine.state.mana = self.player.mana
        self.state_machine.emit(GameEvent.CARD_PLAYED, player=self.player, card=card)
        self._log(f"Spieler spielt {card.name}.")

        self.check_match_status()
        return True

    def attack_hero(self, minion_index: int) -> bool:
        """Human player attacks opponent hero with selected board minion."""
        if self.status != MatchStatus.IN_PROGRESS:
            return False
        if minion_index < 0 or minion_index >= len(self.player.board):
            return False

        minion = self.player.board[minion_index]
        if not isinstance(minion, Minion) or not minion.can_attack or minion.attack <= 0:
            return False

        # Taunt check
        has_taunt = any(m.has_taunt and m.is_alive() for m in self.opponent.board if isinstance(m, Minion))
        if has_taunt:
            self._log("Gegner hat einen Diener mit Spott! Du musst diesen zuerst angreifen.")
            return False

        damage = minion.attack
        self.opponent.hero.take_damage(damage, self.state_machine.state)
        minion.can_attack = False

        self.state_machine.emit(
            GameEvent.DAMAGE_DEALT,
            source=minion,
            target=self.opponent.hero,
            amount=damage,
        )
        self._log(f"{minion.card.name} greift {self.opponent.hero.name} für {damage} Schaden an.")

        self.check_match_status()
        return True

    def attack_minion(self, attacker_index: int, target_index: int) -> bool:
        """Human player attacks an enemy minion with a friendly board minion."""
        if self.status != MatchStatus.IN_PROGRESS:
            return False
        if attacker_index < 0 or attacker_index >= len(self.player.board):
            return False
        if target_index < 0 or target_index >= len(self.opponent.board):
            return False

        attacker = self.player.board[attacker_index]
        target = self.opponent.board[target_index]

        if not isinstance(attacker, Minion) or not attacker.can_attack or attacker.attack <= 0:
            return False
        if not isinstance(target, Minion) or not target.is_alive():
            return False

        # Taunt check: If any taunt minion exists, target MUST have taunt
        enemy_taunts = [m for m in self.opponent.board if isinstance(m, Minion) and m.has_taunt and m.is_alive()]
        if enemy_taunts and not target.has_taunt:
            self._log("Du musst ein Ziel mit Spott angreifen.")
            return False

        atk_dmg = attacker.attack
        tgt_dmg = target.attack

        target_died = target.take_damage(atk_dmg, self.state_machine.state)
        attacker_died = attacker.take_damage(tgt_dmg, self.state_machine.state)
        attacker.can_attack = False

        self.state_machine.emit(GameEvent.DAMAGE_DEALT, source=attacker, target=target, amount=atk_dmg)
        self._log(f"{attacker.card.name} greift {target.card.name} an ({atk_dmg} vs {tgt_dmg} Schaden).")

        if target_died and target in self.opponent.board:
            self.opponent.board.remove(target)
            self.state_machine.emit(GameEvent.MINION_DIED, minion=target, player=self.opponent)
            self._log(f"{target.card.name} wurde vernichtet.")

        if attacker_died and attacker in self.player.board:
            self.player.board.remove(attacker)
            self.state_machine.emit(GameEvent.MINION_DIED, minion=attacker, player=self.player)
            self._log(f"{attacker.card.name} wurde vernichtet.")

        self.check_match_status()
        return True

    def end_player_turn(self) -> None:
        """End player's turn, execute AI turn, and return control to player."""
        if self.status != MatchStatus.IN_PROGRESS:
            return

        # 1. Player Turn End
        self.state_machine.transition(GamePhase.TURN_END)
        self.state_machine.emit(GameEvent.TURN_END, player=self.player)
        self.player.end_turn()

        # 2. Transition to Opponent Turn
        self.state_machine.transition(GamePhase.NEXT_TURN)
        if self.opponent.turn_number > 0:
            self.opponent.max_mana = min(10, self.opponent.max_mana + 1)
        self.opponent.mana = self.opponent.max_mana

        self.state_machine.transition(GamePhase.TURN_START)
        self.state_machine.transition(GamePhase.DRAW)
        self.state_machine.transition(GamePhase.MAIN_PHASE)
        self.state_machine.emit(GameEvent.TURN_START, player=self.opponent)

        for m in self.opponent.board:
            if isinstance(m, Minion):
                m.can_attack = True

        self._log("Gegner ist am Zug.")

        # 3. AI plays turn
        ai_actions = self.ai.play_full_turn(
            ai_player=self.opponent,
            opponent_player=self.player,
            state_machine=self.state_machine,
        )
        for act in ai_actions:
            if act.action_type != ActionType.END_TURN:
                self._log(f"KI: {act.reason}")

        # Check status after AI actions
        if self.check_match_status() != MatchStatus.IN_PROGRESS:
            return

        # 4. Opponent Turn End
        self.state_machine.transition(GamePhase.TURN_END)
        self.state_machine.emit(GameEvent.TURN_END, player=self.opponent)
        self.opponent.end_turn()

        # 5. Return to Player Turn
        self.state_machine.transition(GamePhase.NEXT_TURN)
        self.player.max_mana = min(10, self.player.max_mana + 1)
        self.player.mana = self.player.max_mana
        self.state_machine.state.turn_number += 1
        self.state_machine.state.mana = self.player.mana
        self.state_machine.state.max_mana = self.player.max_mana

        self.state_machine.transition(GamePhase.TURN_START)
        self.state_machine.transition(GamePhase.DRAW)
        self.state_machine.transition(GamePhase.MAIN_PHASE)
        self.state_machine.emit(GameEvent.TURN_START, player=self.player)

        for m in self.player.board:
            if isinstance(m, Minion):
                m.can_attack = True

        self._log("Dein Zug.")

    def claim_rewards(self) -> Optional[EncounterReward]:
        """Grant encounter rewards if match resulted in victory."""
        if self.status != MatchStatus.VICTORY:
            return None
        if self.rewards_claimed:
            return None

        self.rewards_claimed = True
        if self.config.encounter:
            return self.config.encounter.rewards
        return EncounterReward(gold=10, experience=20)

    def retry_match(self) -> None:
        """Cleanly restart the match after a defeat without losing persistent progression."""
        self._log("Kampf wird neu gestartet...")
        self._initialize_match()
