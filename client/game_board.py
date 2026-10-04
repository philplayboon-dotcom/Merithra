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
from typing import Any, Callable, List, Optional

import flet as ft
from client.theme import CombatColors
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
from core.engine.match import MatchManager, MatchStatus
from core.pve import PvEAI, AIArchetype, ActionType


# ---------------------------------------------------------------------------
# GameBoard Layout Constants
# ---------------------------------------------------------------------------

# Colors (Dark Mode theme) - using theme tokens where possible
DARK_BG = CombatColors.BACKGROUND
DARK_CARD = CombatColors.PANEL
TEXT_WHITE = CombatColors.TEXT_PRIMARY
TEXT_GRAY = CombatColors.TEXT_SECONDARY


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
        match_manager: Optional[MatchManager] = None,
        on_match_end: Optional[Callable[[MatchStatus], None]] = None,
        **kwargs: Any,
    ):
        kwargs.setdefault("controls", [])
        super().__init__(**kwargs)
        self.player = player
        self.opponent_player = opponent_player
        self.state_machine = state_machine or StateMachine(create_initial_state("merithra_test", "player", "opponent"))
        self.match_manager = match_manager
        self.on_match_end = on_match_end
        self.match_status = (
            match_manager.status if match_manager is not None else MatchStatus.IN_PROGRESS
        )

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
        self._end_turn_button: Optional[ft.FilledButton] = None
        self.minion_slots: List[ft.Control] = []
        self.opponent_minion_slots: List[ft.Control] = []
        self.hand_cards: List[CardWidget] = []
        self._board_row: Optional[ft.Row] = None
        self._opponent_board_row: Optional[ft.Row] = None
        self._turn_banner: Optional[ft.Container] = None
        self._turn_banner_text: Optional[ft.Text] = None
        self._target_help_text: Optional[ft.Text] = None
        self._hand_row: Optional[ft.Row] = None
        self._hero_hp_text: Optional[ft.Text] = None
        self._opponent_hp_text: Optional[ft.Text] = None
        self._player_hp_bar: Optional[ft.ProgressBar] = None
        self._opponent_hp_bar: Optional[ft.ProgressBar] = None
        self._mana_text: Optional[ft.Text] = None
        self._selected_attacker_text: Optional[ft.Text] = None
        self._selected_attacker_panel: Optional[ft.Container] = None
        self._result_banner: Optional[ft.Container] = None
        self._result_text: Optional[ft.Text] = None
        self.hand_container: Optional[ft.Container] = None
        self._game_log: ft.Text = ft.Text("", size=11, color=CombatColors.TEXT_SECONDARY)
        self._combat_log_entries: list[str] = []

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
        self._turn_banner = self._build_turn_banner()
        # --- Top Section: Hero Area ---
        hero_area = self._build_hero_area()
        self.hero_widget = hero_area

        # --- Battlefield: enemy minions first, then the player's minions ---
        self._opponent_board_row = self._build_opponent_board_slots()
        self._board_row = self._build_board_slots()
        board_row = self._board_row
        opponent_board_panel = self._build_field_panel(
            "GEGNERISCHES FELD", self._opponent_board_row, enemy=True
        )
        player_board_panel = self._build_field_panel(
            "DEIN FELD", board_row, enemy=False
        )

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
            color=CombatColors.RESOURCE,
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
            expand=3,
            height=200,
            bgcolor=CombatColors.PANEL,
            border=ft.Border.all(1, CombatColors.PANEL_HOVER),
            border_radius=10,
            padding=ft.Padding.all(8),
            margin=ft.Margin(top=4),
        )
        self.hand_container = hand_container

        # --- Game Log / Status ---
        self._game_log = ft.Text(
            "Kampf gestartet.",
            size=12,
            color=CombatColors.TEXT_SECONDARY,
            selectable=True,
        )
        self._result_text = ft.Text("", size=18, weight=ft.FontWeight.BOLD)
        self._result_banner = ft.Container(
            content=self._result_text,
            bgcolor=CombatColors.PANEL,
            border=ft.Border.all(2, CombatColors.SUCCESS),
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            visible=False,
            alignment=ft.Alignment.CENTER,
        )
        self._selected_attacker_text = ft.Text(
            "Wähle zuerst einen bereiten Diener.",
            size=12,
            color=CombatColors.TEXT_SECONDARY,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        self._target_help_text = self._selected_attacker_text
        self._selected_attacker_panel = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.SPORTS_MARTIAL_ARTS, color=CombatColors.PLAYER, size=18),
                    self._selected_attacker_text,
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=CombatColors.PANEL,
            border=ft.Border.all(1, CombatColors.PLAYER),
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            expand=True,
        )

        attack_button = ft.FilledButton(
            "Angreifen",
            on_click=self._on_attack_button_click,
            disabled=True,
            width=180,
            bgcolor=CombatColors.PANEL_HOVER,
            color=CombatColors.TEXT_PRIMARY,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
            ),
        )
        self._attack_button = attack_button
        end_turn_button = ft.FilledButton(
            "Zug beenden",
            on_click=self._on_end_turn_click,
            width=160,
            bgcolor=CombatColors.PANEL_HOVER,
            color=CombatColors.TEXT_PRIMARY,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
            ),
        )
        self._end_turn_button = end_turn_button
        action_controls: list[ft.Control] = [
            self._selected_attacker_panel,
            attack_button,
            end_turn_button,
            ft.FilledButton(
                "Heldenmacht",
                on_click=self._on_hero_power_click,
                width=160,
                bgcolor=CombatColors.PANEL_HOVER,
                color=CombatColors.TEXT_PRIMARY,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=6),
                ),
            ),
        ]
        footer_controls: list[ft.Control] = [
            ft.Row(
                action_controls,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                expand=True,
            ),
        ]
        footer = ft.Row(
            footer_controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            width=page.width if page else 800,
        )
        hand_and_log = ft.Row(
            [
                hand_container,
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "KAMPFLOG",
                                size=11,
                                weight=ft.FontWeight.BOLD,
                                color=CombatColors.TEXT_SECONDARY,
                            ),
                            ft.Column(
                                [self._game_log],
                                scroll=ft.ScrollMode.AUTO,
                                expand=True,
                            ),
                        ],
                        spacing=8,
                    ),
                    expand=1,
                    height=200,
                    bgcolor=CombatColors.PANEL,
                    border=ft.Border.all(1, CombatColors.PANEL_HOVER),
                    border_radius=10,
                    padding=ft.Padding.all(10),
                    margin=ft.Margin(top=4),
                ),
            ],
            spacing=8,
            width=page.width if page else 800,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )
        main_controls: list[ft.Control] = [
            self._turn_banner,
            hero_area,
            opponent_board_panel,
            self._result_banner,
            ft.Container(height=4),
            player_board_panel,
            ft.Container(height=4),
            mana_row,
            hand_and_log,
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

    def _build_turn_banner(self) -> ft.Container:
        turn_text = ft.Text(
            "DEIN ZUG",
            size=12,
            weight=ft.FontWeight.BOLD,
            color=CombatColors.PLAYER,
        )
        self._turn_banner_text = turn_text
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.BOLT, size=16, color=CombatColors.PLAYER),
                    turn_text,
                    ft.Text(
                        f"RUNDE {max(1, self.state_machine.state.turn_number)}",
                        size=11,
                        color=CombatColors.TEXT_SECONDARY,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=CombatColors.PANEL,
            border=ft.Border.all(1, CombatColors.PLAYER),
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
        )

    def _build_field_panel(
        self, title: str, board_row: ft.Row, *, enemy: bool
    ) -> ft.Container:
        accent = CombatColors.ENEMY if enemy else CombatColors.PLAYER
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        title,
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=accent,
                    ),
                    board_row,
                ],
                spacing=8,
            ),
            bgcolor=CombatColors.PANEL,
            border=ft.Border.all(1, accent),
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            width=(self._page_or_none().width if self._page_or_none() else 800),
        )

    def _build_hero_area(self) -> ft.Container:
        """Build the hero portrait + HP + hero power area."""
        page = self._page_or_none()

        # Hero portrait placeholder
        hero_portrait = ft.Container(
            content=ft.Icon(ft.Icons.PERSON, size=40, color=CombatColors.PLAYER),
            width=100,
            height=60,
            bgcolor=CombatColors.PANEL_HOVER,
            border=ft.Border.all(2, CombatColors.PLAYER),
            border_radius=6,
            alignment=ft.Alignment.CENTER,
        )

        # Hero name
        hero_name = ft.Text(
            self.player.hero.name,
            size=14,
            weight=ft.FontWeight.BOLD,
            color=CombatColors.TEXT_PRIMARY,
        )

        # Hero HP
        hero_hp_text = ft.Text(
            f"{self.player.hero.current_health}/{self.player.hero.max_health}",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=CombatColors.TEXT_PRIMARY,
        )
        self._hero_hp_text = hero_hp_text
        self._player_hp_bar = ft.ProgressBar(
            value=self.player.hero.current_health / self.player.hero.max_health,
            color=CombatColors.PLAYER,
            bgcolor=CombatColors.PANEL_HOVER,
            width=132,
            height=7,
        )

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
                [hero_portrait, hero_name, hero_hp_text, self._player_hp_bar],
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
                size=20,
                weight=ft.FontWeight.BOLD,
                color=CombatColors.TEXT_PRIMARY,
            )
            self._opponent_hp_bar = ft.ProgressBar(
                value=opponent_hero.current_health / opponent_hero.max_health,
                color=CombatColors.ENEMY,
                bgcolor=CombatColors.PANEL_HOVER,
                width=132,
                height=7,
            )
            hero_controls.append(
                ft.Column(
                    [
                        ft.Text(
                            opponent_hero.name,
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=CombatColors.TEXT_SECONDARY,
                        ),
                        ft.Text("Gegnerheld", size=11, color=CombatColors.TEXT_SECONDARY),
                        self._opponent_hp_text,
                        self._opponent_hp_bar,
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
            bgcolor=CombatColors.PANEL,
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
            border=ft.Border.all(1, CombatColors.PANEL_HOVER),
            border_radius=8,
        )

    def _build_board_slots(self) -> ft.Row:
        """Build the 7 minion board slots."""
        self._board_row = ft.Row(
            [
                ft.Container(
                    width=124,
                    height=104,
                    bgcolor=CombatColors.BACKGROUND,
                    border=ft.Border.all(1, CombatColors.PANEL_HOVER),
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

    def _build_opponent_board_slots(self) -> ft.Row:
        self._opponent_board_row = ft.Row(
            [
                self._empty_minion_slot()
                for _ in range(7)
            ],
            wrap=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        )
        self._refresh_opponent_board()
        return self._opponent_board_row

    @staticmethod
    def _empty_minion_slot() -> ft.Container:
        return ft.Container(
            width=124,
            height=104,
            bgcolor=CombatColors.BACKGROUND,
            border=ft.Border.all(1, CombatColors.PANEL_HOVER),
            border_radius=6,
        )

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
                    is_playable=(
                        not self._is_opponent_turn
                        and self.match_status == MatchStatus.IN_PROGRESS
                        and self.player.hand[i].cost <= self.player.mana
                    ),
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
                    selected_for_attack=minion is self._selected_minion,
                )
                self.minion_slots.append(widget)
                slots.append(widget)
            else:
                empty_slot = ft.Container(
                    width=124,
                    height=96,
                    bgcolor=CombatColors.BACKGROUND,
                    border=ft.Border.all(1, CombatColors.PANEL_HOVER),
                    border_radius=6,
                )
                self.minion_slots.append(empty_slot)
                slots.append(empty_slot)

        self._board_row.controls = slots
        if not self._is_building:
            try:
                self._board_row.page
            except RuntimeError:
                pass
            else:
                self._board_row.update()
        self._refresh_opponent_board()

    def _refresh_opponent_board(self) -> None:
        if self._opponent_board_row is None:
            return

        opponent_minions = self.opponent_player.board if self.opponent_player else []
        living_taunts = [
            minion
            for minion in opponent_minions
            if isinstance(minion, Minion) and minion.has_taunt and minion.is_alive()
        ]
        slots: list[ft.Control] = []
        self.opponent_minion_slots = []
        for index in range(7):
            if index < len(opponent_minions):
                minion = opponent_minions[index]
                if not isinstance(minion, Minion):
                    raise TypeError(
                        f"Expected Minion in opponent.board, got {type(minion).__name__}"
                    )
                target_selectable = (
                    self._selected_minion is not None
                    and minion.is_alive()
                    and (not living_taunts or minion.has_taunt)
                    and self.match_status == MatchStatus.IN_PROGRESS
                    and not self._is_opponent_turn
                )
                widget = MinionWidget(
                    minion=minion,
                    on_target_select=self._on_enemy_minion_select,
                    target_selectable=target_selectable,
                    selected_for_target=minion is self._attack_target,
                    is_enemy=True,
                )
                self.opponent_minion_slots.append(widget)
                slots.append(widget)
            else:
                empty_slot = self._empty_minion_slot()
                self.opponent_minion_slots.append(empty_slot)
                slots.append(empty_slot)

        self._opponent_board_row.controls = slots
        if not self._is_building:
            try:
                self._opponent_board_row.page
            except RuntimeError:
                return
            self._opponent_board_row.update()

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
                self._hero_hp_text.color = CombatColors.ENEMY
            elif hp_percent < 0.6:
                self._hero_hp_text.color = CombatColors.RESOURCE
            else:
                self._hero_hp_text.color = CombatColors.PLAYER
            if self._page_or_none():
                self._hero_hp_text.update()
        if self._player_hp_bar:
            self._player_hp_bar.value = max(
                0.0,
                self.player.hero.current_health / self.player.hero.max_health,
            )
            self._player_hp_bar.color = (
                CombatColors.ENEMY
                if self.player.hero.current_health / self.player.hero.max_health < 0.3
                else CombatColors.RESOURCE
                if self.player.hero.current_health / self.player.hero.max_health < 0.6
                else CombatColors.SUCCESS
            )
            if self._page_or_none():
                self._player_hp_bar.update()
        if self.opponent_player and self._opponent_hp_text:
            self._opponent_hp_text.value = (
                f"{self.opponent_player.hero.current_health}/"
                f"{self.opponent_player.hero.max_health}"
            )
            if self._page_or_none():
                self._opponent_hp_text.update()
        if self.opponent_player and self._opponent_hp_bar:
            self._opponent_hp_bar.value = max(
                0.0,
                self.opponent_player.hero.current_health
                / self.opponent_player.hero.max_health,
            )
            opponent_hp_percent = (
                self.opponent_player.hero.current_health
                / self.opponent_player.hero.max_health
            )
            self._opponent_hp_bar.color = (
                CombatColors.ENEMY
                if opponent_hp_percent < 0.3
                else CombatColors.RESOURCE
                if opponent_hp_percent < 0.6
                else CombatColors.SUCCESS
            )
            if self._page_or_none():
                self._opponent_hp_bar.update()

    def _refresh_status_text(self) -> None:
        """Refresh the compact turn and resource status without replacing the log."""
        if self._turn_banner_text:
            self._turn_banner_text.value = (
                "GEGNER IST AM ZUG" if self._is_opponent_turn else "DEIN ZUG"
            )
            self._turn_banner_text.color = (
                CombatColors.ENEMY if self._is_opponent_turn else CombatColors.PLAYER
            )
        if self._turn_banner and self._page_or_none():
            self._turn_banner.border = ft.Border.all(
                1,
                CombatColors.ENEMY if self._is_opponent_turn else CombatColors.PLAYER,
            )
            self._turn_banner.update()
        if self._end_turn_button:
            self._end_turn_button.disabled = self._is_opponent_turn
            self._end_turn_button.content = (
                "Gegner ist am Zug" if self._is_opponent_turn else "Zug beenden"
            )
            if self._page_or_none():
                self._end_turn_button.update()

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
        if self.match_status != MatchStatus.IN_PROGRESS:
            return
        if self.state_machine.state.phase != GamePhase.MAIN_PHASE or self._is_opponent_turn:
            self._add_log("Karten können nur in der eigenen Hauptphase gespielt werden.")
            return

        if card.cost > self.player.mana:
            self._add_log(f"Zu wenig Mana: {card.name} kostet {card.cost}.")
            return
        if card.card_type == CardType.MINION and len(self.player.board) >= 7:
            self._add_log("Dein Feld ist voll. Es passen höchstens sieben Diener darauf.")
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
                has_taunt="TAUNT" in card.keywords,
                divine_shield="DIVINE_SHIELD" in card.keywords,
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
            or self.match_status != MatchStatus.IN_PROGRESS
            or self.state_machine.state.phase != GamePhase.MAIN_PHASE
            or minion.owner is not self.player
            or not minion.can_attack
        ):
            return
        self._selected_minion = minion
        self._attack_target = None
        taunts = self._living_enemy_taunts()
        self._add_log(f"Minion ausgewählt für Angriff: {minion.card.name if minion.card else 'Unknown'}")
        if self._selected_attacker_text:
            self._selected_attacker_text.value = (
                f"{minion.card.name} ({minion.attack}/{minion.current_health}) — "
                f"wähle einen Spott-Diener."
                if taunts
                else f"{minion.card.name} ({minion.attack}/{minion.current_health}) — "
                "Ziel: gegnerischer Held oder Diener"
            )
            self._selected_attacker_text.color = CombatColors.TEXT_PRIMARY
        if self._selected_attacker_panel:
            self._selected_attacker_panel.border = ft.Border.all(2, CombatColors.PLAYER)
        self._refresh_board()
        if self._selected_attacker_panel and self._page_or_none():
            self._selected_attacker_panel.update()
        if self._attack_button:
            self._attack_button.disabled = self.opponent_player is None or bool(taunts)
            self._attack_button.content = (
                "Ziel wählen" if taunts else "Angreifen · Gegnerheld"
            )
            if self._page_or_none():
                self._attack_button.update()

        if taunts:
            self._add_log("Spott blockiert den Gegnerhelden. Wähle einen markierten Spott-Diener.")
        else:
            self._add_log("Gegnerheld oder gegnerischer Diener kann angegriffen werden.")

    def _show_attack_targets(self, attacker: Minion) -> None:
        """Show available attack targets (enemy hero, enemy minions)."""
        self._refresh_opponent_board()

    def _living_enemy_taunts(self) -> list[Minion]:
        if self.opponent_player is None:
            return []
        return [
            minion
            for minion in self.opponent_player.board
            if isinstance(minion, Minion) and minion.has_taunt and minion.is_alive()
        ]

    def _on_enemy_minion_select(self, minion: Minion) -> None:
        attacker = self._selected_minion
        if (
            attacker is None
            or self.opponent_player is None
            or self.match_status != MatchStatus.IN_PROGRESS
            or self._is_opponent_turn
            or self.state_machine.state.phase != GamePhase.MAIN_PHASE
            or minion not in self.opponent_player.board
            or not minion.is_alive()
        ):
            return

        taunts = self._living_enemy_taunts()
        if taunts and not minion.has_taunt:
            self._add_log("Du musst einen gegnerischen Spott-Diener angreifen.")
            return

        self._attack_target = minion
        if self._selected_attacker_text:
            self._selected_attacker_text.value = (
                f"{attacker.card.name} → {minion.card.name} "
                f"({minion.attack}/{minion.current_health})"
            )
            self._selected_attacker_text.color = CombatColors.TEXT_PRIMARY
        if self._attack_button:
            self._attack_button.disabled = False
            self._attack_button.content = f"Angreifen · {minion.card.name}"
            if self._page_or_none():
                self._attack_button.update()
        self._refresh_opponent_board()
        self._add_log(f"Angriffsziel gewählt: {minion.card.name}.")

    def _on_attack_button_click(self, e: ft.Event[ft.Button]) -> None:
        attacker = self._selected_minion
        opponent = self.opponent_player
        if (
            self.match_status != MatchStatus.IN_PROGRESS
            or attacker is None
            or opponent is None
            or self._is_opponent_turn
            or self.state_machine.state.phase != GamePhase.MAIN_PHASE
            or not attacker.can_attack
        ):
            self._add_log("Kein angreifender Minion ausgewählt.")
            return

        if self._living_enemy_taunts() and self._attack_target is None:
            self._add_log("Wähle zuerst einen gegnerischen Spott-Diener als Ziel.")
            return

        if self._attack_target is not None:
            target = self._attack_target
            if self.match_manager is not None:
                attacker_index = self.player.board.index(attacker)
                target_index = self.opponent_player.board.index(target)
                if not self.match_manager.attack_minion(attacker_index, target_index):
                    self._add_log("Dieser Diener kann nicht als Angriffsziel gewählt werden.")
                    return
            else:
                target_died = target.take_damage(attacker.attack, self.state_machine.state)
                attacker_died = attacker.take_damage(target.attack, self.state_machine.state)
                attacker.can_attack = False
                if target_died:
                    self.opponent_player.board.remove(target)
                if attacker_died:
                    self.player.board.remove(attacker)
            self._add_log(
                f"{attacker.card.name} greift {target.card.name} an · "
                f"{attacker.attack} Schaden."
            )
        else:
            if self.match_manager is not None:
                attacker_index = self.player.board.index(attacker)
                if not self.match_manager.attack_hero(attacker_index):
                    self._add_log("Der Angriff konnte nicht ausgeführt werden.")
                    return
            else:
                damage = attacker.attack
                opponent.hero.take_damage(damage, self.state_machine.state)
                attacker.can_attack = False
                self.state_machine.emit(
                    GameEvent.DAMAGE_DEALT,
                    source=attacker,
                    target=opponent.hero,
                    amount=damage,
                )
            self._add_log(f"{attacker.card.name} greift {opponent.hero.name} an · {attacker.attack} Schaden.")
        self._selected_minion = None
        self._attack_target = None
        match_ended = self._refresh_match_status()
        if self._attack_button:
            self._attack_button.disabled = True
            self._attack_button.content = "Angreifen"
            if self._page_or_none():
                self._attack_button.update()
        if self._selected_attacker_text:
            self._selected_attacker_text.value = "Wähle zuerst einen bereiten Diener."
            self._selected_attacker_text.color = CombatColors.TEXT_SECONDARY
        if self._selected_attacker_panel:
            self._selected_attacker_panel.border = ft.Border.all(1, CombatColors.PLAYER)
            if self._page_or_none():
                self._selected_attacker_panel.update()
        self._refresh_board()
        self._refresh_opponent_board()
        self._refresh_hero_hp()
        if match_ended:
            self._notify_match_end()

    def _on_end_turn_click(self, e: ft.Event[ft.Button]) -> None:
        """Handle end turn button click."""
        self._on_end_turn()

    def _on_end_turn(self) -> None:
        """End the current turn - transition to next turn."""
        if self.match_status != MatchStatus.IN_PROGRESS:
            return
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
        self._attack_target = None
        if self._attack_button:
            self._attack_button.disabled = True
            self._attack_button.content = "Angreifen"
        if self._selected_attacker_text:
            self._selected_attacker_text.value = "Wähle zuerst einen bereiten Diener."
            self._selected_attacker_text.color = CombatColors.TEXT_SECONDARY
        if self._selected_attacker_panel:
            self._selected_attacker_panel.border = ft.Border.all(1, CombatColors.PLAYER)
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
        if self.match_status != MatchStatus.IN_PROGRESS:
            return
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
        """Add a compact, categorized combat event and retain only recent entries."""
        if self._game_log:
            if "greift" in message or "Angriff" in message:
                icon = "⚔"
            elif "Heil" in message:
                icon = "✚"
            elif "Zug" in message or "KI ist am Zug" in message:
                icon = "↻"
            elif "Spott" in message:
                icon = "⚠"
            else:
                icon = "◆"
            self._combat_log_entries.append(f"{icon} {message}")
            self._combat_log_entries = self._combat_log_entries[-6:]
            self._game_log.value = "\n".join(reversed(self._combat_log_entries))
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
        if self._refresh_match_status():
            self._notify_match_end()
            return
        self._on_end_turn()

    def _refresh_match_status(self) -> bool:
        """Resolve a finished match and update the board's terminal-state UI."""
        if self.match_status != MatchStatus.IN_PROGRESS:
            return True

        if self.match_manager is not None:
            status = self.match_manager.check_match_status()
        elif self.opponent_player is not None and not self.player.hero.is_alive():
            status = MatchStatus.DEFEAT
        elif self.opponent_player is not None and not self.opponent_player.hero.is_alive():
            status = MatchStatus.VICTORY
        else:
            status = MatchStatus.IN_PROGRESS

        if status == MatchStatus.IN_PROGRESS:
            return False

        self.match_status = status
        self._selected_minion = None
        victory = status == MatchStatus.VICTORY
        if self._result_text:
            self._result_text.value = (
                f"Sieg! {self.opponent_player.hero.name} wurde besiegt."
                if victory and self.opponent_player
                else "Niederlage – dein Held wurde besiegt."
            )
            self._result_text.color = (
                CombatColors.SUCCESS if victory else CombatColors.ENEMY
            )
        if self._result_banner:
            self._result_banner.visible = True
            self._result_banner.bgcolor = CombatColors.PANEL
        if self._attack_button:
            self._attack_button.disabled = True
        if self._end_turn_button:
            self._end_turn_button.disabled = True
        if self.hero_power_btn:
            self.hero_power_btn.button.disabled = True

        page = self._page_or_none()
        if page:
            if self._result_banner:
                self._result_banner.update()
            if self._attack_button:
                self._attack_button.update()
            if self._end_turn_button:
                self._end_turn_button.update()
            if self.hero_power_btn:
                self.hero_power_btn.update()
        return True

    def _notify_match_end(self) -> None:
        if self.on_match_end:
            self.on_match_end(self.match_status)

def main(page: ft.Page) -> None:
    """Entry point for the Merithra Flet application."""

    # --- Page Setup ---
    page.title = "Merithra - Card Game"
    page.theme_mode = ft.ThemeMode.DARK  # Dark mode basis
    page.bgcolor = CombatColors.BACKGROUND
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