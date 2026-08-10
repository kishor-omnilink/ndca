"""
SYNC-005 - Inventory Synchronization Orchestration.

Coordinates:

    NSP collection
        -> InventorySnapshot
        -> NetworkElement DTO
        -> NetworkElement ORM
        -> InventorySyncService
        -> PostgreSQL
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from ndca.mappers.network_element_mapper import NetworkElementMapper
from ndca.models.sync_result import SyncResult
from ndca.services.inventory_snapshot_service import (
    InventorySnapshotService,
)
from ndca.services.inventory_sync_service import InventorySyncService


class InventorySynchronizationService:
    """
    Orchestrate one complete Network Element synchronization run.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize the synchronization orchestration service.
        """

        self._snapshot_service = InventorySnapshotService()
        self._mapper = NetworkElementMapper()
        self._sync_service = InventorySyncService(session)

    def synchronize(self) -> SyncResult:
        """
        Collect and synchronize the current NSP inventory.

        Processing sequence:

            NSP
             ↓
            Snapshot
             ↓
            DTO
             ↓
            ORM
             ↓
            InventorySyncService
             ↓
            PostgreSQL

        Returns
        -------
        SyncResult
            Result produced by InventorySyncService.

        Raises
        ------
        Exception
            Propagates collection, mapping, or synchronization errors.
        """

        try:
            snapshot = self._snapshot_service.collect()

            discovered = self._mapper.map_to_models(
                snapshot
            )

            return self._sync_service.synchronize(
                discovered
            )

        finally:
            self._snapshot_service.close()