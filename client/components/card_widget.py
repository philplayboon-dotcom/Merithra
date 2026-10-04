"""Reusable Card Widget for Merithra Flet UI.

Represents a card that can be displayed in hand, on the board, or as a spell target.
Supports Drag & Drop interactions via Flet event handlers.
"""

from __future__ import annotations

from typing import Any, Optional, Callable

import flet as ft
from client.theme import ThemeColors
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
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.card = card
        self.on_play = on_play
        self.on_card_click = on_click
        self.on_drag_start = on_drag_start
        self.on_drag_end = on_drag_end
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
        self.border_radius = 8
        self.padding = ft.Padding.all(4)
        self.on_click = self._handle_click
        self.data = self.card

    def _get_bgcolor(self) -> str:
        """Get background color based on card rarity using theme colors."""
        rarity_colors = {
            "COMMON": ThemeColors.ACCENT_1,
            "RARE": ThemeColors.ACCENT_2,
            "EPIC": ThemeColors.ACCENT_3,
            "LEGENDARY": ThemeColors.ACCENT_4,
            "FREE": ThemeColors.TEXT_MUTED,
        }
        return rarity_colors.get(self.card.rarity.name, ThemeColors.DARKER_BG)

    def _get_border_color(self) -> str:
        """Get border color: gold border if selected for attack."""
        # This will be updated when minion is selected for attack
        return ThemeColors.ACCENT_4 if getattr(self, "_selected_for_attack", False) else ThemeColors.TEXT_MUTED

    def _build_card_content(self) -> ft.Control:
        """Build the inner card content showing card stats."""
        # Card type icon
        type_icon = self._get_type_icon()

        # Card name
        name_text = ft.Text(
            self.card.name,
            size=10,
            weight=ft.FontWeight.BOLD,
            color=ThemeColors.TEXT_PRIMARY,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        # Card cost
        cost_text = ft.Text(
            f"💰 {self.card.cost}",
            size=10,
            color=ThemeColors.ACCENT_4,
        )

        # Attack/Health (for minions)
        stats_text = ft.Text(
            "",
            size=10,
            color=ThemeColors.TEXT_PRIMARY,
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
            size=8,
            color=ThemeColors.TEXT_MUTED,
            overflow=ft.TextOverflow.ELLIPSIS,
            max_lines=2,
        )

        # Drag area indicator (dashed border when draggable)
        drag_indicator = ft.Container(
            content=ft.Icon(ft.Icons.DRAG_HANDLE, size=12, color=ThemeColors.TEXT_MUTED),
            width=120,
            height=15,
            alignment=ft.Alignment.CENTER,
        )

        return ft.Column(
            [
                ft.Row(
                    [type_icon, ft.Text(str(self.card.cost), size=12, color=ThemeColors.ACCENT_4)],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Row([name_text], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([cost_text], alignment=ft.MainAxisAlignment.CENTER),
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
        return ft.Icon(icon, size=16, color="#ffffff")

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
        if self.on_card_click:
            self.on_card_click(self.card)
        if self.on_play:
            self.on_play(self.card)


class MinionWidget(ft.Container):
    """Widget representing a minion on the board with attack targeting support."""

    def __init__(
        self,
        minion: Any,  # Minion object from core.entities
        on_attack_select: Optional[Callable[[Any], None]] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.minion = minion
        self.on_attack_select = on_attack_select
        self._is_attacking = False
        self.build()

    def build(self) -> None:
        """Build the minion widget with attack indicator."""
        # Minion color based on current health
        bg_opacity = 1.0 if self.minion.is_alive() else 0.3

        self.content = self._build_minion_content()
        self.width = 100
        self.height = 80
        self.bgcolor = self._get_bgcolor(bg_opacity)
        self.border = ft.Border.all(2, self._get_attack_border_color())
        self.border_radius = 6
        self.padding = ft.Padding.all(2)
        self.on_click = self._on_click
        self.data = self.minion

    def _get_bgcolor(self, opacity: float) -> str:
        """Get background color with opacity."""
        return f"rgba(18, 18, 24, {opacity})"

    def _get_attack_border_color(self) -> str:
        """Get border color indicating attack capability."""
        if self.minion.can_attack:
            return ThemeColors.ACCENT_3  # Subtle red border
        return ThemeColors.TEXT_MUTED  # Gray: cannot attack

    def _build_minion_content(self) -> ft.Control:
        """Build the minion visual content."""
        # Attack
        attack_text = ft.Text(
            str(self.minion.attack),
            size=18,
            weight=ft.FontWeight.BOLD,
            color=ThemeColors.ACCENT_4,
        )

        # Health
        health_text = ft.Text(
            str(self.minion.current_health),
            size=18,
            color=ThemeColors.HP_LOW,
        )

        # Taunt indicator
        taunt_indicator = ft.Container()
        if self.minion.has_taunt:
            taunt_indicator = ft.Container(
                content=ft.Icon(ft.Icons.SECURITY, size=14, color=ThemeColors.ACCENT_4),
                width=20,
                height=20,
                border=ft.Border.all(1, ThemeColors.ACCENT_4),
                border_radius=10,
                alignment=ft.Alignment.CENTER,
            )

        # Divine Shield indicator
        shield_indicator = ft.Container()
        if self.minion.divine_shield:
            shield_indicator = ft.Container(
                content=ft.Icon(ft.Icons.SHIELD, size=14, color=ThemeColors.TEXT_PRIMARY),
                width=20,
                height=20,
                border=ft.Border.all(1, ThemeColors.TEXT_PRIMARY),
                border_radius=10,
                alignment=ft.Alignment.CENTER,
            )

        # Windfury indicator
        windfury_indicator = ft.Container()
        if self.minion.windfury > 0:
            windfury_indicator = ft.Container(
                content=ft.Icon(ft.Icons.SPORTS_MARTIAL_ARTS, size=12, color=ThemeColors.ACCENT_3),
                width=16,
                height=16,
                alignment=ft.Alignment.CENTER,
            )

        return ft.Column(
            [
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
            spacing=1,
        )

    def _on_click(self, e: ft.Event[ft.Container]) -> None:
        """Handle click - select this minion as attack target."""
        if self.on_attack_select and self.minion.can_attack:
            self.on_attack_select(self.minion)
            self._selected_for_attack = True
            self.update()


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
            color="#ffffff" if can_use else ThemeColors.TEXT_MUTED,
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
            bgcolor=ThemeColors.DARKER_BG if can_use else ThemeColors.DARKEST_BG_V2,
            disabled=not can_use,
            color="#ffffff" if can_use else ThemeColors.TEXT_MUTED,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                overlay_color=ThemeColors.BORDER_TRANSPARENT,
            ),
            on_click=self._on_click,
        )
        self.content = self.button

        # Update mana display
        self._update_mana_display()

    def _update_mana_display(self) -> None:
        """Update button appearance based on current mana."""
        can_use = self.player_mana >= 2 and self.hero_power_card is not None
        self.button.bgcolor = ThemeColors.DARKER_BG if can_use else ThemeColors.DARKEST_BG_V2
        self.button.disabled = not can_use
        self._label.color = ThemeColors.TEXT_PRIMARY if can_use else ThemeColors.TEXT_MUTED
        try:
            if getattr(self, 'page', None) is not None:
                self.update()
        except RuntimeError:
            pass  # update only allowed after control is added to page

    def _on_click(self, e: ft.Event[ft.Button]) -> None:
        """Handle hero power button click."""
        if self.on_hero_power:
            self.on_hero_power()