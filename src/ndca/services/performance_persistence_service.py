"""
SYNC-012-D.1.4.4 - Performance persistence service.

Persists normalized PerformanceRecord DTOs into PostgreSQL/TimescaleDB.

Transaction lifecycle is owned by this service.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ndca.models.dto.performance_record import PerformanceRecord
from ndca.models.performance_record import PerformanceRecordModel
from ndca.repositories.performance_record_repository import (
    PerformanceRecordRepository,
)


class PerformancePersistenceService:
    """Persist normalized performance records."""

    def __init__(self, session: Session) -> None:
        """Initialize the persistence service."""
        self._session = session
        self._repository = PerformanceRecordRepository(session)

    def persist(
        self,
        records: list[PerformanceRecord],
    ) -> int:
        """Persist performance records as one transaction.

        Parameters
        ----------
        records:
            Normalized PerformanceRecord DTOs.

        Returns
        -------
        int
            Number of records submitted for persistence.

        Raises
        ------
        Exception
            Any persistence failure is rolled back and re-raised.
        """
        if not records:
            return 0

        try:
            now = datetime.now(timezone.utc)

            entities = [
                self._to_model(record, now)
                for record in records
            ]

            self._repository.save_all(entities)
            self._session.commit()

            return len(entities)

        except Exception:
            self._session.rollback()
            raise

    @staticmethod
    def _to_model(
        record: PerformanceRecord,
        persistence_time: datetime,
    ) -> PerformanceRecordModel:
        """Convert one normalized DTO into the persistence model."""
        return PerformanceRecordModel(
            sync_id=record.sync_id,
            source=record.source,
            xml_class=record.xml_class,
            category=record.category,
            object_id=record.object_id,
            object_name=record.object_name,
            metric=record.metric,
            metric_source_name=record.metric_source_name,
            value=record.value,
            collection_time=record.collection_time,
            source_time=record.source_time,
            persistence_time=persistence_time,
            is_historical=record.is_historical,
            raw_payload=record.raw_payload,
            evidence_status=record.evidence_status,
            notes=record.notes,
        )
