"""
SYNC-006 - Scheduled Inventory Synchronization.

Provides periodic inventory synchronization using APScheduler.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from ndca.core.config import settings
from ndca.database.session import get_session
from ndca.models.sync_result import SyncResult
from ndca.services.inventory_synchronization_service import (
    InventorySynchronizationService,
)

logger = logging.getLogger(__name__)


class InventorySyncScheduler:
    """
    Schedule periodic inventory synchronization.

    Scheduling responsibility remains here. Inventory synchronization
    business logic remains in InventorySynchronizationService.
    """

    def __init__(
        self,
        interval_seconds: int | None = None,
        session_factory: Callable[[], Session] = get_session,
    ) -> None:
        """
        Initialize the inventory synchronization scheduler.
        """

        interval = (
            settings.collection_interval
            if interval_seconds is None
            else interval_seconds
        )

        if interval <= 0:
            raise ValueError(
                "interval_seconds must be greater than zero"
            )

        self._interval_seconds = interval
        self._session_factory = session_factory

        self._scheduler = BackgroundScheduler()

        self._scheduler.add_job(
            self.run_once,
            trigger="interval",
            seconds=self._interval_seconds,
            id="inventory_synchronization",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )

    @property
    def interval_seconds(self) -> int:
        """Return the configured scheduling interval."""

        return self._interval_seconds

    @property
    def scheduler(self) -> BackgroundScheduler:
        """Return the underlying APScheduler instance."""

        return self._scheduler

    def run_once(self) -> SyncResult:
        """
        Execute one inventory synchronization run.

        A fresh database session is created for every run and is
        always closed after execution.
        """

        session = self._session_factory()

        try:
            service = InventorySynchronizationService(
                session
            )

            logger.info(
                "Starting scheduled inventory synchronization"
            )

            result = service.synchronize()

            logger.info(
                "Scheduled inventory synchronization completed",
                extra={
                    "sync_id": result.sync_id,
                    "status": result.status,
                    "total_discovered": result.total_discovered,
                    "created": result.created,
                    "updated": result.updated,
                    "unchanged": result.unchanged,
                    "deactivated": result.deactivated,
                },
            )

            return result

        except Exception:
            logger.exception(
                "Scheduled inventory synchronization failed"
            )
            raise

        finally:
            session.close()

    def start(
        self,
        run_immediately: bool = True,
    ) -> None:
        """
        Start the background scheduler.

        Parameters
        ----------
        run_immediately:
            Execute one synchronization immediately before starting
            the periodic APScheduler job.
        """

        if run_immediately:
            try:
                self.run_once()
            except Exception:
                logger.exception(
                    "Initial inventory synchronization failed"
                )

        if not self._scheduler.running:
            self._scheduler.start()

        logger.info(
            "Inventory synchronization scheduler started",
            extra={
                "interval_seconds": self._interval_seconds,
            },
        )

    def stop(
        self,
        wait: bool = True,
    ) -> None:
        """
        Stop the background scheduler.

        Parameters
        ----------
        wait:
            Wait for currently executing jobs to complete.
        """

        if self._scheduler.running:
            self._scheduler.shutdown(
                wait=wait
            )

        logger.info(
            "Inventory synchronization scheduler stopped"
        )