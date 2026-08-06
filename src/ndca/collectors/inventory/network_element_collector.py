"""
Network Element Collector
"""

from ndca.api.base_client import BaseApiClient
from ndca.core.config import settings
from ndca.core.logging import get_logger


class NetworkElementCollector:
    """
    Collect Network Element inventory from Nokia NSP.
    """

    def __init__(self):

        self.logger = get_logger(__name__)

        self.client = BaseApiClient()

    def collect(self) -> dict:
        """
        Retrieve Network Element inventory.

        Returns
        -------
        dict
            Raw RESTCONF response.
        """

        self.logger.info(
            "Collecting Network Elements..."
        )

        response = self.client.get(
            settings.nsp_network_element_endpoint
        )

        self.logger.info(
            "Network Elements collected successfully."
        )

        return response

    def close(self):

        self.client.close()