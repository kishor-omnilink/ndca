from __future__ import annotations

import pathlib
import unittest


class TestSync012BPerformanceCollectorB3Blocker(unittest.TestCase):
    """Offline validation that SYNC-012-B.3 remains explicitly blocked."""

    BLOCKER_DOC = pathlib.Path("docs/sync/SYNC-012-B.3_BGP_Current_Data_Blocker.md")

    def test_blocker_document_exists(self) -> None:
        self.assertTrue(self.BLOCKER_DOC.exists(), f"Blocker document not found: {self.BLOCKER_DOC}")

    def test_blocker_status_is_blocked(self) -> None:
        text = self.BLOCKER_DOC.read_text(encoding="utf-8")
        self.assertIn("BLOCKED", text)
        self.assertIn("SYNC-012-B.3 is BLOCKED", text)

    def test_bgp_peerstats_is_identified(self) -> None:
        text = self.BLOCKER_DOC.read_text(encoding="utf-8")
        self.assertIn("bgp.PeerStats", text)
        self.assertIn("Candidate capability", text)

    def test_missing_evidence_is_documented(self) -> None:
        text = self.BLOCKER_DOC.read_text(encoding="utf-8")
        for requirement in [
            "documented BGP response XML/schema",
            "exact BGP counter/field names",
            "response-to-normalized-field mapping",
            "exact registerLogToFile request schema",
            "bgp.PeerStatsLogRecord response structure",
            "source page/section evidence",
        ]:
            self.assertIn(requirement, text, f"Missing evidence requirement not documented: {requirement}")

    def test_implementation_gates_are_documented(self) -> None:
        text = self.BLOCKER_DOC.read_text(encoding="utf-8")
        self.assertIn("Gate 1", text)
        self.assertIn("Gate 2", text)
        self.assertIn("API/request structure verified", text)
        self.assertIn("response structure and field mapping verified", text)

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
