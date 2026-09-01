from unittest.mock import Mock

from ndca.services.performance_collection_service import (
    PerformanceCollectionService,
)


def test_collect_and_persist_passes_collector_records_to_persistence() -> None:
    collector = Mock()
    persistence = Mock()

    records = [Mock(), Mock()]
    collector.collect.return_value = records
    persistence.persist.return_value = 2

    service = PerformanceCollectionService(
        collector,
        persistence,
        instance_names=["ne-1", "ne-2"],
        current_data_classes=[
            "equipment.InterfaceStats",
            "equipment.InterfaceAdditionalStats",
        ],
    )

    result = service.collect_and_persist(sync_id="sync-test-1")

    assert result == 2

    collector.collect.assert_called_once_with(
        (
            "equipment.InterfaceStats",
            "equipment.InterfaceAdditionalStats",
        ),
        ("ne-1", "ne-2"),
        "sync-test-1",
    )
    persistence.persist.assert_called_once_with(records)


def test_empty_targets_skip_collection() -> None:
    collector = Mock()
    persistence = Mock()

    service = PerformanceCollectionService(
        collector,
        persistence,
        instance_names=[],
        current_data_classes=["equipment.InterfaceStats"],
    )

    assert service.collect_and_persist(sync_id="sync-test-2") == 0

    collector.collect.assert_not_called()
    persistence.persist.assert_not_called()


def test_empty_classes_skip_collection() -> None:
    collector = Mock()
    persistence = Mock()

    service = PerformanceCollectionService(
        collector,
        persistence,
        instance_names=["ne-1"],
        current_data_classes=[],
    )

    assert service.collect_and_persist(sync_id="sync-test-3") == 0

    collector.collect.assert_not_called()
    persistence.persist.assert_not_called()


def test_empty_collector_result_does_not_persist() -> None:
    collector = Mock()
    persistence = Mock()

    collector.collect.return_value = []

    service = PerformanceCollectionService(
        collector,
        persistence,
        instance_names=["ne-1"],
        current_data_classes=["equipment.InterfaceStats"],
    )

    assert service.collect_and_persist(sync_id="sync-test-4") == 0

    persistence.persist.assert_not_called()
