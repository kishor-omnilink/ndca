"""
Network Element ORM model.

Represents a managed network element discovered from Nokia NFM-P.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from ndca.models.inventory_base import InventoryBase

if TYPE_CHECKING:
    from ndca.models.shelf import Shelf


class NetworkElement(InventoryBase):
    """
    Root inventory object.

    One Network Element
        -> many Shelves
        -> many Cards
        -> many Ports
    """

    __tablename__ = "inventory_network_element"

    ne_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
        doc="Business key returned by NFM-P",
    )

    ne_name: Mapped[str | None] = mapped_column(
        String(255)
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(64)
    )

    system_type: Mapped[str | None] = mapped_column(
        String(128)
    )

    software_version: Mapped[str | None] = mapped_column(
        String(128)
    )

    vendor: Mapped[str | None] = mapped_column(
        String(64),
        default="Nokia"
    )

    shelves: Mapped[list["Shelf"]] = relationship(
        "Shelf",
        back_populates="network_element",
        cascade="all, delete-orphan",
    )
