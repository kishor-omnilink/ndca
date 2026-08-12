"""
SYNC-004 / SYNC-011-A - Inventory Synchronization Service.

Synchronizes discovered Network Elements into PostgreSQL.

SYNC-011-A adds explicit snapshot completeness handling:

    COMPLETE snapshot
        -> missing active Network Elements may be deactivated

    PARTIAL snapshot
        -> missing Network Elements must NOT be deactivated

Transaction ownership remains inside this service.
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
    """Synchronize discovered Network Elements into PostgreSQL."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        """Initialize the synchronization service."""

        self._session = session

        self._repository = NetworkElementRepository(
            session
        )

        self._run_repository = SynchronizationRunRepository(
            session
        )

    def synchronize(
        self,
        discovered: list[NetworkElement],
        *,
        complete_snapshot: bool = True,
        snapshot_complete: bool | None = None,
    ) -> SyncResult:

        """
        Synchronize discovered Network Elements.

        Parameters
        ----------
        discovered:
            Network Elements produced by the collector and mapper.

        complete_snapshot:
            Indicates whether the Network Element collection is
            authoritative.

            True:
                Missing active Network Elements may be deactivated.

            False:
                Missing Network Elements are left untouched.

        Returns
        -------
        SyncResult
            Statistics for the synchronization.

        Raises
        ------
        Exception
            Any synchronization error is rolled back and re-raised.

        Notes
        -----
        The default value remains True for backward compatibility with
        the previously frozen SYNC-010 direct service contract.

        The production orchestration layer must explicitly pass the
        InventorySnapshot completeness state.
        """
        # SYNC-011-A compatibility alias.
        # Keep complete_snapshot as the existing SYNC-010/SYNC-011
        # service contract while accepting snapshot_complete from
        # the snapshot-safety orchestration/tests.
        if snapshot_complete is not None:
            complete_snapshot = snapshot_complete

        sync_id = str(
            uuid4()
        )

        synchronized_at = datetime.now(
            timezone.utc
        )

        result = SyncResult(
            sync_id=sync_id,
            total_discovered=len(discovered),
        )

        try:
            existing_entities = {
                entity.ne_id: entity
                for entity in self._repository.find_all()
            }

            discovered_ids: set[str] = set()

            for incoming in discovered:
                if not incoming.ne_id:
                    raise ValueError(
                        "Network Element is missing required ne_id"
                    )

                if incoming.ne_id in discovered_ids:
                    raise ValueError(
                        "Duplicate Network Element identity: "
                        f"{incoming.ne_id}"
                    )

                discovered_ids.add(
                    incoming.ne_id
                )

                current = existing_entities.get(
                    incoming.ne_id
                )

                if current is None:
                    incoming.is_active = True
                    incoming.sync_status = (
                        SyncStatus.SUCCESS
                    )
                    incoming.last_sync = (
                        synchronized_at
                    )

                    self._repository.save(
                        incoming
                    )

                    result.created += 1

                    continue

                changed = self._update_entity(
                    current=current,
                    incoming=incoming,
                    synchronized_at=synchronized_at,
                )

                if changed:
                    result.updated += 1
                else:
                    result.unchanged += 1

            if complete_snapshot:
                for (
                    ne_id,
                    current,
                ) in existing_entities.items():

                    if (
                        ne_id not in discovered_ids
                        and current.is_active
                    ):
                        current.is_active = False

                        current.sync_status = (
                            SyncStatus.SUCCESS
                        )

                        current.last_sync = (
                            synchronized_at
                        )

                        result.deactivated += 1

            completed_at = datetime.now(
                timezone.utc
            )

            result.status = "SUCCESS"

            synchronization_run = SynchronizationRun(
                sync_id=sync_id,
                started_at=synchronized_at,
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

            self._run_repository.save(
                synchronization_run
            )

            self._session.commit()

            return result

        except Exception:
            self._session.rollback()

            result.status = "FAILED"
            result.failed = 1

            raise

    @staticmethod
    def _update_entity(
        *,
        current: NetworkElement,
        incoming: NetworkElement,
        synchronized_at: datetime,
    ) -> bool:
        """
        Update an existing Network Element.

        Returns
        -------
        bool
            True when the existing entity changed.
        """

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

        for field_name in fields:
            incoming_value = getattr(
                incoming,
                field_name,
            )

            current_value = getattr(
                current,
                field_name,
            )

            if current_value != incoming_value:
                setattr(
                    current,
                    field_name,
                    incoming_value,
                )

                changed = True

        if not current.is_active:
            current.is_active = True
            changed = True

        current.sync_status = (
            SyncStatus.SUCCESS
        )

        current.last_sync = (
            synchronized_at
        )

        return changed