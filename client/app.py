from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import flet as ft

from core.engine.match import MatchConfig, MatchManager, MatchStatus
from core.models.savegame import SaveGameData
from core.pve.encounters import get_encounter
from client.game_board import GameBoard
from client.theme import CombatColors, ThemeColors
from client.state import (
    APP_VERSION,
    AppSettings,
    AppState,
    build_profile_slug,
    create_profile_record,
    get_profile_store,
    load_settings,
    normalize_profile_name,
    save_settings,
)


class AppController:
    """Small app-level controller for start, menu, settings and match flow."""

    def __init__(self, page: Optional[ft.Page] = None, storage_dir: str | Path | None = None):
        self.page = page
        self.storage_dir = Path(storage_dir) if storage_dir is not None else Path("saves")
        self.profile_store = get_profile_store(self.storage_dir)
        self.settings_path = Path(self.storage_dir) / "settings.json"
        self.state = AppState(settings=load_settings(self.settings_path))
        self._page_title = "Merithra"

    def can_start_match(self) -> bool:
        return self.state.active_profile is not None and self.state.active_match is None

    def validate_profile_name(self, name: str) -> str:
        return normalize_profile_name(name)

    def load_profile_list(self) -> list[str]:
        saves = self.profile_store.list_saves()
        return [save.get("player_name", "Unbekannt") for save in saves if save.get("player_name")]

    def _existing_profile_by_name(self, player_name: str) -> Optional[Any]:
        profile_name = normalize_profile_name(player_name)
        for save in self.profile_store.list_saves():
            if save.get("player_name") == profile_name:
                return self.profile_store.load(save["slot_id"])
        return None

    def login_profile(self, player_name: str) -> SaveGameData:
        validated_name = normalize_profile_name(player_name)
        existing = self._existing_profile_by_name(validated_name)
        if existing is not None:
            self.state.active_profile = existing
            self.state.last_profile_name = validated_name
            self.state.current_screen = "menu"
            return existing

        profile = create_profile_record(validated_name)
        profile_id = f"profile_{build_profile_slug(validated_name)}"
        self.profile_store.save(profile, slot_id=profile_id)
        self.state.active_profile = profile
        self.state.last_profile_name = validated_name
        self.state.current_screen = "menu"
        return profile

    def show_start_screen(self) -> ft.Column:
        form = ft.Column(
            spacing=16,
            width=420,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text("MERITHRA", size=34, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Text(f"Version {APP_VERSION}", size=14, color=ft.Colors.BLUE_GREY_200),
                ft.Text("Lokales Testprofil – kein Onlinekonto.", size=12, color=ft.Colors.GREY_400),
                ft.TextField(
                    label="Spielername",
                    hint_text="3–24 Zeichen",
                    value=self.state.last_profile_name,
                    max_length=24,
                    autofocus=True,
                    border_color=ft.Colors.OUTLINE,
                ),
                ft.Button(
                    content="Anmelden",
                    on_click=self._on_login_click,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                ),
                ft.Text("", size=12, color=ft.Colors.RED_200, visible=False, key="login_error"),
            ],
        )
        return form

    def _on_login_click(self, e: ft.ControlEvent) -> None:
        if not self.page:
            return
        field = next((c for c in self.page.controls if isinstance(c, ft.Column) and any(getattr(item, 'key', None) == 'login_error' for item in getattr(c, 'controls', []))), None)
        if field is None:
            return
        target = next((c for c in field.controls if getattr(c, 'key', None) == 'login_error'), None)
        if target is None:
            return
        target.visible = False
        try:
            value = next((c for c in field.controls if isinstance(c, ft.TextField)), None)
            if value is None:
                raise ValueError("Bitte gib einen Spielernamen ein.")
            self.login_profile(value.value)
            self.state.current_screen = "menu"
            self.page.controls.clear()
            self.page.add(self.show_menu_screen())
            self.page.update()
        except ValueError as exc:  # pragma: no cover - Flet interaction path
            target.value = str(exc)
            target.visible = True
            self.page.update()

    def show_menu_screen(self) -> ft.Column:
        version_text = ft.Text(f"Version {APP_VERSION}", size=11, color=ft.Colors.BLUE_GREY_300)
        player_text = ft.Text(
            f"Profil: {self.state.active_profile.player_name if self.state.active_profile else 'Gast'}",
            size=13,
            color=ft.Colors.WHITE,
        )
        return ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,
            controls=[
                ft.Text("Hauptmenü", size=28, weight=ft.FontWeight.BOLD),
                version_text,
                player_text,
                ft.Button(
                    content="Start",
                    on_click=self._on_start_match_click,
                    width=200,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                ),
                ft.TextButton(content="Optionen", on_click=self._on_options_click),
                ft.TextButton(content="Profil wechseln", on_click=self._on_profile_switch_click),
            ],
        )

    def _on_start_match_click(self, e: ft.ControlEvent) -> None:
        if not self.page or self.state.active_match is not None:
            return
        self.start_match()
        self.page.controls.clear()
        self.page.add(self.state.active_match)
        self.page.update()

    def _on_match_end(self, status: MatchStatus) -> None:
        if not self.page:
            return
        self.state.current_screen = "result"
        self.page.controls.clear()
        self.page.add(self.show_result_screen(status))
        self.page.update()

    def show_result_screen(self, status: MatchStatus) -> ft.Column:
        victory = status == MatchStatus.VICTORY
        return ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,
            controls=[
                ft.Icon(
                    ft.Icons.EMOJI_EVENTS if victory else ft.Icons.REPLAY,
                    size=64,
                    color=ThemeColors.ACCENT_4 if victory else ThemeColors.HP_LOW,
                ),
                ft.Text(
                    "Sieg!" if victory else "Niederlage",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=ThemeColors.ACCENT_4 if victory else ThemeColors.HP_LOW,
                ),
                ft.Text(
                    "Der Gegner ist besiegt." if victory else "Dein Held wurde besiegt.",
                    size=14,
                    color=ThemeColors.TEXT_SECONDARY,
                ),
                ft.Button(
                    content="Neuen Kampf starten",
                    on_click=self._on_retry_match_click,
                    width=220,
                ),
                ft.TextButton(
                    content="Zurück zum Hauptmenü",
                    on_click=self._on_return_from_result_click,
                ),
            ],
        )

    def _on_retry_match_click(self, e: ft.ControlEvent) -> None:
        if not self.page:
            return
        self.state.active_match = None
        board = self.start_match()
        self.page.controls.clear()
        self.page.add(board)
        self.page.update()

    def _on_return_from_result_click(self, e: ft.ControlEvent) -> None:
        if not self.page:
            return
        self.state.active_match = None
        self.state.current_screen = "menu"
        self.page.controls.clear()
        self.page.add(self.show_menu_screen())
        self.page.update()

    def _on_options_click(self, e: ft.ControlEvent) -> None:
        if not self.page:
            return
        self.page.controls.clear()
        self.page.add(self.show_options_screen())
        self.page.update()

    def _on_profile_switch_click(self, e: ft.ControlEvent) -> None:
        if not self.page:
            return
        self.state.active_profile = None
        self.state.current_screen = "start"
        self.page.controls.clear()
        self.page.add(self.show_start_screen())
        self.page.update()

    def show_options_screen(self) -> ft.Column:
        settings = self.state.settings
        return ft.Column(
            spacing=12,
            controls=[
                ft.Text("Optionen", size=26, weight=ft.FontWeight.BOLD),
                ft.Checkbox(label="Vollbild", value=settings.fullscreen),
                ft.Checkbox(label="Kampflog anzeigen", value=settings.show_battle_log),
                ft.Checkbox(label="Animationen reduzieren", value=settings.reduce_animations),
                ft.Row([
                    ft.Button(content="Speichern", on_click=self._on_save_settings_click),
                    ft.TextButton(content="Abbrechen", on_click=self._on_return_to_menu_click),
                    ft.TextButton(content="Standardwerte", on_click=self._on_reset_settings_click),
                ]),
            ],
        )

    def _on_save_settings_click(self, e: ft.ControlEvent) -> None:
        if not self.page:
            return
        column = next((c for c in self.page.controls if isinstance(c, ft.Column)), None)
        if column is None:
            return
        checkboxes = [c for c in column.controls if isinstance(c, ft.Checkbox)]
        self.state.settings = AppSettings(
            fullscreen=checkboxes[0].value if len(checkboxes) > 0 else False,
            show_battle_log=checkboxes[1].value if len(checkboxes) > 1 else True,
            reduce_animations=checkboxes[2].value if len(checkboxes) > 2 else False,
        )
        save_settings(self.state.settings, self.settings_path)
        self._on_return_to_menu_click(e)

    def _on_reset_settings_click(self, e: ft.ControlEvent) -> None:
        if not self.page:
            return
        self.state.settings = AppSettings()
        self.page.controls.clear()
        self.page.add(self.show_options_screen())
        self.page.update()

    def _on_return_to_menu_click(self, e: ft.ControlEvent) -> None:
        if not self.page:
            return
        self.state.current_screen = "menu"
        self.page.controls.clear()
        self.page.add(self.show_menu_screen())
        self.page.update()

    def start_match(self) -> GameBoard:
        if self.state.active_profile is None:
            raise ValueError("Ein aktives Profil ist erforderlich, um einen Kampf zu starten.")
        if self.state.active_match is not None:
            return self.state.active_match

        encounter = get_encounter("enc_wild_wolf")
        if encounter is None:
            raise ValueError("Starter-Kampf konnte nicht geladen werden.")

        config = MatchConfig(
            player_hero_name=self.state.active_profile.player_name,
            player_hero_class="MAGE",
            player_deck_ids=[],
            encounter=encounter,
        )
        manager = MatchManager(config)
        board = GameBoard(
            player=manager.player,
            opponent_player=manager.opponent,
            state_machine=manager.state_machine,
            match_manager=manager,
            on_match_end=self._on_match_end,
        )
        board.build()
        self.state.active_match = board
        self.state.current_screen = "match"
        return board


def main(page: ft.Page) -> None:
    page.title = "Merithra"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = CombatColors.BACKGROUND
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    page.window.width = 960
    page.window.height = 720

    controller = AppController(page=page)
    page.add(controller.show_start_screen())
    page.update()


if __name__ == "__main__":
    ft.run(main)
