"""
SYNC-001 Inventory Synchronization Service tests.

Uses Python unittest and mocked repository/session objects.

These tests validate the inventory synchronization business logic:

- create new Network Elements
- update changed Network Elements
- reactivate previously inactive Network Elements
- count unchanged Network Elements
- deactivate missing Network Elements
- aggregate synchronization statistics
- rollback on synchronization failure
- complete/partial snapshot safety
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from ndca.models.network_element import NetworkElement
from ndca.models.sync_result import SyncResult
from ndca.services.inventory_sync_service import InventorySyncService


class TestInventorySyncService(unittest.TestCase):
    """Validate InventorySyncService behavior."""

    def setUp(self) -> None:
        """Create mocked dependencies for each test."""

        self.session = MagicMock()

        self.service = InventorySyncService(
            self.session
        )

        self.repository = MagicMock()
        self.service._repository = self.repository

        self.ne1 = NetworkElement(
            component_id="172.26.0.8",
            ne_id="172.26.0.8",
            ne_name="OCAC-BHADRAK-AR01",
            ip_address="172.26.0.8",
            system_type="7750 SR",
            software_version="24.4",
            vendor="Nokia",
            display_name="OCAC-BHADRAK-AR01",
            is_active=True,
        )

        self.ne2 = NetworkElement(
            component_id="172.26.0.9",
            ne_id="172.26.0.9",
            ne_name="OCAC-BHADRAK-AR02",
            ip_address="172.26.0.9",
            system_type="7750 SR",
            software_version="24.4",
            vendor="Nokia",
            display_name="OCAC-BHADRAK-AR02",
            is_active=True,
        )

    def _network_element(
        self,
        ne_id: str,
        *,
        is_active: bool = True,
    ) -> NetworkElement:
        """
        Build a standard NetworkElement for synchronization tests.

        This helper is intentionally kept in the existing SYNC-011 test
        class so SYNC-011-A can reuse the established test structure.
        """

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

    def test_create_new_network_element(self) -> None:
        """New discovered NE should be created."""

        self.repository.find_by_ne_id.return_value = None
        self.repository.find_all.return_value = []

        discovered = [
            self.ne1,
        ]

        result = self.service.synchronize(
            discovered,
            complete_snapshot=True,
        )

        self.repository.save.assert_called_once_with(
            self.ne1
        )

        self.session.commit.assert_called_once()

        self.assertIsInstance(
            result,
            SyncResult,
        )

        self.assertEqual(
            result.total_discovered,
            1,
        )

        self.assertEqual(
            result.created,
            1,
        )

        self.assertEqual(
            result.updated,
            0,
        )

        self.assertEqual(
            result.unchanged,
            0,
        )

        self.assertEqual(
            result.deactivated,
            0,
        )

    def test_update_changed_network_element(self) -> None:
        """Changed discovered NE should be updated."""

        existing = NetworkElement(
            component_id="172.26.0.8",
            ne_id="172.26.0.8",
            ne_name="OCAC-BHADRAK-AR01",
            ip_address="172.26.0.8",
            system_type="7750 SR",
            software_version="24.3",
            vendor="Nokia",
            display_name="OCAC-BHADRAK-AR01",
            is_active=True,
        )

        discovered = NetworkElement(
            component_id="172.26.0.8",
            ne_id="172.26.0.8",
            ne_name="OCAC-BHADRAK-AR01",
            ip_address="172.26.0.8",
            system_type="7750 SR",
            software_version="24.4",
            vendor="Nokia",
            display_name="OCAC-BHADRAK-AR01",
            is_active=True,
        )

        self.repository.find_by_ne_id.return_value = existing
        self.repository.find_all.return_value = [existing]

        result = self.service.synchronize(
            [discovered],
            complete_snapshot=True,
        )

        self.assertEqual(
            result.total_discovered,
            1,
        )

        self.assertEqual(
            result.updated,
            1,
        )

        self.assertEqual(
            result.created,
            0,
        )

        self.session.commit.assert_called_once()

    def test_unchanged_network_element(self) -> None:
        """Unchanged discovered NE should be counted as unchanged."""

        existing = NetworkElement(
            component_id="172.26.0.8",
            ne_id="172.26.0.8",
            ne_name="OCAC-BHADRAK-AR01",
            ip_address="172.26.0.8",
            system_type="7750 SR",
            software_version="24.4",
            vendor="Nokia",
            display_name="OCAC-BHADRAK-AR01",
            is_active=True,
        )

        discovered = NetworkElement(
            component_id="172.26.0.8",
            ne_id="172.26.0.8",
            ne_name="OCAC-BHADRAK-AR01",
            ip_address="172.26.0.8",
            system_type="7750 SR",
            software_version="24.4",
            vendor="Nokia",
            display_name="OCAC-BHADRAK-AR01",
            is_active=True,
        )

        self.repository.find_by_ne_id.return_value = existing
        self.repository.find_all.return_value = [existing]

        result = self.service.synchronize(
            [discovered],
            complete_snapshot=True,
        )

        self.assertEqual(
            result.total_discovered,
            1,
        )

        self.assertEqual(
            result.unchanged,
            1,
        )

        self.assertEqual(
            result.created,
            0,
        )

        self.assertEqual(
            result.updated,
            0,
        )

        self.assertEqual(
            result.deactivated,
            0,
        )

        self.session.commit.assert_called_once()

    def test_reactivate_previously_inactive_network_element(
        self,
    ) -> None:
        """A returning inactive NE should be reactivated."""

        existing = NetworkElement(
            component_id="172.26.0.8",
            ne_id="172.26.0.8",
            ne_name="OCAC-BHADRAK-AR01",
            ip_address="172.26.0.8",
            system_type="7750 SR",
            software_version="24.4",
            vendor="Nokia",
            display_name="OCAC-BHADRAK-AR01",
            is_active=False,
        )

        discovered = NetworkElement(
            component_id="172.26.0.8",
            ne_id="172.26.0.8",
            ne_name="OCAC-BHADRAK-AR01",
            ip_address="172.26.0.8",
            system_type="7750 SR",
            software_version="24.4",
            vendor="Nokia",
            display_name="OCAC-BHADRAK-AR01",
            is_active=True,
        )

        self.repository.find_by_ne_id.return_value = existing
        self.repository.find_all.return_value = [existing]

        result = self.service.synchronize(
            [discovered],
            complete_snapshot=True,
        )

        self.assertTrue(
            existing.is_active
        )

        self.assertEqual(
            result.updated,
            1,
        )

        self.session.commit.assert_called_once()

    def test_deactivate_missing_network_element(self) -> None:
        """Previously known but missing NE should be deactivated."""

        existing = NetworkElement(
            component_id="172.26.0.8",
            ne_id="172.26.0.8",
            ne_name="OCAC-BHADRAK-AR01",
            ip_address="172.26.0.8",
            system_type="7750 SR",
            software_version="24.4",
            vendor="Nokia",
            display_name="OCAC-BHADRAK-AR01",
            is_active=True,
        )

        self.repository.find_by_ne_id.return_value = None
        self.repository.find_all.return_value = [existing]

        result = self.service.synchronize(
            [],
            complete_snapshot=True,
        )

        self.assertFalse(
            existing.is_active
        )

        self.assertEqual(
            result.total_discovered,
            0,
        )

        self.assertEqual(
            result.deactivated,
            1,
        )

        self.session.commit.assert_called_once()

    def test_multiple_network_elements(self) -> None:
        """Synchronization should produce correct aggregate statistics."""

        existing_updated = NetworkElement(
            component_id="172.26.0.8",
            ne_id="172.26.0.8",
            ne_name="OCAC-BHADRAK-AR01",
            ip_address="172.26.0.8",
            system_type="7750 SR",
            software_version="24.3",
            vendor="Nokia",
            display_name="OCAC-BHADRAK-AR01",
            is_active=True,
        )

        existing_unchanged = NetworkElement(
            component_id="172.26.0.9",
            ne_id="172.26.0.9",
            ne_name="OCAC-BHADRAK-AR02",
            ip_address="172.26.0.9",
            system_type="7750 SR",
            software_version="24.4",
            vendor="Nokia",
            display_name="OCAC-BHADRAK-AR02",
            is_active=True,
        )

        existing_missing = NetworkElement(
            component_id="172.26.0.10",
            ne_id="172.26.0.10",
            ne_name="OCAC-BHADRAK-AR03",
            ip_address="172.26.0.10",
            system_type="7750 SR",
            software_version="24.4",
            vendor="Nokia",
            display_name="OCAC-BHADRAK-AR03",
            is_active=True,
        )

        discovered_updated = NetworkElement(
            component_id="172.26.0.8",
            ne_id="172.26.0.8",
            ne_name="OCAC-BHADRAK-AR01",
            ip_address="172.26.0.8",
            system_type="7750 SR",
            software_version="24.5",
            vendor="Nokia",
            display_name="OCAC-BHADRAK-AR01",
            is_active=True,
        )

        discovered_new = NetworkElement(
            component_id="172.26.0.11",
            ne_id="172.26.0.11",
            ne_name="OCAC-BHADRAK-AR04",
            ip_address="172.26.0.11",
            system_type="7750 SR",
            software_version="24.4",
            vendor="Nokia",
            display_name="OCAC-BHADRAK-AR04",
            is_active=True,
        )

        self.repository.find_all.return_value = [
            existing_updated,
            existing_unchanged,
            existing_missing,
        ]

        def find_by_ne_id(ne_id: str):
            mapping = {
                existing_updated.ne_id: existing_updated,
                existing_unchanged.ne_id: existing_unchanged,
            }

            return mapping.get(ne_id)

        self.repository.find_by_ne_id.side_effect = (
            find_by_ne_id
        )

        discovered = [
            discovered_updated,
            existing_unchanged,
            discovered_new,
        ]

        result = self.service.synchronize(
            discovered,
            complete_snapshot=True,
        )

        self.assertEqual(
            result.total_discovered,
            3,
        )

        self.assertEqual(
            result.created,
            1,
        )

        self.assertEqual(
            result.updated,
            1,
        )

        self.assertEqual(
            result.unchanged,
            1,
        )

        self.assertEqual(
            result.deactivated,
            1,
        )

        self.session.commit.assert_called_once()

    def test_failure_rolls_back_transaction(self) -> None:
        """Synchronization failure should rollback."""

        self.repository.find_all.side_effect = (
            RuntimeError(
                "Simulated repository failure"
            )
        )

        with self.assertRaises(RuntimeError):
            self.service.synchronize(
                [self.ne1],
                complete_snapshot=True,
            )

        self.session.rollback.assert_called_once()

        self.session.commit.assert_not_called()

    def test_partial_snapshot_does_not_deactivate(
        self,
    ) -> None:
        """
        A partial snapshot must never deactivate a missing NE.

        This is the SYNC-011-A safety requirement.
        """

        existing = self._network_element(
            "172.26.0.8",
            is_active=True,
        )

        self.repository.find_all.return_value = [
            existing,
        ]

        result = self.service.synchronize(
            [],
            complete_snapshot=False,
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


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )