"""
SYNC-009.3 - Real NSP Network Element payload validation.

This test intentionally consumes the captured Nokia NSP
Get-Network-Element payload rather than a synthetic fixture.

Expected local fixture:
    tests/fixtures/Get-Network-Element.txt
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import unittest

from ndca.mappers.equipment_mapper import EquipmentMapper
from ndca.models.inventory_snapshot import InventorySnapshot


REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_FIXTURE = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "Get-Network-Element.txt"
)


def _fixture_path() -> Path:
    configured = os.environ.get(
        "NDCA_NSP_NETWORK_ELEMENT_FIXTURE"
    )
    if configured:
        return Path(configured)
    return DEFAULT_FIXTURE


def _load_real_nsp_payload() -> dict:
    path = _fixture_path()

    if not path.is_file():
        raise unittest.SkipTest(
            "Real NSP payload fixture not found: "
            f"{path}. Copy the captured Get-Network-Element.txt "
            "into tests/fixtures/ or set "
            "NDCA_NSP_NETWORK_ELEMENT_FIXTURE."
        )

    try:
        payload = json.loads(
            path.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"Real NSP payload is not valid JSON: {path}"
        ) from exc

    if not isinstance(payload, dict):
        raise AssertionError(
            "Real NSP payload root must be a JSON object"
        )

    return payload


class TestEquipmentMapperRealNSPPayload(unittest.TestCase):
    """Validate EquipmentMapper against the captured NSP payload."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = _load_real_nsp_payload()

    def _snapshot(self) -> InventorySnapshot:
        return InventorySnapshot(
            sync_id="sync-009-real-nsp-payload",
            source="Nokia NSP",
            endpoint=(
                "/restconf/data/"
                "nsp-equipment:network/network-element"
            ),
            raw_data=self.payload,
        )

    def test_real_payload_has_expected_network_element_structure(self) -> None:
        elements = self.payload.get(
            "nsp-equipment:network-element"
        )
        self.assertIsInstance(elements, list)
        self.assertGreater(len(elements), 0)

        for element in elements:
            self.assertIsInstance(element, dict)
            self.assertTrue(element.get("ne-id"))

    def test_real_payload_contains_hardware_components(self) -> None:
        elements = self.payload[
            "nsp-equipment:network-element"
        ]

        elements_with_hardware = [
            element
            for element in elements
            if isinstance(
                element.get("hardware-component"),
                dict,
            )
        ]

        self.assertGreater(
            len(elements_with_hardware),
            0,
        )

    def test_real_payload_maps_all_hardware_classes(self) -> None:
        result = EquipmentMapper.map(self._snapshot())

        self.assertGreater(len(result), 0)

        classes = {
            dto.component_class
            for dto in result
        }

        expected_classes = {
            "shelf",
            "container",
            "card",
            "port",
            "fan",
            "power-supply",
        }

        self.assertTrue(
            expected_classes.issubset(classes),
            msg=(
                "Missing expected hardware classes: "
                f"{expected_classes - classes}"
            ),
        )

    def test_real_payload_produces_valid_equipment_dtos(self) -> None:
        result = EquipmentMapper.map(self._snapshot())

        self.assertGreater(len(result), 0)

        for dto in result:
            self.assertEqual(dto.source_system, "NSP")
            self.assertTrue(dto.ne_id)
            self.assertTrue(dto.component_id)
            self.assertTrue(dto.component_class)
            self.assertIsInstance(dto.raw_component, dict)

    def test_real_payload_preserves_component_identity(self) -> None:
        result = EquipmentMapper.map(self._snapshot())

        dto_by_id = {
            dto.component_id: dto
            for dto in result
        }

        expected_ids = {
            "shelf=1",
            "shelf=1/fan=1",
            "shelf=1/powerSupplySlot=2/powerSupply=2",
        }

        missing = expected_ids - dto_by_id.keys()

        self.assertFalse(
            missing,
            msg=(
                "Expected component IDs were not mapped: "
                f"{missing}"
            ),
        )

    def test_real_payload_maps_known_network_element(self) -> None:
        elements = self.payload[
            "nsp-equipment:network-element"
        ]

        matching = [
            element
            for element in elements
            if element.get("ne-id") == "172.26.0.27"
        ]

        self.assertEqual(len(matching), 1)

        snapshot = InventorySnapshot(
            sync_id="sync-009-real-ne-172-26-0-27",
            source="Nokia NSP",
            endpoint=(
                "/restconf/data/"
                "nsp-equipment:network/network-element"
            ),
            raw_data={
                "nsp-equipment:network-element": matching
            },
        )

        result = EquipmentMapper.map(snapshot)

        self.assertGreater(len(result), 0)
        self.assertTrue(
            all(
                dto.ne_id == "172.26.0.27"
                for dto in result
            )
        )

    def test_real_payload_preserves_nested_component_data(self) -> None:
        result = EquipmentMapper.map(self._snapshot())

        nested_components = [
            dto
            for dto in result
            if (
                "card-details" in dto.raw_component
                or "port-details" in dto.raw_component
                or "transceiver-details" in dto.raw_component
            )
        ]

        self.assertGreater(len(nested_components), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
