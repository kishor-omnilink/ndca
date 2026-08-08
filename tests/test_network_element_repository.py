"""
DB-003 repository layer tests.

Uses Python unittest and mocks the SQLAlchemy Session.
Database transaction testing will be performed during SYNC-001.
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from ndca.models.network_element import NetworkElement
from ndca.repositories.network_element_repository import (
    NetworkElementRepository,
)


class TestNetworkElementRepository(unittest.TestCase):
    """Validate NetworkElementRepository behavior."""

    def setUp(self) -> None:
        """Create a mocked SQLAlchemy session."""

        self.session = MagicMock()

        self.repository = NetworkElementRepository(
            self.session
        )

    def test_repository_initialization(self) -> None:
        """Repository should initialize with NetworkElement model."""

        self.assertIs(
            self.repository._model,
            NetworkElement,
        )

        self.assertIs(
            self.repository._session,
            self.session,
        )

    def test_save(self) -> None:
        """save() should add entity without committing."""

        entity = NetworkElement(
            component_id="172.26.0.8",
            ne_id="172.26.0.8",
            ne_name="OCAC-BHADRAK-AR01",
        )

        result = self.repository.save(entity)

        self.assertIs(result, entity)

        self.session.add.assert_called_once_with(
            entity
        )

        self.session.commit.assert_not_called()

    def test_save_all(self) -> None:
        """save_all() should add all entities without committing."""

        entities = [
            NetworkElement(
                component_id="172.26.0.8",
                ne_id="172.26.0.8",
                ne_name="OCAC-BHADRAK-AR01",
            ),
            NetworkElement(
                component_id="172.26.0.9",
                ne_id="172.26.0.9",
                ne_name="OCAC-BHADRAK-AR02",
            ),
        ]

        result = self.repository.save_all(entities)

        self.assertIsNone(result)

        self.session.add_all.assert_called_once_with(
            entities
        )

        self.session.commit.assert_not_called()

    def test_find_by_ne_id(self) -> None:
        """find_by_ne_id() should execute a scalar query."""

        expected = NetworkElement(
            component_id="172.26.0.8",
            ne_id="172.26.0.8",
            ne_name="OCAC-BHADRAK-AR01",
        )

        self.session.scalar.return_value = expected

        result = self.repository.find_by_ne_id(
            "172.26.0.8"
        )

        self.assertIs(result, expected)

        self.session.scalar.assert_called_once()

    def test_find_by_name(self) -> None:
        """find_by_name() should return matching entities."""

        expected = [
            NetworkElement(
                component_id="172.26.0.8",
                ne_id="172.26.0.8",
                ne_name="OCAC-BHADRAK-AR01",
            )
        ]

        scalar_result = MagicMock()
        scalar_result.all.return_value = expected

        self.session.scalars.return_value = scalar_result

        result = self.repository.find_by_name(
            "BHADRAK"
        )

        self.assertEqual(result, expected)

        self.session.scalars.assert_called_once()

    def test_exists_by_ne_id(self) -> None:
        """exists_by_ne_id() should return True when ID exists."""

        self.session.scalar.return_value = 1

        result = self.repository.exists_by_ne_id(
            "172.26.0.8"
        )

        self.assertTrue(result)

        self.session.scalar.assert_called_once()

    def test_exists_by_ne_id_not_found(self) -> None:
        """exists_by_ne_id() should return False when absent."""

        self.session.scalar.return_value = None

        result = self.repository.exists_by_ne_id(
            "172.26.99.99"
        )

        self.assertFalse(result)

        self.session.scalar.assert_called_once()

    def test_find_all(self) -> None:
        """find_all() should return all Network Elements."""

        ne1 = NetworkElement(
            component_id="172.26.0.8",
            ne_id="172.26.0.8",
            ne_name="OCAC-BHADRAK-AR01",
        )

        ne2 = NetworkElement(
            component_id="172.26.0.9",
            ne_id="172.26.0.9",
            ne_name="OCAC-BHADRAK-AR02",
        )

        self.session.scalars.return_value.all.return_value = [
            ne1,
            ne2,
        ]

        result = self.repository.find_all()

        self.session.scalars.assert_called_once()

        self.assertEqual(
            result,
            [ne1, ne2],
        )

if __name__ == "__main__":
    unittest.main(verbosity=2)
