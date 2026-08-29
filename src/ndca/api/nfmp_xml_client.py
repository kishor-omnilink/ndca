"""
NFM-P XML API client abstraction.

This module provides a minimal, offline-testable client abstraction used by
the SYNC-012 performance collector foundation.

Current-data support:
    generic.GenericObject.triggerCollect

Historical performance support:
    findToFile
    equipment.InterfaceAdditionalStatsLogRecord

The historical Interface Additional LogRecord contract is based on the
authoritative Nokia NFM-P 24.4 XML API documentation.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any, Iterable
from xml.sax.saxutils import escape

from ndca.core.logging import get_logger


class NFMPXmlClient:
    """Skeleton NFM-P XML API client.

    The client remains transport-injectable and offline-testable.

    Verified operations currently represented here:

    * generic.GenericObject.triggerCollect
    * findToFile

    The historical Interface Additional LogRecord class is:

        equipment.InterfaceAdditionalStatsLogRecord
    """

    _INTERFACE_CURRENT_DATA_CLASSES = {
        "equipment.InterfaceStats",
        "equipment.InterfaceAdditionalStats",
    }

    _HISTORICAL_DATA_CLASSES = {
        "equipment.InterfaceAdditionalStatsLogRecord",
    }

    _INTERFACE_ADDITIONAL_HISTORICAL_CLASS = (
        "equipment.InterfaceAdditionalStatsLogRecord"
    )

    _INTERFACE_ADDITIONAL_HISTORICAL_METRICS = (
        "receivedTotalOctets",
        "receivedTotalOctetsPeriodic",
        "receivedUnicastPackets",
        "receivedUnicastPacketsPeriodic",
        "receivedMulticastPackets",
        "receivedMulticastPacketsPeriodic",
        "receivedBroadcastPackets",
        "receivedBroadcastPacketsPeriodic",
        "transmittedTotalOctets",
        "transmittedTotalOctetsPeriodic",
        "transmittedUnicastPackets",
        "transmittedUnicastPacketsPeriodic",
        "transmittedMulticastPackets",
        "transmittedMulticastPacketsPeriodic",
        "transmittedBroadcastPackets",
        "transmittedBroadcastPacketsPeriodic",
    )

    _INTERFACE_ADDITIONAL_HISTORICAL_ATTRIBUTES = (
        "monitoredObjectClass",
        "monitoredObjectPointer",
        "displayedName",
        "monitoredObjectSiteId",
        "monitoredObjectSiteName",
        "timeCaptured",
        "periodicTime",
        "suspect",
        "objectFullName",
        "name",
        "createdOnPollType",
        "updatedOnPollType",
        "recordId",
        "bucketId",
        "deploymentState",
        *_INTERFACE_ADDITIONAL_HISTORICAL_METRICS,
    )

    def __init__(self, transport: Any | None = None) -> None:
        self.logger = get_logger(__name__)
        self.transport = transport

    @staticmethod
    def _strip_xml_namespace(tag: str) -> str:
        """Return an XML tag without its namespace qualification."""

        if "}" in tag:
            return tag.rsplit("}", 1)[-1]

        return tag

    @staticmethod
    def _xml_class_from_tag(tag: str) -> str:
        """Return the full Nokia XML API class name represented by a tag.

        Examples:

            {xmlapi_1.0}equipment.InterfaceAdditionalStatsLogRecord
                ->
            equipment.InterfaceAdditionalStatsLogRecord

            equipment.InterfaceAdditionalStatsLogRecord
                ->
            equipment.InterfaceAdditionalStatsLogRecord

        The dotted Nokia class name is intentionally preserved in full.
        """

        return NFMPXmlClient._strip_xml_namespace(tag)

    @classmethod
    def _element_to_record(cls, node: ET.Element) -> dict[str, Any]:
        """Convert a historical LogRecord XML element into a raw dictionary.

        Source attribute names are deliberately preserved exactly as supplied
        by Nokia. No metric normalization is performed at this layer.
        """

        payload: dict[str, Any] = {}

        for child in list(node):
            tag = cls._strip_xml_namespace(child.tag)

            if tag == "children-Set":
                continue

            value = child.text.strip() if child.text is not None else None
            payload[tag] = value

        return payload

    @classmethod
    def _validate_historical_record(
        cls,
        payload: dict[str, Any],
    ) -> None:
        """Validate the minimum identity/time fields of a historical record.

        The parser does not require every documented statistic counter to be
        present because resultFilter may intentionally restrict returned
        attributes.
        """

        required_fields = (
            "monitoredObjectPointer",
            "timeCaptured",
        )

        missing = [
            field
            for field in required_fields
            if not str(payload.get(field, "")).strip()
        ]

        if missing:
            raise ValueError(
                "Historical Interface Additional LogRecord is missing "
                "required field(s): "
                + ", ".join(missing)
            )

    @classmethod
    def parse_find_to_file_response(
        cls,
        xml_payload: str,
        expected_class: str | None = None,
    ) -> list[dict[str, Any]]:
        """Parse a Nokia findToFile historical statistics response.

        The Nokia 24.4 response has the following logical structure:

            findToFileResponse
              └── equipment.InterfaceAdditionalStatsLogRecord
                    ├── monitoredObjectPointer
                    ├── timeCaptured
                    ├── ...
                    └── statistic counters

        XML namespaces are ignored for matching, while the original Nokia
        field names are preserved in the returned dictionaries.

        The complete Nokia XML API class name is used for matching.
        """

        if not isinstance(xml_payload, str) or not xml_payload.strip():
            raise ValueError("xml_payload is required")

        try:
            root = ET.fromstring(xml_payload)
        except ET.ParseError as exc:
            raise ValueError("MalformedXML") from exc

        target_class = (
            expected_class or cls._INTERFACE_ADDITIONAL_HISTORICAL_CLASS
        ).strip()

        if not target_class:
            raise ValueError("expected_class must not be empty")

        records: list[dict[str, Any]] = []

        for node in root.iter():
            xml_class = cls._xml_class_from_tag(node.tag)

            if xml_class != target_class:
                continue

            payload = cls._element_to_record(node)

            cls._validate_historical_record(payload)

            payload["xml_class"] = target_class

            records.append(payload)

        return records

    @classmethod
    def parse_interface_additional_historical_response(
        cls,
        xml_payload: str,
    ) -> list[dict[str, Any]]:
        """Parse Interface Additional historical statistics."""

        return cls.parse_find_to_file_response(
            xml_payload,
            expected_class=cls._INTERFACE_ADDITIONAL_HISTORICAL_CLASS,
        )

    @staticmethod
    def build_trigger_collect_request(
        instance_names: Iterable[str],
        current_data_classes: Iterable[str],
    ) -> str:
        """Build the documented generic.GenericObject.triggerCollect request."""

        names = [
            str(name).strip()
            for name in instance_names
            if str(name).strip()
        ]

        classes = [
            str(cls).strip()
            for cls in current_data_classes
            if str(cls).strip()
        ]

        instance_xml = "".join(
            f"<instanceName>{escape(name)}</instanceName>"
            for name in names
        )

        class_xml = "".join(
            f"<currentDataClass>{escape(cls)}</currentDataClass>"
            for cls in classes
        )

        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<generic.GenericObject.triggerCollect>\n"
            f"  <instanceNames>{instance_xml}</instanceNames>\n"
            f"  <currentDataClasses>{class_xml}</currentDataClasses>\n"
            "</generic.GenericObject.triggerCollect>"
        )

    @staticmethod
    def _build_result_filter_xml(
        result_filter: Iterable[str] | None,
    ) -> str:
        """Build an optional Nokia findToFile resultFilter block."""

        if result_filter is None:
            return ""

        attributes = [
            str(attribute).strip()
            for attribute in result_filter
            if str(attribute).strip()
        ]

        if not attributes:
            return ""

        attribute_xml = "".join(
            f"      <attribute>{escape(attribute)}</attribute>\n"
            for attribute in attributes
        )

        return (
            "  <resultFilter>\n"
            f"{attribute_xml}"
            "  </resultFilter>\n"
        )

    @staticmethod
    def build_find_to_file_request(
        query: dict[str, Any],
    ) -> str:
        """Build the documented generic findToFile request.

        Required query fields:

            full_class_name
            monitored_object_pointer
            time_captured.first
            time_captured.second
            file_name

        Optional query field:

            result_filter
        """

        full_class_name = str(
            query.get("full_class_name", "")
        ).strip()

        monitored_object_pointer = str(
            query.get("monitored_object_pointer", "")
        ).strip()

        file_name = str(
            query.get("file_name", "")
        ).strip()

        time_captured = query.get("time_captured")

        if not isinstance(time_captured, dict):
            raise ValueError("time_captured must be a dictionary")

        first = str(
            time_captured.get("first", "")
        ).strip()

        second = str(
            time_captured.get("second", "")
        ).strip()

        if not full_class_name:
            raise ValueError("full_class_name is required")

        if not monitored_object_pointer:
            raise ValueError(
                "monitored_object_pointer is required"
            )

        if not first:
            raise ValueError(
                "time_captured.first is required"
            )

        if not second:
            raise ValueError(
                "time_captured.second is required"
            )

        if not file_name:
            raise ValueError("file_name is required")

        result_filter_xml = NFMPXmlClient._build_result_filter_xml(
            query.get("result_filter")
        )

        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<findToFile xmlns="xmlapi_1.0">\n'
            f"  <fullClassName>{escape(full_class_name)}</fullClassName>\n"
            "  <filter>\n"
            "    <and>\n"
            '      <equal name="monitoredObjectPointer" '
            f'value="{escape(monitored_object_pointer)}"/>\n'
            '      <between name="timeCaptured" '
            f'first="{escape(first)}" '
            f'second="{escape(second)}"/>\n'
            "    </and>\n"
            "  </filter>\n"
            f"{result_filter_xml}"
            f"  <fileName>{escape(file_name)}</fileName>\n"
            "</findToFile>"
        )

    @staticmethod
    def parse_trigger_collect_response(
        xml_payload: str,
    ) -> list[dict[str, Any]]:
        """Parse a minimal triggerCollect response into record dictionaries.

        This parser intentionally remains separate from the historical
        findToFile parser because CurrentData and LogRecord XML have different
        semantics.
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

            local_tag = NFMPXmlClient._strip_xml_namespace(
                node.tag
            )

            if local_tag not in {
                "record",
                "item",
                "performanceRecord",
            }:
                continue

            payload: dict[str, Any] = {}

            for child in list(node):
                tag = NFMPXmlClient._strip_xml_namespace(
                    child.tag
                )

                value = (
                    child.text.strip()
                    if child.text is not None
                    else None
                )

                normalized = {
                    "xmlClass": "xml_class",
                    "xml_class": "xml_class",
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
        """Trigger on-demand collection for the given classes."""

        instance_names = list(instance_names)
        current_data_classes = list(current_data_classes)

        request_xml = self.build_trigger_collect_request(
            instance_names,
            current_data_classes,
        )

        self.logger.info(
            "generic.GenericObject.triggerCollect prepared",
            operation="generic.GenericObject.triggerCollect",
            instance_names=instance_names,
            current_data_classes=current_data_classes,
            request_xml=request_xml,
        )

        if response_xml is not None:
            return self.parse_trigger_collect_response(
                response_xml
            )

        if self.transport is not None:
            raw_response = self.transport(request_xml)

            if isinstance(raw_response, str):
                return self.parse_trigger_collect_response(
                    raw_response
                )

            return raw_response

        raise NotImplementedError(
            "NFMPXmlClient.trigger_collect requires a mock or "
            "transport implementation in offline tests"
        )

    def register_log_to_file(
        self,
        classes: Iterable[str],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Register continual logging for specified classes.

        Skeleton only — NotImplemented.
        """

        raise NotImplementedError(
            "NFMPXmlClient.register_log_to_file is intentionally "
            "not implemented in this task"
        )

    def find_to_file(
        self,
        query: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a historical findToFile request.

        The transport is injected for offline tests.

        The response is returned as raw XML evidence. No conversion into
        PerformanceRecord instances occurs here.
        """

        full_class_name = str(
            query.get("full_class_name", "")
        ).strip()

        if full_class_name not in self._HISTORICAL_DATA_CLASSES:
            raise ValueError(
                "Unsupported historical XML class: "
                f"{full_class_name}. "
                "Allowed classes: "
                + ", ".join(
                    sorted(self._HISTORICAL_DATA_CLASSES)
                )
            )

        request_xml = self.build_find_to_file_request(query)

        self.logger.info(
            "generic findToFile prepared",
            operation="findToFile",
            full_class_name=full_class_name,
            monitored_object_pointer=query.get(
                "monitored_object_pointer"
            ),
            file_name=query.get("file_name"),
            request_xml=request_xml,
        )

        if self.transport is None:
            raise NotImplementedError(
                "NFMPXmlClient.find_to_file requires a mock or "
                "transport implementation in offline tests"
            )

        raw_response = self.transport(request_xml)

        if not isinstance(raw_response, str):
            raise ValueError(
                "findToFile transport must return XML as a string"
            )

        return {
            "operation": "findToFile",
            "full_class_name": full_class_name,
            "monitored_object_pointer": query.get(
                "monitored_object_pointer"
            ),
            "time_captured": query.get(
                "time_captured"
            ),
            "result_filter": query.get(
                "result_filter"
            ),
            "file_name": query.get(
                "file_name"
            ),
            "request_xml": request_xml,
            "raw_xml": raw_response,
        }