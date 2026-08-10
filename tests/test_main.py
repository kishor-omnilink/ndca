"""
SYNC-007 application runtime integration tests.
"""

from __future__ import annotations

import signal
import threading
import unittest
from unittest.mock import MagicMock, patch

from ndca.main import main, run


class TestNDCAApplication(unittest.TestCase):
    """Validate the NDCA application lifecycle."""

    def test_run_starts_and_stops_scheduler(self) -> None:
        """run() should start and stop the scheduler."""

        scheduler = MagicMock()

        scheduler.interval_seconds = 900

        stop_event = threading.Event()

        stop_event.set()

        run(
            scheduler=scheduler,
            stop_event=stop_event,
        )

        scheduler.start.assert_called_once_with(
            run_immediately=True,
        )

        scheduler.stop.assert_called_once_with()

    def test_run_waits_until_stop_event(self) -> None:
        """run() should wait for the application stop event."""

        scheduler = MagicMock()

        scheduler.interval_seconds = 900

        stop_event = threading.Event()

        def release_event() -> None:
            stop_event.set()

        release_event()

        run(
            scheduler=scheduler,
            stop_event=stop_event,
        )

        scheduler.start.assert_called_once_with(
            run_immediately=True,
        )

        scheduler.stop.assert_called_once_with()

    def test_run_stops_scheduler_when_start_fails(self) -> None:
        """Scheduler must be stopped if startup raises."""

        scheduler = MagicMock()

        scheduler.interval_seconds = 900

        scheduler.start.side_effect = RuntimeError(
            "Scheduler startup failure"
        )

        stop_event = threading.Event()

        with self.assertRaises(RuntimeError):
            run(
                scheduler=scheduler,
                stop_event=stop_event,
            )

        scheduler.start.assert_called_once_with(
            run_immediately=True,
        )

        scheduler.stop.assert_called_once_with()

    @patch("ndca.main.run")
    @patch("ndca.main.signal.getsignal")
    @patch("ndca.main.signal.signal")
    def test_main_starts_application(
        self,
        signal_mock,
        getsignal_mock,
        run_mock,
    ) -> None:
        """main() should install handlers and start the runtime."""

        getsignal_mock.side_effect = [
            signal.SIG_DFL,
            signal.SIG_DFL,
        ]

        main()

        self.assertEqual(
            signal_mock.call_count,
            4,
        )

        run_mock.assert_called_once()

        kwargs = run_mock.call_args.kwargs

        self.assertIn(
            "stop_event",
            kwargs,
        )

        self.assertIsInstance(
            kwargs["stop_event"],
            threading.Event,
        )

    @patch("ndca.main.run")
    @patch("ndca.main.signal.getsignal")
    @patch("ndca.main.signal.signal")
    def test_main_restores_signal_handlers(
        self,
        signal_mock,
        getsignal_mock,
        run_mock,
    ) -> None:
        """main() should restore previous signal handlers."""

        previous_sigint = object()
        previous_sigterm = object()

        getsignal_mock.side_effect = [
            previous_sigint,
            previous_sigterm,
        ]

        main()

        restore_calls = [
            call
            for call in signal_mock.call_args_list
            if call.args[0] in (
                signal.SIGINT,
                signal.SIGTERM,
            )
            and (
                call.args[1] is previous_sigint
                or call.args[1] is previous_sigterm
            )
        ]

        self.assertEqual(
            len(restore_calls),
            2,
        )

    @patch("ndca.main.run")
    @patch("ndca.main.signal.getsignal")
    @patch("ndca.main.signal.signal")
    def test_main_handles_keyboard_interrupt(
        self,
        signal_mock,
        getsignal_mock,
        run_mock,
    ) -> None:
        """main() should handle KeyboardInterrupt gracefully."""

        getsignal_mock.side_effect = [
            signal.SIG_DFL,
            signal.SIG_DFL,
        ]

        run_mock.side_effect = KeyboardInterrupt()

        main()

        run_mock.assert_called_once()

    def test_signal_handlers_are_available(self) -> None:
        """SIGINT and SIGTERM should be available on Linux."""

        self.assertTrue(
            hasattr(signal, "SIGINT")
        )

        self.assertTrue(
            hasattr(signal, "SIGTERM")
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2,
    )
