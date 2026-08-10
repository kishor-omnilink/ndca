"""
Network Element Collector
"""

from typing import Any

from ndca.api.base_client import BaseApiClient
from ndca.core.config import settings
from ndca.core.exceptions import CollectorError
from ndca.core.logging import get_logger


class NetworkElementCollector:
    """Collect Network Element inventory from Nokia NSP."""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.client = BaseApiClient()

    def collect(self) -> dict[str, Any]:
        """Retrieve and validate Network Element inventory.

        A JSON object, including an empty object, is considered a valid
        collection result. Non-object API responses are rejected so that a
        malformed response cannot be mistaken for an empty inventory.
        """
        self.logger.info("Collecting Network Elements...")

        try:
            response = self.client.get(settings.nsp_network_element_endpoint)
        except Exception as exc:
            self.logger.error("Network Element collection failed", error=str(exc))
            raise CollectorError("Network Element collection failed") from exc

        if not isinstance(response, dict):
            self.logger.error(
                "Invalid Network Element response type",
                response_type=type(response).__name__,
            )
            raise CollectorError("Network Element API response must be a JSON object")

        self.logger.info(
            "Network Elements collected successfully.",
            empty=not bool(response),
        )
        return response

    def close(self) -> None:
        """Release collector resources."""
        self.client.close()
