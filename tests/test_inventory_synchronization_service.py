"""
SYNC-002 - End-to-End Inventory Synchronization Service tests.
"""

from unittest.mock import MagicMock, patch
import unittest

from ndca.models.inventory_snapshot import InventorySnapshot
from ndca.models.network_element import NetworkElement
from ndca.models.sync_result import SyncResult
from ndca.services.inventory_synchronization_service import (
    InventorySynchronizationService,
)


def make_ne() -> NetworkElement:
    """Create a representative Network Element."""

    return NetworkElement(
        component_id="172.26.0.8",
        ne_id="172.26.0.8",
        ne_name="OCAC-BHADRAK-AR01",
        ip_address="172.26.0.8",
        system_type="7750 SR",
        software_version="24.4",
        vendor="Nokia",
        display_name="OCAC-BHADRAK-AR01",
        admin_state="UP",
        oper_state="UP",
        is_active=True,
    )


class TestInventorySynchronizationService(unittest.TestCase):
    """Validate SYNC-002 orchestration."""

    def setUp(self) -> None:
        self.session = MagicMock()

        self.snapshot_service = MagicMock()
        self.mapper = MagicMock()
        self.sync_service = MagicMock()

        self.snapshot = InventorySnapshot(
            sync_id="snapshot-001",
            source="Nokia NSP",
            endpoint="/restconf/data/nsp-equipment:network-element",
            raw_data={
                "nsp-equipment:network-element": [
                    {
                        "ne-id": "172.26.0.8",
                        "ne-name": "OCAC-BHADRAK-AR01",
                    }
                ]
            },
        )

        self.discovered = [make_ne()]

        self.result = SyncResult(
            sync_id="sync-001",
            total_discovered=1,
            created=1,
            status="SUCCESS",
        )

        snapshot_patcher = patch(
            "ndca.services.inventory_synchronization_service."
            "InventorySnapshotService",
            return_value=self.snapshot_service,
        )

        mapper_patcher = patch(
            "ndca.services.inventory_synchronization_service."
            "NetworkElementMapper",
            return_value=self.mapper,
        )

        sync_patcher = patch(
            "ndca.services.inventory_synchronization_service."
            "InventorySyncService",
            return_value=self.sync_service,
        )

        self.addCleanup(snapshot_patcher.stop)
        self.addCleanup(mapper_patcher.stop)
        self.addCleanup(sync_patcher.stop)

        snapshot_patcher.start()
        mapper_patcher.start()
        sync_patcher.start()

        self.service = InventorySynchronizationService(
            self.session
        )

    def test_successful_synchronization(self) -> None:
        """Successful collection, mapping, and synchronization."""

        self.snapshot_service.collect.return_value = self.snapshot
        self.mapper.map.return_value = self.discovered
        self.sync_service.synchronize.return_value = self.result

        result = self.service.synchronize()

        self.assertIs(result, self.result)

        self.snapshot_service.collect.assert_called_once_with()
        self.mapper.map.assert_called_once_with(
            self.snapshot
        )
        self.sync_service.synchronize.assert_called_once_with(
            self.discovered
        )
        self.snapshot_service.close.assert_called_once_with()

    def test_collection_failure_closes_snapshot_service(self) -> None:
        """Collection failure must still close the collector."""

        error = RuntimeError("NSP collection failed")

        self.snapshot_service.collect.side_effect = error

        with self.assertRaises(RuntimeError):
            self.service.synchronize()

        self.mapper.map.assert_not_called()
        self.sync_service.synchronize.assert_not_called()
        self.snapshot_service.close.assert_called_once_with()

    def test_mapping_failure_closes_snapshot_service(self) -> None:
        """Mapping failure must still close the collector."""

        self.snapshot_service.collect.return_value = self.snapshot
        self.mapper.map.side_effect = RuntimeError(
            "mapping failed"
        )

        with self.assertRaises(RuntimeError):
            self.service.synchronize()

        self.sync_service.synchronize.assert_not_called()
        self.snapshot_service.close.assert_called_once_with()

    def test_sync_failure_closes_snapshot_service(self) -> None:
        """SYNC-001 failure must still close the collector."""

        self.snapshot_service.collect.return_value = self.snapshot
        self.mapper.map.return_value = self.discovered
        self.sync_service.synchronize.side_effect = RuntimeError(
            "database synchronization failed"
        )

        with self.assertRaises(RuntimeError):
            self.service.synchronize()

        self.snapshot_service.close.assert_called_once_with()

    def test_sync_result_is_propagated(self) -> None:
        """SYNC-001 SyncResult must be returned unchanged."""

        self.snapshot_service.collect.return_value = self.snapshot
        self.mapper.map.return_value = self.discovered
        self.sync_service.synchronize.return_value = self.result

        result = self.service.synchronize()

        self.assertEqual(result.sync_id, "sync-001")
        self.assertEqual(result.total_discovered, 1)
        self.assertEqual(result.created, 1)
        self.assertEqual(result.status, "SUCCESS")


if __name__ == "__main__":
    unittest.main(verbosity=2)