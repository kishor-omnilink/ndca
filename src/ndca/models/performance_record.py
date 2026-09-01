"""
Performance Record ORM model.

SYNC-012-D.1.4
----------------
Durable persistence model for normalized NDCA performance records.

The model intentionally mirrors the normalized PerformanceRecord DTO while
remaining independent from the collector and mapper implementations.

TimescaleDB:
    collection_time is the hypertable time dimension because it is mandatory
    for every normalized record. source_time preserves the source/NFM-P
    measurement timestamp when available.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ndca.database.base import Base
from ndca.models.base_mixin import BaseMixin


class PerformanceRecordModel(Base, BaseMixin):
    """
    Persistent normalized performance measurement.

    ``id`` is the internal surrogate key inherited from BaseMixin.

    No database-level uniqueness constraint is imposed on the observation
    identity at this stage. Historical idempotency is handled explicitly by
    the repository/service boundary until the domain observation identity is
    fully established.
    """

    __tablename__ = "performance_record"

    sync_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        comment="NDCA synchronization run identifier",
    )

    source: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="Source system, for example NFM-P",
    )

    xml_class: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
        index=True,
        comment="Verified source XML API class",
    )

    category: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        index=True,
        comment="Normalized performance category",
    )

    object_id: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
        index=True,
        comment="Source object identifier",
    )

    object_name: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
        comment="Source object display/name",
    )

    metric: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        index=True,
        comment="Normalized metric name",
    )

    metric_source_name: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        comment="Original source metric name",
    )

    value: Mapped[Any] = mapped_column(
        JSONB,
        nullable=True,
        comment="Normalized metric value",
    )

    collection_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        primary_key=True,
        index=True,
        comment="NDCA collection/ingestion timestamp (UTC); TimescaleDB time dimension",
    )

    source_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Source measurement timestamp (UTC), when supplied by source",
    )

    persistence_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="NDCA persistence timestamp (UTC)",
    )

    is_historical: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        index=True,
        default=False,
        comment="True for historical source observations",
    )

    raw_payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Complete normalized-source payload retained for evidence/audit",
    )

    evidence_status: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
        comment="Evidence/verification status",
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Persistence or normalization notes",
    )
