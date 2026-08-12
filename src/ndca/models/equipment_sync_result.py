"""
SYNC-010 - Equipment synchronization result.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class EquipmentSyncResult:
    """Statistics and outcome for one equipment reconciliation run."""

    total_discovered: int = 0
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    reactivated: int = 0
    deactivated: int = 0
    failed: int = 0
    status: str = "SUCCESS"

    @property
    def processed(self) -> int:
        """Return the number of successfully processed equipment records."""
        return self.created + self.updated + self.unchanged + self.reactivated
