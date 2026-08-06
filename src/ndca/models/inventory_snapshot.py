"""
Inventory Snapshot Model

Represents one immutable inventory collection obtained from Nokia NSP.

The snapshot is the boundary between data collection and data processing.
All downstream components (mappers, validators, repositories) consume
InventorySnapshot instead of raw JSON.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class InventorySnapshot:
    """
    Immutable inventory snapshot.

    Attributes
    ----------
    sync_id:
        Unique synchronization identifier.

    collected_at:
        UTC timestamp when inventory was collected.

    source:
        Source system.

    endpoint:
        REST endpoint used.

    raw_data:
        Complete RESTCONF response.
    """

    sync_id: str

    source: str

    endpoint: str

    raw_data: dict[str, Any]

    collected_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def network_elements(self) -> list[dict[str, Any]]:
        """
        Return network element list.
        """

        return self.raw_data.get(
            "nsp-equipment:network-element",
            [],
        )

    @property
    def network_element_count(self) -> int:
        """
        Number of Network Elements.
        """

        return len(self.network_elements)