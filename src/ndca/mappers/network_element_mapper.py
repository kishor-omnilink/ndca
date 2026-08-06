"""
Network Element Mapper
"""

from ndca.models.dto.network_element import NetworkElementDTO


class NetworkElementMapper:
    """
    Maps Nokia NSP RESTCONF response to NetworkElementDTO objects.
    """

    @staticmethod
    def map(response: dict) -> list[NetworkElementDTO]:

        network_elements = response.get(
            "nsp-equipment:network-element",
            []
        )

        dto_list = []

        for ne in network_elements:

            dto = NetworkElementDTO(
                ne_id=ne.get("ne-id", ""),
                ne_name=ne.get("ne-name", ""),
                admin_state=ne.get("admin-state"),
                oper_state=ne.get("oper-state"),
                availability_state=ne.get("availability-state"),
                description=ne.get("description"),
                source_type=ne.get("source-type"),
            )

            dto_list.append(dto)

        return dto_list