"""
Synchronization Run repository.

Provides persistence operations for synchronization run history.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ndca.models.synchronization_run import SynchronizationRun
from ndca.repositories.base_repository import BaseRepository
from ndca.repositories.exceptions import RepositoryQueryError


class SynchronizationRunRepository(BaseRepository[SynchronizationRun]):
    """
    Repository for SynchronizationRun entities.

    The synchronization ``sync_id`` is treated as the business key.

    Transaction lifecycle is deliberately not managed here.
    The calling service owns commit, rollback, and session close.
    """

    def __init__(self, session: Session) -> None:
        """Initialize the Synchronization Run repository."""

        super().__init__(
            session=session,
            model=SynchronizationRun,
        )

    def find_by_sync_id(
        self,
        sync_id: str,
    ) -> SynchronizationRun | None:
        """
        Find a synchronization run by its business identifier.

        Parameters
        ----------
        sync_id:
            Unique synchronization run identifier.

        Returns
        -------
        SynchronizationRun | None
            Matching synchronization run, or None.
        """

        statement = select(SynchronizationRun).where(
            SynchronizationRun.sync_id == sync_id
        )

        try:
            return self._session.scalar(statement)

        except SQLAlchemyError as ex:
            raise RepositoryQueryError(
                "Failed to find synchronization run "
                f"with sync_id={sync_id!r}: {ex}"
            ) from ex

    def find_all(self) -> list[SynchronizationRun]:
        """Return all synchronization runs."""

        statement = (
            select(SynchronizationRun)
            .order_by(
                SynchronizationRun.started_at.desc()
            )
        )

        try:
            return list(
                self._session.scalars(statement).all()
            )

        except SQLAlchemyError as ex:
            raise RepositoryQueryError(
                "Failed to retrieve synchronization runs"
            ) from ex

    def save(
        self,
        entity: SynchronizationRun,
    ) -> SynchronizationRun:
        """
        Add a synchronization run to the current transaction.

        This method does not commit.
        """

        self._session.add(entity)

        return entity

    def update(
        self,
        entity: SynchronizationRun,
    ) -> SynchronizationRun:
        """
        Mark an existing synchronization run for persistence.

        This method does not commit.
        """

        self._session.add(entity)

        return entity

    def save_or_update(
        self,
        entity: SynchronizationRun,
    ) -> SynchronizationRun:
        """
        Add or update a synchronization run.

        The SQLAlchemy session determines whether the supplied
        entity is transient or already persistent.
        """

        self._session.add(entity)

        return entity