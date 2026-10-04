"""Mana Crystal Component for Merithra Flet UI.

Displays the current and maximum mana as a row of crystals.
Can show current mana spent vs. available crystals.
"""

from __future__ import annotations

from typing import Any

import flet as ft
from client.theme import CombatColors


class ManaCrystal(ft.Container):
    """A single mana crystal that can be highlighted or dimmed.

    Attributes:
        is_current: Whether this crystal represents current mana.
        is_max: Whether this crystal represents max mana (extra beyond current).
    """

    def __init__(
        self,
        is_current: bool = True,
        is_max: bool = False,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.is_current = is_current
        self.is_max = is_max
        self._build()

    def _build(self) -> None:
        """Build the crystal visual."""
        # Crystal appearance based on state
        if self.is_max and not self.is_current:
            # Extra/maximized crystal (red accent)
            self.crystal = ft.Container(
                content=ft.Icon(ft.Icons.BOLT, size=20, color=CombatColors.RESOURCE),
                width=30,
                height=30,
                border=ft.Border.all(1, CombatColors.RESOURCE),
                border_radius=6,
                alignment=ft.Alignment.CENTER,
            )
        elif self.is_current:
            # Current mana crystal (bright red)
            self.crystal = ft.Container(
                content=ft.Icon(ft.Icons.BOLT, size=20, color=CombatColors.RESOURCE),
                width=30,
                height=30,
                border=ft.Border.all(1, CombatColors.RESOURCE),
                border_radius=6,
                alignment=ft.Alignment.CENTER,
            )
        else:
            # Empty/max-only crystal (muted gray)
            self.crystal = ft.Container(
                content=ft.Icon(ft.Icons.BOLT, size=20, color=CombatColors.TEXT_SECONDARY),
                width=30,
                height=30,
                border=ft.Border.all(1, CombatColors.TEXT_SECONDARY),
                border_radius=6,
                alignment=ft.Alignment.CENTER,
            )
        self.content = self.crystal
        self.width = 30
        self.height = 30

    def build(self) -> None:
        """Build the crystal contents."""
        self._build()

    def update_state(self, is_current: bool, is_max: bool = False) -> None:
        """Update the crystal state dynamically."""
        self.is_current = is_current
        self.is_max = is_max
        self._build()
        try:
            page = self.page
        except RuntimeError:
            return
        if page:
            self.update()