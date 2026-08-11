"""
SYNC-009.4 - NFM-T Network Element Equipment Adapter tests.

The default test fixture is the real NFM-T response supplied for this
project:

    tests/fixtures/networkElements.json

Set NDCA_NFMT_NETWORK_ELEMENTS_FIXTURE to override the fixture path.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import unittest

from ndca.mappers.nfmt_equipment_mapper import (
    NfmtNetworkElementEquipmentMapper,
)
from ndca.models.dto.equipment import EquipmentDTO
from ndca.models.inventory_snapshot import InventorySnapshot


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = (
    REPO_ROOT / "tests" / "fixtures" / "networkElements.json"
)


def fixture_path() -> Path:
    """Return the configured NFM-T fixture path."""
    configured = os.environ.get(
        "NDCA_NFMT_NETWORK_ELEMENTS_FIXTURE"
    )
    return Path(configured) if configured else DEFAULT_FIXTURE


def load_fixture() -> dict:
    """Load the captured NFM-T Network Elements response."""
    path = fixture_path()

    if not path.is_file():
        raise unittest.SkipTest(
            "NFM-T fixture not found: "
            f"{path}. Copy networkElements.json to "
            "tests/fixtures/ or set "
            "NDCA_NFMT_NETWORK_ELEMENTS_FIXTURE."
        )

    try:
        payload = json.loads(
            path.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"NFM-T fixture is not valid JSON: {path}"
        ) from exc

    if not isinstance(payload, dict):
        raise AssertionError(
            "NFM-T fixture root must be a JSON object"
        )

    return payload


class TestNfmtNetworkElementEquipmentMapper(unittest.TestCase):
    """Validate the NFM-T Network Element adapter."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = load_fixture()

    def snapshot(self) -> InventorySnapshot:
        """Build an NFM-T snapshot from the captured response."""
        return InventorySnapshot(
            sync_id="sync-009-4-nfmt-ne",
            source="NFM-T",
            endpoint=(
                "/NetworkSupervision/rest/api/v1/"
                "networkElements"
            ),
            raw_data=self.payload,
        )

    def test_real_payload_has_response_object(self) -> None:
        response = self.payload.get("response")
        self.assertIsInstance(response, dict)

    def test_real_payload_has_success_status(self) -> None:
        response = self.payload["response"]
        self.assertEqual(response.get("status"), 0)

    def test_real_payload_has_network_elements(self) -> None:
        data = self.payload["response"].get("data")
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_real_payload_contains_18_elements(self) -> None:
        response = self.payload["response"]
        self.assertEqual(response.get("totalRows"), 18)
        self.assertEqual(len(response.get("data", [])), 18)

    def test_mapper_returns_equipment_dtos(self) -> None:
        result = NfmtNetworkElementEquipmentMapper.map(
            self.snapshot()
        )

        self.assertEqual(len(result), 18)
        self.assertTrue(
            all(isinstance(dto, EquipmentDTO) for dto in result)
        )

    def test_mapper_preserves_nfmt_identity(self) -> None:
        result = NfmtNetworkElementEquipmentMapper.map(
            self.snapshot()
        )

        first = result[0]
        self.assertEqual(first.source_system, "NFM-T")
        self.assertTrue(first.ne_id)
        self.assertTrue(first.component_id)
        self.assertEqual(first.component_class, "network-element")

    def test_mapper_preserves_real_fdn_and_ne_id(self) -> None:
        result = NfmtNetworkElementEquipmentMapper.map(
            self.snapshot()
        )

        by_ne_id = {dto.ne_id: dto for dto in result}

        self.assertIn("10.254.0.11", by_ne_id)
        self.assertEqual(
            by_ne_id["10.254.0.11"].component_id,
            "fdn:model:equipment:NetworkElement:603",
        )

    def test_mapper_preserves_raw_nfmt_object(self) -> None:
        result = NfmtNetworkElementEquipmentMapper.map(
            self.snapshot()
        )

        dto = next(
            item
            for item in result
            if item.ne_id == "10.254.0.16"
        )

        self.assertEqual(
            dto.raw_component["neName"],
            "ONET-MRDL-OADM-1",
        )
        self.assertEqual(
            dto.raw_component["product"],
            "1830 PSS",
        )
        self.assertEqual(
            dto.raw_component["version"],
            "24.12",
        )
        self.assertEqual(
            dto.raw_component["networkType"],
            "optical",
        )

    def test_mapper_preserves_shelves_and_radio_links(self) -> None:
        data = self.payload["response"]["data"]
        element = next(
            item
            for item in data
            if item["neId"] == "10.254.0.16"
        )

        shelves = NfmtNetworkElementEquipmentMapper.extract_links(
            element,
            "shelves",
        )
        radio = NfmtNetworkElementEquipmentMapper.extract_links(
            element,
            "radioEquipment",
        )

        self.assertEqual(len(shelves), 1)
        self.assertEqual(len(radio), 1)
        self.assertIn("/shelves", shelves[0])
        self.assertIn("/radioEquipment", radio[0])

    def test_mapper_rejects_missing_response(self) -> None:
        snapshot = InventorySnapshot(
            sync_id="invalid",
            source="NFM-T",
            endpoint="/test",
            raw_data={},
        )

        with self.assertRaisesRegex(
            ValueError,
            "missing required 'response'",
        ):
            NfmtNetworkElementEquipmentMapper.map(snapshot)

    def test_mapper_rejects_malformed_element(self) -> None:
        snapshot = InventorySnapshot(
            sync_id="invalid-element",
            source="NFM-T",
            endpoint="/test",
            raw_data={
                "response": {
                    "status": 0,
                    "data": [{"neId": "10.0.0.1"}],
                }
            },
        )

        with self.assertRaisesRegex(
            ValueError,
            "missing required field",
        ):
            NfmtNetworkElementEquipmentMapper.map(snapshot)


if __name__ == "__main__":
    unittest.main(verbosity=2)
