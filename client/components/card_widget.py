"""Reusable Card Widget for Merithra Flet UI.

Represents a card that can be displayed in hand, on the board, or as a spell target.
Supports Drag & Drop interactions via Flet event handlers.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

import flet as ft

from client.theme import CombatColors
from core.cards import Card, CardType


class CardWidget(ft.Container):
    """A reusable card widget that can be dragged and clicked.

    Attributes:
        card: The Card object to display.
        on_play: Callback when card is played from hand to board.
        on_click: Callback when card/minion is clicked (for target selection).
        on_drag_start: Callback when drag starts.
        on_drag_end: Callback when drag ends.
    """

    def __init__(
        self,
        card: Card,
        on_play: Optional[Callable[[Card], None]] = None,
        on_click: Optional[Callable[[Card], None]] = None,
        on_drag_start: Optional[Callable[[], None]] = None,
        on_drag_end: Optional[Callable[[], None]] = None,
        is_playable: bool = True,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.card = card
        self.on_play = on_play
        self.on_card_click = on_click
        self.on_drag_start = on_drag_start
        self.on_drag_end = on_drag_end
        self.is_playable = is_playable
        # Drag state
        self._is_dragging = False
        self._drag_offset = (0, 0)
        self.build()

    def build(self) -> None:
        """Build the card visual representation."""
        self.content = self._build_card_content()
        self.width = 120
        self.height = 180
        self.bgcolor = self._get_bgcolor()
        self.border = ft.Border.all(1, self._get_border_color())
        self.opacity = 1 if self.is_playable else 0.58
        self.border_radius = 8
        self.padding = ft.Padding.all(4)
        self.on_click = self._handle_click
        self.data = self.card

    def _get_bgcolor(self) -> str:
        """Use a quiet surface so card information stays more prominent than rarity."""
        return CombatColors.PANEL_HOVER if self.is_playable else CombatColors.PANEL

    def _get_border_color(self) -> str:
        """Use the player accent to identify cards that can currently be played."""
        return CombatColors.PLAYER if self.is_playable else "#34415A"

    def _build_card_content(self) -> ft.Control:
        """Build the inner card content showing card stats."""
        # Card type icon
        type_icon = self._get_type_icon()

        # Card name
        name_text = ft.Text(
            self.card.name,
            size=13,
            weight=ft.FontWeight.BOLD,
            color=CombatColors.TEXT_PRIMARY,
            overflow=ft.TextOverflow.ELLIPSIS,
            max_lines=2,
        )

        cost_badge = ft.Container(
            content=ft.Text(
                str(self.card.cost),
                size=12,
                weight=ft.FontWeight.BOLD,
                color=CombatColors.BACKGROUND,
                text_align=ft.TextAlign.CENTER,
            ),
            width=24,
            height=24,
            bgcolor=CombatColors.RESOURCE,
            border_radius=12,
            alignment=ft.Alignment.CENTER,
        )

        # Attack/Health (for minions)
        stats_text = ft.Text(
            "",
            size=12,
            weight=ft.FontWeight.BOLD,
            color=CombatColors.PLAYER,
        )

        if self.card.card_type == CardType.MINION:
            stats_text.value = f"💪 {self.card.attack} / {self.card.health}"
        elif self.card.card_type == CardType.HERO_POWER:
            stats_text.value = f"⚡ {self.card.name}"
        elif self.card.card_type == CardType.SPELL:
            stats_text.value = f"🔮 {self.card.cost} Mana"

        # Card text/tooltip
        text_text = ft.Text(
            self.card.text,
            size=10,
            color=CombatColors.TEXT_SECONDARY,
            overflow=ft.TextOverflow.ELLIPSIS,
            max_lines=3,
        )

        # Drag area indicator (dashed border when draggable)
        drag_indicator = ft.Container(
            content=ft.Icon(ft.Icons.DRAG_HANDLE, size=12, color=CombatColors.TEXT_SECONDARY),
            width=120,
            height=12,
            alignment=ft.Alignment.CENTER,
        )

        return ft.Column(
            [
                ft.Row(
                    [cost_badge, type_icon],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Row([name_text], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([stats_text], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([text_text], alignment=ft.MainAxisAlignment.CENTER, expand=True),
                drag_indicator,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
        )

    def _get_type_icon(self) -> ft.Control:
        """Get the card type icon."""
        icons = {
            CardType.MINION: ft.Icons.PETS,
            CardType.SPELL: ft.Icons.INSERT_DRIVE_FILE,
            CardType.WEAPON: ft.Icons.FORWARD,
            CardType.HERO_POWER: ft.Icons.STAR,
            CardType.LOCATION: ft.Icons.LOCATION_ON,
        }
        icon = icons.get(self.card.card_type, ft.Icons.INSERT_DRIVE_FILE)
        return ft.Icon(icon, size=16, color=CombatColors.TEXT_SECONDARY)

    # --- Drag & Drop Event Handlers ---

    def _on_drag_start(self, e: ft.DragStartEvent) -> None:
        """Handle drag start - called when user starts dragging the card."""
        self._is_dragging = True
        self._drag_offset = (e.control.local_x, e.control.local_y)
        if self.on_drag_start:
            self.on_drag_start()

    def _on_drag_end(self, e: ft.DragEndEvent) -> None:
        """Handle drag end - called when drag finishes."""
        self._is_dragging = False
        if self.on_drag_end:
            self.on_drag_end()
        # Reset container position
        self.left = None
        self.top = None
        self.update()

    def _handle_click(self, e: ft.Event[ft.Container]) -> None:
        if self.is_playable and self.on_play:
            self.on_play(self.card)
        elif self.on_card_click and not self.on_play:
            self.on_card_click(self.card)


class MinionWidget(ft.Container):
    """Widget representing a minion on the board with attack targeting support."""

    def __init__(
        self,
        minion: Any,  # Minion object from core.entities
        on_attack_select: Optional[Callable[[Any], None]] = None,
        on_target_select: Optional[Callable[[Any], None]] = None,
        selected_for_attack: bool = False,
        selected_for_target: bool = False,
        target_selectable: bool = False,
        can_attack: bool | None = None,
        is_enemy: bool = False,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.minion = minion
        self.on_attack_select = on_attack_select
        self.on_target_select = on_target_select
        self.selected_for_attack = selected_for_attack
        self.selected_for_target = selected_for_target
        self.target_selectable = target_selectable
        self.can_attack = minion.can_attack if can_attack is None else can_attack
        self.is_enemy = is_enemy
        self.build()

    def build(self) -> None:
        """Build the minion widget with attack indicator."""
        # Minion color based on current health
        bg_opacity = 1.0 if self.minion.is_alive() else 0.3

        self.content = self._build_minion_content()
        self.width = 124
        self.height = 104
        self.bgcolor = self._get_bgcolor(bg_opacity)
        self.border = ft.Border.all(3 if self.selected_for_attack else 2, self._get_attack_border_color())
        self.border_radius = 6
        self.padding = ft.Padding.all(2)
        self.on_click = self._on_click
        self.data = self.minion

    def _get_bgcolor(self, opacity: float) -> str:
        """Get background color with opacity."""
        if self.selected_for_attack:
            return f"rgba(92, 169, 255, {opacity})"
        if self.is_enemy:
            return f"rgba(229, 101, 101, {opacity * 0.18})"
        return f"rgba(32, 42, 64, {opacity})"

    def _get_attack_border_color(self) -> str:
        """Get border color indicating attack capability."""
        if self.selected_for_attack:
            return CombatColors.PLAYER
        if self.selected_for_target:
            return CombatColors.RESOURCE
        if self.target_selectable:
            return CombatColors.ENEMY
        if self.can_attack:
            return CombatColors.PLAYER
        return CombatColors.TEXT_SECONDARY

    def _build_minion_content(self) -> ft.Control:
        """Build the minion visual content."""
        name_text = ft.Text(
            self.minion.card.name,
            size=12,
            weight=ft.FontWeight.BOLD,
            color=CombatColors.TEXT_PRIMARY,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        selection_text = ft.Text(
            "ANGREIFER",
            size=8,
            weight=ft.FontWeight.BOLD,
            color=CombatColors.TEXT_PRIMARY,
            visible=self.selected_for_attack,
        )
        keyword_labels = []
        if self.minion.has_taunt:
            keyword_labels.append(
                ft.Text(
                    "SPOTT",
                    size=9,
                    weight=ft.FontWeight.BOLD,
                    color=CombatColors.ENEMY,
                )
            )
        if self.minion.divine_shield:
            keyword_labels.append(
                ft.Text(
                    "SCHILD",
                    size=9,
                    weight=ft.FontWeight.BOLD,
                    color=CombatColors.RESOURCE,
                )
            )
        keywords_row = ft.Row(
            keyword_labels,
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
            visible=bool(keyword_labels),
        )
        # Attack
        attack_text = ft.Text(
            str(self.minion.attack),
            size=18,
            weight=ft.FontWeight.BOLD,
            color=CombatColors.RESOURCE,
        )

        # Health
        health_text = ft.Text(
            str(self.minion.current_health),
            size=18,
            color=CombatColors.ENEMY if self.is_enemy else CombatColors.PLAYER,
        )

        # Taunt indicator
        taunt_indicator = ft.Container()
        if self.minion.has_taunt:
            taunt_indicator = ft.Container(
                content=ft.Icon(ft.Icons.SECURITY, size=14, color=CombatColors.ENEMY),
                width=20,
                height=20,
                border=ft.Border.all(1, CombatColors.ENEMY),
                border_radius=10,
                alignment=ft.Alignment.CENTER,
            )

        # Divine Shield indicator
        shield_indicator = ft.Container()
        if self.minion.divine_shield:
            shield_indicator = ft.Container(
                content=ft.Icon(ft.Icons.SHIELD, size=14, color=CombatColors.TEXT_PRIMARY),
                width=20,
                height=20,
                border=ft.Border.all(1, CombatColors.TEXT_PRIMARY),
                border_radius=10,
                alignment=ft.Alignment.CENTER,
            )

        # Windfury indicator
        windfury_indicator = ft.Container()
        if self.minion.windfury > 0:
            windfury_indicator = ft.Container(
                content=ft.Icon(ft.Icons.SPORTS_MARTIAL_ARTS, size=12, color=CombatColors.PLAYER),
                width=16,
                height=16,
                alignment=ft.Alignment.CENTER,
            )

        return ft.Column(
            [
                ft.Row(
                    [name_text, selection_text],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                keywords_row,
                ft.Row(
                    [attack_text, taunt_indicator],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Row(
                    [health_text, shield_indicator, windfury_indicator],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
        )

    def _on_click(self, e: ft.Event[ft.Container]) -> None:
        """Handle click - select this minion as attack target."""
        if self.is_enemy and self.on_target_select and self.target_selectable:
            self.on_target_select(self.minion)
        elif self.on_attack_select and self.can_attack:
            self.on_attack_select(self.minion)


class HeroPowerButton(ft.Container):
    """Button for activating Hero Power."""

    def __init__(
        self,
        hero_power_card: Optional[Card],
        player_mana: int,
        max_mana: int,
        on_hero_power: Callable[[], None],
        **kwargs: Any,
    ):
        width = kwargs.pop("width", None)
        height = kwargs.pop("height", None)
        super().__init__(**kwargs)
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        self.hero_power_card = hero_power_card
        self.player_mana = player_mana
        self.max_mana = max_mana
        self.on_hero_power = on_hero_power

    def build(self) -> None:
        """Build the hero power button."""
        # Disable if not enough mana
        can_use = self.player_mana >= 2 and self.hero_power_card is not None
        self._label = ft.Text(
            "Heldenmacht",
            size=12,
            color=CombatColors.TEXT_PRIMARY if can_use else CombatColors.TEXT_SECONDARY,
        )

        self.button = ft.FilledButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.FLASH_ON, size=20, color="#ffffff"),
                    self._label,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            width=self.width or 100,
            height=50,
            bgcolor=CombatColors.PANEL_HOVER if can_use else CombatColors.PANEL,
            disabled=not can_use,
            color=CombatColors.TEXT_PRIMARY if can_use else CombatColors.TEXT_SECONDARY,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                overlay_color="rgba(255, 255, 255, 0.08)",
            ),
            on_click=self._on_click,
        )
        self.content = self.button

        # Update mana display
        self._update_mana_display()

    def _update_mana_display(self) -> None:
        """Update button appearance based on current mana."""
        can_use = self.player_mana >= 2 and self.hero_power_card is not None
        self.button.bgcolor = CombatColors.PANEL_HOVER if can_use else CombatColors.PANEL
        self.button.disabled = not can_use
        self._label.color = (
            CombatColors.TEXT_PRIMARY if can_use else CombatColors.TEXT_SECONDARY
        )
        try:
            if getattr(self, 'page', None) is not None:
                self.update()
        except RuntimeError:
            pass  # update only allowed after control is added to page

    def _on_click(self, e: ft.Event[ft.Button]) -> None:
        """Handle hero power button click."""
        if self.on_hero_power:
            self.on_hero_power()