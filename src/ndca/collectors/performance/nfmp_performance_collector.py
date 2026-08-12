"""
NFM-P Performance Collector skeleton for SYNC-012-B.

Provides an offline, testable collector foundation that uses an XML client
abstraction and produces `PerformanceRecord` DTOs. It enforces the use of
VERIFIED XML API classes discovered by SYNC-012-A.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List

from ndca.api.nfmp_xml_client import NFMPXmlClient
from ndca.core.exceptions import CollectorError
from ndca.core.logging import get_logger
from ndca.models.dto.performance_record import PerformanceRecord

_DEFAULT_REGISTER_CSV = Path("docs/sync/SYNC-012-A_Performance_Counter_Register.csv")


def _load_verified_xml_classes(register_path: str | Path | None = None) -> set[str]:
    """Load VERIFIED xml_api_class values from the SYNC-012-A register.

    This helper is explicit and optional. The normal production path does not
    depend on a repository-relative CSV at runtime.
    """
    verified: set[str] = set()
    register_file = Path(register_path) if register_path else _DEFAULT_REGISTER_CSV
    if not register_file.exists():
        return verified

    with register_file.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            status = row.get("api_verification_status", "").strip()
            xml_class = row.get("xml_api_class", "").strip()
            if status == "VERIFIED" and xml_class and xml_class.upper() != "UNKNOWN":
                verified.add(xml_class)

    return verified


def _coerce_utc_datetime(value: object) -> datetime | None:
    """Normalize a datetime-like payload to UTC-aware UTC.

    Naive datetime values are treated conservatively as UTC because the project
    contract requires timezone-aware UTC timestamps and does not permit naive
    values to be stored.
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        dt = value
    else:
        try:
            dt = datetime.fromisoformat(str(value))
        except (TypeError, ValueError):
            return None

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


class NFMPPerformanceCollector:
    """Performance collector skeleton.

    Methods are intentionally conservative: only XML API classes flagged as
    VERIFIED in the SYNC-012-A register are permitted. The collector delegates
    transport to `NFMPXmlClient` which is expected to be mocked during tests.
    """

    VERIFIED_INTERFACE_CURRENT_DATA_CLASSES = {
        "equipment.InterfaceStats",
        "equipment.InterfaceAdditionalStats",
    }

    def __init__(
        self,
        client: NFMPXmlClient | None = None,
        verified_classes: Iterable[str] | None = None,
        register_path: str | Path | None = None,
    ) -> None:
        self.logger = get_logger(__name__)
        self.client = client or NFMPXmlClient()

        if verified_classes is not None:
            self._verified_classes = {str(item).strip() for item in verified_classes if str(item).strip()}
        elif register_path is not None:
            self._verified_classes = _load_verified_xml_classes(register_path)
        else:
            self._verified_classes = set()

    @classmethod
    def from_register(
        cls,
        client: NFMPXmlClient | None = None,
        register_path: str | Path | None = None,
    ) -> "NFMPPerformanceCollector":
        """Explicitly load VERIFIED XML classes from the SYNC-012-A register.

        This remains opt-in and does not impose a mandatory filesystem dependency
        on production code.
        """
        return cls(
            client=client,
            verified_classes=_load_verified_xml_classes(register_path),
        )

    @property
    def verified_classes(self) -> set[str]:
        return set(self._verified_classes)

    def collect(
        self,
        current_data_classes: Iterable[str],
        instance_names: Iterable[str] | None = None,
        sync_id: str | None = None,
    ) -> List[PerformanceRecord]:
        """Standard collector entry point for NDCA collectors."""
        return self.collect_current(
            current_data_classes=current_data_classes,
            instance_names=instance_names,
            sync_id=sync_id,
        )

    def collect_interface_current_data(
        self,
        instance_names: Iterable[str],
        sync_id: str | None = None,
    ) -> List[PerformanceRecord]:
        """Collect only the verified interface current-data classes."""
        requested = list(self.VERIFIED_INTERFACE_CURRENT_DATA_CLASSES)
        return self.collect_current(
            current_data_classes=requested,
            instance_names=instance_names,
            sync_id=sync_id,
        )

    def collect_current(
        self,
        current_data_classes: Iterable[str],
        instance_names: Iterable[str] | None = None,
        sync_id: str | None = None,
    ) -> List[PerformanceRecord]:
        """Collect current performance data for the specified classes.

        - Validates that requested classes are VERIFIED.
        - Calls the XML client `trigger_collect` and converts returned raw
          record dicts into `PerformanceRecord` objects.
        - Does not attempt historical LogRecord collection.
        """
        if sync_id is None:
            sync_id = "sync-012-b"

        requested = [str(item).strip() for item in current_data_classes if str(item).strip()]
        self.logger.info("Collect current data", classes=requested)

        for cls in requested:
            if cls not in self._verified_classes:
                raise ValueError(f"Requested XML API class is not VERIFIED: {cls}")

        try:
            raw = self.client.trigger_collect(
                instance_names or [],
                requested,
            )
        except Exception as exc:
            self.logger.error("Performance collection failed", error=str(exc))
            raise CollectorError("Performance collection failed") from exc

        if raw is None:
            self.logger.warning("Empty response from current-data trigger", sync_id=sync_id)
            return []

        records: List[PerformanceRecord] = []
        now = datetime.now(timezone.utc)

        for item in raw:
            if not isinstance(item, dict):
                continue

            response_xml_class = item.get("xml_class")
            if response_xml_class is not None:
                response_xml_class = str(response_xml_class).strip()
                if not response_xml_class:
                    response_xml_class = None
                elif response_xml_class not in self._verified_classes:
                    raise ValueError(
                        f"Response XML API class is not VERIFIED: {response_xml_class}"
                    )

            metric = item.get("metric") or item.get("metric_name") or "unknown"
            value = item.get("value")
            object_id = item.get("object_id") or item.get("monitored_object") or ""
            object_name = item.get("object_name")
            source_time = _coerce_utc_datetime(item.get("source_time"))
            xml_class = response_xml_class
            if xml_class is None and len(requested) == 1:
                xml_class = requested[0]

            record = PerformanceRecord(
                sync_id=sync_id,
                source="NFM-P",
                xml_class=xml_class,
                category=item.get("category", "unknown"),
                object_id=object_id,
                object_name=object_name,
                metric=metric,
                metric_source_name=item.get("metric_source_name"),
                value=value,
                collection_time=now,
                source_time=source_time,
                persistence_time=None,
                is_historical=False,
                raw_payload=item,
                evidence_status="VERIFIED",
                notes=None,
            )

            records.append(record)

        return records

    def close(self) -> None:
        # Client cleanup if implemented
        try:
            if hasattr(self.client, "close"):
                self.client.close()
        except Exception:
            self.logger.debug("Client close raised an exception; ignoring")
