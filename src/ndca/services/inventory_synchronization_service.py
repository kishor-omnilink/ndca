"""
SYNC-005 / SYNC-011-A - Inventory Synchronization Orchestration.

Coordinates:

    NSP
      ↓
    InventorySnapshot
      ↓
    NetworkElementMapper
      ↓
    NetworkElement ORM
      ↓
    InventorySyncService
      ↓
    PostgreSQL

SYNC-011-A:
    Snapshot completeness is explicitly propagated to the
    synchronization service.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from ndca.mappers.network_element_mapper import (
    NetworkElementMapper,
)
from ndca.models.sync_result import SyncResult
from ndca.services.inventory_snapshot_service import (
    InventorySnapshotService,
)
from ndca.services.inventory_sync_service import (
    InventorySyncService,
)


class InventorySynchronizationService:
    """
    Orchestrate one Network Element synchronization run.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        """
        Initialize the synchronization orchestration service.
        """

        self._snapshot_service = (
            InventorySnapshotService()
        )

        self._mapper = (
            NetworkElementMapper()
        )

        self._sync_service = (
            InventorySyncService(
                session
            )
        )

    def synchronize(self) -> SyncResult:
        """
        Collect and synchronize the current NSP inventory.

        SYNC-011-A ensures that an incomplete Network Element
        collection cannot trigger deactivation.

        Processing sequence:

            NSP
             ↓
            InventorySnapshot
             ↓
            NetworkElementMapper
             ↓
            NetworkElement ORM
             ↓
            InventorySyncService
             ↓
            PostgreSQL
        """

        try:
            snapshot = (
                self._snapshot_service.collect()
            )

            discovered = (
                self._mapper.map_to_models(
                    snapshot
                )
            )

            return self._sync_service.synchronize(
                discovered,
                complete_snapshot=(
                    snapshot.is_complete
                ),
            )

        finally:
            self._snapshot_service.close()