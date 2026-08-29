from __future__ import annotations

import unittest
from datetime import UTC, datetime
from pathlib import Path

from ndca.api.nfmp_xml_client import NFMPXmlClient
from ndca.mappers.nfmp_interface_historical_mapper import (
    NFMPInterfaceHistoricalMapper,
)
from ndca.models.dto.performance_record import PerformanceRecord

_FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
_INTERFACE_ADDITIONAL_HISTORICAL_FIXTURE = (
    _FIXTURE_DIR / "nfmp_interface_additional_stats_logrecord_24_4.xml"
)


class TestNFMPInterfaceHistoricalMapper(unittest.TestCase):
    """D.1.3 historical Interface Additional normalization contract."""

    def _load_fixture_record(self) -> dict[str, object]:
        xml = _INTERFACE_ADDITIONAL_HISTORICAL_FIXTURE.read_text(
            encoding="utf-8"
        )

        records = NFMPXmlClient.parse_interface_additional_historical_response(
            xml
        )

        self.assertEqual(len(records), 1)
        return records[0]

    def test_maps_verified_received_broadcast_metric(self) -> None:
        raw_record = self._load_fixture_record()

        records = NFMPInterfaceHistoricalMapper.map_record(
            raw_record,
            sync_id="sync-d1-3",
            collection_time=datetime(
                2026,
                8,
                29,
                12,
                0,
                tzinfo=UTC,
            ),
        )

        self.assertEqual(len(records), 1)

        record = records[0]

        self.assertIsInstance(record, PerformanceRecord)
        self.assertEqual(
            record.metric,
            "interface.received_broadcast_packets",
        )
        self.assertEqual(
            record.metric_source_name,
            "receivedBroadcastPackets",
        )
        self.assertEqual(record.value, 400)

    def test_maps_historical_record_metadata(self) -> None:
        raw_record = self._load_fixture_record()

        collection_time = datetime(
            2026,
            8,
            29,
            12,
            0,
            tzinfo=UTC,
        )

        records = NFMPInterfaceHistoricalMapper.map_record(
            raw_record,
            sync_id="sync-d1-3",
            collection_time=collection_time,
        )

        record = records[0]

        self.assertEqual(record.sync_id, "sync-d1-3")
        self.assertEqual(record.source, "NFM-P")
        self.assertEqual(
            record.xml_class,
            "equipment.InterfaceAdditionalStatsLogRecord",
        )
        self.assertEqual(
            record.category,
            "Interface / Network Port",
        )
        self.assertEqual(
            record.object_id,
            "network:example:port-3",
        )
        self.assertEqual(
            record.object_name,
            "port-3",
        )
        self.assertTrue(record.is_historical)
        self.assertEqual(record.collection_time, collection_time)
        self.assertEqual(record.evidence_status, "VERIFIED")

    def test_converts_time_captured_to_utc_source_time(self) -> None:
        raw_record = self._load_fixture_record()

        records = NFMPInterfaceHistoricalMapper.map_record(
            raw_record,
            sync_id="sync-d1-3",
            collection_time=datetime(
                2026,
                8,
                29,
                12,
                0,
                tzinfo=UTC,
            ),
        )

        record = records[0]

        self.assertEqual(
            record.source_time,
            datetime.fromtimestamp(
                1127878285113 / 1000,
                tz=UTC,
            ),
        )
        self.assertIsNotNone(record.source_time)
        self.assertEqual(
            record.source_time.tzinfo,
            UTC,
        )

    def test_preserves_complete_raw_payload(self) -> None:
        raw_record = self._load_fixture_record()

        records = NFMPInterfaceHistoricalMapper.map_record(
            raw_record,
            sync_id="sync-d1-3",
            collection_time=datetime(
                2026,
                8,
                29,
                12,
                0,
                tzinfo=UTC,
            ),
        )

        record = records[0]

        self.assertIsNotNone(record.raw_payload)
        self.assertEqual(record.raw_payload, raw_record)

        self.assertEqual(
            record.raw_payload["receivedBroadcastPacketsPeriodic"],
            "4",
        )
        self.assertEqual(
            record.raw_payload["transmittedBroadcastPackets"],
            "600",
        )

    def test_periodic_counter_is_not_normalized(self) -> None:
        raw_record = self._load_fixture_record()

        records = NFMPInterfaceHistoricalMapper.map_record(
            raw_record,
            sync_id="sync-d1-3",
            collection_time=datetime(
                2026,
                8,
                29,
                12,
                0,
                tzinfo=UTC,
            ),
        )

        metrics = {record.metric for record in records}

        self.assertIn(
            "interface.received_broadcast_packets",
            metrics,
        )
        self.assertNotIn(
            "interface.received_broadcast_packets_periodic",
            metrics,
        )

    def test_requires_object_pointer(self) -> None:
        raw_record = {
            "timeCaptured": "1127878285113",
            "receivedBroadcastPackets": "400",
        }

        with self.assertRaises(ValueError):
            NFMPInterfaceHistoricalMapper.map_record(
                raw_record,
                sync_id="sync-d1-3",
                collection_time=datetime.now(UTC),
            )

    def test_requires_time_captured(self) -> None:
        raw_record = {
            "monitoredObjectPointer": "network:example:port-3",
            "receivedBroadcastPackets": "400",
        }

        with self.assertRaises(ValueError):
            NFMPInterfaceHistoricalMapper.map_record(
                raw_record,
                sync_id="sync-d1-3",
                collection_time=datetime.now(UTC),
            )

    def test_requires_verified_metric_source(self) -> None:
        raw_record = {
            "monitoredObjectPointer": "network:example:port-3",
            "timeCaptured": "1127878285113",
        }

        with self.assertRaises(ValueError):
            NFMPInterfaceHistoricalMapper.map_record(
                raw_record,
                sync_id="sync-d1-3",
                collection_time=datetime.now(UTC),
            )

    def test_rejects_unverified_metric_source(self) -> None:
        raw_record = {
            "monitoredObjectPointer": "network:example:port-3",
            "timeCaptured": "1127878285113",
            "receivedBroadcastPackets": "400",
            "unverifiedMetric": "999",
        }

        records = NFMPInterfaceHistoricalMapper.map_record(
            raw_record,
            sync_id="sync-d1-3",
            collection_time=datetime.now(UTC),
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(
            records[0].metric,
            "interface.received_broadcast_packets",
        )
        self.assertNotEqual(
            records[0].metric_source_name,
            "unverifiedMetric",
        )

    def test_maps_multiple_historical_records(self) -> None:
        raw_records = [
            {
                "monitoredObjectPointer": "network:example:port-1",
                "displayedName": "port-1",
                "timeCaptured": "1127878285000",
                "receivedBroadcastPackets": "10",
            },
            {
                "monitoredObjectPointer": "network:example:port-2",
                "displayedName": "port-2",
                "timeCaptured": "1127878286000",
                "receivedBroadcastPackets": "20",
            },
        ]

        records = NFMPInterfaceHistoricalMapper.map_records(
            raw_records,
            sync_id="sync-d1-3",
            collection_time=datetime(
                2026,
                8,
                29,
                12,
                0,
                tzinfo=UTC,
            ),
        )

        self.assertEqual(len(records), 2)

        self.assertEqual(
            records[0].object_id,
            "network:example:port-1",
        )
        self.assertEqual(records[0].value, 10)

        self.assertEqual(
            records[1].object_id,
            "network:example:port-2",
        )
        self.assertEqual(records[1].value, 20)

        self.assertTrue(records[0].is_historical)
        self.assertTrue(records[1].is_historical)


if __name__ == "__main__":
    unittest.main()
