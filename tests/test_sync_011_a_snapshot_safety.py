"""
SYNC-011-A - Complete/Partial Snapshot Safety tests.

Validation rules:

1. A valid Network Element list is COMPLETE.
2. An explicitly empty Network Element list is COMPLETE.
3. A missing Network Element collection is PARTIAL.
4. A malformed Network Element collection is PARTIAL.
5. COMPLETE snapshots may deactivate missing Network Elements.
6. PARTIAL snapshots must never deactivate missing Network Elements.
7. Returned Network Elements remain active in both cases.
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from ndca.models.inventory_snapshot import (
    InventorySnapshot,
)
from ndca.models.network_element import (
    NetworkElement,
)
from ndca.models.sync_result import (
    SyncResult,
)
from ndca.services.inventory_sync_service import (
    InventorySyncService,
)


class TestInventorySnapshotCompleteness(
    unittest.TestCase
):
    """Validate InventorySnapshot completeness detection."""

    def _snapshot(
        self,
        raw_data: dict,
    ) -> InventorySnapshot:
        """Create a test InventorySnapshot."""

        return InventorySnapshot(
            sync_id="sync-011-a",
            source="Nokia NSP",
            endpoint=(
                "/restconf/data/"
                "nsp-equipment:network/network-element"
            ),
            raw_data=raw_data,
        )

    def test_network_element_list_is_complete(
        self,
    ) -> None:
        """A present Network Element list is complete."""

        snapshot = self._snapshot(
            {
                "nsp-equipment:network-element": []
            }
        )

        self.assertTrue(
            snapshot.is_complete
        )

        self.assertFalse(
            snapshot.is_partial
        )

    def test_network_element_list_with_data_is_complete(
        self,
    ) -> None:
        """A populated Network Element list is complete."""

        snapshot = self._snapshot(
            {
                "nsp-equipment:network-element": [
                    {
                        "ne-id": "172.26.0.8"
                    }
                ]
            }
        )

        self.assertTrue(
            snapshot.is_complete
        )

        self.assertFalse(
            snapshot.is_partial
        )

    def test_missing_network_element_key_is_partial(
        self,
    ) -> None:
        """A missing Network Element collection is partial."""

        snapshot = self._snapshot(
            {}
        )

        self.assertFalse(
            snapshot.is_complete
        )

        self.assertTrue(
            snapshot.is_partial
        )

    def test_invalid_network_element_collection_is_partial(
        self,
    ) -> None:
        """A malformed Network Element collection is partial."""

        snapshot = self._snapshot(
            {
                "nsp-equipment:network-element": {
                    "invalid": "object"
                }
            }
        )

        self.assertFalse(
            snapshot.is_complete
        )

        self.assertTrue(
            snapshot.is_partial
        )


class TestInventorySyncSnapshotSafety(
    unittest.TestCase
):
    """Validate complete/partial synchronization safety."""

    def setUp(self) -> None:
        """Create mocked persistence dependencies."""

        self.session = MagicMock()

        self.service = InventorySyncService(
            self.session
        )

        self.repository = MagicMock()
        self.run_repository = MagicMock()

        self.service._repository = (
            self.repository
        )

        self.service._run_repository = (
            self.run_repository
        )
    
    def _network_element(
        self,
        ne_id: str,
        *,
        is_active: bool = True,
        ) -> NetworkElement:
        """Build a standard NetworkElement for synchronization tests."""

        return NetworkElement(
            component_id=ne_id,
            ne_id=ne_id,
            ne_name=f"OCAC-TEST-{ne_id}",
            ip_address=ne_id,
            system_type="7750 SR",
            software_version="24.4",
            vendor="Nokia",
            display_name=f"OCAC-TEST-{ne_id}",
            is_active=is_active,
        )

    @staticmethod
    def _network_element(
        ne_id: str,
        *,
        active: bool = True,
    ) -> NetworkElement:
        """Create a deterministic test Network Element."""

        return NetworkElement(
            component_id=ne_id,
            ne_id=ne_id,
            ne_name=f"TEST-{ne_id}",
            ip_address=ne_id,
            system_type="7750 SR",
            software_version="24.4",
            vendor="Nokia",
            display_name=f"TEST-{ne_id}",
            is_active=active,
        )

    def test_complete_snapshot_deactivates_missing_network_element(
        self,
    ) -> None:
        """A complete snapshot may deactivate a missing NE."""

        existing = self._network_element(
            "172.26.0.8",
            active=True,
        )

        self.repository.find_all.return_value = [
            existing
        ]

        result = self.service.synchronize(
            [],
            snapshot_complete=True,
        )

        self.assertIsInstance(
            result,
            SyncResult,
        )

        self.assertEqual(
            result.total_discovered,
            0,
        )

        self.assertEqual(
            result.deactivated,
            1,
        )

        self.assertFalse(
            existing.is_active
        )

        self.session.commit.assert_called_once()

    def test_partial_snapshot_does_not_deactivate(
        self,
    ) -> None:
        """A partial snapshot must never deactivate a missing NE."""

        existing = self._network_element(
            "172.26.0.8",
            active=True,
        )

        self.repository.find_all.return_value = [
            existing
        ]

        result = self.service.synchronize(
            [],
            snapshot_complete=False,
        )

        self.assertIsInstance(
            result,
            SyncResult,
        )

        self.assertEqual(
            result.total_discovered,
            0,
        )

        self.assertEqual(
            result.deactivated,
            0,
        )

        self.assertTrue(
            existing.is_active
        )

        self.session.commit.assert_called_once()

    def test_empty_complete_snapshot_is_authoritative(
        self,
    ) -> None:
        """An explicitly empty COMPLETE snapshot is authoritative."""

        existing = self._network_element(
            "172.26.0.8",
            active=True,
        )

        self.repository.find_all.return_value = [
            existing
        ]

        result = self.service.synchronize(
            [],
            snapshot_complete=True,
        )

        self.assertEqual(
            result.deactivated,
            1,
        )

        self.assertFalse(
            existing.is_active
        )

    def test_empty_partial_snapshot_is_safe(
        self,
    ) -> None:
        """An empty PARTIAL snapshot must not deactivate inventory."""

        existing = self._network_element(
            "172.26.0.8",
            active=True,
        )

        self.repository.find_all.return_value = [
            existing
        ]

        result = self.service.synchronize(
            [],
            snapshot_complete=False,
        )

        self.assertEqual(
            result.deactivated,
            0,
        )

        self.assertTrue(
            existing.is_active
        )

    def test_complete_snapshot_keeps_returned_network_element_active(
        self,
    ) -> None:
        """
        A Network Element returned by a complete snapshot remains active.
        """

        existing = self._network_element(
            "172.26.0.8",
            active=True,
        )

        discovered = self._network_element(
            "172.26.0.8",
            active=True,
        )

        self.repository.find_all.return_value = [
            existing
        ]

        result = self.service.synchronize(
            [discovered],
            snapshot_complete=True,
        )

        self.assertEqual(
            result.deactivated,
            0,
        )

        self.assertTrue(
            existing.is_active
        )

    def test_partial_snapshot_keeps_returned_network_element_active(
        self,
    ) -> None:
        """
        A Network Element returned by a partial snapshot is processed.
        """

        existing = self._network_element(
            "172.26.0.8",
            active=True,
        )

        discovered = self._network_element(
            "172.26.0.8",
            active=True,
        )

        self.repository.find_all.return_value = [
            existing
        ]

        result = self.service.synchronize(
            [discovered],
            snapshot_complete=False,
        )

        self.assertEqual(
            result.deactivated,
            0,
        )

        self.assertTrue(
            existing.is_active
        )

        self.assertIn(
            result.unchanged,
            (0, 1),
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )