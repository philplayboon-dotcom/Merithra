"""Versioned, Atomic Save Game Storage Manager for Merithra."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.models.savegame import SaveGameData
from .migrations import MigrationRegistry, migration_registry

logger = logging.getLogger(__name__)


class SaveManager:
    """Handles persistent saving, loading, atomic writing, and validation of savegames."""

    def __init__(
        self,
        save_directory: Optional[str | Path] = None,
        migrations: Optional[MigrationRegistry] = None,
    ):
        if save_directory is None:
            # Default saves directory in user profile or project root
            self.save_dir = Path("saves")
        else:
            self.save_dir = Path(save_directory)

        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.migrations = migrations or migration_registry

    def _get_save_path(self, slot_id: str) -> Path:
        """Resolve file path for a slot ID."""
        # Sanitize slot_id to prevent path traversal
        clean_id = "".join(c for c in slot_id if c.isalnum() or c in ("_", "-"))
        if not clean_id:
            clean_id = "slot_1"
        return self.save_dir / f"{clean_id}.json"

    def save(self, save_data: SaveGameData, slot_id: Optional[str] = None) -> bool:
        """Save game data atomically.

        Writes to a temporary file first and renames it atomically to guarantee
        that power failures or crashes never leave a corrupted save file.
        """
        target_slot = slot_id or save_data.save_id or "slot_1"
        save_data.save_id = target_slot
        save_data.updated_at = datetime.now().isoformat()

        target_path = self._get_save_path(target_slot)
        temp_path = target_path.with_suffix(".tmp")

        try:
            payload = save_data.to_dict()
            json_bytes = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")

            # Calculate checksum
            checksum = hashlib.sha256(json_bytes).hexdigest()

            envelope = {
                "format": "merithra_savegame",
                "version": save_data.version,
                "checksum": checksum,
                "payload": payload,
            }

            # 1. Write to temp file
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(envelope, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())

            # 2. Atomic rename / swap
            temp_path.replace(target_path)
            logger.info(f"Successfully saved game to {target_path}")
            return True

        except Exception as exc:
            logger.error(f"Failed to save game to {target_path}: {exc}")
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass
            return False

    def load(self, slot_id: str = "slot_1") -> Optional[SaveGameData]:
        """Load and deserialize a savegame file with integrity and migration checks."""
        target_path = self._get_save_path(slot_id)
        if not target_path.exists():
            logger.warning(f"Save file {target_path} not found.")
            return None

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                envelope = json.load(f)

            # Check format
            if envelope.get("format") != "merithra_savegame":
                # Legacy raw format fallback check
                if "save_id" in envelope or "player_name" in envelope:
                    raw_payload = envelope
                else:
                    logger.error(f"Invalid save format in {target_path}")
                    return None
            else:
                raw_payload = envelope.get("payload", {})
                expected_checksum = envelope.get("checksum")

                # Verify checksum integrity
                payload_bytes = json.dumps(raw_payload, indent=2, ensure_ascii=False).encode("utf-8")
                actual_checksum = hashlib.sha256(payload_bytes).hexdigest()
                if expected_checksum and expected_checksum != actual_checksum:
                    logger.warning(f"Savegame checksum mismatch in {target_path}, attempting to parse anyway...")

            # Run migrations if necessary
            migrated_payload = self.migrations.migrate(raw_payload)
            return SaveGameData.from_dict(migrated_payload)

        except Exception as exc:
            logger.error(f"Error loading save file {target_path}: {exc}")
            return None

    def list_saves(self) -> List[Dict[str, Any]]:
        """List all valid savegame files in the directory with metadata."""
        saves: List[Dict[str, Any]] = []
        for file in sorted(self.save_dir.glob("*.json")):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    envelope = json.load(f)
                payload = envelope.get("payload", envelope)
                saves.append(
                    {
                        "slot_id": file.stem,
                        "player_name": payload.get("player_name", "Unbekannt"),
                        "chapter": payload.get("current_chapter", 1),
                        "city_id": payload.get("current_city_id", "city_oakhaven"),
                        "updated_at": payload.get("updated_at", ""),
                        "play_time_seconds": payload.get("play_time_seconds", 0),
                        "file_path": str(file),
                    }
                )
            except Exception:
                continue
        return saves

    def delete_save(self, slot_id: str) -> bool:
        """Delete a save file."""
        target_path = self._get_save_path(slot_id)
        if target_path.exists():
            try:
                target_path.unlink()
                return True
            except OSError as exc:
                logger.error(f"Failed to delete {target_path}: {exc}")
                return False
        return False
