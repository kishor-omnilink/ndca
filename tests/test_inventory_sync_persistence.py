"""
SYNC-004 synchronization-run integration tests.

Validates that InventorySyncService creates and persists
SynchronizationRun records together with inventory changes.
"""

from __future__ import annotations

import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from ndca.models.enums import SyncStatus
from ndca.models.network_element import NetworkElement
from ndca.models.synchronization_run import SynchronizationRun
from ndca.services.inventory_sync_service import InventorySyncService


def make_ne(
    ne_id: str,
    name: str,
    ip: str,
    active: bool = True,
) -> NetworkElement:
    """Create a deterministic test Network Element."""

    return NetworkElement(
        component_id=ne_id,
        ne_id=ne_id,
        ne_name=name,
        ip_address=ip,
        system_type="7750 SR",
        software_version="24.4",
        vendor="Nokia",
        display_name=name,
        admin_state="UP",
        oper_state="UP",
        is_active=active,
    )


class TestInventorySyncPersistence(unittest.TestCase):
    """Validate synchronization-run persistence."""

    def setUp(self) -> None:
        """Create a mocked session and mocked repositories."""

        self.session = MagicMock()

        self.service = InventorySyncService(
            self.session
        )

        # The service constructs the repositories internally.
        # Replace them with mocks so this test validates service
        # behavior rather than repository implementation.
        self.service._repository = MagicMock()
        self.service._run_repository = MagicMock()

    @patch(
        "ndca.services.inventory_sync_service.uuid4",
        return_value="sync-test-001",
    )
    @patch(
        "ndca.services.inventory_sync_service.datetime"
    )
    def test_success_persists_synchronization_run(
        self,
        mock_datetime: MagicMock,
        mock_uuid4: MagicMock,
    ) -> None:
        """Successful synchronization should persist its run."""

        now = datetime(
            2026,
            8,
            8,
            12,
            0,
            0,
        )

        mock_datetime.now.return_value = now

        incoming = make_ne(
            "172.26.0.8",
            "OCAC-BHADRAK-AR01",
            "172.26.0.8",
        )

        self.service._repository.find_all.return_value = []

        result = self.service.synchronize(
            [incoming]
        )

        self.assertEqual(
            result.sync_id,
            "sync-test-001",
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
            result.deactivated,
            0,
        )

        self.assertEqual(
            result.unchanged,
            0,
        )

        self.assertEqual(
            result.failed,
            0,
        )

        self.assertEqual(
            result.status,
            "SUCCESS",
        )

        self.service._repository.save.assert_called_once_with(
            incoming
        )

        self.service._run_repository.save.assert_called_once()

        persisted_run = (
            self.service._run_repository.save.call_args.args[0]
        )

        self.assertIsInstance(
            persisted_run,
            SynchronizationRun,
        )

        self.assertEqual(
            persisted_run.sync_id,
            "sync-test-001",
        )

        self.assertEqual(
            persisted_run.total_discovered,
            1,
        )

        self.assertEqual(
            persisted_run.created,
            1,
        )

        self.assertEqual(
            persisted_run.updated,
            0,
        )

        self.assertEqual(
            persisted_run.deactivated,
            0,
        )

        self.assertEqual(
            persisted_run.unchanged,
            0,
        )

        self.assertEqual(
            persisted_run.failed,
            0,
        )

        self.assertEqual(
            persisted_run.status,
            SyncStatus.SUCCESS,
        )

        self.assertIsNone(
            persisted_run.error_message
        )

        self.session.commit.assert_called_once()

    def test_failed_synchronization_does_not_persist_run(
        self,
    ) -> None:
        """Failed synchronization should rollback and not save a run."""

        self.service._repository.find_all.side_effect = (
            RuntimeError("database failure")
        )

        with self.assertRaises(RuntimeError):
            self.service.synchronize([])

        self.session.rollback.assert_called_once()

        self.session.commit.assert_not_called()

        self.service._run_repository.save.assert_not_called()

    def test_run_statistics_match_sync_result(
        self,
    ) -> None:
        """Persisted run statistics should match SyncResult."""

        existing_changed = make_ne(
            "172.26.0.8",
            "OCAC-BHADRAK-AR01",
            "172.26.0.8",
            active=True,
        )

        incoming_changed = make_ne(
            "172.26.0.8",
            "OCAC-BHADRAK-AR01-NEW",
            "172.26.0.8",
            active=True,
        )

        existing_unchanged = make_ne(
            "172.26.0.10",
            "OCAC-PURI-AR01",
            "172.26.0.10",
            active=True,
        )

        incoming_unchanged = make_ne(
            "172.26.0.10",
            "OCAC-PURI-AR01",
            "172.26.0.10",
            active=True,
        )

        existing_missing = make_ne(
            "172.26.0.11",
            "OCAC-JAJPUR-AR01",
            "172.26.0.11",
            active=True,
        )

        incoming_new = make_ne(
            "172.26.0.9",
            "OCAC-CUTTACK-AR01",
            "172.26.0.9",
            active=True,
        )

        self.service._repository.find_all.return_value = [
            existing_changed,
            existing_unchanged,
            existing_missing,
        ]

        result = self.service.synchronize(
            [
                incoming_changed,
                incoming_new,
                incoming_unchanged,
            ]
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

        self.assertEqual(
            result.failed,
            0,
        )

        self.assertEqual(
            result.status,
            "SUCCESS",
        )

        self.service._run_repository.save.assert_called_once()

        persisted_run = (
            self.service._run_repository.save.call_args.args[0]
        )

        self.assertEqual(
            persisted_run.total_discovered,
            result.total_discovered,
        )

        self.assertEqual(
            persisted_run.created,
            result.created,
        )

        self.assertEqual(
            persisted_run.updated,
            result.updated,
        )

        self.assertEqual(
            persisted_run.deactivated,
            result.deactivated,
        )

        self.assertEqual(
            persisted_run.unchanged,
            result.unchanged,
        )

        self.assertEqual(
            persisted_run.failed,
            result.failed,
        )

        self.assertEqual(
            persisted_run.status,
            SyncStatus.SUCCESS,
        )

        self.session.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )