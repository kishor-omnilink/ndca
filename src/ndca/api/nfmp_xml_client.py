"""
NFM-P XML API client abstraction (skeleton).

This module provides a minimal client abstraction used by the SYNC-012-B
collector foundation. It does not implement network calls — methods raise
NotImplementedError by default and are intended to be mocked in offline tests.
"""

from __future__ import annotations

from typing import Any, Iterable

from ndca.core.logging import get_logger


class NFMPXmlClient:
    """Skeleton NFM-P XML API client.

    Implementations should provide XML transport, authentication, and
    translation from XML to structured Python objects. The methods below are
    intentionally unimplemented for SYNC-012-B and are mocked by tests.
    """

    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    def trigger_collect(self, instance_names: Iterable[str], current_data_classes: Iterable[str]) -> list[dict[str, Any]]:
        """Trigger on-demand collection for the given classes.

        Returns a list of parsed record dictionaries. Implementations must be
        mocked for offline tests.
        """
        raise NotImplementedError("NFMPXmlClient.trigger_collect must be implemented by concrete client or mocked in tests")

    def register_log_to_file(self, classes: Iterable[str], params: dict[str, Any]) -> dict[str, Any]:
        """Register continual logging for specified classes.

        Skeleton only — NotImplemented.
        """
        raise NotImplementedError("NFMPXmlClient.register_log_to_file must be implemented by concrete client or mocked in tests")

    def find_to_file(self, query: dict[str, Any]) -> dict[str, Any]:
        """Find statistics and write to file (occasional retrieval).

        Skeleton only — NotImplemented.
        """
        raise NotImplementedError("NFMPXmlClient.find_to_file must be implemented by concrete client or mocked in tests")