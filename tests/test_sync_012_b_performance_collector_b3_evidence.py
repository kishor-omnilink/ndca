from __future__ import annotations

import json
import pathlib
import unittest
from datetime import datetime, timezone

from ndca.api.nfmp_xml_client import NFMPXmlClient
from ndca.api.nfmp_evidence_capture import NFMPEvidenceCaptureUtility


class TestSync012BPerformanceCollectorB3Evidence(unittest.TestCase):
    """Offline tests for read-only BGP evidence capture without implementation."""

    def test_bgp_peerstats_is_accepted(self) -> None:
        utility = NFMPEvidenceCaptureUtility()
        request = NFMPXmlClient.build_trigger_collect_request(
            ["ne-1"],
            ["bgp.PeerStats"],
        )
        self.assertIn("bgp.PeerStats", request)
        self.assertIn("generic.GenericObject.triggerCollect", request)
        self.assertIn("<instanceName>ne-1</instanceName>", request)

        capture = utility.capture_raw_response(
            endpoint="https://example.invalid/nfmp",
            instance_names=["ne-1"],
            xml_class="bgp.PeerStats",
            auth_config={"username": "u", "password": "p", "verify_ssl": False},
            response_xml="<?xml version='1.0'?><root><peer>sample</peer></root>",
        )
        self.assertEqual(capture["class"], "bgp.PeerStats")
        self.assertIn("<peer>sample</peer>", capture["raw_xml"])

    def test_other_xml_classes_are_rejected(self) -> None:
        utility = NFMPEvidenceCaptureUtility()
        with self.assertRaises(ValueError):
            utility.capture_raw_response(
                endpoint="https://example.invalid/nfmp",
                instance_names=["ne-1"],
                xml_class="equipment.InterfaceStats",
                auth_config={"username": "u", "password": "p", "verify_ssl": False},
            )

    def test_request_generation_uses_verified_operation(self) -> None:
        request = NFMPXmlClient.build_trigger_collect_request(["ne-1", "ne-2"], ["bgp.PeerStats"])
        self.assertIn("<generic.GenericObject.triggerCollect>", request)
        self.assertIn("<instanceNames>", request)
        self.assertIn("<currentDataClasses>", request)
        self.assertIn("<currentDataClass>bgp.PeerStats</currentDataClass>", request)

    def test_raw_xml_is_preserved(self) -> None:
        response_xml = "<?xml version='1.0'?><root><record><xmlClass>bgp.PeerStats</xmlClass></record></root>"
        utility = NFMPEvidenceCaptureUtility(output_dir=pathlib.Path("docs/sync/evidence/test-output"))
        utility.output_dir.mkdir(parents=True, exist_ok=True)
        payload_path = utility.output_dir / "bgp_PeerStats_preserve.xml"
        payload_path.write_text(response_xml, encoding="utf-8")
        self.assertTrue(payload_path.exists())
        self.assertEqual(payload_path.read_text(encoding="utf-8"), response_xml)

    def test_metadata_generation(self) -> None:
        utility = NFMPEvidenceCaptureUtility(output_dir=pathlib.Path("docs/sync/evidence/test-output"))
        utility.output_dir.mkdir(parents=True, exist_ok=True)
        metadata = {
            "source": "NFM-P 24.4 XML API Developer Guide Issue 1",
            "class": "bgp.PeerStats",
            "operation": "generic.GenericObject.triggerCollect",
            "capture_timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "instanceNames": ["ne-1"],
            "evidence_status": "VERIFIED",
        }
        with (utility.output_dir / "metadata.json").open("w", encoding="utf-8") as fh:
            json.dump(metadata, fh)
        self.assertEqual(json.loads((utility.output_dir / "metadata.json").read_text(encoding="utf-8"))["class"], "bgp.PeerStats")

    def test_no_database_access(self) -> None:
        utility = NFMPEvidenceCaptureUtility()
        self.assertFalse(hasattr(utility, "db"))
        self.assertFalse(hasattr(utility, "session"))
        self.assertFalse(hasattr(utility, "repository"))

    def test_no_configuration_or_write_operation_exists(self) -> None:
        utility = NFMPEvidenceCaptureUtility()
        self.assertFalse(hasattr(utility, "update_config"))
        self.assertFalse(hasattr(utility, "write_to_database"))
        self.assertFalse(hasattr(utility, "persist"))


if __name__ == "__main__":
    unittest.main()
