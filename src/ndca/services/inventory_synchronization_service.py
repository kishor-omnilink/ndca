"""
SYNC-002 - End-to-End Inventory Synchronization Service.

Orchestrates inventory collection, mapping, and persistence.

SYNC-001 remains responsible for the database synchronization
transaction and entity reconciliation.
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

    The service coordinates:

        NSP collection
            -> InventorySnapshot
            -> Network Element mapping
            -> SYNC-001 persistence synchronization
    """

    def __init__(self, session: Session) -> None:
        """Initialize the end-to-end synchronization service."""

        self._snapshot_service = InventorySnapshotService()
        self._mapper = NetworkElementMapper()
        self._sync_service = InventorySyncService(session)

    def synchronize(self) -> SyncResult:
        """
        Collect, map, and synchronize Network Elements.

        Returns
        -------
        SyncResult
            Result returned by SYNC-001.

        Raises
        ------
        Exception
            Propagates collection, mapping, or synchronization errors.
        """

        try:
            snapshot = self._snapshot_service.collect()

            discovered = self._mapper.map(snapshot)

            return self._sync_service.synchronize(discovered)

        finally:
            self._snapshot_service.close()
