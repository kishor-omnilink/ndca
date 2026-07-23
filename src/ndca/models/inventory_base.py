"""
Abstract base class for all NFM-P inventory entities.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func, text
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from ndca.database.base import Base
from ndca.models.base_mixin import BaseMixin
from ndca.models.enums import SyncStatus

class InventoryBase(Base, BaseMixin):
    """
    Common fields shared by all inventory objects.

    This class is abstract and is not mapped to a database table.
    """

    __abstract__ = True

    component_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        comment="Unique component identifier from NFM-P"
    )

    display_name: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True
    )

    admin_state: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True
    )

    oper_state: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True
    )

    sync_status: Mapped[SyncStatus] = mapped_column(
        Enum(SyncStatus, name="sync_status_enum"),
        nullable=False,
        server_default=text("'PENDING'")
    )

    last_sync: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true")
    )

    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    @declared_attr.directive
    def __mapper_args__(cls):
        return {"eager_defaults": True}
