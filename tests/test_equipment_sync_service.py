"""
SYNC-010 Equipment Synchronization Service tests.
"""

from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import Mock

from ndca.models.dto.equipment import EquipmentDTO
from ndca.models.equipment import Equipment
from ndca.models.enums import SyncStatus
from ndca.services.equipment_sync_service import EquipmentSyncService


class TestEquipmentSyncService(unittest.TestCase):
    """Validate Equipment persistence and lifecycle reconciliation."""

    def setUp(self) -> None:
        self.session = Mock()
        self.service = EquipmentSyncService(self.session)
        self.service._repository = Mock()
        self.service._network_element_repository = Mock()

        self.network_element = Mock()
        self.network_element.id = 101
        self.network_element.ne_id = "172.26.0.20"
        self.service._network_element_repository.find_by_ne_id.return_value = (
            self.network_element
        )

    @staticmethod
    def dto(
        component_id: str = "shelf=1",
        component_class: str = "shelf",
        name: str = "Shelf-1",
    ) -> EquipmentDTO:
        return EquipmentDTO(
            source_system="NSP",
            ne_id="172.26.0.20",
            component_id=component_id,
            component_class=component_class,
            name=name,
            admin_state="unlocked",
            oper_state="enabled",
            raw_component={"component-id": component_id},
        )

    def test_new_equipment_is_created(self) -> None:
        self.service._repository.find_by_identity.return_value = None

        result = self.service.synchronize([self.dto()])

        self.assertEqual(result.created, 1)
        self.assertEqual(result.processed, 1)
        self.service._repository.save.assert_called_once()
        entity = self.service._repository.save.call_args.args[0]
        self.assertIsInstance(entity, Equipment)
        self.assertEqual(entity.source_system, "NSP")
        self.assertEqual(entity.network_element_id, 101)
        self.assertEqual(entity.component_id, "shelf=1")
        self.assertEqual(entity.sync_status, SyncStatus.SUCCESS)
        self.session.commit.assert_called_once()

    def test_existing_unchanged_equipment_is_counted_unchanged(self) -> None:
        current = Equipment(
            source_system="NSP",
            network_element_id=101,
            component_id="shelf=1",
            component_class="shelf",
            display_name="Shelf-1",
            admin_state="unlocked",
            oper_state="enabled",
            raw_component={"component-id": "shelf=1"},
            first_seen=datetime(2026, 1, 1, tzinfo=timezone.utc),
            last_seen=datetime(2026, 1, 2, tzinfo=timezone.utc),
            is_active=True,
            sync_status=SyncStatus.SUCCESS,
        )
        self.service._repository.find_by_identity.return_value = current

        result = self.service.synchronize([self.dto()])

        self.assertEqual(result.unchanged, 1)
        self.assertEqual(result.updated, 0)
        self.assertEqual(current.first_seen, datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.assertGreater(current.last_seen, datetime(2026, 1, 2, tzinfo=timezone.utc))

    def test_changed_equipment_is_updated(self) -> None:
        current = Equipment(
            source_system="NSP",
            network_element_id=101,
            component_id="shelf=1",
            component_class="shelf",
            display_name="Old Shelf Name",
            first_seen=datetime(2026, 1, 1, tzinfo=timezone.utc),
            last_seen=datetime(2026, 1, 2, tzinfo=timezone.utc),
            is_active=True,
            sync_status=SyncStatus.SUCCESS,
        )
        self.service._repository.find_by_identity.return_value = current

        result = self.service.synchronize([self.dto(name="New Shelf Name")])

        self.assertEqual(result.updated, 1)
        self.assertEqual(current.display_name, "New Shelf Name")

    def test_inactive_equipment_is_reactivated(self) -> None:
        current = Equipment(
            source_system="NSP",
            network_element_id=101,
            component_id="shelf=1",
            component_class="shelf",
            display_name="Shelf-1",
            first_seen=datetime(2026, 1, 1, tzinfo=timezone.utc),
            last_seen=datetime(2026, 1, 2, tzinfo=timezone.utc),
            is_active=False,
            sync_status=SyncStatus.SUCCESS,
        )
        self.service._repository.find_by_identity.return_value = current

        result = self.service.synchronize([self.dto()])

        self.assertEqual(result.reactivated, 1)
        self.assertTrue(current.is_active)

    def test_missing_equipment_is_deactivated_only_for_complete_snapshot_ne(self) -> None:
        self.service._repository.find_by_identity.return_value = None
        self.service._repository.mark_missing_inactive.return_value = 2

        result = self.service.synchronize(
            [self.dto()],
            complete_network_element_ids={"172.26.0.20"},
        )

        self.assertEqual(result.created, 1)
        self.assertEqual(result.deactivated, 2)
        self.service._repository.mark_missing_inactive.assert_called_once_with(
            101,
            {("NSP", "shelf", "shelf=1")},
            unittest.mock.ANY,
        )

    def test_unknown_network_element_fails_and_rolls_back(self) -> None:
        self.service._network_element_repository.find_by_ne_id.return_value = None

        with self.assertRaisesRegex(ValueError, "unknown Network Element"):
            self.service.synchronize([self.dto()])

        self.session.rollback.assert_called_once()
        self.session.commit.assert_not_called()

    def test_duplicate_input_identity_fails_and_rolls_back(self) -> None:
        self.service._repository.find_by_identity.return_value = None

        with self.assertRaisesRegex(ValueError, "Duplicate equipment identity"):
            self.service.synchronize([self.dto(), self.dto()])

        self.session.rollback.assert_called_once()
        self.session.commit.assert_not_called()

    def test_partial_snapshot_does_not_deactivate(self) -> None:
        self.service._repository.find_by_identity.return_value = None

        result = self.service.synchronize([self.dto()])

        self.assertEqual(result.created, 1)
        self.service._repository.mark_missing_inactive.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
