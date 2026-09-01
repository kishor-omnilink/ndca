"""SYNC-012-D.1.4 performance persistence.

Revision ID: 0002
Revises: 0001
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the normalized performance persistence table."""

    op.create_table(
        "performance_record",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "sync_id",
            sa.String(length=128),
            nullable=False,
            comment="NDCA synchronization run identifier",
        ),
        sa.Column(
            "source",
            sa.String(length=64),
            nullable=False,
            comment="Source system, for example NFM-P",
        ),
        sa.Column(
            "xml_class",
            sa.String(length=256),
            nullable=True,
            comment="Verified source XML API class",
        ),
        sa.Column(
            "category",
            sa.String(length=256),
            nullable=False,
            comment="Normalized performance category",
        ),
        sa.Column(
            "object_id",
            sa.String(length=1024),
            nullable=False,
            comment="Source object identifier",
        ),
        sa.Column(
            "object_name",
            sa.String(length=1024),
            nullable=True,
            comment="Source object display/name",
        ),
        sa.Column(
            "metric",
            sa.String(length=512),
            nullable=False,
            comment="Normalized metric name",
        ),
        sa.Column(
            "metric_source_name",
            sa.String(length=512),
            nullable=True,
            comment="Original source metric name",
        ),
        sa.Column(
            "value",
            postgresql.JSONB(),
            nullable=True,
            comment="Normalized metric value",
        ),
        sa.Column(
            "collection_time",
            sa.DateTime(timezone=True),
            nullable=False,
            comment=(
                "NDCA collection/ingestion timestamp (UTC); "
                "TimescaleDB time dimension"
            ),
        ),
        sa.Column(
            "source_time",
            sa.DateTime(timezone=True),
            nullable=True,
            comment=(
                "Source measurement timestamp (UTC), "
                "when supplied by source"
            ),
        ),
        sa.Column(
            "persistence_time",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="NDCA persistence timestamp (UTC)",
        ),
        sa.Column(
            "is_historical",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
            comment="True for historical source observations",
        ),
        sa.Column(
            "raw_payload",
            postgresql.JSONB(),
            nullable=True,
            comment="Complete normalized-source payload retained for evidence/audit",
        ),
        sa.Column(
            "evidence_status",
            sa.String(length=64),
            nullable=True,
            comment="Evidence/verification status",
        ),
        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
            comment="Persistence or normalization notes",
        ),
        sa.PrimaryKeyConstraint("id", "collection_time"),
    )

    op.create_index(
        "ix_performance_record_collection_time",
        "performance_record",
        ["collection_time"],
    )
    op.create_index(
        "ix_performance_record_sync_id",
        "performance_record",
        ["sync_id"],
    )
    op.create_index(
        "ix_performance_record_source",
        "performance_record",
        ["source"],
    )
    op.create_index(
        "ix_performance_record_xml_class",
        "performance_record",
        ["xml_class"],
    )
    op.create_index(
        "ix_performance_record_category",
        "performance_record",
        ["category"],
    )
    op.create_index(
        "ix_performance_record_object_id",
        "performance_record",
        ["object_id"],
    )
    op.create_index(
        "ix_performance_record_metric",
        "performance_record",
        ["metric"],
    )
    op.create_index(
        "ix_performance_record_source_time",
        "performance_record",
        ["source_time"],
    )
    op.create_index(
        "ix_performance_record_persistence_time",
        "performance_record",
        ["persistence_time"],
    )
    op.create_index(
        "ix_performance_record_is_historical",
        "performance_record",
        ["is_historical"],
    )
    op.create_index(
        "ix_performance_record_evidence_status",
        "performance_record",
        ["evidence_status"],
    )

    # collection_time is deliberately used as the TimescaleDB time dimension:
    # it is mandatory for both current and historical PerformanceRecord DTOs.
    op.execute(
        """
        SELECT create_hypertable(
            'performance_record',
            'collection_time',
            if_not_exists => TRUE
        )
        """
    )


def downgrade() -> None:
    """Remove the performance persistence table."""

    op.drop_table("performance_record")
