"""
SYNC-010 - Equipment repository.

Provides persistence operations for source-neutral physical equipment.
Transaction lifecycle remains owned by the calling service.
"""

from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ndca.models.equipment import Equipment
from ndca.repositories.base_repository import BaseRepository
from ndca.repositories.exceptions import RepositoryQueryError


class EquipmentRepository(BaseRepository[Equipment]):
    """Repository for durable Equipment entities."""

    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Equipment)

    def find_by_identity(
        self,
        source_system: str,
        network_element_id: int,
        component_class: str,
        component_id: str,
    ) -> Equipment | None:
        """Find an equipment record using its deterministic business identity."""

        stmt = select(Equipment).where(
            Equipment.source_system == source_system,
            Equipment.network_element_id == network_element_id,
            Equipment.component_class == component_class,
            Equipment.component_id == component_id,
        )

        try:
            return self._session.scalar(stmt)
        except SQLAlchemyError as ex:
            raise RepositoryQueryError(
                "Failed to find equipment by identity"
            ) from ex

    def find_by_network_element_id(
        self,
        network_element_id: int,
    ) -> list[Equipment]:
        """Return all equipment associated with one Network Element."""

        stmt = (
            select(Equipment)
            .where(Equipment.network_element_id == network_element_id)
            .order_by(Equipment.component_class, Equipment.component_id)
        )

        try:
            return list(self._session.scalars(stmt).all())
        except SQLAlchemyError as ex:
            raise RepositoryQueryError(
                f"Failed to retrieve equipment for network_element_id={network_element_id}"
            ) from ex

    def find_all(self) -> list[Equipment]:
        """Return all equipment records."""

        stmt = select(Equipment)

        try:
            return list(self._session.scalars(stmt).all())
        except SQLAlchemyError as ex:
            raise RepositoryQueryError("Failed to retrieve all equipment") from ex

    def save(self, entity: Equipment) -> Equipment:
        """Add an equipment entity to the current transaction without committing."""

        self._session.add(entity)
        return entity

    def save_all(self, entities: list[Equipment]) -> None:
        """Add multiple equipment entities to the current transaction."""

        self._session.add_all(entities)

    def mark_missing_inactive(
        self,
        network_element_id: int,
        seen_identity_keys: set[tuple[str, str, str]],
    ) -> int:
        """
        Mark active equipment missing from a complete NE snapshot inactive.

        ``seen_identity_keys`` contains ``(source_system, component_class,
        component_id)`` tuples for the current Network Element.
        """

        try:
            current = self.find_by_network_element_id(network_element_id)
            changed = 0

            for entity in current:
                key = (
                    entity.source_system,
                    entity.component_class,
                    entity.component_id,
                )
                if entity.is_active and key not in seen_identity_keys:
                    entity.is_active = False
                    changed += 1

            return changed
        except SQLAlchemyError as ex:
            raise RepositoryQueryError(
                f"Failed to reconcile missing equipment for network_element_id={network_element_id}"
            ) from ex
