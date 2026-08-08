"""
SYNC-003 repository layer tests.

Uses Python unittest and mocks the SQLAlchemy Session.
Database transaction testing will be performed during
the synchronization integration stage.
"""

from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from ndca.models.enums import SyncStatus
from ndca.models.synchronization_run import SynchronizationRun
from ndca.repositories.synchronization_run_repository import (
    SynchronizationRunRepository,
)


class TestSynchronizationRunRepository(unittest.TestCase):
    """Validate SynchronizationRunRepository behavior."""

    def setUp(self) -> None:
        """Create a mocked SQLAlchemy session."""

        self.session = MagicMock()

        self.repository = SynchronizationRunRepository(
            self.session
        )

        self.run1 = SynchronizationRun(
            sync_id="sync-001",
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            total_discovered=10,
            created=2,
            updated=3,
            deactivated=1,
            unchanged=4,
            failed=0,
            status=SyncStatus.SUCCESS,
        )

        self.run2 = SynchronizationRun(
            sync_id="sync-002",
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            total_discovered=20,
            created=5,
            updated=4,
            deactivated=2,
            unchanged=9,
            failed=0,
            status=SyncStatus.SUCCESS,
        )

    def test_repository_initialization(self) -> None:
        """Repository should initialize with SynchronizationRun model."""

        self.assertIs(
            self.repository._model,
            SynchronizationRun,
        )

        self.assertIs(
            self.repository._session,
            self.session,
        )

    def test_find_by_sync_id(self) -> None:
        """find_by_sync_id() should return the matching run."""

        self.session.scalar.return_value = self.run1

        result = self.repository.find_by_sync_id(
            "sync-001"
        )

        self.assertIs(
            result,
            self.run1,
        )

        self.session.scalar.assert_called_once()

    def test_find_by_sync_id_not_found(self) -> None:
        """find_by_sync_id() should return None when absent."""

        self.session.scalar.return_value = None

        result = self.repository.find_by_sync_id(
            "sync-999"
        )

        self.assertIsNone(result)

        self.session.scalar.assert_called_once()

    def test_find_all(self) -> None:
        """find_all() should return all synchronization runs."""

        scalar_result = MagicMock()
        scalar_result.all.return_value = [
            self.run1,
            self.run2,
        ]

        self.session.scalars.return_value = scalar_result

        result = self.repository.find_all()

        self.assertEqual(
            result,
            [
                self.run1,
                self.run2,
            ],
        )

        self.session.scalars.assert_called_once()

    def test_save(self) -> None:
        """save() should add the entity without committing."""

        result = self.repository.save(
            self.run1
        )

        self.assertIs(
            result,
            self.run1,
        )

        self.session.add.assert_called_once_with(
            self.run1
        )

        self.session.commit.assert_not_called()

    def test_update(self) -> None:
        """update() should add the entity without committing."""

        result = self.repository.update(
            self.run1
        )

        self.assertIs(
            result,
            self.run1,
        )

        self.session.add.assert_called_once_with(
            self.run1
        )

        self.session.commit.assert_not_called()

    def test_save_or_update(self) -> None:
        """save_or_update() should add the entity without committing."""

        result = self.repository.save_or_update(
            self.run1
        )

        self.assertIs(
            result,
            self.run1,
        )

        self.session.add.assert_called_once_with(
            self.run1
        )

        self.session.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)