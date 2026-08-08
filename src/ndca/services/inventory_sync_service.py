"""
SYNC-004 - Inventory Synchronization Service.

Synchronizes discovered Network Elements into the database and
persists the execution history of each successful synchronization.

Transaction lifecycle is owned by this service.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from ndca.models.enums import SyncStatus
from ndca.models.network_element import NetworkElement
from ndca.models.sync_result import SyncResult
from ndca.models.synchronization_run import SynchronizationRun
from ndca.repositories.network_element_repository import (
    NetworkElementRepository,
)
from ndca.repositories.synchronization_run_repository import (
    SynchronizationRunRepository,
)


class InventorySyncService:
    """Synchronize discovered Network Elements into the database."""

    def __init__(self, session: Session) -> None:
        """Initialize the synchronization service."""

        self._session = session
        self._repository = NetworkElementRepository(session)
        self._run_repository = SynchronizationRunRepository(session)

    def synchronize(
        self,
        discovered: list[NetworkElement],
    ) -> SyncResult:
        """
        Synchronize discovered Network Elements.

        The complete synchronization and synchronization-run record
        are persisted as one database transaction.

        Parameters
        ----------
        discovered:
            Network Elements produced by the existing collector/mapper.

        Returns
        -------
        SyncResult
            Statistics for this synchronization run.

        Raises
        ------
        Exception
            Re-raises any synchronization exception after rollback.
        """

        sync_id = str(uuid4())
        started_at = datetime.now(timezone.utc)

        result = SyncResult(
            sync_id=sync_id,
            total_discovered=len(discovered),
        )

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
                    incoming.sync_status = SyncStatus.SUCCESS
                    incoming.last_sync = started_at
                    incoming.is_active = True

                    self._repository.save(incoming)
                    result.created += 1
                    continue

                changed = self._update_entity(
                    current,
                    incoming,
                    started_at,
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
                    current.sync_status = SyncStatus.SUCCESS
                    current.last_sync = started_at
                    result.deactivated += 1

            completed_at = datetime.now(timezone.utc)

            result.status = "SUCCESS"

            synchronization_run = SynchronizationRun(
                sync_id=sync_id,
                started_at=started_at,
                completed_at=completed_at,
                total_discovered=result.total_discovered,
                created=result.created,
                updated=result.updated,
                deactivated=result.deactivated,
                unchanged=result.unchanged,
                failed=result.failed,
                status=SyncStatus.SUCCESS,
                error_message=None,
            )

            self._run_repository.save(synchronization_run)

            self._session.commit()

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

        current.sync_status = SyncStatus.SUCCESS
        current.last_sync = now

        return changed