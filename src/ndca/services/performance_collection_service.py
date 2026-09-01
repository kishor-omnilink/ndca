"""
Performance collection orchestration service.

Coordinates NFMPPerformanceCollector output with
PerformancePersistenceService.

Transaction ownership remains exclusively with
PerformancePersistenceService.
"""

from __future__ import annotations

from collections.abc import Sequence
from uuid import uuid4

from ndca.collectors.performance.nfmp_performance_collector import (
    NFMPPerformanceCollector,
)
from ndca.core.logging import get_logger
from ndca.services.performance_persistence_service import (
    PerformancePersistenceService,
)


class PerformanceCollectionService:
    """Orchestrate performance collection and persistence."""

    def __init__(
        self,
        collector: NFMPPerformanceCollector,
        persistence_service: PerformancePersistenceService,
        *,
        instance_names: Sequence[str],
        current_data_classes: Sequence[str],
    ) -> None:
        self._collector = collector
        self._persistence_service = persistence_service
        self._instance_names = tuple(
            str(value).strip()
            for value in instance_names
            if str(value).strip()
        )
        self._current_data_classes = tuple(
            str(value).strip()
            for value in current_data_classes
            if str(value).strip()
        )
        self._logger = get_logger(__name__)

    def collect_and_persist(
        self,
        *,
        sync_id: str | None = None,
    ) -> int:
        """Collect verified performance data and persist the records."""

        effective_sync_id = sync_id or str(uuid4())

        if not self._instance_names:
            self._logger.warning(
                "Performance collection skipped: no target instances"
            )
            return 0

        if not self._current_data_classes:
            self._logger.warning(
                "Performance collection skipped: no performance classes"
            )
            return 0

        records = self._collector.collect(
            self._current_data_classes,
            self._instance_names,
            effective_sync_id,
        )

        if not records:
            self._logger.info(
                "Performance collection returned no records",
                sync_id=effective_sync_id,
            )
            return 0

        persisted = self._persistence_service.persist(records)

        self._logger.info(
            "Performance collection persisted",
            sync_id=effective_sync_id,
            collected=len(records),
            persisted=persisted,
        )

        return persisted
