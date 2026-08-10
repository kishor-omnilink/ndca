"""
SYNC-006 scheduler unit tests.

Tests the APScheduler-based inventory synchronization scheduler.
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, PropertyMock, patch

from apscheduler.schedulers.background import BackgroundScheduler

from ndca.models.sync_result import SyncResult
from ndca.scheduler.inventory_sync_scheduler import (
    InventorySyncScheduler,
)


class TestInventorySyncScheduler(unittest.TestCase):
    """Validate InventorySyncScheduler behavior."""

    def setUp(self) -> None:
        """Create a scheduler with mocked database sessions."""

        self.session = MagicMock()

        self.session_factory = MagicMock(
            return_value=self.session,
        )

        self.scheduler = InventorySyncScheduler(
            interval_seconds=900,
            session_factory=self.session_factory,
        )

    def tearDown(self) -> None:
        """Clean up the APScheduler instance."""

        if self.scheduler.scheduler.running:
            self.scheduler.stop()

    def test_scheduler_uses_configured_interval(self) -> None:
        """Configured interval should be retained."""

        self.assertEqual(
            self.scheduler.interval_seconds,
            900,
        )

    def test_scheduler_rejects_invalid_interval(self) -> None:
        """Zero and negative intervals should be rejected."""

        with self.assertRaises(ValueError):
            InventorySyncScheduler(
                interval_seconds=0,
                session_factory=self.session_factory,
            )

        with self.assertRaises(ValueError):
            InventorySyncScheduler(
                interval_seconds=-1,
                session_factory=self.session_factory,
            )

    def test_scheduler_creates_interval_job(self) -> None:
        """APScheduler should contain the inventory synchronization job."""

        job = self.scheduler.scheduler.get_job(
            "inventory_synchronization",
        )

        self.assertIsNotNone(job)

        assert job is not None

        self.assertEqual(
            job.trigger.interval.total_seconds(),
            900,
        )

        self.assertEqual(
            job.max_instances,
            1,
        )

        self.assertTrue(
            job.coalesce,
        )

    @patch(
        "ndca.scheduler.inventory_sync_scheduler."
        "InventorySynchronizationService"
    )
    def test_run_once_executes_synchronization(
        self,
        service_class,
    ) -> None:
        """run_once() should execute one synchronization."""

        expected_result = SyncResult(
            sync_id="sync-006-001",
            total_discovered=5,
            created=2,
            updated=1,
            unchanged=1,
            deactivated=1,
            status="SUCCESS",
        )

        service = MagicMock()

        service.synchronize.return_value = expected_result
        service_class.return_value = service

        result = self.scheduler.run_once()

        self.assertIs(
            result,
            expected_result,
        )

        self.session_factory.assert_called_once()

        service_class.assert_called_once_with(
            self.session,
        )

        service.synchronize.assert_called_once()

        self.session.close.assert_called_once()

    @patch(
        "ndca.scheduler.inventory_sync_scheduler."
        "InventorySynchronizationService"
    )
    def test_run_once_closes_session_on_failure(
        self,
        service_class,
    ) -> None:
        """Session must close when synchronization fails."""

        service = MagicMock()

        service.synchronize.side_effect = RuntimeError(
            "Synchronization failure",
        )

        service_class.return_value = service

        with self.assertRaises(RuntimeError):
            self.scheduler.run_once()

        self.session.close.assert_called_once()

    @patch(
        "ndca.scheduler.inventory_sync_scheduler."
        "InventorySynchronizationService"
    )
    def test_start_runs_initial_synchronization(
        self,
        service_class,
    ) -> None:
        """
        start(run_immediately=True) should execute one
        synchronization before starting APScheduler.
        """

        expected_result = SyncResult(
            sync_id="sync-006-002",
            total_discovered=1,
            created=1,
            status="SUCCESS",
        )

        service = MagicMock()

        service.synchronize.return_value = expected_result
        service_class.return_value = service

        with patch.object(
            self.scheduler.scheduler,
            "start",
        ) as scheduler_start:

            self.scheduler.start(
                run_immediately=True,
            )

            service.synchronize.assert_called_once()

            scheduler_start.assert_called_once()

    @patch(
        "ndca.scheduler.inventory_sync_scheduler."
        "InventorySynchronizationService"
    )
    def test_start_without_immediate_run(
        self,
        service_class,
    ) -> None:
        """
        start(run_immediately=False) should only start
        APScheduler without executing synchronization.
        """

        service = MagicMock()

        service_class.return_value = service

        with patch.object(
            self.scheduler.scheduler,
            "start",
        ) as scheduler_start:

            self.scheduler.start(
                run_immediately=False,
            )

            service.synchronize.assert_not_called()

            scheduler_start.assert_called_once()

    def test_stop_shuts_down_running_scheduler(self) -> None:
        """stop() should shut down a running APScheduler."""

        with patch.object(
            BackgroundScheduler,
            "running",
            new_callable=PropertyMock,
            return_value=True,
        ):
            with patch.object(
                self.scheduler.scheduler,
                "shutdown",
            ) as shutdown:

                self.scheduler.stop(
                    wait=True,
                )

                shutdown.assert_called_once_with(
                    wait=True,
                )

    def test_stop_does_nothing_when_scheduler_is_not_running(
        self,
    ) -> None:
        """stop() should be safe when scheduler is stopped."""

        with patch.object(
            BackgroundScheduler,
            "running",
            new_callable=PropertyMock,
            return_value=False,
        ):
            with patch.object(
                self.scheduler.scheduler,
                "shutdown",
            ) as shutdown:

                self.scheduler.stop()

                shutdown.assert_not_called()

    @patch(
        "ndca.scheduler.inventory_sync_scheduler."
        "InventorySynchronizationService"
    )
    def test_start_continues_after_initial_failure(
        self,
        service_class,
    ) -> None:
        """
        A failed initial synchronization should not prevent
        APScheduler from starting.
        """

        service = MagicMock()

        service.synchronize.side_effect = RuntimeError(
            "Initial synchronization failure",
        )

        service_class.return_value = service

        with patch.object(
            self.scheduler.scheduler,
            "start",
        ) as scheduler_start:

            self.scheduler.start(
                run_immediately=True,
            )

            service.synchronize.assert_called_once()

            scheduler_start.assert_called_once()

    def test_periodic_job_targets_run_once(self) -> None:
        """The APScheduler job should target run_once()."""

        job = self.scheduler.scheduler.get_job(
            "inventory_synchronization",
        )

        self.assertIsNotNone(job)

        assert job is not None

        self.assertEqual(
            job.func,
            self.scheduler.run_once,
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2,
    )