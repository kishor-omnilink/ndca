"""
SYNC-001 - Inventory Synchronization Service.

Synchronizes the Network Element inventory discovered from Nokia NSP
into the NDCA PostgreSQL inventory database.

Transaction lifecycle is owned by this service.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from ndca.models.network_element import NetworkElement
from ndca.models.sync_result import SyncResult
from ndca.repositories.network_element_repository import (
    NetworkElementRepository,
)


class InventorySyncService:
    """Synchronize discovered Network Elements into the database."""

    def __init__(self, session: Session) -> None:
        """Initialize the synchronization service."""

        self._session = session
        self._repository = NetworkElementRepository(session)

    def synchronize(
        self,
        discovered: list[NetworkElement],
    ) -> SyncResult:
        """
        Synchronize discovered Network Elements.

        The complete synchronization is performed as one transaction.

        Parameters
        ----------
        discovered:
            Network Elements produced by the existing collector/mapper.

        Returns
        -------
        SyncResult
            Statistics for this synchronization run.
        """

        sync_id = str(uuid4())

        result = SyncResult(
            sync_id=sync_id,
            total_discovered=len(discovered),
        )

        now = datetime.now(timezone.utc)

        try:
            existing = {
                entity.ne_id: entity
                for entity in self._repository.find_all()
            }

            discovered_ids: set[str] = set()

            for incoming in discovered:
                discovered_ids.add(incoming.ne_id)

                current = existing.get(incoming.ne_id)

                if current is None:
                    incoming.sync_status = "SUCCESS"
                    incoming.last_sync = now
                    incoming.is_active = True

                    self._repository.save(incoming)
                    result.created += 1
                    continue

                changed = self._update_entity(
                    current,
                    incoming,
                    now,
                )

                if changed:
                    result.updated += 1
                else:
                    result.unchanged += 1

            # Elements previously known to NDCA but no longer returned
            # by the complete NSP inventory are marked inactive.
            for ne_id, current in existing.items():
                if ne_id not in discovered_ids and current.is_active:
                    current.is_active = False
                    current.sync_status = "SUCCESS"
                    current.last_sync = now
                    result.deactivated += 1

            self._session.commit()

            result.status = "SUCCESS"
            return result

        except Exception:
            self._session.rollback()
            result.status = "FAILED"
            result.failed = 1
            raise

    @staticmethod
    def _update_entity(
        current: NetworkElement,
        incoming: NetworkElement,
        now: datetime,
    ) -> bool:
        """Update an existing entity and return whether it changed."""

        fields = (
            "ne_name",
            "ip_address",
            "system_type",
            "software_version",
            "vendor",
            "component_id",
            "display_name",
            "admin_state",
            "oper_state",
        )

        changed = False

        for field in fields:
            new_value = getattr(incoming, field)
            old_value = getattr(current, field)

            if old_value != new_value:
                setattr(current, field, new_value)
                changed = True

        if not current.is_active:
            current.is_active = True
            changed = True

        current.sync_status = "SUCCESS"
        current.last_sync = now

        return changed
