"""Save Game Migration System for Merithra.

Handles sequential data schema upgrades from version N to N+1 ensuring backward
compatibility of player savegames across updates.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List
import logging

logger = logging.getLogger(__name__)

# Migration function type: receives raw dict from version N, returns migrated dict for version N+1
MigrationFunc = Callable[[Dict[str, Any]], Dict[str, Any]]


class MigrationRegistry:
    """Registry of version-to-version migration functions."""

    CURRENT_VERSION: int = 1

    def __init__(self) -> None:
        # Key: source_version (e.g. 1 -> transforms from v1 to v2)
        self._migrations: Dict[int, MigrationFunc] = {}

    def register_migration(self, from_version: int, func: MigrationFunc) -> None:
        """Register a migration step from from_version to from_version + 1."""
        self._migrations[from_version] = func

    def migrate(self, raw_data: Dict[str, Any], target_version: int = CURRENT_VERSION) -> Dict[str, Any]:
        """Apply sequential migrations until raw_data reaches target_version."""
        current = raw_data.get("version", 1)

        if current > target_version:
            raise ValueError(
                f"Savegame version ({current}) is newer than current supported version ({target_version})."
            )

        data = dict(raw_data)
        while current < target_version:
            if current not in self._migrations:
                raise RuntimeError(
                    f"Missing migration path from version {current} to {current + 1}."
                )

            logger.info(f"Migrating savegame from v{current} to v{current + 1}...")
            data = self._migrations[current](data)
            current += 1
            data["version"] = current

        return data


# Global migration registry
migration_registry = MigrationRegistry()
