"""
SYNC-012-D.1.4.3 - Performance Record repository tests.
"""

from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from ndca.models.performance_record import PerformanceRecordModel
from ndca.repositories.performance_record_repository import (
    PerformanceRecordRepository,
)


class TestPerformanceRecordRepository(unittest.TestCase):
    """Validate PerformanceRecordRepository behavior."""

    def setUp(self) -> None:
        self.session = MagicMock()
        self.repository = PerformanceRecordRepository(self.session)

        self.record = PerformanceRecordModel(
            sync_id="sync-001",
            source="Nokia NSP",
            xml_class="Interface",
            category="interface",
            object_id="object-001",
            object_name="Test Interface",
            metric="inputOctets",
            metric_source_name="inputOctets",
            value={"value": 123},
            collection_time=datetime.now(timezone.utc),
            source_time=None,
            persistence_time=datetime.now(timezone.utc),
            is_historical=False,
            raw_payload={"source": "test"},
        )

    def test_repository_initialization(self) -> None:
        self.assertIs(
            self.repository._model,
            PerformanceRecordModel,
        )
        self.assertIs(
            self.repository._session,
            self.session,
        )

    def test_save(self) -> None:
        result = self.repository.save(self.record)

        self.assertIs(result, self.record)
        self.session.add.assert_called_once_with(self.record)
        self.session.commit.assert_not_called()

    def test_save_all(self) -> None:
        records = [self.record]

        result = self.repository.save_all(records)

        self.assertIsNone(result)
        self.session.add_all.assert_called_once_with(records)
        self.session.commit.assert_not_called()

    def test_find_by_sync_id(self) -> None:
        expected = [self.record]
        self.session.scalars.return_value.all.return_value = expected

        result = self.repository.find_by_sync_id("sync-001")

        self.assertEqual(result, expected)
        self.session.scalars.assert_called_once()

    def test_find_by_object_id(self) -> None:
        expected = [self.record]
        self.session.scalars.return_value.all.return_value = expected

        result = self.repository.find_by_object_id("object-001")

        self.assertEqual(result, expected)
        self.session.scalars.assert_called_once()

    def test_find_by_metric(self) -> None:
        expected = [self.record]
        self.session.scalars.return_value.all.return_value = expected

        result = self.repository.find_by_metric("inputOctets")

        self.assertEqual(result, expected)
        self.session.scalars.assert_called_once()

    def test_find_by_time_range(self) -> None:
        expected = [self.record]
        self.session.scalars.return_value.all.return_value = expected

        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        end = datetime(2026, 1, 2, tzinfo=timezone.utc)

        result = self.repository.find_by_time_range(start, end)

        self.assertEqual(result, expected)
        self.session.scalars.assert_called_once()

    def test_find_latest(self) -> None:
        self.session.scalar.return_value = self.record

        result = self.repository.find_latest(
            "object-001",
            "inputOctets",
        )

        self.assertIs(result, self.record)
        self.session.scalar.assert_called_once()

    def test_save_does_not_commit(self) -> None:
        self.repository.save(self.record)

        self.session.commit.assert_not_called()
        self.session.rollback.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
