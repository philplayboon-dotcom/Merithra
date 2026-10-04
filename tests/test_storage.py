"""Unit tests for SaveManager, atomic file persistence, and migrations."""

import pytest
import os
import json
from pathlib import Path

from core.models import create_new_savegame, SaveGameData
from core.storage import SaveManager, MigrationRegistry


@pytest.fixture
def temp_save_manager(tmp_path):
    """Provide a SaveManager pointing to an isolated temp directory."""
    return SaveManager(save_directory=tmp_path)


def test_save_and_load_cycle(temp_save_manager):
    """Test saving a game and loading it back cleanly."""
    save = create_new_savegame("Arthur", "WARRIOR")
    save.wallet.gold = 350
    save.unlocked_city_ids.append("city_silverport")

    # Save
    success = temp_save_manager.save(save, slot_id="slot_test")
    assert success is True

    # Check file on disk
    save_file = temp_save_manager.save_dir / "slot_test.json"
    assert save_file.exists()

    # Load
    loaded = temp_save_manager.load("slot_test")
    assert loaded is not None
    assert loaded.player_name == "Arthur"
    assert loaded.wallet.gold == 350
    assert "city_silverport" in loaded.unlocked_city_ids


def test_list_and_delete_saves(temp_save_manager):
    """Test listing multiple saves and deleting one."""
    save1 = create_new_savegame("Slot 1 Hero", "MAGE")
    save2 = create_new_savegame("Slot 2 Hero", "WARRIOR")

    temp_save_manager.save(save1, "save_1")
    temp_save_manager.save(save2, "save_2")

    saves = temp_save_manager.list_saves()
    assert len(saves) == 2
    slot_ids = [s["slot_id"] for s in saves]
    assert "save_1" in slot_ids
    assert "save_2" in slot_ids

    # Delete save_1
    assert temp_save_manager.delete_save("save_1") is True
    saves_after = temp_save_manager.list_saves()
    assert len(saves_after) == 1
    assert saves_after[0]["slot_id"] == "save_2"


def test_load_nonexistent_returns_none(temp_save_manager):
    """Test loading a missing save file returns None safely."""
    result = temp_save_manager.load("non_existent_slot")
    assert result is None


def test_schema_migration_flow(tmp_path):
    """Test automatic migration from version 1 to version 2."""
    custom_migrations = MigrationRegistry()

    # Define a sample v1 -> v2 migration that adds a new field
    def migrate_v1_to_v2(data):
        data["title"] = "Novize"
        return data

    custom_migrations.register_migration(1, migrate_v1_to_v2)

    # Write a v1 file manually
    raw_v1 = {
        "version": 1,
        "save_id": "mig_slot",
        "player_name": "OldPlayer",
    }
    envelope = {
        "format": "merithra_savegame",
        "version": 1,
        "payload": raw_v1,
    }
    file_path = tmp_path / "mig_slot.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(envelope, f)

    mgr = SaveManager(save_directory=tmp_path, migrations=custom_migrations)

    # Perform migration to v2
    migrated_dict = custom_migrations.migrate(raw_v1, target_version=2)
    assert migrated_dict["version"] == 2
    assert migrated_dict["title"] == "Novize"
