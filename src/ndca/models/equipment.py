"""
SYNC-010 - Source-neutral physical equipment ORM model.

Represents a physical equipment component discovered from an inventory
source and associated with an NDCA Network Element.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from ndca.models.inventory_base import InventoryBase


class Equipment(InventoryBase):
    """Durable source-neutral physical equipment inventory object."""

    __tablename__ = "inventory_equipment"

    __table_args__ = (
        UniqueConstraint(
            "source_system",
            "network_element_id",
            "component_class",
            "component_id",
            name="uq_inventory_equipment_identity",
        ),
    )

    source_system: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        doc="Source system identifier, for example NSP or NFM-T",
    )

    network_element_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_network_element.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    component_class: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    parent: Mapped[str | None] = mapped_column(String(1024))
    description: Mapped[str | None] = mapped_column(String(1024))
    availability_state: Mapped[list | None] = mapped_column(JSON)

    part_number: Mapped[str | None] = mapped_column(String(256))
    serial_number: Mapped[str | None] = mapped_column(String(256))
    manufacturer: Mapped[str | None] = mapped_column(String(256))
    manufacturer_assembly_number: Mapped[str | None] = mapped_column(String(256))

    parent_rel_pos: Mapped[int | None] = mapped_column(Integer)
    source_type: Mapped[str | None] = mapped_column(String(128))

    raw_component: Mapped[dict | None] = mapped_column(JSON)

    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="First successful observation of this equipment identity",
    )

    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Most recent successful observation of this equipment identity",
    )
