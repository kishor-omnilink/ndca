"""
Equipment DTOs.

Normalized representation of physical equipment discovered from
Nokia NSP inventory responses.

SYNC-009:
    Collection and normalization only.

ORM persistence/reconciliation belongs to SYNC-010.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class EquipmentDTO:
    """Normalized physical equipment component."""

    source_system: str
    ne_id: str
    component_id: str
    component_class: str

    name: str | None = None
    parent: str | None = None
    description: str | None = None

    admin_state: str | None = None
    oper_state: str | None = None
    availability_state: list[Any] | None = None

    part_number: str | None = None
    serial_number: str | None = None

    manufacturer: str | None = None
    manufacturer_assembly_number: str | None = None

    parent_rel_pos: int | None = None
    source_type: str | None = None

    raw_component: dict[str, Any] | None = None