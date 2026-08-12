from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from ndca.api.nfmp_xml_client import NFMPXmlClient
from ndca.collectors.performance.nfmp_performance_collector import NFMPPerformanceCollector
from ndca.models.dto.performance_record import PerformanceRecord


class TestSync012BPerformanceCollectorB2(unittest.TestCase):
    """Offline contract tests for SYNC-012-B.2."""

    def test_trigger_collect_request_contains_documented_operation(self) -> None:
        request = NFMPXmlClient.build_trigger_collect_request(
            ["ne-1"],
            ["equipment.InterfaceStats", "equipment.InterfaceAdditionalStats"],
        )

        self.assertIn("generic.GenericObject.triggerCollect", request)
        self.assertIn("<instanceNames>", request)
        self.assertIn("<currentDataClasses>", request)
        self.assertIn("equipment.InterfaceStats", request)
        self.assertIn("equipment.InterfaceAdditionalStats", request)

    def test_instance_names_are_generated_correctly(self) -> None:
        request = NFMPXmlClient.build_trigger_collect_request(
            ["ne-1", "ne-2"],
            ["equipment.InterfaceStats"],
        )

        self.assertIn("<instanceName>ne-1</instanceName>", request)
        self.assertIn("<instanceName>ne-2</instanceName>", request)

    def test_current_data_classes_include_only_verified_interface_classes(self) -> None:
        collector = NFMPPerformanceCollector(
            verified_classes={
                "equipment.InterfaceStats",
                "equipment.InterfaceAdditionalStats",
            }
        )
        self.assertSetEqual(
            collector.verified_classes,
            {"equipment.InterfaceStats", "equipment.InterfaceAdditionalStats"},
        )

    def test_unverified_classes_are_rejected(self) -> None:
        client = MagicMock(spec=NFMPXmlClient)
        client.trigger_collect.return_value = []
        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={"equipment.InterfaceStats", "equipment.InterfaceAdditionalStats"},
        )

        with self.assertRaises(ValueError):
            collector.collect_current(["unknown.UnverifiedClass"], ["ne-1"], sync_id="sync-1")

    def test_mocked_current_data_xml_is_parsed(self) -> None:
        response_xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<root>\n'
            '  <record>\n'
            '    <xmlClass>equipment.InterfaceStats</xmlClass>\n'
            '    <metric>Received Octets</metric>\n'
            '    <value>1234</value>\n'
            '    <objectId>ne-1:if-1</objectId>\n'
            '    <sourceTime>2024-01-01T12:00:00+02:00</sourceTime>\n'
            '  </record>\n'
            '</root>'
        )

        parsed = NFMPXmlClient.parse_trigger_collect_response(response_xml)
        self.assertEqual(parsed[0]["xml_class"], "equipment.InterfaceStats")
        self.assertEqual(parsed[0]["metric"], "Received Octets")
        self.assertEqual(parsed[0]["value"], "1234")

    def test_normalized_performance_record_has_is_historical_false(self) -> None:
        now = datetime.now(timezone.utc)
        record = PerformanceRecord(
            sync_id="sync-1",
            source="NFM-P",
            xml_class="equipment.InterfaceStats",
            category="Interface / Network Port",
            object_id="ne-1:if-1",
            object_name="if-1",
            metric="received_octets",
            metric_source_name="Received Octets",
            value=1234,
            collection_time=now,
            source_time=now,
            is_historical=False,
            evidence_status="VERIFIED",
        )

        self.assertFalse(record.is_historical)
        self.assertEqual(record.source, "NFM-P")
        self.assertEqual(record.xml_class, "equipment.InterfaceStats")
        self.assertEqual(record.evidence_status, "VERIFIED")

    def test_xml_class_is_preserved(self) -> None:
        client = MagicMock(spec=NFMPXmlClient)
        client.trigger_collect.return_value = [{
            "metric": "received_octets",
            "value": 999,
            "object_id": "ne-1:if-1",
            "object_name": "if-1",
            "category": "Interface / Network Port",
            "xml_class": "equipment.InterfaceAdditionalStats",
        }]

        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={"equipment.InterfaceAdditionalStats"},
        )

        records = collector.collect_current(["equipment.InterfaceAdditionalStats"], ["ne-1"], sync_id="sync-2")
        self.assertEqual(records[0].xml_class, "equipment.InterfaceAdditionalStats")

    def test_malformed_xml_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            NFMPXmlClient.parse_trigger_collect_response("<broken>")

    def test_empty_response_is_handled_as_empty_response(self) -> None:
        client = MagicMock(spec=NFMPXmlClient)
        client.trigger_collect.return_value = []
        collector = NFMPPerformanceCollector(
            client=client,
            verified_classes={"equipment.InterfaceStats"},
        )

        records = collector.collect_current(["equipment.InterfaceStats"], ["ne-1"], sync_id="sync-3")
        self.assertEqual(records, [])

    def test_no_live_nfmp_connection_is_required(self) -> None:
        collector = NFMPPerformanceCollector(
            verified_classes={"equipment.InterfaceStats"},
        )
        self.assertIsNotNone(collector)
        self.assertEqual(collector.verified_classes, {"equipment.InterfaceStats"})


if __name__ == "__main__":
    unittest.main()
