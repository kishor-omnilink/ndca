from __future__ import annotations

import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

from ndca.api.nfmp_xml_client import NFMPXmlClient
from ndca.collectors.performance.nfmp_performance_collector import (
    NFMPPerformanceCollector,
)
from ndca.models.dto.performance_record import PerformanceRecord


_FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
_INTERFACE_ADDITIONAL_HISTORICAL_FIXTURE = (
    _FIXTURE_DIR / "nfmp_interface_additional_stats_logrecord_24_4.xml"
)


class TestNFMPPerformanceCollectorSkeleton(unittest.TestCase):

    def test_performance_record_dto_fields(self) -> None:
        now = datetime.now(timezone.utc)
        pr = PerformanceRecord(
            sync_id="s-1",
            source="NFM-P",
            xml_class="equipment.InterfaceStats",
            category="Interface / Network Port",
            object_id="ne1:if1",
            object_name="if1",
            metric="received_octets",
            metric_source_name="Received Octets",
            value=1234,
            collection_time=now,
            source_time=now,
        )

        self.assertEqual(pr.source, "NFM-P")
        self.assertEqual(pr.metric, "received_octets")
        self.assertEqual(pr.collection_time.tzinfo, timezone.utc)

    def test_collect_entry_point(self) -> None:
        client = MagicMock(spec=NFMPXmlClient)
        client.trigger_collect.return_value = [
            {
                "metric": "received_octets",
                "value": 1000,
                "object_id": "ne1:if1",
                "object_name": "if1",
                "category": "Interface / Network Port",
                "xml_class": "equipment.InterfaceStats",
            }
        ]

        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={"equipment.InterfaceStats"},
        )

        records = collector.collect(
            ["equipment.InterfaceStats"],
            ["ne1"],
            sync_id="s-2",
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(
            records[0].xml_class,
            "equipment.InterfaceStats",
        )

    def test_collector_rejects_unverified_class(self) -> None:
        client = MagicMock(spec=NFMPXmlClient)

        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={"equipment.InterfaceStats"},
        )

        with self.assertRaises(ValueError):
            collector.collect_current(
                ["unverified.Class"],
                ["ne1"],
                sync_id="s-3",
            )

    def test_collector_calls_client_and_normalizes(self) -> None:
        sample = [
            {
                "metric": "received_octets",
                "value": 1000,
                "object_id": "ne1:if1",
                "object_name": "if1",
                "source_time": "2024-01-01T12:00:00+02:00",
                "category": "Interface / Network Port",
                "xml_class": "equipment.InterfaceStats",
            }
        ]

        client = MagicMock(spec=NFMPXmlClient)
        client.trigger_collect.return_value = sample

        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={"equipment.InterfaceStats"},
        )

        records = collector.collect_current(
            ["equipment.InterfaceStats"],
            ["ne1:if1"],
            sync_id="s-4",
        )

        self.assertIsInstance(records, list)
        self.assertTrue(records)
        self.assertIsInstance(records[0], PerformanceRecord)
        self.assertEqual(records[0].metric, "received_octets")
        self.assertEqual(
            records[0].collection_time.tzinfo,
            timezone.utc,
        )
        self.assertEqual(
            records[0].source_time,
            datetime(
                2024,
                1,
                1,
                10,
                0,
                tzinfo=timezone.utc,
            ),
        )

    def test_naive_source_time_is_assumed_utc(self) -> None:
        client = MagicMock(spec=NFMPXmlClient)
        client.trigger_collect.return_value = [
            {
                "metric": "received_octets",
                "value": 500,
                "object_id": "ne1:if1",
                "object_name": "if1",
                "source_time": "2024-01-01T12:00:00",
                "category": "Interface / Network Port",
                "xml_class": "equipment.InterfaceStats",
            }
        ]

        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={"equipment.InterfaceStats"},
        )

        records = collector.collect_current(
            ["equipment.InterfaceStats"],
            ["ne1:if1"],
            sync_id="s-5",
        )

        self.assertEqual(
            records[0].source_time,
            datetime(
                2024,
                1,
                1,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )
        self.assertEqual(
            records[0].source_time.tzinfo,
            timezone.utc,
        )

    def test_injected_verified_classes_are_used(self) -> None:
        client = MagicMock(spec=NFMPXmlClient)
        client.trigger_collect.return_value = [
            {
                "metric": "received_octets",
                "value": 777,
                "object_id": "ne1:if1",
                "object_name": "if1",
                "category": "Interface / Network Port",
                "xml_class": "equipment.InterfaceStats",
            }
        ]

        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={"equipment.InterfaceStats"},
        )

        self.assertIn(
            "equipment.InterfaceStats",
            collector.verified_classes,
        )

        records = collector.collect_current(
            ["equipment.InterfaceStats"],
            ["ne1:if1"],
            sync_id="s-6",
        )

        self.assertEqual(records[0].value, 777)

    def test_correct_per_record_xml_class_when_present(self) -> None:
        client = MagicMock(spec=NFMPXmlClient)
        client.trigger_collect.return_value = [
            {
                "metric": "received_octets",
                "value": 42,
                "object_id": "ne1:if1",
                "object_name": "if1",
                "category": "Interface / Network Port",
                "xml_class": "equipment.InterfaceStats",
            }
        ]

        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={"equipment.InterfaceStats"},
        )

        records = collector.collect_current(
            ["equipment.InterfaceStats"],
            ["ne1:if1"],
            sync_id="s-7",
        )

        self.assertEqual(
            records[0].xml_class,
            "equipment.InterfaceStats",
        )

    def test_response_xml_class_must_be_verified(self) -> None:
        client = MagicMock(spec=NFMPXmlClient)
        client.trigger_collect.return_value = [
            {
                "metric": "received_octets",
                "value": 42,
                "object_id": "ne1:if1",
                "object_name": "if1",
                "category": "Interface / Network Port",
                "xml_class": "unknown.UnverifiedClass",
            }
        ]

        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={"equipment.InterfaceStats"},
        )

        with self.assertRaises(ValueError):
            collector.collect_current(
                ["equipment.InterfaceStats"],
                ["ne1:if1"],
                sync_id="s-8",
            )

    def test_ambiguous_multi_class_response_without_xml_class_keeps_none(
        self,
    ) -> None:
        client = MagicMock(spec=NFMPXmlClient)
        client.trigger_collect.return_value = [
            {
                "metric": "received_octets",
                "value": 99,
                "object_id": "ne1:if1",
                "object_name": "if1",
                "category": "Interface / Network Port",
            }
        ]

        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={
                "equipment.InterfaceStats",
                "equipment.InterfaceAdditionalStats",
            },
        )

        records = collector.collect_current(
            [
                "equipment.InterfaceStats",
                "equipment.InterfaceAdditionalStats",
            ],
            ["ne1:if1"],
            sync_id="s-9",
        )

        self.assertIsNone(records[0].xml_class)

    def test_trigger_collect_request_contains_documented_operation(
        self,
    ) -> None:
        request = NFMPXmlClient.build_trigger_collect_request(
            ["ne1"],
            [
                "equipment.InterfaceStats",
                "equipment.InterfaceAdditionalStats",
            ],
        )

        self.assertIn(
            "generic.GenericObject.triggerCollect",
            request,
        )
        self.assertIn(
            "<instanceNames>",
            request,
        )
        self.assertIn(
            "<currentDataClasses>",
            request,
        )
        self.assertIn(
            "equipment.InterfaceStats",
            request,
        )
        self.assertIn(
            "equipment.InterfaceAdditionalStats",
            request,
        )

    def test_find_to_file_request_contains_documented_operation(
        self,
    ) -> None:
        request = NFMPXmlClient.build_find_to_file_request(
            {
                "full_class_name": "example.VerifiedHistoricalClass",
                "monitored_object_pointer": "network:example:port-3",
                "time_captured": {
                    "first": "1127142900000",
                    "second": "1127143800000",
                },
                "file_name": "historical.xml",
            }
        )

        self.assertIn(
            '<findToFile xmlns="xmlapi_1.0">',
            request,
        )
        self.assertIn(
            "<fullClassName>example.VerifiedHistoricalClass</fullClassName>",
            request,
        )
        self.assertIn(
            '<equal name="monitoredObjectPointer" '
            'value="network:example:port-3"/>',
            request,
        )
        self.assertIn(
            '<between name="timeCaptured" '
            'first="1127142900000" second="1127143800000"/>',
            request,
        )
        self.assertIn(
            "<fileName>historical.xml</fileName>",
            request,
        )

    def test_find_to_file_request_requires_historical_query_fields(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            NFMPXmlClient.build_find_to_file_request({})

        with self.assertRaises(ValueError):
            NFMPXmlClient.build_find_to_file_request(
                {
                    "full_class_name": "example.VerifiedHistoricalClass",
                    "monitored_object_pointer": "network:example:port-3",
                    "time_captured": {
                        "first": "1127142900000",
                    },
                    "file_name": "historical.xml",
                }
            )

        with self.assertRaises(ValueError):
            NFMPXmlClient.build_find_to_file_request(
                {
                    "full_class_name": "example.VerifiedHistoricalClass",
                    "monitored_object_pointer": "network:example:port-3",
                    "time_captured": {
                        "first": "1127142900000",
                        "second": "1127143800000",
                    },
                }
            )

    def test_find_to_file_request_escapes_xml_values(self) -> None:
        request = NFMPXmlClient.build_find_to_file_request(
            {
                "full_class_name": "example.Class<Name>",
                "monitored_object_pointer": "network:a&b:port-3",
                "time_captured": {
                    "first": "1127142900000",
                    "second": "1127143800000",
                },
                "file_name": "historical&data.xml",
            }
        )

        self.assertIn(
            "<fullClassName>example.Class&lt;Name&gt;</fullClassName>",
            request,
        )
        self.assertIn(
            '<equal name="monitoredObjectPointer" '
            'value="network:a&amp;b:port-3"/>',
            request,
        )
        self.assertIn(
            "<fileName>historical&amp;data.xml</fileName>",
            request,
        )

    def test_parse_trigger_collect_response(self) -> None:
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<root>\n"
            "  <record>\n"
            "    <xmlClass>equipment.InterfaceStats</xmlClass>\n"
            "    <metric>received_octets</metric>\n"
            "    <value>123</value>\n"
            "    <objectId>ne1:if1</objectId>\n"
            "    <sourceTime>2024-01-01T12:00:00+00:00</sourceTime>\n"
            "  </record>\n"
            "</root>"
        )

        parsed = NFMPXmlClient.parse_trigger_collect_response(xml)

        self.assertEqual(
            parsed[0]["xml_class"],
            "equipment.InterfaceStats",
        )
        self.assertEqual(
            parsed[0]["metric"],
            "received_octets",
        )
        self.assertEqual(
            parsed[0]["value"],
            "123",
        )

    def test_malformed_xml_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            NFMPXmlClient.parse_trigger_collect_response("<broken>")

    def test_empty_response_is_handled_without_inventory_assumption(
        self,
    ) -> None:
        client = MagicMock(spec=NFMPXmlClient)
        client.trigger_collect.return_value = []

        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={"equipment.InterfaceStats"},
        )

        records = collector.collect_current(
            ["equipment.InterfaceStats"],
            ["ne1"],
            sync_id="s-10",
        )

        self.assertEqual(records, [])

    # ------------------------------------------------------------------
    # SYNC-012-D.1.2 — Historical Interface Additional parser tests
    # ------------------------------------------------------------------

    def test_parse_interface_additional_historical_response(self) -> None:
        xml = _INTERFACE_ADDITIONAL_HISTORICAL_FIXTURE.read_text(
            encoding="utf-8"
        )

        records = (
            NFMPXmlClient.parse_interface_additional_historical_response(
                xml
            )
        )

        self.assertEqual(len(records), 1)

        record = records[0]

        self.assertEqual(
            record["xml_class"],
            "equipment.InterfaceAdditionalStatsLogRecord",
        )
        self.assertEqual(
            record["monitoredObjectPointer"],
            "network:example:port-3",
        )
        self.assertEqual(
            record["displayedName"],
            "port-3",
        )
        self.assertEqual(
            record["timeCaptured"],
            "1127878285113",
        )
        self.assertEqual(
            record["periodicTime"],
            "938610",
        )
        self.assertEqual(
            record["suspect"],
            "false",
        )

    def test_historical_parser_preserves_exact_nokia_metric_names(
        self,
    ) -> None:
        xml = _INTERFACE_ADDITIONAL_HISTORICAL_FIXTURE.read_text(
            encoding="utf-8"
        )

        records = NFMPXmlClient.parse_interface_additional_historical_response(
            xml
        )

        record = records[0]

        expected_metrics = {
            "receivedTotalOctets": "100000",
            "receivedTotalOctetsPeriodic": "1000",
            "receivedUnicastPackets": "2000",
            "receivedUnicastPacketsPeriodic": "20",
            "receivedMulticastPackets": "300",
            "receivedMulticastPacketsPeriodic": "3",
            "receivedBroadcastPackets": "400",
            "receivedBroadcastPacketsPeriodic": "4",
            "transmittedTotalOctets": "200000",
            "transmittedTotalOctetsPeriodic": "2000",
            "transmittedUnicastPackets": "4000",
            "transmittedUnicastPacketsPeriodic": "40",
            "transmittedMulticastPackets": "500",
            "transmittedMulticastPacketsPeriodic": "5",
            "transmittedBroadcastPackets": "600",
            "transmittedBroadcastPacketsPeriodic": "6",
        }

        for source_name, expected_value in expected_metrics.items():
            self.assertIn(source_name, record)
            self.assertEqual(
                record[source_name],
                expected_value,
            )

    def test_historical_parser_preserves_metadata_fields(self) -> None:
        xml = _INTERFACE_ADDITIONAL_HISTORICAL_FIXTURE.read_text(
            encoding="utf-8"
        )

        records = NFMPXmlClient.parse_interface_additional_historical_response(
            xml
        )

        record = records[0]

        self.assertEqual(
            record["monitoredObjectClass"],
            "equipment.Interface",
        )
        self.assertEqual(
            record["monitoredObjectSiteId"],
            "site-1",
        )
        self.assertEqual(
            record["monitoredObjectSiteName"],
            "Example Site",
        )
        self.assertEqual(
            record["objectFullName"],
            "network:example:port-3",
        )
        self.assertEqual(
            record["recordId"],
            "1001",
        )
        self.assertEqual(
            record["bucketId"],
            "1",
        )
        self.assertEqual(
            record["deploymentState"],
            "DEPLOYED",
        )

    def test_historical_parser_supports_multiple_records(self) -> None:
        xml = """
        <findToFileResponse xmlns="xmlapi_1.0">
          <equipment.InterfaceAdditionalStatsLogRecord>
            <monitoredObjectPointer>network:example:port-1</monitoredObjectPointer>
            <timeCaptured>1127878285000</timeCaptured>
            <receivedBroadcastPackets>10</receivedBroadcastPackets>
          </equipment.InterfaceAdditionalStatsLogRecord>
          <equipment.InterfaceAdditionalStatsLogRecord>
            <monitoredObjectPointer>network:example:port-2</monitoredObjectPointer>
            <timeCaptured>1127878286000</timeCaptured>
            <receivedBroadcastPackets>20</receivedBroadcastPackets>
          </equipment.InterfaceAdditionalStatsLogRecord>
        </findToFileResponse>
        """

        records = NFMPXmlClient.parse_interface_additional_historical_response(
            xml
        )

        self.assertEqual(len(records), 2)
        self.assertEqual(
            records[0]["monitoredObjectPointer"],
            "network:example:port-1",
        )
        self.assertEqual(
            records[1]["monitoredObjectPointer"],
            "network:example:port-2",
        )
        self.assertEqual(
            records[0]["receivedBroadcastPackets"],
            "10",
        )
        self.assertEqual(
            records[1]["receivedBroadcastPackets"],
            "20",
        )

    def test_historical_parser_requires_object_pointer(self) -> None:
        xml = """
        <findToFileResponse xmlns="xmlapi_1.0">
          <equipment.InterfaceAdditionalStatsLogRecord>
            <timeCaptured>1127878285113</timeCaptured>
            <receivedBroadcastPackets>10</receivedBroadcastPackets>
          </equipment.InterfaceAdditionalStatsLogRecord>
        </findToFileResponse>
        """

        with self.assertRaises(ValueError):
            NFMPXmlClient.parse_interface_additional_historical_response(
                xml
            )

    def test_historical_parser_requires_time_captured(self) -> None:
        xml = """
        <findToFileResponse xmlns="xmlapi_1.0">
          <equipment.InterfaceAdditionalStatsLogRecord>
            <monitoredObjectPointer>network:example:port-3</monitoredObjectPointer>
            <receivedBroadcastPackets>10</receivedBroadcastPackets>
          </equipment.InterfaceAdditionalStatsLogRecord>
        </findToFileResponse>
        """

        with self.assertRaises(ValueError):
            NFMPXmlClient.parse_interface_additional_historical_response(
                xml
            )

    def test_historical_parser_rejects_malformed_xml(self) -> None:
        with self.assertRaises(ValueError):
            NFMPXmlClient.parse_interface_additional_historical_response(
                "<findToFileResponse>"
            )

    def test_historical_parser_rejects_empty_xml(self) -> None:
        with self.assertRaises(ValueError):
            NFMPXmlClient.parse_interface_additional_historical_response(
                ""
            )

    def test_find_to_file_supports_interface_additional_historical_class(
        self,
    ) -> None:
        response_xml = (
            "<findToFileResponse xmlns=\"xmlapi_1.0\">"
            "<equipment.InterfaceAdditionalStatsLogRecord>"
            "<monitoredObjectPointer>network:example:port-3"
            "</monitoredObjectPointer>"
            "<timeCaptured>1127878285113</timeCaptured>"
            "</equipment.InterfaceAdditionalStatsLogRecord>"
            "</findToFileResponse>"
        )

        transport = MagicMock(return_value=response_xml)

        client = NFMPXmlClient(
            transport=transport,
        )

        query = {
            "full_class_name": (
                "equipment.InterfaceAdditionalStatsLogRecord"
            ),
            "monitored_object_pointer": "network:example:port-3",
            "time_captured": {
                "first": "1127878285000",
                "second": "1127878286000",
            },
            "file_name": "InterfaceAdditionalStatsLogRecord.xml",
        }

        result = client.find_to_file(query)

        self.assertEqual(
            result["operation"],
            "findToFile",
        )
        self.assertEqual(
            result["full_class_name"],
            "equipment.InterfaceAdditionalStatsLogRecord",
        )
        self.assertIn(
            "equipment.InterfaceAdditionalStatsLogRecord",
            result["request_xml"],
        )
        self.assertIn(
            "network:example:port-3",
            result["request_xml"],
        )
        self.assertIn(
            "InterfaceAdditionalStatsLogRecord.xml",
            result["request_xml"],
        )

        transport.assert_called_once_with(
            result["request_xml"]
        )

    def test_find_to_file_result_filter_is_optional(self) -> None:
        request = NFMPXmlClient.build_find_to_file_request(
            {
                "full_class_name": (
                    "equipment.InterfaceAdditionalStatsLogRecord"
                ),
                "monitored_object_pointer": "network:example:port-3",
                "time_captured": {
                    "first": "1127142900000",
                    "second": "1127143800000",
                },
                "result_filter": [
                    "receivedBroadcastPackets",
                    "receivedBroadcastPacketsPeriodic",
                ],
                "file_name": "historical.xml",
            }
        )

        self.assertIn(
            "<resultFilter>",
            request,
        )
        self.assertIn(
            "<attribute>receivedBroadcastPackets</attribute>",
            request,
        )
        self.assertIn(
            "<attribute>receivedBroadcastPacketsPeriodic</attribute>",
            request,
        )


if __name__ == "__main__":
    unittest.main()