# SPDX-License-Identifier: MIT
"""Unit tests for SYNC-012-B.3 Kafka BGP components."""

from __future__ import annotations

import json
import pathlib
import unittest
from datetime import datetime, timezone

from ndca.collectors.performance.kafka_bgp_performance_consumer import (
    KafkaBGPPerformanceConsumer,
    KafkaRecord,
)
from ndca.mappers.bgp_kafka_mapper import (
    BGP_KPI_TYPE,
    BGPKafkaMapper,
    BGPKafkaPayloadError,
)
from ndca.models.dto.performance_record import PerformanceRecord


class FakeSource:
    """In-memory Kafka source for unit tests."""

    def __init__(self, records: list[KafkaRecord]) -> None:
        self.records = iter(records)
        self.closed = False

    def poll(self, timeout: float) -> KafkaRecord | None:
        del timeout
        try:
            return next(self.records)
        except StopIteration:
            return None

    def close(self) -> None:
        self.closed = True


class TestSync012BKafkaBGPPerformance(unittest.TestCase):
    """Validate Kafka transport and mapping boundaries."""

    def _payload(self) -> dict:
        return {
            "ietf-restconf:notification": {
                "eventTime": "2026-08-15T18:03:22Z",
                "nsp-kpi:real_time_kpi-event": {
                    "kpiType": BGP_KPI_TYPE,
                    "neId": "TEST-NE",
                    "system-id": "TEST-NE",
                    "objectId": (
                        "/state/service/vprn[service-name='OSWAN']/"
                        "bgp/neighbor[ip-address='192.0.2.2']"
                    ),
                    "time-captured": 1786817002475,
                    "session-state": "Established",
                    "peer-as": 64200,
                    "received_messages": 185,
                    "received_messages-periodic": 21,
                    "received_route-refresh": 2,
                    "received_route-refresh-periodic": 1,
                    "sent_messages": 297,
                    "sent_route-refresh": 3,
                    "sent_route-refresh-periodic": 1,
                    "family-prefix_ipv4_received": 1,
                    "family-prefix_ipv4_sent": 5891,
                    "family-prefix_ipv6_received": 0,
                },
            }
        }

    def test_mapper_accepts_verified_kpi_type(self) -> None:
        """Valid BGP envelope is accepted."""
        records = BGPKafkaMapper().map_record(
            value=self._payload(),
            topic="test-topic",
        )
        metrics = {record.metric for record in records}
        self.assertIn("session-state", metrics)
        self.assertIn("peer-as", metrics)
        self.assertIn("received_messages-periodic", metrics)

    def test_mapper_preserves_identity(self) -> None:
        """Peer and service identity are preserved."""
        records = BGPKafkaMapper().map_record(
            value=self._payload(),
            topic="test-topic",
        )
        self.assertTrue(records)
        for record in records:
            self.assertIn("OSWAN", record.object_name or "")
            self.assertIn("192.0.2.2", record.object_name or "")
            self.assertEqual(record.evidence_status, "VERIFIED")

    def test_mapper_rejects_non_bgp_kpi(self) -> None:
        """Wrong kpiType is rejected."""
        payload = self._payload()
        payload["ietf-restconf:notification"]["nsp-kpi:real_time_kpi-event"][
            "kpiType"
        ] = "telemetry:/other"
        with self.assertRaises(BGPKafkaPayloadError):
            BGPKafkaMapper().map_record(value=payload, topic="test-topic")

    def test_mapper_rejects_missing_envelope(self) -> None:
        """Invalid or missing envelope is rejected."""
        with self.assertRaises(BGPKafkaPayloadError):
            BGPKafkaMapper().map_record(
                value={"unexpected": {}},
                topic="test-topic",
            )

    def test_mapper_rejects_missing_ne_id(self) -> None:
        """Missing neId/system-id is rejected."""
        payload = self._payload()
        del payload["ietf-restconf:notification"]["nsp-kpi:real_time_kpi-event"]["neId"]
        del payload["ietf-restconf:notification"]["nsp-kpi:real_time_kpi-event"]["system-id"]
        with self.assertRaises(BGPKafkaPayloadError):
            BGPKafkaMapper().map_record(value=payload, topic="test-topic")

    def test_mapper_rejects_missing_object_id(self) -> None:
        """Missing objectId is rejected."""
        payload = self._payload()
        del payload["ietf-restconf:notification"]["nsp-kpi:real_time_kpi-event"]["objectId"]
        with self.assertRaises(BGPKafkaPayloadError):
            BGPKafkaMapper().map_record(value=payload, topic="test-topic")

    def test_mapper_handles_session_state(self) -> None:
        """Session state field is mapped."""
        records = BGPKafkaMapper().map_record(
            value=self._payload(),
            topic="test-topic",
        )
        session_states = [
            r.value for r in records if r.metric == "session-state"
        ]
        self.assertIn("Established", session_states)

    def test_mapper_handles_prefix_counters(self) -> None:
        """IPv4 and IPv6 prefix counters are mapped."""
        records = BGPKafkaMapper().map_record(
            value=self._payload(),
            topic="test-topic",
        )
        metrics = {record.metric for record in records}
        self.assertIn("family-prefix_ipv4_received", metrics)
        self.assertIn("family-prefix_ipv4_sent", metrics)

    def test_mapper_handles_traffic_counters(self) -> None:
        """Message and octets counters are mapped."""
        records = BGPKafkaMapper().map_record(
            value=self._payload(),
            topic="test-topic",
        )
        metrics = {record.metric for record in records}
        self.assertIn("received_messages", metrics)
        self.assertIn("sent_messages", metrics)

    def test_mapper_handles_periodic_counters(self) -> None:
        """Periodic counter variants are accepted."""
        records = BGPKafkaMapper().map_record(
            value=self._payload(),
            topic="test-topic",
        )
        metrics = {record.metric for record in records}
        self.assertIn("received_messages-periodic", metrics)

    def test_mapper_handles_route_refresh_counters(self) -> None:
        """Evidence-observed route-refresh counters are mapped."""
        records = BGPKafkaMapper().map_record(
            value=self._payload(),
            topic="test-topic",
        )
        metrics = {record.metric for record in records}
        self.assertIn("received_route-refresh", metrics)
        self.assertIn("received_route-refresh-periodic", metrics)
        self.assertIn("sent_route-refresh", metrics)
        self.assertIn("sent_route-refresh-periodic", metrics)

    def test_mapper_rejects_unverified_periodic_fields(self) -> None:
        """Only periodic variants of verified fields are accepted."""
        payload = self._payload()
        payload["ietf-restconf:notification"]["nsp-kpi:real_time_kpi-event"][
            "unverified_metric-periodic"
        ] = 123
        records = BGPKafkaMapper().map_record(
            value=payload,
            topic="test-topic",
        )
        metrics = {record.metric for record in records}
        self.assertNotIn("unverified_metric-periodic", metrics)

    def test_mapper_normalizes_timestamp_to_utc(self) -> None:
        """Source timestamps are normalized to UTC."""
        records = BGPKafkaMapper().map_record(
            value=self._payload(),
            topic="test-topic",
        )
        self.assertTrue(records)
        for record in records:
            if record.source_time is not None:
                self.assertEqual(record.source_time.tzinfo, timezone.utc)

    def test_mapper_preserves_raw_payload(self) -> None:
        """Raw payload is preserved in record."""
        records = BGPKafkaMapper().map_record(
            value=self._payload(),
            topic="test-topic",
            partition=5,
            offset=42,
        )
        self.assertTrue(records)
        for record in records:
            self.assertIsNotNone(record.raw_payload)
            self.assertIn("kafka", record.raw_payload)
            self.assertEqual(record.raw_payload["kafka"]["topic"], "test-topic")
            self.assertEqual(record.raw_payload["kafka"]["partition"], 5)
            self.assertEqual(record.raw_payload["kafka"]["offset"], 42)
            self.assertIn("payload", record.raw_payload)
            self.assertEqual(record.raw_payload["payload"], self._payload())

    def test_mapper_rejects_json_decode_error(self) -> None:
        """Malformed JSON is rejected."""
        with self.assertRaises(BGPKafkaPayloadError):
            BGPKafkaMapper().map_record(
                value=b"not valid json",
                topic="test-topic",
            )

    def test_mapper_accepts_sse_format(self) -> None:
        """SSE-framed payloads are parsed."""
        payload = self._payload()
        sse_value = f"data:{json.dumps(payload)}"
        records = BGPKafkaMapper().map_record(
            value=sse_value,
            topic="test-topic",
        )
        self.assertTrue(records)
        metrics = {record.metric for record in records}
        self.assertIn("session-state", metrics)

    def test_mapper_handles_bytes_value(self) -> None:
        """Kafka bytes values are handled."""
        payload = self._payload()
        records = BGPKafkaMapper().map_record(
            value=json.dumps(payload).encode("utf-8"),
            topic="test-topic",
        )
        self.assertTrue(records)
        self.assertGreater(len(records), 0)

    def test_consumer_processes_records(self) -> None:
        """Consumer delegates to handler."""
        payload = self._payload()
        source = FakeSource([
            KafkaRecord(
                value=json.dumps(payload),
                topic="test-topic",
                partition=0,
                offset=1,
            )
        ])
        received: list[KafkaRecord] = []
        consumer = KafkaBGPPerformanceConsumer(
            source,
            received.append,
        )

        self.assertEqual(consumer.consume(max_messages=1), 1)
        self.assertEqual(len(received), 1)
        consumer.close()
        self.assertTrue(source.closed)

    def test_consumer_handles_empty_source(self) -> None:
        """Consumer handles empty source gracefully."""
        source = FakeSource([])
        received: list[KafkaRecord] = []
        consumer = KafkaBGPPerformanceConsumer(
            source,
            received.append,
        )

        processed = consumer.consume(max_messages=10)
        self.assertEqual(processed, 0)
        consumer.close()

    def test_consumer_consume_once_returns_none_when_empty(self) -> None:
        """consume_once returns None when no records available."""
        source = FakeSource([])
        consumer = KafkaBGPPerformanceConsumer(
            source,
            lambda x: x,
        )

        result = consumer.consume_once()
        self.assertIsNone(result)

    def test_malformed_kafka_record_does_not_crash_consumer(self) -> None:
        """Consumer loop continues after malformed record."""
        payload = self._payload()
        source = FakeSource([
            KafkaRecord(
                value=b"invalid json",
                topic="test-topic",
                partition=0,
                offset=1,
            ),
        ])

        results: list[Exception | None] = []

        def handler(record: KafkaRecord) -> Exception | None:
            try:
                BGPKafkaMapper().map_record(
                    value=record.value,
                    topic=record.topic,
                )
                return None
            except BGPKafkaPayloadError as e:
                return e

        consumer = KafkaBGPPerformanceConsumer(source, handler)
        for _ in range(2):
            result = consumer.consume_once()
            results.append(result)

        # First record should produce an error, second should be None
        self.assertIsInstance(results[0], BGPKafkaPayloadError)
        self.assertIsNone(results[1])

    def test_real_payload_fixture_parses(self) -> None:
        """Real payload fixture from Kafka topic parses successfully."""
        fixture_path = pathlib.Path("tests/fixtures/nsp_bgp_neighbor_statistics_20260815.json")
        
        if not fixture_path.exists():
            self.skipTest(f"Real payload fixture not found: {fixture_path}")

        with fixture_path.open() as f:
            payload_dict = json.load(f)

        # Wrap in required envelope
        full_payload = {
            "ietf-restconf:notification": {
                "nsp-kpi:real_time_kpi-event": payload_dict,
            }
        }

        # Should parse without error
        records = BGPKafkaMapper().map_record(
            value=full_payload,
            topic="ns-eg-1716a23b-7c94-4393-831d-cd97c20c1e70",
        )
        self.assertGreater(len(records), 0)
        
        # Verify verified fields are present
        for record in records:
            if record.metric in {"established-transitions", "family-prefix_ipv4_received"}:
                self.assertIsNotNone(record.value)
    def test_consumer_continues_after_malformed_record(self) -> None:
        records = [
            KafkaRecord(
                topic="test-topic",
                partition=0,
                offset=1,
                value=b"bad",
            ),
            KafkaRecord(
                topic="test-topic",
                partition=0,
                offset=2,
                value=b"good",
            ),
        ]

        source = FakeSource(records)

        processed = []

        def handler(record):
            if record.value == b"bad":
                raise BGPKafkaPayloadError("malformed payload")
            processed.append(record)

        consumer = KafkaBGPPerformanceConsumer(
            source=source,
            handler=handler,
        )

        count = consumer.consume(max_messages=2)
        self.assertEqual(count, 1)
        self.assertEqual(len(processed), 1)
        self.assertEqual(processed[0].offset, 2)


if __name__ == "__main__":
    unittest.main()

