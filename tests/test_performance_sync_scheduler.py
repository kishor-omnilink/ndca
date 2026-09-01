from unittest.mock import Mock

from ndca.scheduler.performance_sync_scheduler import (
    PerformanceSyncScheduler,
)


def test_run_once_skips_when_no_targets() -> None:
    session_factory = Mock()
    collector_factory = Mock()
    target_provider = Mock(return_value=[])

    scheduler = PerformanceSyncScheduler(
        session_factory=session_factory,
        target_provider=target_provider,
        collector_factory=collector_factory,
    )

    assert scheduler.run_once() == 0

    target_provider.assert_called_once_with()
    session_factory.assert_not_called()
    collector_factory.assert_not_called()


def test_run_once_collects_and_persists() -> None:
    session = Mock()
    collector = Mock()

    session_factory = Mock(return_value=session)
    collector_factory = Mock(return_value=collector)
    target_provider = Mock(return_value=["ne-1", "ne-2"])

    collector.collect.return_value = [Mock()]

    scheduler = PerformanceSyncScheduler(
        session_factory=session_factory,
        target_provider=target_provider,
        collector_factory=collector_factory,
    )

    # Avoid testing the database implementation here. Replace the
    # orchestration service at the boundary with a deterministic mock.
    from unittest.mock import patch

    with patch(
        "ndca.scheduler.performance_sync_scheduler.PerformanceCollectionService"
    ) as service_class:
        service = service_class.return_value
        service.collect_and_persist.return_value = 1

        result = scheduler.run_once()

    assert result == 1

    target_provider.assert_called_once_with()
    session_factory.assert_called_once_with()
    collector_factory.assert_called_once_with()

    service_class.assert_called_once()

    kwargs = service_class.call_args.kwargs

    assert kwargs["instance_names"] == ("ne-1", "ne-2")
    assert kwargs["current_data_classes"] == (
        "equipment.InterfaceStats",
        "equipment.InterfaceAdditionalStats",
    )

    service.collect_and_persist.assert_called_once()

    collector.close.assert_called_once_with()
    session.close.assert_called_once_with()


def test_run_once_closes_resources_when_collection_fails() -> None:
    session = Mock()
    collector = Mock()

    session_factory = Mock(return_value=session)
    collector_factory = Mock(return_value=collector)
    target_provider = Mock(return_value=["ne-1"])

    from unittest.mock import patch

    with patch(
        "ndca.scheduler.performance_sync_scheduler.PerformanceCollectionService"
    ) as service_class:
        service = service_class.return_value
        service.collect_and_persist.side_effect = RuntimeError(
            "collection failure"
        )

        scheduler = PerformanceSyncScheduler(
            session_factory=session_factory,
            target_provider=target_provider,
            collector_factory=collector_factory,
        )

        try:
            scheduler.run_once()
        except RuntimeError:
            pass
        else:
            raise AssertionError("RuntimeError was expected")

    collector.close.assert_called_once_with()
    session.close.assert_called_once_with()
