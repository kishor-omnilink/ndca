"""
Inventory Snapshot Service
"""

from uuid import uuid4

from ndca.collectors.inventory.network_element_collector import (
    NetworkElementCollector,
)

from ndca.core.config import settings

from ndca.models.inventory_snapshot import InventorySnapshot


class InventorySnapshotService:
    """
    Creates InventorySnapshot objects.
    """

    def __init__(self):

        self.collector = NetworkElementCollector()

    def collect(self) -> InventorySnapshot:

        response = self.collector.collect()

        return InventorySnapshot(

            sync_id=str(uuid4()),

            source="Nokia NSP",

            endpoint=settings.nsp_network_element_endpoint,

            raw_data=response,
        )

    def close(self):

        self.collector.close()