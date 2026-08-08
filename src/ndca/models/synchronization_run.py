"""
Synchronization Run ORM model.

Represents the persistent execution history of one inventory
synchronization run.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ndca.database.base import Base
from ndca.models.base_mixin import BaseMixin
from ndca.models.enums import SyncStatus


class SynchronizationRun(Base, BaseMixin):
    """
    Persistent history of one inventory synchronization run.

    This is an operational/audit entity rather than a network
    inventory entity, so it intentionally does not inherit
    InventoryBase.
    """

    __tablename__ = "inventory_synchronization_run"

    sync_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique synchronization run identifier",
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Synchronization start timestamp (UTC)",
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Synchronization completion timestamp (UTC)",
    )

    total_discovered: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total Network Elements discovered",
    )

    created: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Network Elements created",
    )

    updated: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Network Elements updated",
    )

    deactivated: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Network Elements deactivated",
    )

    unchanged: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Network Elements unchanged",
    )

    failed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Network Elements that failed processing",
    )

    status: Mapped[SyncStatus] = mapped_column(
        Enum(SyncStatus, name="sync_status_enum"),
        nullable=False,
        default=SyncStatus.PENDING,
        comment="Synchronization execution status",
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Synchronization failure details",
    )