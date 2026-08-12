"""
SYNC-010 - Equipment synchronization service.

Persists normalized EquipmentDTO objects and reconciles their lifecycle
against a complete Network Element inventory snapshot.

Transaction lifecycle is owned by this service.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ndca.models.dto.equipment import EquipmentDTO
from ndca.models.equipment import Equipment
from ndca.models.equipment_sync_result import EquipmentSyncResult
from ndca.models.enums import SyncStatus
from ndca.repositories.equipment_repository import EquipmentRepository
from ndca.repositories.network_element_repository import NetworkElementRepository


class EquipmentSyncService:
    """Synchronize normalized physical equipment into PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._repository = EquipmentRepository(session)
        self._network_element_repository = NetworkElementRepository(session)

    def synchronize(
        self,
        discovered: list[EquipmentDTO],
        complete_network_element_ids: set[str] | None = None,
    ) -> EquipmentSyncResult:
        """
        Synchronize equipment and optionally reconcile missing equipment.

        Parameters
        ----------
        discovered:
            Normalized equipment produced by EquipmentMapper.
        complete_network_element_ids:
            Network Element identifiers covered by a complete inventory
            snapshot. Missing equipment is deactivated only for these NEs.
            If omitted, no deactivation is performed.
        """

        now = datetime.now(timezone.utc)
        result = EquipmentSyncResult(total_discovered=len(discovered))
        seen_by_ne: dict[int, set[tuple[str, str, str]]] = {}
        seen_input_keys: set[tuple[str, str, str, str]] = set()

        try:
            for dto in discovered:
                network_element = self._network_element_repository.find_by_ne_id(dto.ne_id)
                if network_element is None:
                    raise ValueError(
                        f"Cannot synchronize equipment for unknown Network Element "
                        f"ne_id={dto.ne_id!r}"
                    )

                identity = (
                    dto.source_system,
                    dto.ne_id,
                    dto.component_class,
                    dto.component_id,
                )
                if identity in seen_input_keys:
                    raise ValueError(
                        f"Duplicate equipment identity in snapshot: {identity!r}"
                    )
                seen_input_keys.add(identity)

                internal_key = (
                    dto.source_system,
                    dto.component_class,
                    dto.component_id,
                )
                seen_by_ne.setdefault(network_element.id, set()).add(internal_key)

                current = self._repository.find_by_identity(
                    source_system=dto.source_system,
                    network_element_id=network_element.id,
                    component_class=dto.component_class,
                    component_id=dto.component_id,
                )

                if current is None:
                    entity = self._to_entity(dto, network_element.id, now)
                    self._repository.save(entity)
                    result.created += 1
                    continue

                if not current.is_active:
                    self._update_entity(current, dto, now)
                    current.is_active = True
                    current.sync_status = SyncStatus.SUCCESS
                    result.reactivated += 1
                    continue

                changed = self._update_entity(current, dto, now)
                if changed:
                    result.updated += 1
                else:
                    result.unchanged += 1

            if complete_network_element_ids is not None:
                for ne_id in complete_network_element_ids:
                    network_element = self._network_element_repository.find_by_ne_id(ne_id)
                    if network_element is None:
                        raise ValueError(
                            f"Complete snapshot references unknown Network Element "
                            f"ne_id={ne_id!r}"
                        )

                    seen = seen_by_ne.get(network_element.id, set())
                    result.deactivated += self._repository.mark_missing_inactive(
                        network_element.id,
                        seen,
                        now,
                    )

            self._session.commit()
            return result

        except Exception:
            self._session.rollback()
            result.status = "FAILED"
            result.failed = 1
            raise

    @staticmethod
    def _to_entity(
        dto: EquipmentDTO,
        network_element_id: int,
        now: datetime,
    ) -> Equipment:
        """Convert an EquipmentDTO into a new ORM entity."""

        return Equipment(
            source_system=dto.source_system,
            network_element_id=network_element_id,
            component_id=dto.component_id,
            component_class=dto.component_class,
            display_name=dto.name,
            parent=dto.parent,
            description=dto.description,
            admin_state=dto.admin_state,
            oper_state=dto.oper_state,
            availability_state=dto.availability_state,
            part_number=dto.part_number,
            serial_number=dto.serial_number,
            manufacturer=dto.manufacturer,
            manufacturer_assembly_number=dto.manufacturer_assembly_number,
            parent_rel_pos=dto.parent_rel_pos,
            source_type=dto.source_type,
            raw_component=dto.raw_component,
            first_seen=now,
            last_seen=now,
            is_active=True,
            sync_status=SyncStatus.SUCCESS,
            last_sync=now,
        )

    @staticmethod
    def _update_entity(
        current: Equipment,
        dto: EquipmentDTO,
        now: datetime,
    ) -> bool:
        """Update mutable source attributes and return whether they changed."""

        fields = {
            "display_name": dto.name,
            "parent": dto.parent,
            "description": dto.description,
            "admin_state": dto.admin_state,
            "oper_state": dto.oper_state,
            "availability_state": dto.availability_state,
            "part_number": dto.part_number,
            "serial_number": dto.serial_number,
            "manufacturer": dto.manufacturer,
            "manufacturer_assembly_number": dto.manufacturer_assembly_number,
            "parent_rel_pos": dto.parent_rel_pos,
            "source_type": dto.source_type,
            "raw_component": dto.raw_component,
        }

        changed = False
        for field, new_value in fields.items():
            if getattr(current, field) != new_value:
                setattr(current, field, new_value)
                changed = True

        current.last_seen = now
        current.last_sync = now
        current.sync_status = SyncStatus.SUCCESS

        return changed
