"""
Network Element Mapper.

Converts Nokia NSP inventory snapshot data into NDCA DTOs and
SQLAlchemy NetworkElement objects.
"""

from __future__ import annotations

from ndca.models.dto.network_element import NetworkElementDTO
from ndca.models.inventory_snapshot import InventorySnapshot
from ndca.models.network_element import NetworkElement


class NetworkElementMapper:
    """
    Map Nokia NSP Network Element data into NDCA representations.
    """

    @staticmethod
    def map(
        snapshot: InventorySnapshot,
    ) -> list[NetworkElementDTO]:
        """
        Convert an InventorySnapshot into NetworkElementDTO objects.

        Parameters
        ----------
        snapshot:
            Immutable inventory snapshot produced by the collector.

        Returns
        -------
        list[NetworkElementDTO]
            Network Element DTOs extracted from the snapshot.

        Raises
        ------
        ValueError
            If a Network Element does not contain required identity
            fields.
        """

        dto_list: list[NetworkElementDTO] = []

        for element in snapshot.network_elements:
            ne_id = element.get("ne-id")
            component_id = element.get("component-id")

            if not ne_id:
                raise ValueError(
                    "Network Element is missing required field: ne-id"
                )

            if not component_id:
                raise ValueError(
                    f"Network Element {ne_id!r} is missing "
                    "required field: component-id"
                )

            dto = NetworkElementDTO(
                ne_id=ne_id,
                ne_name=element.get("ne-name") or ne_id,
                component_id=component_id,
                ip_address=element.get("ip-address"),
                system_type=element.get("product"),
                software_version=element.get("version"),
                vendor="Nokia",
                admin_state=element.get("admin-state"),
                oper_state=element.get("oper-state"),
                availability_state=element.get(
                    "availability-state"
                ),
                description=element.get("description"),
                source_type=element.get("source-type"),
            )

            dto_list.append(dto)

        return dto_list

    @staticmethod
    def to_model(
        dto: NetworkElementDTO,
    ) -> NetworkElement:
        """
        Convert a NetworkElementDTO into a NetworkElement ORM object.

        Parameters
        ----------
        dto:
            Network Element DTO.

        Returns
        -------
        NetworkElement
            SQLAlchemy Network Element instance.
        """

        return NetworkElement(
            ne_id=dto.ne_id,
            ne_name=dto.ne_name,
            component_id=dto.component_id,
            display_name=dto.ne_name,
            ip_address=dto.ip_address,
            system_type=dto.system_type,
            software_version=dto.software_version,
            vendor=dto.vendor or "Nokia",
            admin_state=dto.admin_state,
            oper_state=dto.oper_state,
        )

    @classmethod
    def map_to_models(
        cls,
        snapshot: InventorySnapshot,
    ) -> list[NetworkElement]:
        """
        Convert an InventorySnapshot directly into ORM objects.

        This is a convenience method for the synchronization
        orchestration layer.
        """

        dto_list = cls.map(snapshot)

        return [
            cls.to_model(dto)
            for dto in dto_list
        ]