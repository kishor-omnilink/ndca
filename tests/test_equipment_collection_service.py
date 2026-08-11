"""
SYNC-009 Equipment Collection Service tests.
"""

from __future__ import annotations

import unittest
from unittest.mock import Mock

from ndca.models.dto.equipment import EquipmentDTO
from ndca.models.inventory_snapshot import InventorySnapshot
from ndca.services.equipment_collection_service import (
    EquipmentCollectionService,
)


class TestEquipmentCollectionService(unittest.TestCase):
    """Validate equipment collection orchestration."""

    def setUp(self) -> None:
        self.snapshot = InventorySnapshot(
            sync_id="sync-009-service-test",
            source="Nokia NSP",
            endpoint=(
                "/restconf/data/"
                "nsp-equipment:network/network-element"
            ),
            raw_data={
                "nsp-equipment:network-element": [
                    {
                        "ne-id": "172.26.0.20",
                        "ne-name": "TEST-NE",
                        "hardware-component": {
                            "shelf": [
                                {
                                    "component-id": "shelf=1",
                                    "class": "shelf",
                                    "name": "Shelf-1",
                                }
                            ],
                            "card": [
                                {
                                    "component-id": (
                                        "shelf=1/cardSlot=1/card=1"
                                    ),
                                    "class": "card",
                                    "name": "Card-1/1",
                                }
                            ],
                        },
                    }
                ]
            },
        )

    def test_collect_returns_equipment_dtos(self) -> None:
        service = EquipmentCollectionService()
        result = service.collect(self.snapshot)

        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], EquipmentDTO)
        self.assertIsInstance(result[1], EquipmentDTO)

    def test_collect_extracts_expected_components(self) -> None:
        service = EquipmentCollectionService()
        result = service.collect(self.snapshot)

        component_ids = {dto.component_id for dto in result}

        self.assertEqual(
            component_ids,
            {
                "shelf=1",
                "shelf=1/cardSlot=1/card=1",
            },
        )

    def test_collect_preserves_network_element_identity(self) -> None:
        service = EquipmentCollectionService()
        result = service.collect(self.snapshot)

        self.assertTrue(result)

        for dto in result:
            self.assertEqual(dto.ne_id, "172.26.0.20")

    def test_collect_uses_injected_mapper(self) -> None:
        mapper = Mock()

        expected = [
            EquipmentDTO(
                source_system="NSP",
                ne_id="172.26.0.20",
                component_id="shelf=1",
                component_class="shelf",
            )
        ]

        mapper.map.return_value = expected

        service = EquipmentCollectionService(mapper=mapper)
        result = service.collect(self.snapshot)

        self.assertEqual(result, expected)
        mapper.map.assert_called_once_with(self.snapshot)

    def test_collect_propagates_mapper_failure(self) -> None:
        mapper = Mock()
        mapper.map.side_effect = ValueError(
            "Invalid equipment structure"
        )

        service = EquipmentCollectionService(mapper=mapper)

        with self.assertRaisesRegex(
            ValueError,
            "Invalid equipment structure",
        ):
            service.collect(self.snapshot)

    def test_collect_rejects_invalid_snapshot(self) -> None:
        service = EquipmentCollectionService()

        with self.assertRaises(TypeError):
            service.collect({"invalid": "snapshot"})  # type: ignore[arg-type]

    def test_empty_snapshot_returns_empty_list(self) -> None:
        snapshot = InventorySnapshot(
            sync_id="empty",
            source="Nokia NSP",
            endpoint="/test",
            raw_data={
                "nsp-equipment:network-element": []
            },
        )

        service = EquipmentCollectionService()
        result = service.collect(snapshot)

        self.assertEqual(result, [])

    def test_missing_hardware_component_returns_empty_list(self) -> None:
        snapshot = InventorySnapshot(
            sync_id="no-hardware",
            source="Nokia NSP",
            endpoint="/test",
            raw_data={
                "nsp-equipment:network-element": [
                    {
                        "ne-id": "172.26.0.20",
                        "ne-name": "TEST-NE",
                    }
                ]
            },
        )

        service = EquipmentCollectionService()
        result = service.collect(snapshot)

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)