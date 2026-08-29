"""
NFM-P historical Interface Additional statistics mapper.

SYNC-012-D.1.3
----------------
Normalizes the verified historical
``equipment.InterfaceAdditionalStatsLogRecord`` representation produced by
the D.1.2 NFM-P XML parser into NDCA ``PerformanceRecord`` objects.

Only mappings explicitly authorized by the SYNC-012-A performance counter
register are implemented here.

Verified mapping:

    receivedBroadcastPackets
        -> interface.received_broadcast_packets

The mapper deliberately preserves the complete Nokia source record in
``PerformanceRecord.raw_payload`` and does not normalize unverified or
periodic source fields.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from ndca.models.dto.performance_record import PerformanceRecord


class NFMPInterfaceHistoricalMapper:
    """Normalize verified NFM-P historical Interface Additional records."""

    SOURCE = "NFM-P"

    XML_CLASS = "equipment.InterfaceAdditionalStatsLogRecord"

    CATEGORY = "Interface / Network Port"

    EVIDENCE_STATUS = "VERIFIED"

    VERIFIED_METRIC_MAPPINGS: dict[str, str] = {
        "receivedBroadcastPackets": (
            "interface.received_broadcast_packets"
        ),
    }

    @classmethod
    def map_record(
        cls,
        raw_record: Mapping[str, Any],
        *,
        sync_id: str,
        collection_time: datetime | None = None,
    ) -> list[PerformanceRecord]:
        """Normalize one verified historical Interface Additional record.

        The input is expected to be the raw dictionary returned by
        ``NFMPXmlClient.parse_interface_additional_historical_response``.

        Only the explicitly verified Nokia source metric
        ``receivedBroadcastPackets`` is normalized.

        The complete raw source record is retained in ``raw_payload``.
        """

        if not isinstance(raw_record, Mapping):
            raise ValueError("Historical record must be a mapping")

        object_id = cls._required_value(
            raw_record,
            "monitoredObjectPointer",
        )

        time_captured = cls._required_value(
            raw_record,
            "timeCaptured",
        )

        collection_time_utc = cls._coerce_collection_time(
            collection_time,
        )

        source_time = cls._coerce_source_time(
            time_captured,
        )

        normalized_records: list[PerformanceRecord] = []

        for source_metric, normalized_metric in (
            cls.VERIFIED_METRIC_MAPPINGS.items()
        ):
            if source_metric not in raw_record:
                continue

            value = cls._coerce_metric_value(
                raw_record[source_metric],
                source_metric=source_metric,
            )

            object_name = cls._optional_value(
                raw_record,
                "displayedName",
            ) or cls._optional_value(
                raw_record,
                "name",
            )

            normalized_records.append(
                PerformanceRecord(
                    sync_id=sync_id,
                    source=cls.SOURCE,
                    xml_class=cls.XML_CLASS,
                    category=cls.CATEGORY,
                    object_id=object_id,
                    object_name=object_name,
                    metric=normalized_metric,
                    metric_source_name=source_metric,
                    value=value,
                    collection_time=collection_time_utc,
                    source_time=source_time,
                    is_historical=True,
                    raw_payload=dict(raw_record),
                    evidence_status=cls.EVIDENCE_STATUS,
                )
            )

        if not normalized_records:
            raise ValueError(
                "Historical Interface Additional record contains no "
                "verified metric source"
            )

        return normalized_records

    @classmethod
    def map_records(
        cls,
        raw_records: list[Mapping[str, Any]],
        *,
        sync_id: str,
        collection_time: datetime | None = None,
    ) -> list[PerformanceRecord]:
        """Normalize multiple historical Interface Additional records."""

        records: list[PerformanceRecord] = []

        for raw_record in raw_records:
            records.extend(
                cls.map_record(
                    raw_record,
                    sync_id=sync_id,
                    collection_time=collection_time,
                )
            )

        return records

    @staticmethod
    def _required_value(
        raw_record: Mapping[str, Any],
        field_name: str,
    ) -> str:
        """Return a required non-empty source field."""

        value = raw_record.get(field_name)

        if value is None:
            raise ValueError(
                f"Historical record requires {field_name}"
            )

        value_text = str(value).strip()

        if not value_text:
            raise ValueError(
                f"Historical record requires {field_name}"
            )

        return value_text

    @staticmethod
    def _optional_value(
        raw_record: Mapping[str, Any],
        field_name: str,
    ) -> str | None:
        """Return an optional non-empty source field."""

        value = raw_record.get(field_name)

        if value is None:
            return None

        value_text = str(value).strip()

        return value_text or None

    @staticmethod
    def _coerce_source_time(
        time_captured: str,
    ) -> datetime:
        """Convert Nokia epoch milliseconds to UTC-aware datetime."""

        try:
            milliseconds = float(time_captured)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Historical timeCaptured must be epoch milliseconds"
            ) from exc

        try:
            return datetime.fromtimestamp(
                milliseconds / 1000.0,
                tz=UTC,
            )
        except (OverflowError, OSError, ValueError) as exc:
            raise ValueError(
                "Historical timeCaptured is outside the supported "
                "datetime range"
            ) from exc

    @staticmethod
    def _coerce_collection_time(
        collection_time: datetime | None,
    ) -> datetime:
        """Return a timezone-aware UTC collection timestamp."""

        if collection_time is None:
            return datetime.now(UTC)

        if collection_time.tzinfo is None:
            return collection_time.replace(tzinfo=UTC)

        return collection_time.astimezone(UTC)

    @staticmethod
    def _coerce_metric_value(
        value: Any,
        *,
        source_metric: str,
    ) -> int | float:
        """Convert a verified Nokia numeric metric to a numeric value."""

        if value is None:
            raise ValueError(
                f"Historical metric {source_metric} must have a value"
            )

        if isinstance(value, bool):
            raise ValueError(
                f"Historical metric {source_metric} must be numeric"
            )

        if isinstance(value, (int, float)):
            return value

        value_text = str(value).strip()

        if not value_text:
            raise ValueError(
                f"Historical metric {source_metric} must have a value"
            )

        try:
            if any(
                character in value_text
                for character in (".", "e", "E")
            ):
                return float(value_text)

            return int(value_text)
        except ValueError as exc:
            raise ValueError(
                f"Historical metric {source_metric} must be numeric"
            ) from exc
