from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from ndca.api.nfmp_xml_client import NFMPXmlClient
from ndca.collectors.performance.nfmp_performance_collector import NFMPPerformanceCollector
from ndca.models.dto.performance_record import PerformanceRecord


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
        client.trigger_collect.return_value = [{
            "metric": "received_octets",
            "value": 1000,
            "object_id": "ne1:if1",
            "object_name": "if1",
            "category": "Interface / Network Port",
            "xml_class": "equipment.InterfaceStats",
        }]

        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={"equipment.InterfaceStats"},
        )

        records = collector.collect(["equipment.InterfaceStats"], ["ne1"], sync_id="s-2")

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].xml_class, "equipment.InterfaceStats")

    def test_collector_rejects_unverified_class(self) -> None:
        client = MagicMock(spec=NFMPXmlClient)
        collector = NFMPPerformanceCollector(client=client, verified_classes={"equipment.InterfaceStats"})

        with self.assertRaises(ValueError):
            collector.collect_current(["unverified.Class"], ["ne1"], sync_id="s-3")

    def test_collector_calls_client_and_normalizes(self) -> None:
        sample = [{
            "metric": "received_octets",
            "value": 1000,
            "object_id": "ne1:if1",
            "object_name": "if1",
            "source_time": "2024-01-01T12:00:00+02:00",
            "category": "Interface / Network Port",
            "xml_class": "equipment.InterfaceStats",
        }]

        client = MagicMock(spec=NFMPXmlClient)
        client.trigger_collect.return_value = sample

        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={"equipment.InterfaceStats"},
        )

        records = collector.collect_current(["equipment.InterfaceStats"], ["ne1:if1"], sync_id="s-4")

        self.assertIsInstance(records, list)
        self.assertTrue(records)
        self.assertIsInstance(records[0], PerformanceRecord)
        self.assertEqual(records[0].metric, "received_octets")
        self.assertEqual(records[0].collection_time.tzinfo, timezone.utc)
        self.assertEqual(records[0].source_time, datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc))

    def test_naive_source_time_is_assumed_utc(self) -> None:
        client = MagicMock(spec=NFMPXmlClient)
        client.trigger_collect.return_value = [{
            "metric": "received_octets",
            "value": 500,
            "object_id": "ne1:if1",
            "object_name": "if1",
            "source_time": "2024-01-01T12:00:00",
            "category": "Interface / Network Port",
            "xml_class": "equipment.InterfaceStats",
        }]

        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={"equipment.InterfaceStats"},
        )

        records = collector.collect_current(["equipment.InterfaceStats"], ["ne1:if1"], sync_id="s-5")

        self.assertEqual(records[0].source_time, datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc))
        self.assertEqual(records[0].source_time.tzinfo, timezone.utc)

    def test_injected_verified_classes_are_used(self) -> None:
        client = MagicMock(spec=NFMPXmlClient)
        client.trigger_collect.return_value = [{
            "metric": "received_octets",
            "value": 777,
            "object_id": "ne1:if1",
            "object_name": "if1",
            "category": "Interface / Network Port",
            "xml_class": "equipment.InterfaceStats",
        }]

        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={"equipment.InterfaceStats"},
        )

        self.assertIn("equipment.InterfaceStats", collector.verified_classes)
        records = collector.collect_current(["equipment.InterfaceStats"], ["ne1:if1"], sync_id="s-6")
        self.assertEqual(records[0].value, 777)

    def test_correct_per_record_xml_class_when_present(self) -> None:
        client = MagicMock(spec=NFMPXmlClient)
        client.trigger_collect.return_value = [{
            "metric": "received_octets",
            "value": 42,
            "object_id": "ne1:if1",
            "object_name": "if1",
            "category": "Interface / Network Port",
            "xml_class": "equipment.InterfaceStats",
        }]

        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={"equipment.InterfaceStats"},
        )

        records = collector.collect_current(["equipment.InterfaceStats"], ["ne1:if1"], sync_id="s-7")
        self.assertEqual(records[0].xml_class, "equipment.InterfaceStats")

    def test_response_xml_class_must_be_verified(self) -> None:
        client = MagicMock(spec=NFMPXmlClient)
        client.trigger_collect.return_value = [{
            "metric": "received_octets",
            "value": 42,
            "object_id": "ne1:if1",
            "object_name": "if1",
            "category": "Interface / Network Port",
            "xml_class": "unknown.UnverifiedClass",
        }]

        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={"equipment.InterfaceStats"},
        )

        with self.assertRaises(ValueError):
            collector.collect_current(["equipment.InterfaceStats"], ["ne1:if1"], sync_id="s-8")

    def test_ambiguous_multi_class_response_without_xml_class_keeps_none(self) -> None:
        client = MagicMock(spec=NFMPXmlClient)
        client.trigger_collect.return_value = [{
            "metric": "received_octets",
            "value": 99,
            "object_id": "ne1:if1",
            "object_name": "if1",
            "category": "Interface / Network Port",
        }]

        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={"equipment.InterfaceStats", "equipment.InterfaceAdditionalStats"},
        )

        records = collector.collect_current([
            "equipment.InterfaceStats",
            "equipment.InterfaceAdditionalStats",
        ], ["ne1:if1"], sync_id="s-9")
        self.assertIsNone(records[0].xml_class)

    def test_trigger_collect_request_contains_documented_operation(self) -> None:
        request = NFMPXmlClient.build_trigger_collect_request(
            ["ne1"],
            ["equipment.InterfaceStats", "equipment.InterfaceAdditionalStats"],
        )

        self.assertIn("generic.GenericObject.triggerCollect", request)
        self.assertIn("<instanceNames>", request)
        self.assertIn("<currentDataClasses>", request)
        self.assertIn("equipment.InterfaceStats", request)
        self.assertIn("equipment.InterfaceAdditionalStats", request)

    def test_parse_trigger_collect_response(self) -> None:
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<root>\n'
            '  <record>\n'
            '    <xmlClass>equipment.InterfaceStats</xmlClass>\n'
            '    <metric>received_octets</metric>\n'
            '    <value>123</value>\n'
            '    <objectId>ne1:if1</objectId>\n'
            '    <sourceTime>2024-01-01T12:00:00+00:00</sourceTime>\n'
            '  </record>\n'
            '</root>'
        )

        parsed = NFMPXmlClient.parse_trigger_collect_response(xml)
        self.assertEqual(parsed[0]["xml_class"], "equipment.InterfaceStats")
        self.assertEqual(parsed[0]["metric"], "received_octets")
        self.assertEqual(parsed[0]["value"], "123")

    def test_malformed_xml_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            NFMPXmlClient.parse_trigger_collect_response("<broken>")

    def test_empty_response_is_handled_without_inventory_assumption(self) -> None:
        client = MagicMock(spec=NFMPXmlClient)
        client.trigger_collect.return_value = []
        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={"equipment.InterfaceStats"},
        )
        records = collector.collect_current(["equipment.InterfaceStats"], ["ne1"], sync_id="s-10")
        self.assertEqual(records, [])


if __name__ == "__main__":
    unittest.main()
