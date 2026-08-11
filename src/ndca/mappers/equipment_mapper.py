"""
Equipment Mapper.

Extracts physical equipment components from an InventorySnapshot.

The current NSP Network Element response contains physical equipment
under:

    hardware-component

including shelf, container, card and port objects.

SYNC-009 performs extraction and normalization only.
Persistence/reconciliation belongs to SYNC-010.
"""

from __future__ import annotations

from typing import Any

from ndca.models.dto.equipment import EquipmentDTO
from ndca.models.inventory_snapshot import InventorySnapshot


class EquipmentMapper:
    """Map NSP hardware components into normalized EquipmentDTO objects."""

    SUPPORTED_CLASSES = {
        "shelf",
        "container",
        "card",
        "port",
        "fan",
        "power-supply",
    }

    @classmethod
    def map(
        cls,
        snapshot: InventorySnapshot,
    ) -> list[EquipmentDTO]:
        """
        Extract equipment components from an inventory snapshot.

        Unknown hardware-component classes are retained rather than
        silently discarded. They are normalized using their original
        class value.
        """

        result: list[EquipmentDTO] = []

        for network_element in snapshot.network_elements:
            ne_id = network_element.get("ne-id")

            if not ne_id:
                raise ValueError(
                    "Network Element is missing required field: ne-id"
                )

            components = network_element.get(
                "hardware-component",
                {},
            )

            if not isinstance(components, dict):
                raise ValueError(
                    f"Network Element {ne_id!r} has invalid "
                    "hardware-component structure"
                )

            for component_class, component_list in components.items():
                if not isinstance(component_list, list):
                    continue

                for component in component_list:
                    if not isinstance(component, dict):
                        raise ValueError(
                            f"Network Element {ne_id!r} contains a "
                            f"non-object {component_class!r} component"
                        )

                    result.append(
                        cls._to_dto(
                            ne_id=ne_id,
                            component_class=component_class,
                            component=component,
                        )
                    )

        return result

    @staticmethod
    def _to_dto(
        *,
        ne_id: str,
        component_class: str,
        component: dict[str, Any],
    ) -> EquipmentDTO:
        """Convert one raw component into an EquipmentDTO."""

        component_id = component.get("component-id")

        if not component_id:
            raise ValueError(
                f"Network Element {ne_id!r} contains "
                f"{component_class!r} without component-id"
            )

        return EquipmentDTO(
            source_system="NSP",
            ne_id=ne_id,
            component_id=component_id,
            component_class=component_class,
            name=component.get("name"),
            parent=component.get("parent"),
            description=component.get("description"),
            admin_state=component.get("admin-state"),
            oper_state=component.get("oper-state"),
            availability_state=component.get(
                "availability-state"
            ),
            part_number=component.get("part-number"),
            serial_number=component.get("serial-num"),
            manufacturer=component.get("mfg-name"),
            manufacturer_assembly_number=component.get(
                "mfg-assembly-number"
            ),
            parent_rel_pos=component.get("parent-rel-pos"),
            source_type=component.get("source-type"),
            raw_component=component,
        )