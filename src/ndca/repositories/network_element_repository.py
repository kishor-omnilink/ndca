"""
Network Element repository.

Provides persistence operations specific to NetworkElement entities.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ndca.models.network_element import NetworkElement
from ndca.repositories.base_repository import BaseRepository
from ndca.repositories.exceptions import RepositoryQueryError


class NetworkElementRepository(BaseRepository[NetworkElement]):
    """
    Repository for NetworkElement entities.

    The NSP ``ne_id`` is treated as the business key.

    Transaction lifecycle is deliberately not managed here.
    The calling service owns commit, rollback, and session close.
    """

    def __init__(self, session: Session) -> None:
        """Initialize the Network Element repository."""

        super().__init__(
            session=session,
            model=NetworkElement,
        )

    def find_by_ne_id(
        self,
        ne_id: str,
    ) -> NetworkElement | None:
        """
        Find a Network Element using its NSP business identifier.

        Parameters
        ----------
        ne_id:
            Network Element identifier returned by NSP.

        Returns
        -------
        NetworkElement | None
            Matching entity, or None when not found.
        """

        stmt = select(NetworkElement).where(
            NetworkElement.ne_id == ne_id
        )

        try:
            return self._session.scalar(stmt)

        except SQLAlchemyError as ex:
            raise RepositoryQueryError(
                f"Failed to find Network Element "
                f"with ne_id={ne_id!r}: {ex}"
            ) from ex

    def find_by_name(
        self,
        name: str,
    ) -> list[NetworkElement]:
        """
        Find Network Elements by partial name.

        The search is case-insensitive.

        Parameters
        ----------
        name:
            Full or partial Network Element name.

        Returns
        -------
        list[NetworkElement]
            Matching Network Elements.
        """

        stmt = (
            select(NetworkElement)
            .where(
                NetworkElement.ne_name.ilike(
                    f"%{name}%"
                )
            )
            .order_by(
                NetworkElement.ne_name.asc()
            )
        )

        try:
            return list(
                self._session.scalars(stmt).all()
            )

        except SQLAlchemyError as ex:
            raise RepositoryQueryError(
                f"Failed to search Network Elements "
                f"by name={name!r}: {ex}"
            ) from ex

    def exists_by_ne_id(
        self,
        ne_id: str,
    ) -> bool:
        """
        Determine whether a Network Element exists.

        Parameters
        ----------
        ne_id:
            NSP Network Element identifier.

        Returns
        -------
        bool
            True when the entity exists.
        """

        stmt = (
            select(NetworkElement.id)
            .where(
                NetworkElement.ne_id == ne_id
            )
            .limit(1)
        )

        try:
            return (
                self._session.scalar(stmt)
                is not None
            )

        except SQLAlchemyError as ex:
            raise RepositoryQueryError(
                f"Failed to check existence of "
                f"Network Element with ne_id={ne_id!r}: {ex}"
            ) from ex

    def save(
        self,
        entity: NetworkElement,
    ) -> NetworkElement:
        """
        Add a Network Element to the current transaction.

        This method does NOT commit.

        Parameters
        ----------
        entity:
            NetworkElement ORM entity.

        Returns
        -------
        NetworkElement
            The supplied entity.
        """

        self._session.add(entity)

        return entity

    def save_all(
        self,
        entities: list[NetworkElement],
    ) -> None:
        """
        Add multiple Network Elements to the current transaction.

        This method does NOT commit.

        Parameters
        ----------
        entities:
            NetworkElement ORM entities.
        """

        self._session.add_all(entities)