"""Main GameBoard UserControl for Merithra Flet UI.

The GameBoard displays the full game state including:
- Hero area (HP, Mana, Hero Power)
- 7 Minion board slots
- 5-card hand with Drag & Drop
- Mana crystal bar

Interacts with the Core Engine through:
- Player object (core.entities.Player)
- State Machine (core.engine.state_machine)
- Card Registry (core.cards)
"""

from __future__ import annotations

import asyncio
from typing import Any, List, Optional

import flet as ft
from client.theme import ThemeColors
from client.components.card_widget import CardWidget, MinionWidget, HeroPowerButton
from client.components.mana_crystal import ManaCrystal
from core.entities import Player, Hero, Minion, card_registry
from core.cards import Card, CardType
from core.engine.state_machine import (
    GamePhase,
    GameEvent,
    StateMachine,
    create_initial_state,
)
from core.pve import PvEAI, AIArchetype, ActionType


# ---------------------------------------------------------------------------
# GameBoard Layout Constants
# ---------------------------------------------------------------------------

# Colors (Dark Mode theme) - using theme tokens where possible
DARK_BG = ThemeColors.DARK_BG
DARK_CARD = ThemeColors.DARKER_BG
TEXT_WHITE = ThemeColors.TEXT_PRIMARY
TEXT_GRAY = ThemeColors.TEXT_SECONDARY


class GameBoard(ft.Column):
    """Main GameBoard UserControl displaying the full board state.

    Attributes:
        player: The local Player object from core.entities.
        opponent_player: The opponent Player object.
        state_machine: The game StateMachine controlling phases.
        on_end_turn: Callback when player ends their turn.
        on_hero_power: Callback when hero power is activated.
        on_minion_attack: Callback when a minion is selected to attack.
    """

    def __init__(
        self,
        player: Player,
        opponent_player: Optional[Player] = None,
        state_machine: Optional[StateMachine] = None,
        **kwargs: Any,
    ):
        kwargs.setdefault("controls", [])
        super().__init__(**kwargs)
        self.player = player
        self.opponent_player = opponent_player
        self.state_machine = state_machine or StateMachine(create_initial_state("merithra_test", "player", "opponent"))

        # Initialize card registry if not already done
        if card_registry is None:
            from core.cards import get_card_registry
            get_card_registry()  # Loads defaults

        # UI state tracking
        self._selected_minion: Optional[Minion] = None
        self._attack_target: Optional[Minion] = None
        self._phase_history: List[GamePhase] = []
        self._is_opponent_turn = False
        self._is_building = False

        # PvE AI Engine
        self.pve_ai = PvEAI(AIArchetype.MIDRANGE)

        # UI Components
        self.hero_widget: Optional[ft.Container] = None
        self.mana_bar: Optional[ManaCrystal] = None
        self._mana_crystals: list[ManaCrystal] = []
        self._mana_crystal_row: Optional[ft.Row] = None
        self.hero_power_btn: Optional[HeroPowerButton] = None
        self._attack_button: Optional[ft.FilledButton] = None
        self.minion_slots: List[ft.Control] = []
        self.hand_cards: List[CardWidget] = []
        self._board_row: Optional[ft.Row] = None
        self._hand_row: Optional[ft.Row] = None
        self._hero_hp_text: Optional[ft.Text] = None
        self._opponent_hp_text: Optional[ft.Text] = None
        self._mana_text: Optional[ft.Text] = None
        self.hand_container: Optional[ft.Container] = None
        self._game_log: ft.Text = ft.Text("", size=11, color=ThemeColors.TEXT_SECONDARY)

    def _page_or_none(self):
        """Return the Flet Page this control is attached to, or None if not yet added."""
        try:
            return self.page
        except RuntimeError:
            return None

    def build(self) -> None:
        """Build the complete GameBoard layout."""
        self._is_building = True
        page = self._page_or_none()
        # --- Top Section: Hero Area ---
        hero_area = self._build_hero_area()
        self.hero_widget = hero_area

        # --- Middle Section: Board Minion Slots ---
        self._board_row = self._build_board_slots()
        board_row = self._board_row

        # --- Bottom Section: Mana Crystal Bar + Hand ---
        # Mana bar at left bottom
        self._mana_crystals = [
            ManaCrystal(is_current=index < self.player.mana, is_max=False)
            for index in range(min(self.player.max_mana, 10))
        ]
        self.mana_bar = self._mana_crystals[0] if self._mana_crystals else None
        self._mana_crystal_row = ft.Row(self._mana_crystals, spacing=2)
        self._mana_text = ft.Text(
            f"{self.player.mana}/{self.player.max_mana}",
            size=12,
            color=ThemeColors.ACCENT_4,
        )
        mana_row = ft.Row(
            [
                ft.Text("Mana:", size=12, color=TEXT_GRAY),
                self._mana_crystal_row,
                self._mana_text,
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=4,
        )

        # Hand area - 5 cards with Drag & Drop
        hand_container = ft.Container(
            content=self._build_hand_area(),
            width=page.width if page else 800,
            height=200,
            bgcolor=DARK_CARD,
            padding=ft.Padding.all(8),
            margin=ft.Margin(top=4),
        )
        self.hand_container = hand_container

        # --- Game Log / Status ---
        self._game_log = ft.Text(
            self._get_initial_status_text(),
            size=11,
            color=ThemeColors.TEXT_SECONDARY,
        )

        attack_button = ft.FilledButton(
            "Angreifen",
            on_click=self._on_attack_button_click,
            disabled=True,
            width=140,
            bgcolor=ThemeColors.DARKER_BG,
            color=ThemeColors.TEXT_PRIMARY,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
            ),
        )
        self._attack_button = attack_button
        action_controls: list[ft.Control] = [
            attack_button,
            ft.FilledButton(
                "Zug beenden",
                on_click=self._on_end_turn_click,
                width=160,
                bgcolor=ThemeColors.DARKER_BG,
                color=ThemeColors.TEXT_PRIMARY,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=6),
                ),
            ),
            ft.FilledButton(
                "Heldenmacht",
                on_click=self._on_hero_power_click,
                width=160,
                bgcolor=ThemeColors.DARKER_BG,
                color=ThemeColors.TEXT_PRIMARY,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=6),
                ),
            ),
        ]
        footer_controls: list[ft.Control] = [
            ft.Column(
                [self._game_log],
                width=200,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                action_controls,
                alignment=ft.MainAxisAlignment.END,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
        ]
        footer = ft.Row(
            footer_controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            width=page.width if page else 800,
        )
        main_controls: list[ft.Control] = [
            hero_area,
            ft.Container(height=4),
            board_row,
            ft.Container(height=4),
            mana_row,
            hand_container,
            footer,
        ]
        self.controls = main_controls
        self.width = page.width if page else 800
        self.spacing = 0
        self.scroll = ft.ScrollMode.AUTO
        self._is_building = False

    # -------------------------------------------------------------------
    # Layout Builders
    # -------------------------------------------------------------------

    def _build_hero_area(self) -> ft.Container:
        """Build the hero portrait + HP + hero power area."""
        page = self._page_or_none()

        # Hero portrait placeholder
        hero_portrait = ft.Container(
            content=ft.Icon(ft.Icons.PERSON, size=40, color=ThemeColors.ACCENT_3),
            width=100,
            height=60,
            bgcolor=ThemeColors.DARKER_BG,
            border=ft.Border.all(2, ThemeColors.ACCENT_3),
            border_radius=6,
            alignment=ft.Alignment.CENTER,
        )

        # Hero name
        hero_name = ft.Text(
            self.player.hero.name,
            size=14,
            weight=ft.FontWeight.BOLD,
            color=ThemeColors.TEXT_PRIMARY,
        )

        # Hero HP
        hero_hp_text = ft.Text(
            f"{self.player.hero.current_health}/{self.player.hero.max_health}",
            size=12,
            color=ThemeColors.HP_LOW if self.player.hero.current_health < 10 else ThemeColors.TEXT_PRIMARY,
        )
        self._hero_hp_text = hero_hp_text

        # Hero Power button (initially, we use a simple button)
        self.hero_power_btn = HeroPowerButton(
            hero_power_card=self.player.hero.hero_power,
            player_mana=self.player.mana,
            max_mana=self.player.max_mana,
            on_hero_power=self._on_hero_power_used,
            width=140,
            height=50,
        )

        self.hero_power_btn.build()

        hero_controls: list[ft.Control] = [
            ft.Column(
                [hero_portrait, hero_name, hero_hp_text],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            ft.Column(
                [self.hero_power_btn],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
        ]
        if self.opponent_player:
            opponent_hero = self.opponent_player.hero
            self._opponent_hp_text = ft.Text(
                f"{opponent_hero.current_health}/{opponent_hero.max_health}",
                size=12,
                color=ThemeColors.TEXT_PRIMARY,
            )
            hero_controls.append(
                ft.Column(
                    [
                        ft.Text(
                            opponent_hero.name,
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=ThemeColors.TEXT_SECONDARY,
                        ),
                        ft.Text("Gegnerheld", size=11, color=ThemeColors.TEXT_MUTED),
                        self._opponent_hp_text,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                )
            )

        return ft.Container(
            content=ft.Row(
                hero_controls,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=24,
            ),
            width=page.width if page else 800,
            bgcolor=ThemeColors.DARKER_BG,
            padding=ft.Padding.all(8),
        )

    def _build_hand_area(self) -> ft.Row:
        """Build the hand area with 5 cards and Drag & Drop support."""
        self._hand_row = ft.Row(
            [
                self._empty_hand_slot()
                for _ in range(5)
            ],
            wrap=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        )
        self._refresh_hand_cards()
        return self._hand_row

    @staticmethod
    def _empty_hand_slot() -> ft.Container:
        return ft.Container(
            width=120,
            height=180,
            bgcolor=DARK_CARD,
            border=ft.Border.all(1, ThemeColors.TEXT_MUTED),
            border_radius=8,
        )

    def _build_board_slots(self) -> ft.Row:
        """Build the 7 minion board slots."""
        self._board_row = ft.Row(
            [
                ft.Container(
                    width=100,
                    height=80,
                    bgcolor=ThemeColors.DARKER_BG,
                    border=ft.Border.all(1, ThemeColors.TEXT_MUTED),
                    border_radius=6,
                )
                for _ in range(7)
            ],
            wrap=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        )
        self._refresh_board()
        return self._board_row

    # -------------------------------------------------------------------
    # State Refresh & UI Updates
    # -------------------------------------------------------------------

    def _refresh_hand_cards(self) -> None:
        """Refresh the hand card widgets based on player.hand."""
        if self._hand_row is None:
            return

        new_cards = []
        self.hand_cards = []
        for i in range(5):
            if i < len(self.player.hand):
                card_widget = CardWidget(
                    card=self.player.hand[i],
                    on_play=self._on_card_play_from_hand,
                    on_click=self._on_card_click,
                    on_drag_start=self._on_hand_drag_start,
                    on_drag_end=self._on_hand_drag_end,
                )
                self.hand_cards.append(card_widget)
                new_cards.append(card_widget)
            else:
                new_cards.append(self._empty_hand_slot())

        self._hand_row.controls = new_cards
        if not self._is_building:
            try:
                self._hand_row.page
            except RuntimeError:
                return
            self._hand_row.update()

    def _refresh_board(self) -> None:
        """Refresh the board minion slots based on player.board."""
        if self._board_row is None:
            return

        slots: list[ft.Control] = []
        self.minion_slots = []
        for i in range(7):
            if i < len(self.player.board):
                minion = self.player.board[i]
                if not isinstance(minion, Minion):
                    raise TypeError(f"Expected Minion in player.board, got {type(minion).__name__}")
                widget = MinionWidget(
                    minion=minion,
                    on_attack_select=self._on_minion_attack_select,
                )
                self.minion_slots.append(widget)
                slots.append(widget)
            else:
                empty_slot = ft.Container(
                    width=100,
                    height=80,
                    bgcolor=ThemeColors.DARKER_BG,
                    border=ft.Border.all(1, ThemeColors.TEXT_MUTED),
                    border_radius=6,
                )
                self.minion_slots.append(empty_slot)
                slots.append(empty_slot)

        self._board_row.controls = slots
        if not self._is_building:
            try:
                self._board_row.page
            except RuntimeError:
                return
            self._board_row.update()

    def _refresh_mana(self) -> None:
        """Update the mana crystal display."""
        crystal_count = min(self.player.max_mana, 10)
        if len(self._mana_crystals) != crystal_count:
            self._mana_crystals = [
                ManaCrystal(is_current=index < self.player.mana, is_max=False)
                for index in range(crystal_count)
            ]
            self.mana_bar = self._mana_crystals[0] if self._mana_crystals else None
            if self._mana_crystal_row:
                self._mana_crystal_row.controls = self._mana_crystals
                page = self._page_or_none()
                if page:
                    self._mana_crystal_row.update()
        else:
            for index, crystal in enumerate(self._mana_crystals):
                crystal.update_state(
                    is_current=index < self.player.mana,
                    is_max=False,
                )
        if self._mana_text:
            self._mana_text.value = f"{self.player.mana}/{self.player.max_mana}"
            if self._page_or_none():
                self._mana_text.update()
        if self.hero_power_btn:
            self.hero_power_btn.player_mana = self.player.mana
            self.hero_power_btn.max_mana = self.player.max_mana
            self.hero_power_btn._update_mana_display()

    def _refresh_hero_hp(self) -> None:
        """Update hero health display."""
        if self._hero_hp_text:
            self._hero_hp_text.value = (
                f"{self.player.hero.current_health}/{self.player.hero.max_health}"
            )
            hp_percent = self.player.hero.current_health / self.player.hero.max_health
            if hp_percent < 0.3:
                self._hero_hp_text.color = ThemeColors.HP_LOW
            elif hp_percent < 0.6:
                self._hero_hp_text.color = ThemeColors.ACCENT_4
            else:
                self._hero_hp_text.color = ThemeColors.TEXT_PRIMARY
            if self._page_or_none():
                self._hero_hp_text.update()
        if self.opponent_player and self._opponent_hp_text:
            self._opponent_hp_text.value = (
                f"{self.opponent_player.hero.current_health}/"
                f"{self.opponent_player.hero.max_health}"
            )
            if self._page_or_none():
                self._opponent_hp_text.update()

    def _refresh_status_text(self) -> None:
        """Refresh the game status/log text."""
        if self._game_log:
            phase_name = self.state_machine.state.phase.name if self.state_machine else "UNKNOWN"
            text = (
                f"Phase: {phase_name} | Zug: {self.player.turn_number} | "
                f"Mana: {self.player.mana}/{self.player.max_mana} | "
                f"HP: {self.player.hero.current_health}/{self.player.hero.max_health}"
            )
            self._game_log.value = text
            if self._page_or_none():
                self._game_log.update()

    def _get_initial_status_text(self) -> str:
        """Get initial status text."""
        return (
            f"Phase: {self.state_machine.state.phase.name if self.state_machine else 'UNKNOWN'} | "
            f"Zug: {self.player.turn_number} | "
            f"Mana: {self.player.mana}/{self.player.max_mana} | "
            f"HP: {self.player.hero.current_health}/{self.player.hero.max_health}"
        )

    # -------------------------------------------------------------------
    # Event Handlers
    # -------------------------------------------------------------------

    def _on_card_play_from_hand(self, card: Card) -> None:
        """Handle playing a card from hand to board."""
        if self.state_machine.state.phase != GamePhase.MAIN_PHASE or self._is_opponent_turn:
            self._add_log("Karten können nur in der eigenen Hauptphase gespielt werden.")
            return

        if not self._play_card_for_player(self.player, card):
            self._add_log(f"Karte konnte nicht gespielt werden: {card.name}")
            return

        self._add_log(f"Karte gespielt: {card.name}")
        self._refresh_hand_cards()
        self._refresh_board()
        self._refresh_mana()
        self._refresh_status_text()

    def _play_card_for_player(self, player: Player, card: Card) -> bool:
        if card.card_type == CardType.MINION and len(player.board) >= 7:
            return False
        if not player.play_card(card.id):
            return False

        if card.card_type == CardType.MINION:
            minion = Minion(
                card=card,
                owner=player,
                can_attack="CHARGE" in card.keywords,
            )
            player.board.append(minion)
            self.state_machine.emit(
                GameEvent.MINION_SUMMONED,
                player=player,
                minion=minion,
            )
        else:
            player.graveyard.append(card)

        self.state_machine.state.mana = player.mana
        self.state_machine.emit(GameEvent.CARD_PLAYED, player=player, card=card)
        return True

    def _on_card_click(self, card: Card) -> None:
        """Handle card click (e.g., for spell targeting)."""
        self._add_log(f"Karte geklickt: {card.name} - Zielauswahl nötig")

    def _on_hand_drag_start(self) -> None:
        """Handle drag start from hand."""
        self._add_log("Ziehen begonnen")

    def _on_hand_drag_end(self) -> None:
        """Handle drag end from hand."""
        self._add_log("Ziehen beendet")

    def _on_minion_attack_select(self, minion: Minion) -> None:
        """Handle minion attack target selection."""
        if (
            self._is_opponent_turn
            or self.state_machine.state.phase != GamePhase.MAIN_PHASE
            or minion.owner is not self.player
            or not minion.can_attack
        ):
            return
        self._selected_minion = minion
        self._add_log(f"Minion ausgewählt für Angriff: {minion.card.name if minion.card else 'Unknown'}")
        if self._attack_button:
            self._attack_button.disabled = self.opponent_player is None
            if self._page_or_none():
                self._attack_button.update()

        # Highlight the selected minion
        if minion and minion.can_attack:
            self._add_log("Gegnerheld kann angegriffen werden.")

    def _show_attack_targets(self, attacker: Minion) -> None:
        """Show available attack targets (enemy hero, enemy minions)."""
        self._add_log("Angriffsziele verfügbar: Gegner-Heror oder gegnerische Minions")

    def _on_attack_button_click(self, e: ft.Event[ft.Button]) -> None:
        attacker = self._selected_minion
        opponent = self.opponent_player
        if (
            attacker is None
            or opponent is None
            or self._is_opponent_turn
            or self.state_machine.state.phase != GamePhase.MAIN_PHASE
            or not attacker.can_attack
        ):
            self._add_log("Kein angreifender Minion ausgewählt.")
            return

        damage = attacker.attack
        opponent.hero.take_damage(damage, self.state_machine.state)
        attacker.can_attack = False
        self.state_machine.emit(
            GameEvent.DAMAGE_DEALT,
            source=attacker,
            target=opponent.hero,
            amount=damage,
        )
        self._add_log(
            f"{attacker.card.name} greift den Gegnerhelden für {damage} Schaden an."
        )
        self._selected_minion = None
        if self._attack_button:
            self._attack_button.disabled = True
            if self._page_or_none():
                self._attack_button.update()
        self._refresh_hero_hp()

    def _on_end_turn_click(self, e: ft.Event[ft.Button]) -> None:
        """Handle end turn button click."""
        self._on_end_turn()

    def _on_end_turn(self) -> None:
        """End the current turn - transition to next turn."""
        if self.state_machine.state.phase != GamePhase.MAIN_PHASE:
            self._add_log("Der Zug kann nur in der Hauptphase beendet werden.")
            return

        ending_ai_turn = self._is_opponent_turn
        active_player = self.opponent_player if ending_ai_turn else self.player
        if active_player is None:
            self._add_log("Kein aktiver Spieler für den Zugwechsel.")
            return

        if not self.state_machine.transition(GamePhase.TURN_END):
            self._add_log("Phase Transition to TURN_END failed.")
            return
        self.state_machine.emit(GameEvent.TURN_END, player=active_player)
        active_player.end_turn()

        if not self.state_machine.transition(GamePhase.NEXT_TURN):
            self._add_log("Phase Transition to NEXT_TURN failed.")
            return

        self._is_opponent_turn = not ending_ai_turn and self.opponent_player is not None
        next_player = (
            self.opponent_player
            if self._is_opponent_turn and self.opponent_player is not None
            else self.player
        )
        if next_player.turn_number:
            next_player.max_mana = min(10, next_player.max_mana + 1)
        next_player.mana = next_player.max_mana
        self.state_machine.state.turn_number += 1
        self.state_machine.state.mana = next_player.mana
        self.state_machine.state.max_mana = next_player.max_mana

        for phase in (GamePhase.TURN_START, GamePhase.DRAW, GamePhase.MAIN_PHASE):
            if not self.state_machine.transition(phase):
                self._add_log(f"Phase Transition to {phase.name} failed.")
                return
        self.state_machine.emit(GameEvent.TURN_START, player=next_player)
        for minion in next_player.board:
            if isinstance(minion, Minion):
                minion.can_attack = True

        self._selected_minion = None
        if self._attack_button:
            self._attack_button.disabled = True
        self._refresh_hand_cards()
        self._refresh_board()
        self._refresh_mana()
        self._refresh_hero_hp()
        self._refresh_status_text()
        if self._is_opponent_turn:
            self._check_opponent_turn()
        else:
            self._add_log("Dein Zug.")

    def _on_hero_power_used(self) -> None:
        """Handle hero power activation."""
        # Cost is already validated in the button, but let's ensure
        if self.player.mana >= 2:
            # Apply hero power effects
            if self.player.hero.hero_power:
                # Remove 2 mana
                self.player.mana -= 2

                # TODO: Apply hero power effects via engine
                # For now, just end the hero power action
                self._add_log(f"Heldenmacht aktiviert: {self.player.hero.hero_power.name if self.player.hero.hero_power else 'Unknown'}")

            # Refresh UI
            self._refresh_mana()
            self._refresh_status_text()

            # After hero power, typically end turn or continue
            # For MVP, we'll let the player continue their turn
        else:
            self._add_log("Nicht genug Mana für Heldenmacht!")

    def _on_hero_power_click(self, e: ft.Event[ft.Button]) -> None:
        """Hero power button click handler wrapper."""
        self._on_hero_power_used()

    def _check_game_phase(self) -> None:
        """Check game phase and potentially end turn."""
        # Simple MVP: after playing a card, check phase
        current_phase = self.state_machine.state.phase if self.state_machine else GamePhase.MAIN_PHASE
        if current_phase == GamePhase.MAIN_PHASE:
            # Could auto-end or let player decide
            pass

    def _check_opponent_turn(self) -> None:
        """Check if it's now the opponent's turn (AI)."""
        page = self._page_or_none()
        if self._is_opponent_turn and page:
            self._add_log("KI ist am Zug.")
            page.run_task(self._ai_turn)

    # -------------------------------------------------------------------
    # Helper & Utility Methods
    # -------------------------------------------------------------------

    def _add_log(self, message: str) -> None:
        """Add a message to the game log."""
        if self._game_log:
            # Prepend timestamp/phase info
            from datetime import datetime
            ts = datetime.now().strftime("%H:%M:%S")
            self._game_log.value = f"[{ts}] {message}\n{self._game_log.value or ''}"
            if self._page_or_none():
                self._game_log.update()

    async def _ai_turn(self) -> None:
        """Execute AI turn using PvEAI engine and return control to player."""
        if not self._is_opponent_turn or self.opponent_player is None:
            return
        if self.state_machine.state.phase != GamePhase.MAIN_PHASE:
            return

        await asyncio.sleep(0.2)
        ai_player = self.opponent_player

        if hasattr(self, "pve_ai") and self.pve_ai:
            actions = self.pve_ai.play_full_turn(ai_player, self.player, self.state_machine)
            for act in actions:
                if act.action_type != ActionType.END_TURN:
                    self._add_log(f"KI: {act.reason}")
        else:
            for card in list(ai_player.hand):
                if card.cost > ai_player.mana:
                    continue
                if card.card_type == CardType.MINION and len(ai_player.board) >= 7:
                    continue
                if self._play_card_for_player(ai_player, card):
                    self._add_log(f"KI spielt: {card.name}")
                    break

        self._refresh_board()
        self._refresh_hero_hp()
        self._on_end_turn()

def main(page: ft.Page) -> None:
    """Entry point for the Merithra Flet application."""

    # --- Page Setup ---
    page.title = "Merithra - Card Game"
    page.theme_mode = ft.ThemeMode.DARK  # Dark mode basis
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    page.window.width = 800
    page.window.height = 600

    # --- Game State Initialization ---
    # Initialize card registry (loads default cards)
    from core.cards import get_card_registry
    registry = get_card_registry()

    # Create players
    # For MVP: Human player with MAGE hero, AI opponent with WARRIOR hero
    hero1 = Hero(
        name="Jaina",
        max_health=30,
        class_type="MAGE",
        hero_power=None,  # No hero power for MVP
    )

    hero2 = Hero(
        name="Thrall",
        max_health=30,
        class_type="WARRIOR",
        # Warrior hero power: "Waffe attackieren" - simplified
        hero_power=None,  # Will use weapon mechanic later
    )

    player1 = Player(hero=hero1, max_mana=1)
    player1.mana = 1  # Start mana

    player1.deck = registry.get_random_starting_deck("MAGE", count=20)
    player2 = Player(hero=hero2, max_mana=1)
    player2.mana = 1
    player2.deck = registry.get_random_starting_deck("WARRIOR", count=20)

    for player in (player1, player2):
        for _ in range(5):
            player.draw_card()

    # Set game state
    initial_state = create_initial_state("merithra_demo", "player1", "player2")
    state_machine = StateMachine(initial_state)
    state_machine.transition(GamePhase.TURN_START)
    state_machine.transition(GamePhase.DRAW)
    state_machine.transition(GamePhase.MAIN_PHASE)

    # Connect state machine to players
    player1.game_state = initial_state
    player2.game_state = initial_state

    # --- UI Setup ---
    # Create GameBoard for local player
    game_board = GameBoard(
        player=player1,
        opponent_player=player2,
        state_machine=state_machine,
    )

    # Add game board to page
    page.add(game_board)
    page.update()


if __name__ == "__main__":
    ft.run(main)