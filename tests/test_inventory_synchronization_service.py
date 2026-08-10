"""
SYNC-005 end-to-end orchestration unit tests.
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from ndca.models.inventory_snapshot import InventorySnapshot
from ndca.models.network_element import NetworkElement
from ndca.models.sync_result import SyncResult
from ndca.services.inventory_snapshot_service import (
    InventorySnapshotService,
)
from ndca.services.inventory_synchronization_service import (
    InventorySynchronizationService,
)


class TestInventorySynchronizationService(unittest.TestCase):
    """Validate SYNC-005 orchestration."""

    def setUp(self) -> None:
        """Create mocked dependencies."""

        self.session = MagicMock()

        # Patch the real close() method at the class level.
        # This gives the test a reliable MagicMock to verify.
        self.close_patcher = patch.object(
            InventorySnapshotService,
            "close",
            autospec=True,
        )

        self.close_mock = self.close_patcher.start()

        self.service = InventorySynchronizationService(
            self.session
        )

        # synchronize() is a real method, so replace it with a
        # MagicMock to verify whether it was called.
        self.service._sync_service.synchronize = MagicMock()

        self.snapshot = InventorySnapshot(
            sync_id="snapshot-001",
            source="Nokia NSP",
            endpoint="test",
            raw_data={
                "nsp-equipment:network-element": [
                    {
                        "ne-id": "NE-001",
                        "ne-name": "ROUTER-001",
                        "component-id": "COMP-001",
                        "ip-address": "192.0.2.1",
                        "product": "7750 SR",
                        "version": "24.4.1",
                        "admin-state": "UP",
                        "oper-state": "UP",
                        "source-type": "NFM-P",
                    }
                ]
            },
        )

    def tearDown(self) -> None:
        """Stop the class-level close() patch."""

        self.close_patcher.stop()

    def test_synchronize_collects_and_maps_inventory(
        self,
    ) -> None:
        """Collector data should reach InventorySyncService."""

        self.service._snapshot_service.collect = MagicMock(
            return_value=self.snapshot
        )

        expected_result = SyncResult(
            sync_id="sync-result-001",
            total_discovered=1,
            created=1,
            status="SUCCESS",
        )

        self.service._sync_service.synchronize.return_value = (
            expected_result
        )

        result = self.service.synchronize()

        self.assertIs(
            result,
            expected_result,
        )

        self.service._snapshot_service.collect.assert_called_once()

        self.service._sync_service.synchronize.assert_called_once()

        discovered = (
            self.service
            ._sync_service
            .synchronize
            .call_args.args[0]
        )

        self.assertEqual(
            len(discovered),
            1,
        )

        self.assertIsInstance(
            discovered[0],
            NetworkElement,
        )

        self.assertEqual(
            discovered[0].ne_id,
            "NE-001",
        )

        self.assertEqual(
            discovered[0].component_id,
            "COMP-001",
        )

        self.assertEqual(
            discovered[0].ip_address,
            "192.0.2.1",
        )

        self.assertEqual(
            discovered[0].system_type,
            "7750 SR",
        )

        self.assertEqual(
            discovered[0].software_version,
            "24.4.1",
        )

    def test_snapshot_service_is_closed(
        self,
    ) -> None:
        """Snapshot service must be closed after synchronization."""

        self.service._snapshot_service.collect = MagicMock(
            return_value=self.snapshot
        )

        self.service._sync_service.synchronize.return_value = (
            SyncResult(
                sync_id="sync-result-002",
                total_discovered=1,
                created=1,
                status="SUCCESS",
            )
        )

        self.service.synchronize()

        self.close_mock.assert_called_once_with(
            self.service._snapshot_service
        )

    def test_snapshot_collection_failure_closes_service(
        self,
    ) -> None:
        """Collector failure must still close resources."""

        self.service._snapshot_service.collect = MagicMock(
            side_effect=RuntimeError(
                "NSP collection failure"
            )
        )

        with self.assertRaises(RuntimeError):
            self.service.synchronize()

        self.close_mock.assert_called_once_with(
            self.service._snapshot_service
        )

        self.service._sync_service.synchronize.assert_not_called()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )