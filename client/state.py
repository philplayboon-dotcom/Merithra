from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any

from core.models import SaveGameData, create_new_savegame
from core.storage import SaveManager


APP_VERSION = "0.1.0"
PROFILE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9 _-]{3,24}$")


@dataclass
class AppSettings:
    fullscreen: bool = False
    show_battle_log: bool = True
    reduce_animations: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "fullscreen": self.fullscreen,
            "show_battle_log": self.show_battle_log,
            "reduce_animations": self.reduce_animations,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "AppSettings":
        payload = data or {}
        return cls(
            fullscreen=bool(payload.get("fullscreen", False)),
            show_battle_log=bool(payload.get("show_battle_log", True)),
            reduce_animations=bool(payload.get("reduce_animations", False)),
        )


@dataclass
class AppState:
    current_screen: str = "start"
    active_profile: SaveGameData | None = None
    settings: AppSettings = field(default_factory=AppSettings)
    active_match: Any = None
    last_profile_name: str = ""


def normalize_profile_name(name: str) -> str:
    cleaned = (name or "").strip()
    if not cleaned:
        raise ValueError("Bitte gib einen Spielernamen ein.")
    if len(cleaned) < 3 or len(cleaned) > 24:
        raise ValueError("Der Spielername muss 3 bis 24 Zeichen lang sein.")
    if not PROFILE_NAME_PATTERN.fullmatch(cleaned):
        raise ValueError("Nur Buchstaben, Zahlen, Leerzeichen, Unterstriche und Bindestriche sind erlaubt.")
    return cleaned


def build_profile_slug(name: str) -> str:
    cleaned = normalize_profile_name(name)
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", cleaned).strip("_")
    return slug.lower() or "profile"


def save_settings(settings: AppSettings, settings_path: str | Path) -> None:
    target = Path(settings_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(__import__("json").dumps(settings.to_dict(), indent=2), encoding="utf-8")


def load_settings(settings_path: str | Path) -> AppSettings:
    target = Path(settings_path)
    if not target.exists():
        return AppSettings()
    try:
        return AppSettings.from_dict(__import__("json").loads(target.read_text(encoding="utf-8")))
    except Exception:
        return AppSettings()


def get_profile_store(directory: str | Path | None = None) -> SaveManager:
    return SaveManager(save_directory=directory or Path("saves"))


def create_profile_record(name: str) -> SaveGameData:
    profile_name = normalize_profile_name(name)
    save = create_new_savegame(profile_name, "MAGE")
    save.save_id = f"profile_{build_profile_slug(profile_name)}"
    return save
