"""Merithra - Central Design Tokens and Theme System for Flet UI.

This module defines the complete design tokens including color palettes,
gradients, typography, spacing, and styling helpers implementing the
Dark Modern Glassmorphism aesthetic specified for Merithra.

All colors use the specified palette:
- Primary: Black (#0A0A0C) and dark grays
- Accent: Muted/damped reds (#8B1E2D through #E63950)
- Surfaces: Semi-transparent dark rgba values
- Borders: Translucent with subtle red or white tints
"""

from __future__ import annotations

from typing import Any, ClassVar, Dict, Literal

import flet as ft


# ---------------------------------------------------------------------------
# Color Palette — Dark Modern Glassmorphism
# ---------------------------------------------------------------------------

class ThemeColors:
    """Primary color palette for Merithra UI.

    All values are hex or RGBA strings suitable for Flet `bgcolor`, `color`,
    `border_color`, etc. Colors are grouped by semantic role, not just hue,
    to support the Dark Fantasy / Sleek Minimalist aesthetic.
    """

    # ── Background Surfaces ─────────────────────────────────────────────────

    # Deepest background — full opacity black
    BLACK: str = "#0A0A0C"

    # Primary dark backgrounds (low opacity for glassmorphism layers)
    DARKEST_BG: str = "#0A0A0C"       # #0A0A0C — full black
    DARK_BG: str = "#121216"           # Primary panel background
    DARKER_BG: str = "#1A1A22"         # Secondary panels
    DARK_BG_V2: str = "#242430"        # Accent panels, cards
    DARKEST_BG_V2: str = "#323242"     # Minimal elevation surfaces

    # ── Surface / Card Backgrounds (semi-transparent) ───────────────────────

    # Semi-transparent surfaces for glassmorphism effect
    SURFACE_TRANSPARENT: str = "rgba(18, 18, 24, 0.75)"   # Base glass surface
    SURFACE_SUBTLE: str = "rgba(22, 22, 30, 0.80)"        # Slightly stronger
    SURFACE_MODERATE: str = "rgba(36, 36, 48, 0.85)"      # Card backgrounds
    SURFACE_ELEVATED: str = "rgba(44, 44, 62, 0.90)"      # Elevated panels

    # ── Borders ──────────────────────────────────────────────────────────────

    # Translucent borders — nearly invisible but present for layout structure
    BORDER_TRANSPARENT: str = "rgba(255, 255, 255, 0.08)"  # Nearly invisible white
    BORDER_SUBTLE_RED: str = "rgba(192, 57, 75, 0.3)"       # Subtle red glow border
    BORDER_MEDIUM: str = "rgba(255, 255, 255, 0.12)"       # Medium contrast
    BORDER_STRONG: str = "rgba(255, 255, 255, 0.20)"       # Stronger focus border

    # ── Accent / Red Palette (damped, muted, glass-compatible) ──────────────

    ACCENT_DEEPEST: str = "#0A0A0C"  # Fallback — pure black
    ACCENT_1: str = "#8B1E2D"        # Deepest red — used for subtle text/icons
    ACCENT_2: str = "#A62B3B"        # Stronger red — buttons, active states
    ACCENT_3: str = "#C0394B"        # Primary accent — borders, highlights
    ACCENT_4: str = "#E63950"        # Brightest red — glows, active states
    ACCENT_GLOW: str = "rgba(192, 57, 75, 0.45)"   # Red glow effect
    ACCENT_GLOW_STRONG: str = "rgba(192, 57, 75, 0.65)"  # Strong glow

    # ── Text Colors ────────────────────────────────────────────────────────

    TEXT_PRIMARY: str = "#F5F5F5"    # Main body text
    TEXT_SECONDARY: str = "#AAAAAA"  # Secondary/placeholder text
    TEXT_MUTED: str = "#666666"      # Muted text, captions
    TEXT_DISABLED: str = "#333333"   # Disabled state text
    TEXT_ON_ACCENT: str = "#FFFFFF"  # Text on red accents

    # ── Special / Status Colors ────────────────────────────────────────────

    HP_LOW: str = "#E63950"          # Low health — bright red
    HP_CRITICAL: str = "#FF0000"     # Critical health — pure red
    MANA_CURRENT: str = "#FFD700"    # Current mana — gold accent
    MANA_AVAILABLE: str = "#FFFFFF"  # Available mana text
    ARMOR: str = "#C0C0C0"           # Armor color
    COOLDOWN_OVERLAY: str = "rgba(255, 255, 255, 0.15)"  # Cooldown tint


class CombatColors:
    """Semantic colors from the tactical combat UI design."""

    BACKGROUND: str = "#0B1020"
    PANEL: str = "#151C2E"
    PANEL_HOVER: str = "#202A40"
    TEXT_PRIMARY: str = "#F4F7FB"
    TEXT_SECONDARY: str = "#9AA7BD"
    RESOURCE: str = "#E7B85C"
    PLAYER: str = "#5CA9FF"
    ENEMY: str = "#E56565"
    SUCCESS: str = "#68C98B"


# ---------------------------------------------------------------------------
# Gradients — for buttons, orbs, Glow effects
# ---------------------------------------------------------------------------

class ThemeGradients:
    """Pre-defined gradients used across the UI."""

    # Linear gradient for hero health orb (dark to red transition)
    HP_ORB: tuple[str, str] = (
        "linear gradient:#0D0D12 (#0D0D12) to #E63950",
    )

    # Panel shadow / depth gradient
    PANEL_SHADOW: tuple[str, str] = (
        "linear gradient:#1a1a22 0% to #0a0a0c 100%",
    )

    # Button hover gradient
    BUTTON_HOVER: tuple[str, str] = (
        "linear gradient:#242430 0% to #1a1a1e 100%",
    )

    # Card inner glow (for glassmorphism depth)
    CARD_INNER_GLOW: tuple[str, str] = (
        "linear gradient:(radial) rgba(255,255,255,0.03) 0% to transparent 70%",
    )

    # Red accent gradient (for glows / highlights)
    ACCENT_GRADIENT: tuple[str, str] = (
        "linear gradient:#C0394B 0% to #8B1E2D 100%",
    )


# ---------------------------------------------------------------------------
# Typography Scale
# ---------------------------------------------------------------------------

class ThemeTypography:
    """Typography scale — consistent rhythm across all text elements."""

    # Header levels
    H1: dict[str, Any] = {
        "size": 32,
        "weight": ft.FontWeight.BOLD,
        "color": ThemeColors.TEXT_PRIMARY,
        "letter_spacing": -0.5,
    }
    H2: dict[str, Any] = {
        "size": 24,
        "weight": ft.FontWeight.BOLD,
        "color": ThemeColors.TEXT_PRIMARY,
        "letter_spacing": -0.3,
    }
    H3: dict[str, Any] = {
        "size": 20,
        "weight": ft.FontWeight.W_600,
        "color": ThemeColors.TEXT_PRIMARY,
        "letter_spacing": 0,
    }

    # Body text
    Body1: dict[str, Any] = {
        "size": 16,
        "weight": ft.FontWeight.NORMAL,
        "color": ThemeColors.TEXT_PRIMARY,
        "letter_spacing": 0.2,
    }
    Body2: dict[str, Any] = {
        "size": 14,
        "weight": ft.FontWeight.NORMAL,
        "color": ThemeColors.TEXT_SECONDARY,
        "letter_spacing": 0.1,
    }
    Body3: dict[str, Any] = {
        "size": 12,
        "weight": ft.FontWeight.NORMAL,
        "color": ThemeColors.TEXT_MUTED,
        "letter_spacing": 0.3,
    }

    # Label / small text
    Caption: dict[str, Any] = {
        "size": 10,
        "weight": ft.FontWeight.NORMAL,
        "color": ThemeColors.TEXT_MUTED,
        "letter_spacing": 0.5,
    }
    Overline: dict[str, Any] = {
        "size": 10,
        "weight": ft.FontWeight.W_600,
        "color": ThemeColors.TEXT_SECONDARY,
        "letter_spacing": 1.0,
    }

    # Numeric / small labels
    Overline2: dict[str, Any] = {
        "size": 11,
        "weight": ft.FontWeight.BOLD,
        "color": ThemeColors.TEXT_PRIMARY,
        "letter_spacing": 0.5,
    }


# ---------------------------------------------------------------------------
# Shadow & Blur Helpers for Flet Glassmorphism
# ---------------------------------------------------------------------------

class ThemeShadows:
    """Pre-defined shadow styles mapped to Flet's `BoxShadow` syntax.

    Flet supports `BoxShadow` as a string like:
    "2 2 5 rgba(0,0,0,0.3)"
    """

    # Subtle elevation — for glass containers
    ELEVATED_SUBTLE: str = "0 2 5 rgba(0, 0, 0, 0.20)"
    ELEVATED_MODERATE: str = "0 4 10 rgba(0, 0, 0, 0.30)"
    ELEVATED_NOTICE: str = "0 6 15 rgba(0, 0, 0, 0.40)"

    # Focus / selection glow
    FOCUS_GLOW: str = "0 0 0 1px rgba(192, 57, 75, 0.5)"
    FOCUS_GLOW_STRONG: str = "0 0 0 2px rgba(192, 57, 75, 0.75)"

    # Inner shadow for glass depth
    INNER_GLASS: str = "inset 0 2 4 rgba(0, 0, 0, 0.30)"


class ThemeBlur:
    """Blur strategies for Flet Glassmorphism.

    Flet's `ft.Blur` works with `control=ft.Ref[ft.Container]` or via
    `theme` property. These constants define the blur intensity.
    """

    # Light frosted glass — most common
    FROST_LIGHT: ft.Blur = ft.Blur(sigma_x=4, sigma_y=4)
    # Medium frosted glass — panels with more depth
    FROST_MEDIUM: ft.Blur = ft.Blur(sigma_x=8, sigma_y=8)
    # Heavy frosted glass — modal backdrops
    FROST_HEAVY: ft.Blur = ft.Blur(sigma_x=12, sigma_y=12)


# ---------------------------------------------------------------------------
# Reusable Helper Functions
# ---------------------------------------------------------------------------

def create_glass_container(
    content: ft.Control,
    *,
    width: float | None = None,
    height: float | None = None,
    padding: ft.Padding | None = None,
    border_radius: int | ft.border_radius.BorderRadius = 12,
    bg_opacity: float = 0.75,
    border: ft.Border | None = None,
    shadow: str = ThemeShadows.ELEVATED_SUBTLE,
    blur: ft.Blur | None = ThemeBlur.FROST_LIGHT,
    alignment: ft.Alignment | None = None,
    expand: bool = False,
) -> ft.Container:
    """Create a glassmorphism-styled Container for Merithra UI.

    This is the primary building block for glass panels, card areas,
    hero zones, and any semi-transparent surface that benefits from the
    frosted-glass effect.

    The function constructs an `rgba(18, 18, 24, bg_opacity)` background
    with a translucent white border (`rgba(255, 255, 255, 0.08)`) by
    default, and applies a light sigma blur for the frosted effect.

    Args:
        content: The Flet control to place inside the container.
        width: Optional fixed width. If not set, the container expands.
        height: Optional fixed height.
        padding: Interior padding. Defaults to `ft.padding.all(12)`.
        border_radius: Corner rounding. Defaults to 12.
        bg_opacity: Surface opacity in range (0, 1]. Default 0.75.
        border: Optional explicit border. If None, a subtle
            `rgba(255, 255, 255, 0.08)` 1px border is applied.
        shadow: BoxShadow string from ThemeShadows.
        blur: ft.Blur instance. Defaults to FROST_LIGHT.
        alignment: Alignment within the container.
        expand: Whether the container should expand to fill available space.

    Returns:
        A configured ft.Container with glassmorphism styling.
    """
    if padding is None:
        padding = ft.Padding.all(12)

    # Build the border — subtle translucent white by default,
    # but allow override with red-tinted border for specific contexts
    if border is None:
        border = ft.Border.all(
            1,
            ThemeColors.BORDER_TRANSPARENT,
        )

    # Determine final background color
    bg_color = ThemeColors.SURFACE_TRANSPARENT if bg_opacity >= 0.7 else (
        ThemeColors.DARK_BG_V2 if bg_opacity >= 0.5 else ThemeColors.DARKER_BG
    )
    # Apply opacity if not already rgba in the constant
    # (We compute a dynamic rgba string here for the exact opacity)
    final_bg = f"rgba(18, 18, 24, {bg_opacity})"

    return ft.Container(
        content=content,
        width=width,
        height=height,
        padding=padding,
        bgcolor=final_bg,
        border=border,
        border_radius=border_radius,
        shadow=shadow,
        blur=blur,
        alignment=alignment,
        expand=expand,
    )


def create_accent_button(
    text: str,
    *,
    on_click: ft.ControlEventHandler | None = None,
    width: float | None = None,
    height: float | None = None,
    bgcolor: str = ThemeColors.ACCENT_3,
    color: str = ThemeColors.TEXT_ON_ACCENT,
    hover_bgcolor: str | None = None,
    disabled_bgcolor: str = ThemeColors.DARKER_BG,
    disabled_color: str = ThemeColors.TEXT_MUTED,
    radius: int = 8,
) -> ft.FilledButton:
    """Create a styled accent button using the muted red palette.

    The button uses `ACCENT_3` (#C0394B) as the default background,
    which provides contrast against the dark surfaces while staying
    within the muted red palette. Hover states subtly shift toward
    `ACCENT_4` (#E63950) for visual feedback.

    Args:
        text: Button label text.
        on_click: Click event handler.
        width: Optional fixed width.
        height: Optional fixed height.
        bgcolor: Background color. Defaults to `ACCENT_3` (#C0394B).
        color: Text color. Defaults to `#FFFFFF` (contrast on red).
        hover_bgcolor: Hover background. If None, auto-shifts to ACCENT_4.
        disabled_bgcolor: Background when disabled.
        disabled_color: Text color when disabled.
        radius: Border radius in pixels.

    Returns:
        A configured ft.FilledButton with glassmorphism-aware styling.
    """
    if hover_bgcolor is None:
        hover_bgcolor = ThemeColors.ACCENT_4

    return ft.FilledButton(
        text=text,
        on_click=on_click,
        width=width,
        height=height,
        bgcolor=bgcolor,
        color=color,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=radius),
            # Hover state — subtle red deepening
            overlay_color=ThemeColors.BORDER_TRANSPARENT,
            # Track cursor hand shape
            animate_bgcolor=True,
            animation_duration=150,
        ),
    )


def create_glass_cards_row(
    cards: list[ft.Control],
    *,
    spacing: int = 8,
    width: float | None = None,
    height: float | None = None,
    opacity: float = 0.70,
) -> ft.Row:
    """Create a row of glassmorphism-styled card containers.

    Each card in *cards* is wrapped in a `create_glass_container` with
    the specified opacity, producing a consistent frosted-row effect
    useful for hand displays or board side panels.

    Args:
        cards: List of Flet controls to place as individual card slots.
        spacing: Horizontal spacing between cards in pixels.
        width: Row width. If None, content-determined.
        height: Row height. If None, content-determined.
        opacity: Surface opacity for all cards (0.0–1.0). Default 0.70.

    Returns:
        An ft.Row containing the glass-styled card containers.
    """
    glass_cards = []
    for i, card in enumerate(cards):
        # Alternate slight opacity variation for visual rhythm
        card_opacity = opacity if i % 2 == 0 else opacity - 0.03
        card_container = create_glass_container(
            content=card,
            width=100 if len(cards) > 5 else 120,
            height=150,
            bg_opacity=card_opacity,
            border_radius=8,
            shadow=ThemeShadows.ELEVATED_SUBTLE,
            blur=ThemeBlur.FROST_MEDIUM,
        )
        glass_cards.append(card_container)

    return ft.Row(
        controls=glass_cards,
        width=width,
        height=height,
        spacing=spacing,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


# ---------------------------------------------------------------------------
# Flet Theme Configuration
# ---------------------------------------------------------------------------

class MerithraTheme(ft.Theme):
    """Custom Flet Theme encapsulating the Merithra design system.

    This theme can be applied to a `page.theme = MerithraTheme()` and
    provides default text styles, color schemes, and asset defaults
    consistent with the Dark Modern Glassmorphism aesthetic.

    Usage:
        page.theme = MerithraTheme()
        page.theme_mode = ft.ThemeMode.DARK
    """

    #: Primary color scheme — dark mode colors for background, surface,
    #: on-surface, etc. Flet maps these theming properties.
    color_scheme: ClassVar[ft.ColorScheme] = ft.ColorScheme(
        # Background
        primary=ThemeColors.ACCENT_3,       # Primary accent for highlights
        on_primary=ThemeColors.TEXT_ON_ACCENT,
        surface=ThemeColors.DARK_BG,        # Main surface
        on_surface=ThemeColors.TEXT_PRIMARY,
        # Error / warning use red from our palette
        error=ThemeColors.ACCENT_4,
        on_error=ThemeColors.TEXT_PRIMARY,
        # Secondary is typically the dark gray backdrop
        secondary=ThemeColors.DARKER_BG,
        on_secondary=ThemeColors.TEXT_SECONDARY,
    )

    #: Text theming overrides — maps typography constants to theme roles
    text_styles: ClassVar[dict[str, ft.TextStyle]] = {
        "headlineLarge": ft.TextStyle(
            size=ThemeTypography.H1["size"],
            weight=ThemeTypography.H1["weight"],
            color=ThemeTypography.H1["color"],
            letter_spacing=ThemeTypography.H1["letter_spacing"],
        ),
        "headlineMedium": ft.TextStyle(
            size=ThemeTypography.H2["size"],
            weight=ThemeTypography.H2["weight"],
            color=ThemeTypography.H2["color"],
            letter_spacing=ThemeTypography.H2["letter_spacing"],
        ),
        "titleLarge": ft.TextStyle(
            size=ThemeTypography.H3["size"],
            weight=ThemeTypography.H3["weight"],
            color=ThemeTypography.H3["color"],
            letter_spacing=ThemeTypography.H3["letter_spacing"],
        ),
        "bodyLarge": ft.TextStyle(
            size=ThemeTypography.Body1["size"],
            weight=ThemeTypography.Body1["weight"],
            color=ThemeTypography.Body1["color"],
            letter_spacing=ThemeTypography.Body1["letter_spacing"],
        ),
        "bodyMedium": ft.TextStyle(
            size=ThemeTypography.Body2["size"],
            weight=ThemeTypography.Body2["weight"],
            color=ThemeTypography.Body2["color"],
            letter_spacing=ThemeTypography.Body2["letter_spacing"],
        ),
        "bodySmall": ft.TextStyle(
            size=ThemeTypography.Body3["size"],
            weight=ThemeTypography.Body3["weight"],
            color=ThemeTypography.Body3["color"],
            letter_spacing=ThemeTypography.Body3["letter_spacing"],
        ),
        "labelLarge": ft.TextStyle(
            size=ThemeTypography.Caption["size"],
            weight=ThemeTypography.Caption["weight"],
            color=ThemeTypography.Caption["color"],
            letter_spacing=ThemeTypography.Caption["letter_spacing"],
        ),
        "labelMedium": ft.TextStyle(
            size=ThemeTypography.Overline["size"],
            weight=ThemeTypography.Overline["weight"],
            color=ThemeTypography.Overline["color"],
            letter_spacing=ThemeTypography.Overline["letter_spacing"],
        ),
        "labelSmall": ft.TextStyle(
            size=ThemeTypography.Overline2["size"],
            weight=ThemeTypography.Overline2["weight"],
            color=ThemeTypography.Overline2["color"],
            letter_spacing=ThemeTypography.Overline2["letter_spacing"],
        ),
    }

    #: Elevation / shadow defaults applied to containers by default
    # Flet uses `elevation` integer for shadow depth (platform-dependent)
    # We map our custom shadows via the `theme` property on individual controls
    elevation_map: ClassVar[dict[int, str]] = {
        1: ThemeShadows.ELEVATED_SUBTLE,   # minimal
        2: ThemeShadows.ELEVATED_MODERATE, # standard
        3: ThemeShadows.ELEVATED_NOTICE,   # notice/warning
    }


# ---------------------------------------------------------------------------
# Convenience exports — commonly used constants directly at module level
# ---------------------------------------------------------------------------

# Re-export the most frequently used colors as module-level constants
# so they can be imported as `from client.theme import ACCENT_3, DARK_BG, ...`
BLACK = ThemeColors.BLACK
DARK_BG = ThemeColors.DARK_BG
DARKER_BG = ThemeColors.DARKER_BG
DARK_BG_V2 = ThemeColors.DARK_BG_V2
DARKEST_BG_V2 = ThemeColors.DARKEST_BG_V2

SURFACE_TRANSPARENT = ThemeColors.SURFACE_TRANSPARENT
SURFACE_SUBTLE = ThemeColors.SURFACE_SUBTLE
SURFACE_MODERATE = ThemeColors.SURFACE_MODERATE
SURFACE_ELEVATED = ThemeColors.SURFACE_ELEVATED

BORDER_TRANSPARENT = ThemeColors.BORDER_TRANSPARENT
BORDER_SUBTLE_RED = ThemeColors.BORDER_SUBTLE_RED
BORDER_MEDIUM = ThemeColors.BORDER_MEDIUM
BORDER_STRONG = ThemeColors.BORDER_STRONG

ACCENT_1 = ThemeColors.ACCENT_1
ACCENT_2 = ThemeColors.ACCENT_2
ACCENT_3 = ThemeColors.ACCENT_3
ACCENT_4 = ThemeColors.ACCENT_4
ACCENT_GLOW = ThemeColors.ACCENT_GLOW
ACCENT_GLOW_STRONG = ThemeColors.ACCENT_GLOW_STRONG

TEXT_PRIMARY = ThemeColors.TEXT_PRIMARY
TEXT_SECONDARY = ThemeColors.TEXT_SECONDARY
TEXT_MUTED = ThemeColors.TEXT_MUTED
TEXT_DISABLED = ThemeColors.TEXT_DISABLED
TEXT_ON_ACCENT = ThemeColors.TEXT_ON_ACCENT

HP_LOW = ThemeColors.HP_LOW
HP_CRITICAL = ThemeColors.HP_CRITICAL
MANA_CURRENT = ThemeColors.MANA_CURRENT
MANA_AVAILABLE = ThemeColors.MANA_AVAILABLE
ARMOR = ThemeColors.ARMOR
COOLDOWN_OVERLAY = ThemeColors.COOLDOWN_OVERLAY

# Gradient shortcuts
HP_ORB_GRADIENT = ThemeGradients.HP_ORB
PANEL_SHADOW_GRADIENT = ThemeGradients.PANEL_SHADOW
BUTTON_HOVER_GRADIENT = ThemeGradients.BUTTON_HOVER
CARD_INNER_GLOW_GRADIENT = ThemeGradients.CARD_INNER_GLOW
ACCENT_GRADIENT = ThemeGradients.ACCENT_GRADIENT

# Helper shortcuts
create_glass = create_glass_container
create_button = create_accent_button
create_cards_row = create_glass_cards_row

# Theme instance
merithra_light = MerithraTheme()
merithra_dark = MerithraTheme(
    color_scheme=ft.ColorScheme(
        primary=ThemeColors.ACCENT_3,
        on_primary=ThemeColors.TEXT_ON_ACCENT,
        surface=ThemeColors.DARK_BG,
        on_surface=ThemeColors.TEXT_PRIMARY,
        error=ThemeColors.ACCENT_4,
        on_error=ThemeColors.TEXT_PRIMARY,
        secondary=ThemeColors.DARKER_BG,
        on_secondary=ThemeColors.TEXT_SECONDARY,
    )
)