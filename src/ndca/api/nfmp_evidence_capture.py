"""Read-only NFM-P evidence capture utility for verified XML classes.

This module intentionally captures raw XML responses without parsing or
normalizing BGP fields. It is limited to the verified operation
`generic.GenericObject.triggerCollect` and an allow-list containing only
`bgp.PeerStats`.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import httpx

from ndca.api.nfmp_xml_client import NFMPXmlClient
from ndca.core.config import settings

_ALLOWED_XML_CLASSES = {"bgp.PeerStats"}

_ALLOWED_HISTORICAL_XML_CLASSES = {
    "equipment.InterfaceAdditionalStatsLogRecord",
}

_EVIDENCE_DIR = Path("docs/sync/evidence")


class NFMPEvidenceCaptureUtility:
    """Capture raw XML evidence for a verified NFM-P operation.

    This utility is intentionally read-only and non-production. It supports a
    minimal, allow-listed XML class set and captures the raw server response
    without parsing or persisting BGP metrics.
    """

    allowed_xml_classes = frozenset(_ALLOWED_XML_CLASSES)

    def __init__(
        self,
        client: NFMPXmlClient | None = None,
        output_dir: str | Path | None = None,
    ) -> None:
        self.client = client or NFMPXmlClient()
        self.output_dir = Path(output_dir) if output_dir else _EVIDENCE_DIR

    @staticmethod
    def _normalize_instance_names(instance_names: Iterable[str]) -> list[str]:
        names = [str(name).strip() for name in instance_names if str(name).strip()]
        if not names:
            raise ValueError("instanceNames must contain at least one value")
        return names

    @staticmethod
    def _normalize_xml_class(xml_class: str) -> str:
        normalized = str(xml_class).strip()
        if not normalized:
            raise ValueError("XML class is required")
        if normalized not in _ALLOWED_XML_CLASSES:
            raise ValueError(
                f"Unsupported XML class for evidence capture: {normalized}. "
                "Allowed classes: bgp.PeerStats"
            )
        return normalized

    @staticmethod
    def _normalize_historical_xml_class(
        xml_class: str,
    ) -> str:
        normalized = str(xml_class).strip()

        if not normalized:
            raise ValueError("XML class is required")

        if normalized not in _ALLOWED_HISTORICAL_XML_CLASSES:
            raise ValueError(
                "Unsupported historical XML class: "
                f"{normalized}. Allowed classes: "
                + ", ".join(
                    sorted(_ALLOWED_HISTORICAL_XML_CLASSES)
                )
            )

        return normalized

    @staticmethod
    def _build_auth_config(
        auth_config: dict[str, Any] | None,
        endpoint: str,
    ) -> dict[str, Any]:
        config = dict(auth_config or {})
        config.setdefault("base_url", endpoint)
        config.setdefault("username", settings.nfmp_username)
        config.setdefault("password", settings.nfmp_password)
        config.setdefault("verify_ssl", settings.nfmp_verify_ssl)
        config.setdefault("timeout", 60)
        config.setdefault("operation", "generic.GenericObject.triggerCollect")
        return config

    def _build_transport(self, endpoint: str, auth_config: dict[str, Any] | None) -> Any:
        resolved_auth = self._build_auth_config(auth_config, endpoint)
        username = str(resolved_auth.get("username") or "")
        password = str(resolved_auth.get("password") or "")
        verify_ssl = bool(resolved_auth.get("verify_ssl", False))
        timeout_seconds = float(resolved_auth.get("timeout", 60) or 60)

        auth = (username, password) if username or password else None

        def transport(request_xml: str) -> str:
            with httpx.Client(verify=verify_ssl, timeout=timeout_seconds) as client:
                response = client.post(
                    endpoint,
                    headers={
                        "Content-Type": "application/xml",
                        "Accept": "application/xml",
                    },
                    content=request_xml,
                    auth=auth,
                )
                response.raise_for_status()
                return response.text

        return transport

    def capture_raw_response(
        self,
        endpoint: str,
        instance_names: Iterable[str],
        xml_class: str = "bgp.PeerStats",
        auth_config: dict[str, Any] | None = None,
        response_xml: str | None = None,
        transport: Any | None = None,
    ) -> dict[str, Any]:
        """Capture the raw XML response for the verified class.

        The raw XML is stored under docs/sync/evidence/ and a sidecar metadata
        JSON is also saved. This method intentionally does not parse, normalize,
        or persist BGP metric fields.
        """
        if not endpoint or not str(endpoint).strip():
            raise ValueError("NFM-P endpoint/base URL is required")

        normalized_class = self._normalize_xml_class(xml_class)
        names = self._normalize_instance_names(instance_names)
        request_xml = NFMPXmlClient.build_trigger_collect_request(
            names,
            [normalized_class],
        )

        if response_xml is not None:
            raw_xml = response_xml
        else:
            resolved_transport = transport or self._build_transport(endpoint, auth_config)
            raw_xml = resolved_transport(request_xml)

        capture_ts = datetime.now(timezone.utc)
        timestamp_slug = capture_ts.strftime("%Y%m%dT%H%M%SZ")
        response_filename = f"{normalized_class.replace('.', '_')}_{timestamp_slug}.xml"
        metadata_filename = f"{normalized_class.replace('.', '_')}_{timestamp_slug}.meta.json"

        self.output_dir.mkdir(parents=True, exist_ok=True)
        response_path = self.output_dir / response_filename
        metadata_path = self.output_dir / metadata_filename

        response_path.write_text(raw_xml, encoding="utf-8")
        metadata = {
            "source": "NFM-P 24.4 XML API Developer Guide Issue 1",
            "class": normalized_class,
            "operation": "generic.GenericObject.triggerCollect",
            "capture_timestamp_utc": capture_ts.isoformat().replace("+00:00", "Z"),
            "instanceNames": names,
            "evidence_status": "VERIFIED",
            "response_file": response_filename,
            "metadata_file": metadata_filename,
        }
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")

        return {
            "source": metadata["source"],
            "class": normalized_class,
            "operation": metadata["operation"],
            "capture_timestamp_utc": metadata["capture_timestamp_utc"],
            "instanceNames": names,
            "evidence_status": metadata["evidence_status"],
            "request_xml": request_xml,
            "raw_xml": raw_xml,
            "response_path": str(response_path),
            "metadata_path": str(metadata_path),
        }


    def capture_historical_response(
        self,
        endpoint: str,
        monitored_object_pointer: str,
        time_captured_first: str,
        time_captured_second: str,
        file_name: str,
        xml_class: str = (
            "equipment.InterfaceAdditionalStatsLogRecord"
        ),
        auth_config: dict[str, Any] | None = None,
        response_xml: str | None = None,
        transport: Any | None = None,
    ) -> dict[str, Any]:
        """Capture raw XML from the historical findToFile operation."""
        if not endpoint or not str(endpoint).strip():
            raise ValueError(
                "NFM-P endpoint/base URL is required"
            )

        normalized_class = (
            self._normalize_historical_xml_class(
                xml_class
            )
        )

        query = {
            "full_class_name": normalized_class,
            "monitored_object_pointer": (
                str(monitored_object_pointer).strip()
            ),
            "time_captured": {
                "first": str(
                    time_captured_first
                ).strip(),
                "second": str(
                    time_captured_second
                ).strip(),
            },
            "file_name": str(
                file_name
            ).strip(),
        }

        request_xml = (
            NFMPXmlClient.build_find_to_file_request(
                query
            )
        )

        if response_xml is not None:
            raw_xml = response_xml
        else:
            resolved_transport = (
                transport
                or self._build_transport(
                    endpoint,
                    auth_config,
                )
            )
            raw_xml = resolved_transport(
                request_xml
            )

        if not isinstance(raw_xml, str):
            raise ValueError(
                "findToFile transport must return XML as a string"
            )

        capture_ts = datetime.now(
            timezone.utc
        )
        timestamp_slug = capture_ts.strftime(
            "%Y%m%dT%H%M%SZ"
        )

        response_filename = (
            f"{normalized_class.replace('.', '_')}_"
            f"{timestamp_slug}.xml"
        )
        metadata_filename = (
            f"{normalized_class.replace('.', '_')}_"
            f"{timestamp_slug}.meta.json"
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        response_path = (
            self.output_dir
            / response_filename
        )
        metadata_path = (
            self.output_dir
            / metadata_filename
        )

        response_path.write_text(
            raw_xml,
            encoding="utf-8",
        )

        metadata = {
            "source": (
                "NFM-P 24.4 XML API Developer Guide Issue 1"
            ),
            "class": normalized_class,
            "operation": "findToFile",
            "capture_timestamp_utc": (
                capture_ts.isoformat()
                .replace("+00:00", "Z")
            ),
            "monitoredObjectPointer": (
                query["monitored_object_pointer"]
            ),
            "timeCaptured": (
                query["time_captured"]
            ),
            "fileName": query["file_name"],
            "evidence_status": "CAPTURED",
            "response_file": response_filename,
            "metadata_file": metadata_filename,
        }

        metadata_path.write_text(
            json.dumps(
                metadata,
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        return {
            "source": metadata["source"],
            "class": normalized_class,
            "operation": metadata["operation"],
            "capture_timestamp_utc": (
                metadata["capture_timestamp_utc"]
            ),
            "monitoredObjectPointer": (
                query["monitored_object_pointer"]
            ),
            "timeCaptured": query["time_captured"],
            "fileName": query["file_name"],
            "evidence_status": (
                metadata["evidence_status"]
            ),
            "request_xml": request_xml,
            "raw_xml": raw_xml,
            "response_path": str(
                response_path
            ),
            "metadata_path": str(
                metadata_path
            ),
        }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only NFM-P evidence capture for bgp.PeerStats")
    parser.add_argument("--endpoint", required=True, help="NFM-P base URL or endpoint URL")
    parser.add_argument(
        "--instance-name",
        action="append",
        default=[],
        help="One or more instance names. Repeat the flag for multiple values.",
    )
    parser.add_argument(
        "--xml-class",
        dest="xml_class",
        default="bgp.PeerStats",
        help="XML class to capture. Only bgp.PeerStats is allowed.",
    )
    parser.add_argument("--username", default=settings.nfmp_username, help="NFM-P username")
    parser.add_argument("--password", default=settings.nfmp_password, help="NFM-P password")
    parser.add_argument(
        "--verify-ssl",
        action="store_true",
        default=settings.nfmp_verify_ssl,
        help="Verify TLS certificate when making the live request.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(_EVIDENCE_DIR),
        help="Directory used to save raw XML and metadata.",
    )
    parser.add_argument(
        "--operation",
        choices=["triggerCollect", "findToFile"],
        default="triggerCollect",
        help="NFM-P operation to capture.",
    )
    parser.add_argument(
        "--monitored-object-pointer",
        help="Historical monitoredObjectPointer used by findToFile.",
    )
    parser.add_argument(
        "--time-captured-first",
        help="Historical timeCaptured first epoch-millisecond value.",
    )
    parser.add_argument(
        "--time-captured-second",
        help="Historical timeCaptured second epoch-millisecond value.",
    )
    parser.add_argument(
        "--file-name",
        help="NFM-P findToFile fileName.",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        utility = NFMPEvidenceCaptureUtility(output_dir=args.output_dir)

        auth_config = {
            "username": args.username,
            "password": args.password,
            "verify_ssl": args.verify_ssl,
        }

        if args.operation == "findToFile":
            required = {
                "--monitored-object-pointer": (
                    args.monitored_object_pointer
                ),
                "--time-captured-first": (
                    args.time_captured_first
                ),
                "--time-captured-second": (
                    args.time_captured_second
                ),
                "--file-name": args.file_name,
            }

            missing = [
                name
                for name, value in required.items()
                if not value
            ]

            if missing:
                parser.error(
                    "findToFile requires: "
                    + ", ".join(missing)
                )

            result = utility.capture_historical_response(
                endpoint=args.endpoint,
                monitored_object_pointer=(
                    args.monitored_object_pointer
                ),
                time_captured_first=(
                    args.time_captured_first
                ),
                time_captured_second=(
                    args.time_captured_second
                ),
                file_name=args.file_name,
                xml_class=(
                    args.xml_class
                    if args.xml_class != "bgp.PeerStats"
                    else "equipment.InterfaceAdditionalStatsLogRecord"
                ),
                auth_config=auth_config,
            )
        else:
            result = utility.capture_raw_response(
                endpoint=args.endpoint,
                instance_names=args.instance_name,
                xml_class=args.xml_class,
                auth_config=auth_config,
            )
    except Exception as exc:  # pragma: no cover - CLI surface only
        parser.exit(status=1, message=f"capture failed: {exc}\n")

    output = {
        "source": result["source"],
        "class": result["class"],
        "operation": result["operation"],
        "capture_timestamp_utc": result["capture_timestamp_utc"],
        "evidence_status": result["evidence_status"],
        "response_path": result["response_path"],
        "metadata_path": result["metadata_path"],
    }

    if "instanceNames" in result:
        output["instanceNames"] = result["instanceNames"]

    if "monitoredObjectPointer" in result:
        output["monitoredObjectPointer"] = (
            result["monitoredObjectPointer"]
        )

    if "timeCaptured" in result:
        output["timeCaptured"] = result["timeCaptured"]

    if "fileName" in result:
        output["fileName"] = result["fileName"]

    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
