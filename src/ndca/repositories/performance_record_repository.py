"""
SYNC-012-D.1.4 - Performance Record repository.

Provides persistence and query operations for normalized performance
measurements.

Transaction lifecycle remains owned by the calling service.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ndca.models.performance_record import PerformanceRecordModel
from ndca.repositories.base_repository import BaseRepository
from ndca.repositories.exceptions import RepositoryQueryError


class PerformanceRecordRepository(BaseRepository[PerformanceRecordModel]):
    """Repository for durable performance measurement records."""

    def __init__(self, session: Session) -> None:
        """Initialize the Performance Record repository."""
        super().__init__(
            session=session,
            model=PerformanceRecordModel,
        )

    def save(
        self,
        entity: PerformanceRecordModel,
    ) -> PerformanceRecordModel:
        """Add one performance record to the current transaction.

        This method does not commit.
        """
        self._session.add(entity)
        return entity

    def save_all(
        self,
        entities: list[PerformanceRecordModel],
    ) -> None:
        """Add multiple performance records to the current transaction.

        This method does not commit.
        """
        self._session.add_all(entities)

    def find_by_sync_id(
        self,
        sync_id: str,
    ) -> list[PerformanceRecordModel]:
        """Return performance records belonging to one synchronization run."""
        statement = (
            select(PerformanceRecordModel)
            .where(PerformanceRecordModel.sync_id == sync_id)
            .order_by(PerformanceRecordModel.collection_time.asc())
        )

        try:
            return list(self._session.scalars(statement).all())
        except SQLAlchemyError as ex:
            raise RepositoryQueryError(
                f"Failed to retrieve performance records for sync_id={sync_id!r}"
            ) from ex

    def find_by_object_id(
        self,
        object_id: str,
    ) -> list[PerformanceRecordModel]:
        """Return performance records for one source object."""
        statement = (
            select(PerformanceRecordModel)
            .where(PerformanceRecordModel.object_id == object_id)
            .order_by(PerformanceRecordModel.collection_time.asc())
        )

        try:
            return list(self._session.scalars(statement).all())
        except SQLAlchemyError as ex:
            raise RepositoryQueryError(
                f"Failed to retrieve performance records for object_id={object_id!r}"
            ) from ex

    def find_by_metric(
        self,
        metric: str,
    ) -> list[PerformanceRecordModel]:
        """Return performance records for one normalized metric."""
        statement = (
            select(PerformanceRecordModel)
            .where(PerformanceRecordModel.metric == metric)
            .order_by(PerformanceRecordModel.collection_time.asc())
        )

        try:
            return list(self._session.scalars(statement).all())
        except SQLAlchemyError as ex:
            raise RepositoryQueryError(
                f"Failed to retrieve performance records for metric={metric!r}"
            ) from ex

    def find_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime,
    ) -> list[PerformanceRecordModel]:
        """Return performance records within a collection-time range."""
        statement = (
            select(PerformanceRecordModel)
            .where(
                PerformanceRecordModel.collection_time >= start_time,
                PerformanceRecordModel.collection_time <= end_time,
            )
            .order_by(PerformanceRecordModel.collection_time.asc())
        )

        try:
            return list(self._session.scalars(statement).all())
        except SQLAlchemyError as ex:
            raise RepositoryQueryError(
                "Failed to retrieve performance records for "
                f"time range {start_time!r} - {end_time!r}"
            ) from ex

    def find_latest(
        self,
        object_id: str,
        metric: str,
    ) -> PerformanceRecordModel | None:
        """Return the latest observation for an object/metric pair."""
        statement = (
            select(PerformanceRecordModel)
            .where(
                PerformanceRecordModel.object_id == object_id,
                PerformanceRecordModel.metric == metric,
            )
            .order_by(PerformanceRecordModel.collection_time.desc())
            .limit(1)
        )

        try:
            return self._session.scalar(statement)
        except SQLAlchemyError as ex:
            raise RepositoryQueryError(
                "Failed to retrieve latest performance record for "
                f"object_id={object_id!r}, metric={metric!r}"
            ) from ex
