"""
SYNC-009 Equipment Mapper tests.
"""

from __future__ import annotations

import unittest

from ndca.mappers.equipment_mapper import EquipmentMapper
from ndca.models.inventory_snapshot import InventorySnapshot


class TestEquipmentMapper(unittest.TestCase):
    """Validate physical equipment extraction."""

    def make_snapshot(
        self,
        hardware_component: dict,
    ) -> InventorySnapshot:
        """Create a representative NSP inventory snapshot."""

        return InventorySnapshot(
            sync_id="sync-009-test",
            source="NSP",
            endpoint="/restconf/data/nsp-equipment:network/network-element",
            raw_data={
                "nsp-equipment:network-element": [
                    {
                        "ne-id": "172.26.0.20",
                        "ne-name": "OCAC-JAJPUR-NAR01",
                        "hardware-component": hardware_component,
                    }
                ]
            },
        )

    def test_extracts_shelf(self) -> None:
        """Shelf component should become an EquipmentDTO."""

        snapshot = self.make_snapshot(
            {
                "shelf": [
                    {
                        "component-id": "shelf=1",
                        "class": "shelf",
                        "name": "Shelf-1",
                        "admin-state": "unlocked",
                        "oper-state": "enabled",
                        "parent-rel-pos": 1,
                    }
                ]
            }
        )

        result = EquipmentMapper.map(snapshot)

        self.assertEqual(len(result), 1)

        dto = result[0]

        self.assertEqual(dto.ne_id, "172.26.0.20")
        self.assertEqual(dto.component_id, "shelf=1")
        self.assertEqual(dto.component_class, "shelf")
        self.assertEqual(dto.name, "Shelf-1")
        self.assertEqual(dto.admin_state, "unlocked")
        self.assertEqual(dto.oper_state, "enabled")

    def test_extracts_card(self) -> None:
        """Card fields should be normalized."""

        snapshot = self.make_snapshot(
            {
                "card": [
                    {
                        "component-id": "shelf=1/cardSlot=1/card=1",
                        "class": "card",
                        "name": "Card-1/1",
                        "parent": (
                            "/nsp-equipment:network/"
                            "network-element[ne-id='172.26.0.20']/"
                            "hardware-component/container/"
                            "cardSlot=1"
                        ),
                        "part-number": "3HE11282ABRA01",
                        "serial-num": "NS243560119",
                        "mfg-name": "Nokia",
                        "mfg-assembly-number": "82-1144-03",
                        "admin-state": "unlocked",
                        "oper-state": "enabled",
                        "source-type": "mdm",
                        "parent-rel-pos": 1,
                    }
                ]
            }
        )

        result = EquipmentMapper.map(snapshot)

        self.assertEqual(len(result), 1)

        dto = result[0]

        self.assertEqual(
            dto.component_id,
            "shelf=1/cardSlot=1/card=1",
        )
        self.assertEqual(dto.component_class, "card")
        self.assertEqual(dto.part_number, "3HE11282ABRA01")
        self.assertEqual(dto.serial_number, "NS243560119")
        self.assertEqual(dto.manufacturer, "Nokia")
        self.assertEqual(dto.parent_rel_pos, 1)

    def test_extracts_port(self) -> None:
        """Physical port should be collected."""

        snapshot = self.make_snapshot(
            {
                "port": [
                    {
                        "component-id": (
                            "shelf=1/cardSlot=1/card=1/"
                            "mdaSlot=2/mda=2/port=1/2/12"
                        ),
                        "class": "port",
                        "name": "1/2/12",
                        "parent": (
                            "/nsp-equipment:network/"
                            "network-element[ne-id='172.26.0.20']/"
                            "hardware-component/container/"
                            "mdaSlot=2"
                        ),
                        "admin-state": "unlocked",
                        "oper-state": "enabled",
                        "parent-rel-pos": 12,
                    }
                ]
            }
        )

        result = EquipmentMapper.map(snapshot)

        self.assertEqual(len(result), 1)

        dto = result[0]

        self.assertEqual(dto.component_class, "port")
        self.assertEqual(dto.name, "1/2/12")
        self.assertEqual(dto.parent_rel_pos, 12)

    def test_extracts_multiple_component_types(self) -> None:
        """Multiple physical component classes should be collected."""

        snapshot = self.make_snapshot(
            {
                "shelf": [
                    {
                        "component-id": "shelf=1",
                    }
                ],
                "container": [
                    {
                        "component-id": "shelf=1/cardSlot=1",
                    }
                ],
                "card": [
                    {
                        "component-id": (
                            "shelf=1/cardSlot=1/card=1"
                        ),
                    }
                ],
                "port": [
                    {
                        "component-id": (
                            "shelf=1/cardSlot=1/"
                            "card=1/port=1"
                        ),
                    }
                ],
            }
        )

        result = EquipmentMapper.map(snapshot)

        self.assertEqual(len(result), 4)

        classes = {
            dto.component_class
            for dto in result
        }

        self.assertEqual(
            classes,
            {
                "shelf",
                "container",
                "card",
                "port",
            },
        )

    def test_unknown_component_class_is_retained(self) -> None:
        """Unknown classes must not be silently discarded."""

        snapshot = self.make_snapshot(
            {
                "future-component": [
                    {
                        "component-id": "future=1",
                        "name": "Future Component",
                    }
                ]
            }
        )

        result = EquipmentMapper.map(snapshot)

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0].component_class,
            "future-component",
        )

    def test_empty_hardware_component(self) -> None:
        """An empty hardware-component object is valid."""

        snapshot = self.make_snapshot({})

        result = EquipmentMapper.map(snapshot)

        self.assertEqual(result, [])

    def test_missing_component_id_is_rejected(self) -> None:
        """A component without identity must fail."""

        snapshot = self.make_snapshot(
            {
                "card": [
                    {
                        "name": "Invalid Card",
                    }
                ]
            }
        )

        with self.assertRaises(ValueError):
            EquipmentMapper.map(snapshot)

    def test_invalid_hardware_component_structure_is_rejected(
        self,
    ) -> None:
        """hardware-component must be a JSON object."""

        snapshot = self.make_snapshot(
            []
        )

        with self.assertRaises(ValueError):
            EquipmentMapper.map(snapshot)

    def test_missing_network_element_id_is_rejected(self) -> None:
        """A Network Element without ne-id must fail."""

        snapshot = InventorySnapshot(
            sync_id="sync-009-test",
            source="NSP",
            endpoint="/test",
            raw_data={
                "nsp-equipment:network-element": [
                    {
                        "ne-name": "INVALID",
                        "hardware-component": {},
                    }
                ]
            },
        )

        with self.assertRaises(ValueError):
            EquipmentMapper.map(snapshot)

    def test_raw_component_is_preserved(self) -> None:
        """Original Nokia component data must remain available."""

        component = {
            "component-id": "shelf=1/cardSlot=1/card=1",
            "class": "card",
            "custom-field": "preserve-me",
        }

        snapshot = self.make_snapshot(
            {
                "card": [component],
            }
        )

        result = EquipmentMapper.map(snapshot)

        self.assertEqual(
            result[0].raw_component,
            component,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)