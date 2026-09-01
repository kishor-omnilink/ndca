"""Fix performance_record audit timestamp defaults.

Revision ID: 0003
Revises: 0002
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | Sequence[str] | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add database defaults required by BaseMixin audit timestamps."""

    op.alter_column(
        "performance_record",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
        server_default=sa.func.now(),
    )

    op.alter_column(
        "performance_record",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
        server_default=sa.func.now(),
    )


def downgrade() -> None:
    """Remove the performance audit timestamp defaults."""

    op.alter_column(
        "performance_record",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
        server_default=None,
    )

    op.alter_column(
        "performance_record",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
        server_default=None,
    )
