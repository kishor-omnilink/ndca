"""
SYNC-009.4 - NFM-T Network Element Equipment Adapter.

Maps the verified NFM-T NetworkSupervision /v1/networkElements
response into the existing common EquipmentDTO contract.

This module deliberately contains NFM-T-specific parsing only.
Persistence, inventory identity/reconciliation and shelf/card/port
child collection remain outside this adapter.
"""

from __future__ import annotations

from typing import Any

from ndca.models.dto.equipment import EquipmentDTO
from ndca.models.inventory_snapshot import InventorySnapshot


class NfmtNetworkElementEquipmentMapper:
    """Map NFM-T Network Element records into common EquipmentDTOs."""

    SOURCE_SYSTEM = "NFM-T"
    REQUIRED_RESPONSE_KEYS = {"response"}
    REQUIRED_ELEMENT_FIELDS = {"fdn", "neId"}

    @classmethod
    def map(
        cls,
        snapshot: InventorySnapshot,
    ) -> list[EquipmentDTO]:
        """Map an NFM-T InventorySnapshot into EquipmentDTO objects."""
        if not isinstance(snapshot, InventorySnapshot):
            raise TypeError("snapshot must be an InventorySnapshot")

        if snapshot.source.strip().upper() not in {
            "NFM-T",
            "NFMT",
            "NOKIA NFM-T",
        }:
            raise ValueError(
                "NFM-T mapper requires an NFM-T inventory snapshot"
            )

        payload = snapshot.raw_data

        if not isinstance(payload, dict):
            raise ValueError("NFM-T response root must be a JSON object")

        response = payload.get("response")
        if not isinstance(response, dict):
            raise ValueError(
                "NFM-T response is missing required 'response' object"
            )

        status = response.get("status")
        if status is not None and status != 0:
            raise ValueError(
                f"NFM-T Network Element response has non-zero status: {status!r}"
            )

        data = response.get("data")
        if data is None:
            raise ValueError(
                "NFM-T Network Element response is missing 'data'"
            )

        if not isinstance(data, list):
            raise ValueError(
                "NFM-T Network Element response 'data' must be a list"
            )

        result: list[EquipmentDTO] = []

        for element in data:
            if not isinstance(element, dict):
                raise ValueError(
                    "NFM-T Network Element response contains a "
                    "non-object element"
                )

            missing = [
                field
                for field in cls.REQUIRED_ELEMENT_FIELDS
                if not element.get(field)
            ]
            if missing:
                raise ValueError(
                    "NFM-T Network Element is missing required field(s): "
                    + ", ".join(sorted(missing))
                )

            fdn = str(element["fdn"])
            ne_id = str(element["neId"])

            result.append(
                EquipmentDTO(
                    source_system=cls.SOURCE_SYSTEM,
                    ne_id=ne_id,
                    component_id=fdn,
                    component_class="network-element",
                    raw_component=dict(element),
                )
            )

        return result

    @staticmethod
    def extract_links(
        element: dict[str, Any],
        relation: str,
    ) -> list[str]:
        """Return hrefs for a named NFM-T link relation."""
        links = element.get("links", [])
        if not isinstance(links, list):
            return []

        return [
            str(link["href"])
            for link in links
            if isinstance(link, dict)
            and link.get("rel") == relation
            and link.get("href")
        ]
