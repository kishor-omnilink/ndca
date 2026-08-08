"""
SYNC-004 - Real PostgreSQL integration test.

This test validates the complete InventorySyncService path against
the configured NDCA PostgreSQL database.

The test creates uniquely identified temporary data and removes it
after successful or failed execution.

Existing NDCA inventory is not used for deactivation testing.
"""

from __future__ import annotations

import sys
import unittest
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import delete

from ndca.database.session import get_session
from ndca.models.enums import SyncStatus
from ndca.models.network_element import NetworkElement
from ndca.models.synchronization_run import SynchronizationRun
from ndca.repositories.network_element_repository import (
    NetworkElementRepository,
)
from ndca.repositories.synchronization_run_repository import (
    SynchronizationRunRepository,
)
from ndca.services.inventory_sync_service import InventorySyncService


class TestInventorySyncPostgreSQL(unittest.TestCase):
    """Validate SYNC-004 against real PostgreSQL."""

    TEST_PREFIX = "SYNC004-TEST-"

    def setUp(self) -> None:
        """Create a real PostgreSQL session."""

        self.session = get_session()

        self.ne_repository = NetworkElementRepository(
            self.session
        )

        self.run_repository = SynchronizationRunRepository(
            self.session
        )

        self.test_ne_id = (
            f"{self.TEST_PREFIX}{uuid4().hex}"
        )

        self.test_component_id = (
            f"{self.TEST_PREFIX}COMP-{uuid4().hex}"
        )

    def tearDown(self) -> None:
        """Remove all temporary SYNC-004 test data."""

        try:
            self.session.execute(
                delete(SynchronizationRun).where(
                    SynchronizationRun.sync_id.like(
                        f"{self.TEST_PREFIX}%"
                    )
                )
            )

            self.session.execute(
                delete(NetworkElement).where(
                    NetworkElement.ne_id.like(
                        f"{self.TEST_PREFIX}%"
                    )
                )
            )

            self.session.commit()

        except Exception:
            self.session.rollback()

        finally:
            self.session.close()

    def _create_test_network_element(self) -> NetworkElement:
        """Create a temporary test Network Element."""

        return NetworkElement(
            component_id=self.test_component_id,
            ne_id=self.test_ne_id,
            ne_name="SYNC004-TEST-ROUTER",
            ip_address="192.0.2.250",
            system_type="7750 SR",
            software_version="24.4",
            vendor="Nokia",
            display_name="SYNC004-TEST-ROUTER",
            admin_state="UP",
            oper_state="UP",
            is_active=True,
            sync_status=SyncStatus.PENDING,
        )

    def test_real_postgresql_synchronization(
        self,
    ) -> None:
        """Synchronize a temporary NE and verify PostgreSQL state."""

        test_ne = self._create_test_network_element()

        # Seed the temporary Network Element.
        self.ne_repository.save(test_ne)
        self.session.commit()

        sync_service = InventorySyncService(
            self.session
        )

        discovered = (
            self.ne_repository.find_all()
        )

        # Important:
        # Include all existing inventory so the service does not
        # interpret unrelated existing NEs as missing.
        test_ne_from_db = next(
            entity
            for entity in discovered
            if entity.ne_id == self.test_ne_id
        )

        result = sync_service.synchronize(
            discovered
        )

        self.assertIsNotNone(
            result.sync_id
        )

        self.assertEqual(
            result.status,
            "SUCCESS",
        )

        self.assertGreaterEqual(
            result.total_discovered,
            1,
        )

        # The temporary NE already existed, so this run should
        # classify it as unchanged.
        self.assertGreaterEqual(
            result.unchanged,
            1,
        )

        # Verify the actual Network Element exists in PostgreSQL.
        persisted_ne = (
            self.ne_repository.find_by_ne_id(
                self.test_ne_id
            )
        )

        self.assertIsNotNone(
            persisted_ne
        )

        assert persisted_ne is not None

        self.assertEqual(
            persisted_ne.ne_id,
            self.test_ne_id,
        )

        self.assertTrue(
            persisted_ne.is_active
        )

        self.assertEqual(
            persisted_ne.sync_status,
            SyncStatus.SUCCESS,
        )

        self.assertIsNotNone(
            persisted_ne.last_sync
        )

        # Verify the actual SynchronizationRun exists
        # in PostgreSQL.
        persisted_run = (
            self.run_repository.find_by_sync_id(
                result.sync_id
            )
        )

        self.assertIsNotNone(
            persisted_run
        )

        assert persisted_run is not None

        self.assertEqual(
            persisted_run.sync_id,
            result.sync_id,
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

        self.assertIsNotNone(
            persisted_run.started_at
        )

        self.assertIsNotNone(
            persisted_run.completed_at
        )

        self.assertIsNone(
            persisted_run.error_message
        )

        self.assertLessEqual(
            persisted_run.started_at,
            persisted_run.completed_at,
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )