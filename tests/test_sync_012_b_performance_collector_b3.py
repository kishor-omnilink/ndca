from __future__ import annotations

import pathlib
import unittest


class TestSync012BPerformanceCollectorB3Blocker(unittest.TestCase):
    """Offline validation that SYNC-012-B.3 remains blocked on missing BGP payload evidence."""

    BLOCKER_DOC = pathlib.Path("docs/sync/SYNC-012-B.3_BGP_Current_Data_Blocker.md")

    def test_blocker_document_exists(self) -> None:
        self.assertTrue(self.BLOCKER_DOC.exists(), f"Blocker document not found: {self.BLOCKER_DOC}")

    def test_blocker_status_is_blocked(self) -> None:
        text = self.BLOCKER_DOC.read_text(encoding="utf-8")
        self.assertIn("BLOCKED", text)
        self.assertIn("SYNC-012-B.3 remains BLOCKED", text)

    def test_verified_bgp_and_generic_evidence_is_documented(self) -> None:
        text = self.BLOCKER_DOC.read_text(encoding="utf-8")
        for item in [
            "bgp.PeerStats",
            "bgp.PeerStatsLogRecord",
            "generic.GenericObject.triggerCollect",
            "instanceNames",
            "currentDataClasses",
            "scheduled BGP PeerStats collection example",
            "5-minute scheduled polling example",
            "registerLogToFile",
            "retrieval mechanism",
            "generic input structure",
            "generic XML statistics output structure",
        ]:
            self.assertIn(item, text, f"Verified evidence item missing: {item}")

    def test_missing_bgp_payload_evidence_is_documented(self) -> None:
        text = self.BLOCKER_DOC.read_text(encoding="utf-8")
        for requirement in [
            "exact `bgp.PeerStats` attribute/counter names",
            "exact `bgp.PeerStats` XML response payload",
            "exact `bgp.PeerStatsLogRecord` attributes",
            "BGP-specific response-to-NDCA normalized-field mapping",
            "Gate 1",
            "Gate 2",
        ]:
            self.assertIn(requirement, text, f"Missing BGP evidence requirement not documented: {requirement}")

    def test_evidence_references_are_documented(self) -> None:
        text = self.BLOCKER_DOC.read_text(encoding="utf-8")
        for ref in [
            "§14.4.1, p.175",
            "§14.5.5, p.179",
            "§14.6, p.180",
            "§14.7, p.182",
            "§14.8.2, pp.185-187",
            "§14.8.3, p.188",
            "§7.1.1 / information-model reference, p.85",
        ]:
            self.assertIn(ref, text, f"Evidence reference missing: {ref}")

    def test_no_production_implementation_is_claimed(self) -> None:
        text = self.BLOCKER_DOC.read_text(encoding="utf-8")
        self.assertIn("no production code changes", text)
        self.assertIn("no BGP XML parser", text)
        self.assertIn("no BGP collector", text)
        self.assertIn("no persistence", text)
        self.assertIn("no historical LogRecord implementation", text)

    def test_no_invented_xml_class_names_are_introduced(self) -> None:
        text = self.BLOCKER_DOC.read_text(encoding="utf-8")
        forbidden = [
            "bgp.PeerStatsCurrentData",
            "bgp.PeerStatsResponse",
            "bgp.PeerStatsCurrentDataResponse",
            "bgp.PeerStatsRecord",
        ]
        for name in forbidden:
            self.assertNotIn(name, text, f"Invented XML class name not allowed: {name}")


if __name__ == "__main__":
    unittest.main()
