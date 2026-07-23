"""
Shelf ORM model.

Represents a physical shelf/chassis associated with a Network Element.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ndca.models.inventory_base import InventoryBase

if TYPE_CHECKING:
    from ndca.models.network_element import NetworkElement
    


class Shelf(InventoryBase):
    """Shelf inventory object."""

    __tablename__ = "inventory_shelf"

    component_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
        doc="Shelf identifier returned by NFM-P",
    )

    network_element_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_network_element.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    shelf_name: Mapped[str | None] = mapped_column(String(255))

    shelf_type: Mapped[str | None] = mapped_column(String(128))

    network_element: Mapped["NetworkElement"] = relationship(
        "NetworkElement",
        back_populates="shelves",
    )

    # cards: Mapped[list["Card"]] = relationship(
    #     "Card",
    #     back_populates="shelf",
    #     cascade="all, delete-orphan",
    # )
