"""
SYNC-012-D.1.4.4 - Performance persistence service tests.
"""

from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from ndca.models.dto.performance_record import PerformanceRecord
from ndca.models.performance_record import PerformanceRecordModel
from ndca.services.performance_persistence_service import (
    PerformancePersistenceService,
)


class TestPerformancePersistenceService(unittest.TestCase):
    """Validate performance persistence transaction behavior."""

    def setUp(self) -> None:
        self.session = MagicMock()
        self.service = PerformancePersistenceService(self.session)
        self.repository = MagicMock()
        self.service._repository = self.repository

        self.record = PerformanceRecord(
            sync_id="sync-001",
            source="Nokia NSP",
            xml_class="equipment.InterfaceStats",
            category="interface",
            object_id="object-001",
            object_name="Test Interface",
            metric="inputOctets",
            metric_source_name="inputOctets",
            value={"value": 123},
            collection_time=datetime.now(timezone.utc),
            source_time=datetime.now(timezone.utc),
            is_historical=False,
            raw_payload={"source": "test"},
        )

    def test_empty_records_returns_zero_without_transaction(self) -> None:
        result = self.service.persist([])

        self.assertEqual(result, 0)
        self.session.commit.assert_not_called()
        self.session.rollback.assert_not_called()

    def test_persist_saves_and_commits(self) -> None:
        result = self.service.persist([self.record])

        self.assertEqual(result, 1)
        self.repository.save_all.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.rollback.assert_not_called()

        entities = (
            self.repository.save_all.call_args.args[0]
        )

        self.assertEqual(len(entities), 1)
        self.assertIsInstance(
            entities[0],
            PerformanceRecordModel,
        )
        self.assertEqual(
            entities[0].sync_id,
            self.record.sync_id,
        )
        self.assertEqual(
            entities[0].metric,
            self.record.metric,
        )
        self.assertEqual(
            entities[0].collection_time,
            self.record.collection_time,
        )
        self.assertFalse(entities[0].is_historical)

    def test_persist_multiple_records(self) -> None:
        records = [self.record, self.record]

        result = self.service.persist(records)

        self.assertEqual(result, 2)

        entities = (
            self.repository.save_all.call_args.args[0]
        )

        self.assertEqual(len(entities), 2)

    def test_persist_rolls_back_on_failure(self) -> None:
        self.repository.save_all.side_effect = (
            RuntimeError("database failure")
        )

        with self.assertRaises(RuntimeError):
            self.service.persist([self.record])

        self.session.commit.assert_not_called()
        self.session.rollback.assert_called_once()

    def test_to_model_preserves_normalized_fields(self) -> None:
        persistence_time = datetime.now(timezone.utc)

        model = self.service._to_model(
            self.record,
            persistence_time,
        )

        self.assertEqual(model.sync_id, self.record.sync_id)
        self.assertEqual(model.source, self.record.source)
        self.assertEqual(model.xml_class, self.record.xml_class)
        self.assertEqual(model.category, self.record.category)
        self.assertEqual(model.object_id, self.record.object_id)
        self.assertEqual(model.object_name, self.record.object_name)
        self.assertEqual(model.metric, self.record.metric)
        self.assertEqual(
            model.metric_source_name,
            self.record.metric_source_name,
        )
        self.assertEqual(model.value, self.record.value)
        self.assertEqual(
            model.collection_time,
            self.record.collection_time,
        )
        self.assertEqual(
            model.source_time,
            self.record.source_time,
        )
        self.assertEqual(
            model.raw_payload,
            self.record.raw_payload,
        )
        self.assertEqual(
            model.persistence_time,
            persistence_time,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
