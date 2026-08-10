"""
SYNC-005 Network Element Mapper tests.
"""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from ndca.mappers.network_element_mapper import NetworkElementMapper
from ndca.models.inventory_snapshot import InventorySnapshot
from ndca.models.network_element import NetworkElement


class TestNetworkElementMapper(unittest.TestCase):
    """Validate NSP snapshot to NDCA model mapping."""

    def setUp(self) -> None:
        """Create a representative NSP inventory snapshot."""

        self.snapshot = InventorySnapshot(
            sync_id="sync-005-test",
            source="Nokia NSP",
            endpoint="/restconf/data/nsp-equipment:network-element",
            raw_data={
                "nsp-equipment:network-element": [
                    {
                        "ne-id": "NE-001",
                        "ne-name": "OCAC-CUTTACK-AR01",
                        "component-id": "NE-001",
                        "ip-address": "172.26.0.10",
                        "product": "7750 SR",
                        "version": "24.4.1",
                        "admin-state": "UP",
                        "oper-state": "UP",
                        "availability-state": [],
                        "description": "Test router",
                        "source-type": "NFM-P",
                    }
                ]
            },
            collected_at=datetime.now(timezone.utc),
        )

    def test_map_snapshot_to_dto(self) -> None:
        """Snapshot should map to a complete DTO."""

        result = NetworkElementMapper.map(
            self.snapshot
        )

        self.assertEqual(
            len(result),
            1,
        )

        dto = result[0]

        self.assertEqual(
            dto.ne_id,
            "NE-001",
        )

        self.assertEqual(
            dto.ne_name,
            "OCAC-CUTTACK-AR01",
        )

        self.assertEqual(
            dto.component_id,
            "NE-001",
        )

        self.assertEqual(
            dto.ip_address,
            "172.26.0.10",
        )

        self.assertEqual(
            dto.system_type,
            "7750 SR",
        )

        self.assertEqual(
            dto.software_version,
            "24.4.1",
        )

        self.assertEqual(
            dto.vendor,
            "Nokia",
        )

        self.assertEqual(
            dto.admin_state,
            "UP",
        )

        self.assertEqual(
            dto.oper_state,
            "UP",
        )

    def test_to_model(self) -> None:
        """DTO should map to NetworkElement ORM."""

        dto = NetworkElementMapper.map(
            self.snapshot
        )[0]

        model = NetworkElementMapper.to_model(
            dto
        )

        self.assertIsInstance(
            model,
            NetworkElement,
        )

        self.assertEqual(
            model.ne_id,
            "NE-001",
        )

        self.assertEqual(
            model.ne_name,
            "OCAC-CUTTACK-AR01",
        )

        self.assertEqual(
            model.component_id,
            "NE-001",
        )

        self.assertEqual(
            model.display_name,
            "OCAC-CUTTACK-AR01",
        )

        self.assertEqual(
            model.ip_address,
            "172.26.0.10",
        )

        self.assertEqual(
            model.system_type,
            "7750 SR",
        )

        self.assertEqual(
            model.software_version,
            "24.4.1",
        )

        self.assertEqual(
            model.vendor,
            "Nokia",
        )

        self.assertEqual(
            model.admin_state,
            "UP",
        )

        self.assertEqual(
            model.oper_state,
            "UP",
        )

    def test_map_to_models(self) -> None:
        """Snapshot should map directly to ORM objects."""

        result = NetworkElementMapper.map_to_models(
            self.snapshot
        )

        self.assertEqual(
            len(result),
            1,
        )

        self.assertIsInstance(
            result[0],
            NetworkElement,
        )

        self.assertEqual(
            result[0].ne_id,
            "NE-001",
        )

    def test_missing_ne_id_raises_error(self) -> None:
        """Missing NE ID should be rejected."""

        snapshot = InventorySnapshot(
            sync_id="sync-005-invalid",
            source="Nokia NSP",
            endpoint="test",
            raw_data={
                "nsp-equipment:network-element": [
                    {
                        "ne-name": "INVALID",
                        "component-id": "COMP-001",
                    }
                ]
            },
        )

        with self.assertRaises(ValueError):
            NetworkElementMapper.map(
                snapshot
            )

    def test_missing_component_id_raises_error(self) -> None:
        """Missing component ID should be rejected."""

        snapshot = InventorySnapshot(
            sync_id="sync-005-invalid",
            source="Nokia NSP",
            endpoint="test",
            raw_data={
                "nsp-equipment:network-element": [
                    {
                        "ne-id": "NE-001",
                        "ne-name": "INVALID",
                    }
                ]
            },
        )

        with self.assertRaises(ValueError):
            NetworkElementMapper.map(
                snapshot
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )