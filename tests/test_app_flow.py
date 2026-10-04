from __future__ import annotations

from pathlib import Path

import pytest

from client.app import AppController
from client.state import AppSettings, normalize_profile_name
from core.engine.match import MatchStatus


@pytest.fixture
def app_controller(tmp_path: Path) -> AppController:
    return AppController(storage_dir=tmp_path / "app-state")


def test_start_screen_requires_valid_local_profile_name() -> None:
    with pytest.raises(ValueError):
        normalize_profile_name("  ")

    with pytest.raises(ValueError):
        normalize_profile_name("ab")

    with pytest.raises(ValueError):
        normalize_profile_name("bad@name")

    assert normalize_profile_name("  hero_1  ") == "hero_1"


def test_login_creates_profile_and_routes_to_menu(app_controller: AppController) -> None:
    profile = app_controller.login_profile("  Test Hero  ")

    assert profile.player_name == "Test Hero"
    assert app_controller.state.active_profile is profile
    assert app_controller.state.current_screen == "menu"
    assert app_controller.can_start_match() is True


def test_start_and_menu_screens_build_with_installed_flet_api(
    app_controller: AppController,
) -> None:
    start_screen = app_controller.show_start_screen()
    app_controller.login_profile("Test Hero")
    menu_screen = app_controller.show_menu_screen()
    options_screen = app_controller.show_options_screen()

    assert start_screen.controls
    assert menu_screen.controls
    assert options_screen.controls


def test_result_screen_offers_retry_and_menu_navigation(
    app_controller: AppController,
) -> None:
    result_screen = app_controller.show_result_screen(MatchStatus.VICTORY)

    assert result_screen.controls[1].value == "Sieg!"
    assert result_screen.controls[3].content == "Neuen Kampf starten"
    assert result_screen.controls[4].content == "Zurück zum Hauptmenü"


def test_invalid_profile_name_is_rejected(app_controller: AppController) -> None:
    with pytest.raises(ValueError):
        app_controller.login_profile("bad@name")

    assert app_controller.state.active_profile is None
    assert app_controller.state.current_screen == "start"


def test_start_match_creates_a_fresh_board_only_once(app_controller: AppController) -> None:
    app_controller.login_profile("Alpha")
    board = app_controller.start_match()

    assert board is not None
    assert app_controller.state.current_screen == "match"
    assert app_controller.state.active_match is board

    second_board = app_controller.start_match()
    assert second_board is board
    assert app_controller.state.active_match is board


def test_settings_are_persisted_separately_from_save_data(app_controller: AppController) -> None:
    settings_path = app_controller.settings_path
    assert settings_path.parent.exists()

    app_controller.state.settings = AppSettings(fullscreen=True, show_battle_log=False, reduce_animations=True)
    from client.state import save_settings

    save_settings(app_controller.state.settings, settings_path)
    restored = app_controller.state.settings
    assert restored.fullscreen is True
    assert restored.show_battle_log is False
    assert restored.reduce_animations is True
