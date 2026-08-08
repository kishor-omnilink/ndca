"""
SYNC-003 database persistence validation.

Validates that SynchronizationRun can be persisted and retrieved
using the project's real SQLAlchemy PostgreSQL session configuration.

The test creates the SynchronizationRun table only when it does
not already exist. Test data is removed after the test.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import inspect, select

from ndca.database.base import Base
from ndca.database.engine import engine
from ndca.database.session import get_session
from ndca.models.enums import SyncStatus
from ndca.models.synchronization_run import SynchronizationRun


def ensure_table_exists() -> bool:
    """
    Ensure the SynchronizationRun table exists.

    Returns
    -------
    bool
        True when this test created the table.
        False when the table already existed.
    """

    inspector = inspect(engine)

    table_name = SynchronizationRun.__tablename__

    if inspector.has_table(table_name):
        return False

    Base.metadata.create_all(
        bind=engine,
        tables=[SynchronizationRun.__table__],
    )

    return True


def test_synchronization_run_persistence() -> None:
    """Validate SynchronizationRun persistence with PostgreSQL."""

    ensure_table_exists()

    sync_id = f"sync-test-{uuid4()}"

    session = get_session()

    try:
        started_at = datetime.now(timezone.utc)

        synchronization_run = SynchronizationRun(
            sync_id=sync_id,
            started_at=started_at,
            completed_at=None,
            total_discovered=10,
            created=2,
            updated=3,
            deactivated=1,
            unchanged=4,
            failed=0,
            status=SyncStatus.SUCCESS,
            error_message=None,
        )

        session.add(synchronization_run)
        session.commit()

        session.expire_all()

        statement = select(SynchronizationRun).where(
            SynchronizationRun.sync_id == sync_id
        )

        result = session.scalar(statement)

        assert result is not None
        assert result.sync_id == sync_id
        assert result.total_discovered == 10
        assert result.created == 2
        assert result.updated == 3
        assert result.deactivated == 1
        assert result.unchanged == 4
        assert result.failed == 0
        assert result.status == SyncStatus.SUCCESS
        assert result.started_at is not None

    finally:
        session.rollback()

        existing = session.scalar(
            select(SynchronizationRun).where(
                SynchronizationRun.sync_id == sync_id
            )
        )

        if existing is not None:
            session.delete(existing)
            session.commit()

        session.close()

    # The test deliberately does not drop the table when it had to
    # create it. The table is part of the SYNC-003 schema and should
    # remain available for subsequent validation.



if __name__ == "__main__":
    test_synchronization_run_persistence()
    print("SYNC-003 persistence test: PASS")