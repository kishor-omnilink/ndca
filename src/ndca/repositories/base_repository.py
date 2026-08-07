"""
Generic SQLAlchemy Repository.

Every repository inside NDCA inherits from this class.
"""

from __future__ import annotations

from typing import Generic
from typing import TypeVar

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ndca.repositories.exceptions import RepositoryQueryError

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Generic Repository.

    Parameters
    ----------
    session
        SQLAlchemy Session

    model
        ORM model class
    """

    def __init__(
        self,
        session: Session,
        model: type[T],
    ) -> None:

        self._session = session
        self._model = model

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------

    def add(self, entity: T) -> T:
        """
        Add one entity to current transaction.
        """

        self._session.add(entity)

        return entity

    def add_all(
        self,
        entities: list[T],
    ) -> None:
        """
        Add multiple entities.
        """

        self._session.add_all(entities)

    # ---------------------------------------------------------
    # DELETE
    # ---------------------------------------------------------

    def delete(
        self,
        entity: T,
    ) -> None:

        self._session.delete(entity)

    # ---------------------------------------------------------
    # READ
    # ---------------------------------------------------------

    def get_all(self) -> list[T]:

        stmt = select(self._model)

        try:

            return list(
                self._session.scalars(stmt).all()
            )

        except SQLAlchemyError as ex:

            raise RepositoryQueryError(
                str(ex)
            ) from ex

    def count(self) -> int:

        stmt = (
            select(
                func.count()
            )
            .select_from(self._model)
        )

        try:

            value = self._session.scalar(stmt)

            return int(value or 0)

        except SQLAlchemyError as ex:

            raise RepositoryQueryError(
                str(ex)
            ) from ex

    def exists(self) -> bool:

        return self.count() > 0

    def find_first(self) -> T | None:

        stmt = (
            select(self._model)
            .limit(1)
        )

        try:

            return self._session.scalar(stmt)

        except SQLAlchemyError as ex:

            raise RepositoryQueryError(
                str(ex)
            ) from ex