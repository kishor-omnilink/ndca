"""
SYNC-012-D.1.5 - Performance synchronization scheduler.

The scheduler owns cadence and run-level orchestration only.
Database transaction ownership remains with
PerformancePersistenceService.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from uuid import uuid4

from sqlalchemy.orm import Session

from ndca.collectors.performance.nfmp_performance_collector import (
    NFMPPerformanceCollector,
)
from ndca.core.logging import get_logger
from ndca.services.performance_collection_service import (
    PerformanceCollectionService,
)
from ndca.services.performance_persistence_service import (
    PerformancePersistenceService,
)

VERIFIED_INTERFACE_CURRENT_DATA_CLASSES: tuple[str, ...] = (
    "equipment.InterfaceStats",
    "equipment.InterfaceAdditionalStats",
)


class PerformanceSyncScheduler:
    """Execute one performance synchronization run."""

    def __init__(
        self,
        *,
        session_factory: Callable[[], Session],
        target_provider: Callable[[], Sequence[str]],
        collector_factory: Callable[[], NFMPPerformanceCollector],
    ) -> None:
        self._session_factory = session_factory
        self._target_provider = target_provider
        self._collector_factory = collector_factory
        self._logger = get_logger(__name__)

    def run_once(self) -> int:
        """
        Execute one performance synchronization run.

        No target instances means no NFM-P request and no database transaction.
        """

        instance_names = tuple(
            str(value).strip()
            for value in self._target_provider()
            if str(value).strip()
        )

        if not instance_names:
            self._logger.info(
                "Performance synchronization skipped: no target instances"
            )
            return 0

        sync_id = str(uuid4())
        session = self._session_factory()
        collector = self._collector_factory()

        try:
            persistence_service = PerformancePersistenceService(session)

            service = PerformanceCollectionService(
                collector,
                persistence_service,
                instance_names=instance_names,
                current_data_classes=VERIFIED_INTERFACE_CURRENT_DATA_CLASSES,
            )

            return service.collect_and_persist(sync_id=sync_id)

        finally:
            collector.close()
            session.close()
