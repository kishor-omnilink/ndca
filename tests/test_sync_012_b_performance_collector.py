from __future__ import annotations

import csv
import pathlib
import unittest


class TestSync012BPerformanceCollectorDesign(unittest.TestCase):
    """Validate SYNC-012-B design document and register usage (offline tests)."""

    DESIGN_DOC = pathlib.Path("docs/sync/SYNC-012-B_NFMP_Performance_Collector_Design.md")
    DISCOVERY_DOC = pathlib.Path("docs/sync/SYNC-012-A_NFMP_Performance_API_Discovery.md")
    REGISTER_CSV = pathlib.Path("docs/sync/SYNC-012-A_Performance_Counter_Register.csv")

    def test_design_document_exists(self) -> None:
        self.assertTrue(self.DESIGN_DOC.exists(), f"Design document not found: {self.DESIGN_DOC}")

    def test_design_contains_required_sections(self) -> None:
        text = self.DESIGN_DOC.read_text(encoding="utf-8")
        required_sections = [
            "Objective and Scope",
            "NFM-P Performance Collection Architecture",
            "Separation of Concerns",
            "Collection Lifecycle",
            "Supported Data Types",
            "Internal Normalized Performance Record Contract",
            "Error Handling Categories",
            "Retry Behavior",
            "Idempotency",
            "Logging and Observability",
            "Security Requirements",
            "Test Strategy",
            "Implementation Gates",
        ]
        for sec in required_sections:
            self.assertIn(sec, text, f"Design doc missing required section: {sec}")

    def test_sync_012_a_register_exists(self) -> None:
        self.assertTrue(self.REGISTER_CSV.exists(), f"SYNC-012-A register not found: {self.REGISTER_CSV}")

    def test_verified_entries_present_in_register(self) -> None:
        with self.REGISTER_CSV.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            verified = [r for r in reader if r["api_verification_status"].strip() == "VERIFIED"]
            self.assertTrue(verified, "Expected at least one VERIFIED entry in SYNC-012-A register")

    def test_partial_or_unknown_entries_present(self) -> None:
        with self.REGISTER_CSV.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            others = [r for r in reader if r["api_verification_status"].strip() in {"PARTIAL", "UNKNOWN"}]
            self.assertTrue(others, "Expected at least one PARTIAL or UNKNOWN entry in SYNC-012-A register")

    def test_no_invented_xml_api_class_names_for_unverified(self) -> None:
        # For entries marked PARTIAL or UNKNOWN, xml_api_class must be 'UNKNOWN' or blank
        with self.REGISTER_CSV.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                status = row["api_verification_status"].strip()
                xml_class = row["xml_api_class"].strip()
                if status in {"PARTIAL", "UNKNOWN"}:
                    self.assertTrue(xml_class in {"UNKNOWN", ""} or xml_class.startswith("UNKNOWN"),
                                    f"Unverified entry must not claim concrete xml_api_class: {row}")

    def test_verified_entries_have_xml_class(self) -> None:
        with self.REGISTER_CSV.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                if row["api_verification_status"].strip() == "VERIFIED":
                    self.assertTrue(row["xml_api_class"].strip(), f"VERIFIED entry missing xml_api_class: {row}")

    def test_normalized_contract_documented(self) -> None:
        text = self.DESIGN_DOC.read_text(encoding="utf-8")
        self.assertIn("Normalized Performance Record Contract", text)
        # check required fields listed
        for field in ["sync_id", "source", "metric", "value", "collection_time", "persistence_time"]:
            self.assertIn(field, text, f"Normalized contract missing field: {field}")

    def test_error_categories_documented(self) -> None:
        text = self.DESIGN_DOC.read_text(encoding="utf-8")
        for err in ["Timeout", "AuthenticationFailure", "MalformedXML", "EmptyResponse", "PartialResponse"]:
            self.assertIn(err, text, f"Design doc must document error category: {err}")

    def test_security_requirements_documented(self) -> None:
        text = self.DESIGN_DOC.read_text(encoding="utf-8")
        self.assertIn("Credentials must never be logged", text)
        self.assertIn("TLS verification must be enabled by default", text)

    def test_implementation_gates_documented(self) -> None:
        text = self.DESIGN_DOC.read_text(encoding="utf-8")
        self.assertIn("Implementation Gates", text)
        for gate in ["Gate 1", "Gate 2", "Gate 3", "Gate 4", "Gate 5"]:
            self.assertIn(gate, text, f"Missing implementation gate: {gate}")

    def test_design_is_offline(self) -> None:
        # Ensure tests do not require a live NFM-P client
        self.assertFalse(hasattr(self, "NFMP_CLIENT"), "Design tests must not require a live NFM-P client")


if __name__ == "__main__":
    unittest.main()
