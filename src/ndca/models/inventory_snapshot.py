"""
Inventory Snapshot Model.

Represents one inventory collection obtained from Nokia NSP.

SYNC-011-A:
    Explicitly distinguish COMPLETE and PARTIAL inventory snapshots.

A snapshot is COMPLETE only when the Network Element collection exists
and is represented by a JSON list, including an explicitly empty list.

Examples:

    {
        "nsp-equipment:network-element": []
    }

is a valid COMPLETE empty snapshot.

Where the Network Element collection is missing or malformed, the
snapshot is PARTIAL and must not trigger deactivation of existing
inventory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


NETWORK_ELEMENT_KEY = "nsp-equipment:network-element"


@dataclass(slots=True)
class InventorySnapshot:
    """
    Immutable inventory snapshot.

    Attributes
    ----------
    sync_id:
        Unique synchronization identifier.

    source:
        Source system.

    endpoint:
        REST endpoint used to obtain the snapshot.

    raw_data:
        Complete RESTCONF response.

    collected_at:
        UTC timestamp when the inventory was collected.
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
        Return the Network Element collection when valid.

        A missing or malformed collection is represented as an empty
        list for backward compatibility.

        IMPORTANT:
            Callers that need to determine whether the snapshot is
            authoritative must use ``is_complete`` rather than relying
            only on this property.
        """

        value = self.raw_data.get(
            NETWORK_ELEMENT_KEY
        )

        if not isinstance(value, list):
            return []

        return value

    @property
    def network_element_count(self) -> int:
        """
        Return the number of Network Elements in the snapshot.
        """

        return len(self.network_elements)

    @property
    def is_complete(self) -> bool:
        """
        Return whether the Network Element snapshot is authoritative.

        COMPLETE means:

        1. The Network Element collection key exists.
        2. Its value is a JSON list.

        An empty list is therefore COMPLETE.

        PARTIAL means:

        - the Network Element key is missing, or
        - the Network Element collection is not a list.

        A PARTIAL snapshot must never be interpreted as an empty
        authoritative inventory.
        """

        if NETWORK_ELEMENT_KEY not in self.raw_data:
            return False

        return isinstance(
            self.raw_data[NETWORK_ELEMENT_KEY],
            list,
        )

    @property
    def is_partial(self) -> bool:
        """
        Return whether the snapshot is incomplete/partial.
        """

        return not self.is_complete