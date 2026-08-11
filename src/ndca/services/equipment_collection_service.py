"""
SYNC-009 - Equipment Collection Service.

Coordinates equipment extraction from an InventorySnapshot.

This service performs collection/extraction/normalization only.

Persistence, identity, lifecycle management and reconciliation
belong to SYNC-010.
"""

from __future__ import annotations

from ndca.mappers.equipment_mapper import EquipmentMapper
from ndca.models.dto.equipment import EquipmentDTO
from ndca.models.inventory_snapshot import InventorySnapshot


class EquipmentCollectionService:
    """Extract normalized equipment information from an inventory snapshot."""

    def __init__(
        self,
        mapper: EquipmentMapper | None = None,
    ) -> None:
        """Initialize the equipment collection service."""
        self._mapper = mapper or EquipmentMapper()

    def collect(
        self,
        snapshot: InventorySnapshot,
    ) -> list[EquipmentDTO]:
        """
        Extract equipment DTOs from an inventory snapshot.

        Persistence, identity, lifecycle management and reconciliation
        are intentionally outside this service.
        """
        if not isinstance(snapshot, InventorySnapshot):
            raise TypeError("snapshot must be an InventorySnapshot")

        return self._mapper.map(snapshot)