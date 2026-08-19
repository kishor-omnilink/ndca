# SPDX-License-Identifier: MIT
"""Mapper for verified NSP Kafka BGP telemetry."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from ndca.models.dto.performance_record import PerformanceRecord


BGP_KPI_TYPE = (
    "telemetry:/base/sros-service-vprn/"
    "service_vprn_bgp_neighbor_statistics"
)

VERIFIED_BGP_FIELDS = frozenset({
    "peer-as", "peer-port", "local-port", "session-state",
    "last-state", "last-event", "last-error", "negotiated-family",
    "operational-local-address", "operational-remote-address",
    "peer-identifier", "established-transitions",
    "last-established-time", "number-of-update-flaps",
    "hold-time-interval", "keep-alive-interval",
    "family-prefix_ipv4_received", "family-prefix_ipv4_active",
    "family-prefix_ipv4_sent", "family-prefix_ipv4_backup",
    "family-prefix_ipv4_rejected", "family-prefix_ipv4_suppressed",
    "family-prefix_ipv6_received", "family-prefix_ipv6_active",
    "family-prefix_ipv6_sent", "family-prefix_ipv6_backup",
    "family-prefix_ipv6_rejected", "family-prefix_ipv6_suppressed",
    "received_messages", "received_updates", "received_octets",
    "received_route-refresh", "sent_messages", "sent_updates",
    "sent_octets", "sent_route-refresh", "oper-tcp-mss",
    "rcvd-tcp-mss",
})


class BGPKafkaPayloadError(ValueError):
    """Raised when a Kafka value is not a supported BGP payload."""


def _decode_json(value: bytes | str | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)

    text = value.decode("utf-8") if isinstance(value, bytes) else value
    text = text.strip()

    if text.startswith("data:"):
        records: list[str] = []
        current: list[str] = []
        for line in text.splitlines():
            if line.startswith("data:"):
                current.append(line[5:].lstrip())
            elif not line and current:
                records.append("".join(current))
                current = []
        if current:
            records.append("".join(current))
        if len(records) != 1:
            raise BGPKafkaPayloadError(
                "Kafka value must contain exactly one SSE record"
            )
        text = records[0]

    try:
        decoded = json.loads(text)
    except json.JSONDecodeError as exc:
        raise BGPKafkaPayloadError("Kafka value is not valid JSON") from exc

    if not isinstance(decoded, dict):
        raise BGPKafkaPayloadError("Kafka JSON value must be an object")
    return decoded


def _find_event(payload: Mapping[str, Any]) -> dict[str, Any]:
    notification = payload.get("ietf-restconf:notification")
    if not isinstance(notification, Mapping):
        raise BGPKafkaPayloadError(
            "Missing ietf-restconf:notification envelope"
        )

    event = notification.get("nsp-kpi:real_time_kpi-event")
    if not isinstance(event, Mapping):
        raise BGPKafkaPayloadError(
            "Missing nsp-kpi:real_time_kpi-event envelope"
        )
    return dict(event)


def _iter_scalars(value: Any) -> list[tuple[str, Any]]:
    result: list[tuple[str, Any]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            if isinstance(child, (Mapping, list)):
                result.extend(_iter_scalars(child))
            else:
                result.append((str(key), child))
    elif isinstance(value, list):
        for child in value:
            result.extend(_iter_scalars(child))
    return result


def _lookup(event: Mapping[str, Any], *names: str) -> Any:
    aliases = {name.lower().replace("_", "-") for name in names}
    for key, value in _iter_scalars(event):
        if key.lower().replace("_", "-") in aliases:
            return value
    return None


def _coerce_utc(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(
            float(value) / 1000.0,
            tz=timezone.utc,
        )
    if isinstance(value, str):
        text = value.strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            return None
        return (
            dt.replace(tzinfo=timezone.utc)
            if dt.tzinfo is None
            else dt.astimezone(timezone.utc)
        )
    return None


_OBJECT_RE = re.compile(
    r"/state/service/vprn\[service-name='(?P<service>[^']+)'\]"
    r"/bgp/neighbor\[ip-address='(?P<peer>[^']+)'\]"
)


def _object_parts(object_id: str | None) -> tuple[str | None, str | None]:
    if not object_id:
        return None, None
    match = _OBJECT_RE.search(object_id)
    if not match:
        return None, None
    return match.group("service"), match.group("peer")


class BGPKafkaMapper:
    """Convert verified BGP telemetry into existing PerformanceRecord DTOs."""

    def map_record(
        self,
        *,
        value: bytes | str | Mapping[str, Any],
        topic: str,
        partition: int = 0,
        offset: int = -1,
        sync_id: str = "sync-012-b3-kafka",
    ) -> list[PerformanceRecord]:
        """Parse one Kafka value into normalized records."""
        payload = _decode_json(value)
        event = _find_event(payload)

        kpi_type = _lookup(event, "kpiType", "kpi-type")
        if kpi_type != BGP_KPI_TYPE:
            raise BGPKafkaPayloadError(
                f"Unexpected kpiType: {kpi_type!r}"
            )

        ne_id = _lookup(event, "neId", "ne-id", "system-id")
        object_id = _lookup(event, "objectId", "object-id", "object_id")
        if not ne_id:
            raise BGPKafkaPayloadError("BGP event does not contain neId/system-id")
        if not object_id:
            raise BGPKafkaPayloadError("BGP event does not contain objectId")

        service_name, peer_ip = _object_parts(str(object_id))
        source_time = _coerce_utc(
            _lookup(event, "time-captured", "eventTime")
        )
        collection_time = _coerce_utc(
            _lookup(event, "eventTime", "time-captured")
        ) or datetime.now(timezone.utc)

        records: list[PerformanceRecord] = []
        for name, metric_value in _iter_scalars(event):
            base_name = name[:-9] if name.endswith("-periodic") else name
            if base_name not in VERIFIED_BGP_FIELDS:
                continue

            object_name = (
                f"{service_name}:{peer_ip}"
                if service_name and peer_ip
                else str(object_id)
            )
            records.append(
                PerformanceRecord(
                    sync_id=sync_id,
                    source="NSP-Kafka",
                    xml_class=None,
                    category="bgp_neighbor_statistics",
                    object_id=str(object_id),
                    object_name=object_name,
                    metric=name,
                    metric_source_name=name,
                    value=metric_value,
                    collection_time=collection_time,
                    source_time=source_time,
                    persistence_time=None,
                    is_historical=False,
                    raw_payload={
                        "kafka": {
                            "topic": topic,
                            "partition": partition,
                            "offset": offset,
                        },
                        "payload": payload,
                    },
                    evidence_status="VERIFIED",
                    notes=None,
                )
            )
        return records
