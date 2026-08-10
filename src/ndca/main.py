"""
NDCA application entry point.

SYNC-007 - Application Runtime Integration.

Starts the inventory synchronization scheduler and keeps the
application process alive until SIGINT or SIGTERM is received.
"""

from __future__ import annotations

import logging
import signal
import threading
from collections.abc import Callable
from types import FrameType

from ndca.scheduler.inventory_sync_scheduler import (
    InventorySyncScheduler,
)

logger = logging.getLogger(__name__)


def run(
    scheduler: InventorySyncScheduler | None = None,
    stop_event: threading.Event | None = None,
) -> None:
    """
    Run the NDCA application lifecycle.

    Parameters
    ----------
    scheduler:
        Optional scheduler instance. Primarily used for testing.
    stop_event:
        Optional event used to terminate the application.
        Primarily used for testing.
    """

    application_scheduler = (
        scheduler
        if scheduler is not None
        else InventorySyncScheduler()
    )

    application_stop_event = (
        stop_event
        if stop_event is not None
        else threading.Event()
    )

    logger.info("NDCA application starting")

    try:
        application_scheduler.start(
            run_immediately=True,
        )

        logger.info(
            "NDCA application started",
            extra={
                "collection_interval_seconds": (
                    application_scheduler.interval_seconds
                ),
            },
        )

        application_stop_event.wait()

    finally:
        logger.info("NDCA application stopping")

        application_scheduler.stop()

        logger.info("NDCA application stopped")


def main() -> None:
    """Start the NDCA application."""

    stop_event = threading.Event()

    def handle_signal(
        signum: int,
        frame: FrameType | None,
    ) -> None:
        """Request graceful application shutdown."""

        del frame

        logger.info(
            "Shutdown signal received",
            extra={
                "signal": signum,
            },
        )

        stop_event.set()

    previous_sigint_handler: Callable[
        [int, FrameType | None],
        object,
    ] = signal.getsignal(signal.SIGINT)

    previous_sigterm_handler: Callable[
        [int, FrameType | None],
        object,
    ] = signal.getsignal(signal.SIGTERM)

    signal.signal(
        signal.SIGINT,
        handle_signal,
    )

    signal.signal(
        signal.SIGTERM,
        handle_signal,
    )

    try:
        run(
            stop_event=stop_event,
        )

    except KeyboardInterrupt:
        logger.info(
            "Keyboard interrupt received"
        )

    finally:
        signal.signal(
            signal.SIGINT,
            previous_sigint_handler,
        )

        signal.signal(
            signal.SIGTERM,
            previous_sigterm_handler,
        )


if __name__ == "__main__":
    main()
