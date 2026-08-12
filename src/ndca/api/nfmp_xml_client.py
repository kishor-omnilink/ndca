"""
NFM-P XML API client abstraction (skeleton).

This module provides a minimal client abstraction used by the SYNC-012-B
collector foundation. It does not implement network calls by default; it is
mockable and testable as an offline API contract.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any, Iterable
from xml.sax.saxutils import escape

from ndca.core.logging import get_logger


class NFMPXmlClient:
    """Skeleton NFM-P XML API client.

    The verified NFM-P operation for current-data on-demand collection is
    `generic.GenericObject.triggerCollect`. This client builds that operation
    using the documented request fields `<instanceNames>` and
    `<currentDataClasses>` while keeping transport injectable and offline.
    """

    _INTERFACE_CURRENT_DATA_CLASSES = {
        "equipment.InterfaceStats",
        "equipment.InterfaceAdditionalStats",
    }

    def __init__(self, transport: Any | None = None) -> None:
        self.logger = get_logger(__name__)
        self.transport = transport

    @staticmethod
    def build_trigger_collect_request(
        instance_names: Iterable[str],
        current_data_classes: Iterable[str],
    ) -> str:
        """Build the documented generic.GenericObject.triggerCollect request."""
        names = [str(name).strip() for name in instance_names if str(name).strip()]
        classes = [str(cls).strip() for cls in current_data_classes if str(cls).strip()]

        instance_xml = "".join(
            f"<instanceName>{escape(name)}</instanceName>" for name in names
        )
        class_xml = "".join(
            f"<currentDataClass>{escape(cls)}</currentDataClass>" for cls in classes
        )

        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<generic.GenericObject.triggerCollect>\n'
            f'  <instanceNames>{instance_xml}</instanceNames>\n'
            f'  <currentDataClasses>{class_xml}</currentDataClasses>\n'
            '</generic.GenericObject.triggerCollect>'
        )

    @staticmethod
    def parse_trigger_collect_response(xml_payload: str) -> list[dict[str, Any]]:
        """Parse a minimal triggerCollect response into record dictionaries.

        This intentionally supports only fields that are documented or already
        used in project tests. If unsupported fields exist, they remain unmapped.
        """
        try:
            root = ET.fromstring(xml_payload)
        except ET.ParseError as exc:
            raise ValueError("MalformedXML") from exc

        records: list[dict[str, Any]] = []
        candidates = [root] + list(root.iter())
        for node in candidates:
            if node is root and len(node) == 0:
                continue
            if node.tag in {"record", "item", "performanceRecord"}:
                payload: dict[str, Any] = {}
                for child in list(node):
                    tag = child.tag
                    value = child.text.strip() if child.text is not None else None
                    normalized = {
                        "xml_class": "xml_class",
                        "xmlClass": "xml_class",
                        "metricName": "metric_name",
                        "metric": "metric",
                        "value": "value",
                        "objectId": "object_id",
                        "objectName": "object_name",
                        "sourceTime": "source_time",
                        "category": "category",
                    }.get(tag, tag)
                    payload[normalized] = value
                if payload:
                    records.append(payload)

        return records

    def trigger_collect(
        self,
        instance_names: Iterable[str],
        current_data_classes: Iterable[str],
        response_xml: str | None = None,
    ) -> list[dict[str, Any]]:
        """Trigger on-demand collection for the given classes.

        If `response_xml` is supplied, the XML is parsed without a live network
        call. This keeps the contract offline/testable and mockable.
        """
        request_xml = self.build_trigger_collect_request(instance_names, current_data_classes)
        self.logger.info(
            "generic.GenericObject.triggerCollect prepared",
            operation="generic.GenericObject.triggerCollect",
            instance_names=list(instance_names),
            current_data_classes=list(current_data_classes),
            request_xml=request_xml,
        )

        if response_xml is not None:
            return self.parse_trigger_collect_response(response_xml)

        if self.transport is not None:
            raw_response = self.transport(request_xml)
            if isinstance(raw_response, str):
                return self.parse_trigger_collect_response(raw_response)
            return raw_response

        raise NotImplementedError(
            "NFMPXmlClient.trigger_collect requires a mock or transport implementation in offline tests"
        )

    def register_log_to_file(self, classes: Iterable[str], params: dict[str, Any]) -> dict[str, Any]:
        """Register continual logging for specified classes.

        Skeleton only — NotImplemented. This task intentionally does not define
        a production request schema beyond the documented operation name and the
        fact that it is for ongoing performance statistics retrieval.
        """
        raise NotImplementedError("NFMPXmlClient.register_log_to_file is intentionally not implemented in this task")

    def find_to_file(self, query: dict[str, Any]) -> dict[str, Any]:
        """Find statistics and write to file (occasional retrieval).

        Skeleton only — NotImplemented.
        """
        raise NotImplementedError("NFMPXmlClient.find_to_file is intentionally not implemented in this task")