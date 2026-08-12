"""
PerformanceRecord DTO for normalized performance metrics.

Used by the SYNC-012-B collector foundation as the internal normalized record
contract. This DTO avoids assuming NFM-P XML field names and is populated by
the normalization layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class PerformanceRecord:
    """Normalized performance measurement record."""

    sync_id: str
    source: str
    xml_class: str | None
    category: str
    object_id: str
    object_name: str | None
    metric: str
    metric_source_name: str | None
    value: Any
    collection_time: datetime
    source_time: datetime | None
    persistence_time: datetime | None = None
    is_historical: bool = False
    raw_payload: dict[str, Any] | None = None
    evidence_status: str | None = None
    notes: str | None = None
