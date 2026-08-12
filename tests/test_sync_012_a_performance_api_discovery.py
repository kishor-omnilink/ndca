from __future__ import annotations

import csv
import pathlib
import unittest


class TestSync012APerformanceAPIDiscovery(unittest.TestCase):
    """Validate SYNC-012-A discovery artifact structure."""

    DOC_PATH = pathlib.Path("docs/sync/SYNC-012-A_NFMP_Performance_API_Discovery.md")
    CSV_PATH = pathlib.Path("docs/sync/SYNC-012-A_Performance_Counter_Register.csv")
    EXPECTED_COLUMNS = [
        "category",
        "statistic_name",
        "exact_nfm_p_terminology",
        "xml_api_class",
        "logrecord_class",
        "current_data_availability",
        "historical_data_availability",
        "collection_method",
        "object_scope",
        "collection_interval",
        "api_verification_status",
        "ndca_target_field",
        "source_document",
        "source_section_page",
        "notes",
    ]
    VALID_STATUSES = {"VERIFIED", "PARTIAL", "UNKNOWN"}

    def test_markdown_discovery_document_exists(self) -> None:
        self.assertTrue(
            self.DOC_PATH.exists(),
            f"Discovery document not found: {self.DOC_PATH}"
        )

    def test_csv_register_exists(self) -> None:
        self.assertTrue(
            self.CSV_PATH.exists(),
            f"CSV register not found: {self.CSV_PATH}"
        )

    def test_csv_has_required_columns(self) -> None:
        with self.CSV_PATH.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            self.assertEqual(
                self.EXPECTED_COLUMNS,
                reader.fieldnames,
                "CSV header row does not match expected columns"
            )

    def test_verification_status_is_valid(self) -> None:
        with self.CSV_PATH.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                status = row["api_verification_status"].strip()
                self.assertIn(
                    status,
                    self.VALID_STATUSES,
                    f"Invalid verification status: {status}"
                )

    def test_no_blank_statistic_category(self) -> None:
        with self.CSV_PATH.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                self.assertTrue(
                    row["category"].strip(),
                    "Found blank category in CSV register"
                )

    def test_no_blank_source_document_or_evidence(self) -> None:
        with self.CSV_PATH.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                self.assertTrue(
                    row["source_document"].strip(),
                    "Found blank source_document in CSV register"
                )
                self.assertTrue(
                    row["source_section_page"].strip(),
                    "Found blank source_section_page in CSV register"
                )

    def test_documented_xml_api_class_names_not_blank_for_verified_entries(self) -> None:
        with self.CSV_PATH.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row["api_verification_status"].strip() == "VERIFIED":
                    self.assertTrue(
                        row["xml_api_class"].strip(),
                        f"Verified entry missing xml_api_class: {row}"
                    )

    def test_at_least_one_verified_entry_exists(self) -> None:
        with self.CSV_PATH.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            verified_rows = [row for row in reader if row["api_verification_status"].strip() == "VERIFIED"]
            self.assertTrue(
                verified_rows,
                "Expected at least one VERIFIED entry in the CSV register"
            )

    def test_at_least_one_partial_or_unknown_entry_exists(self) -> None:
        with self.CSV_PATH.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            partial_or_unknown_rows = [
                row for row in reader
                if row["api_verification_status"].strip() in {"PARTIAL", "UNKNOWN"}
            ]
            self.assertTrue(
                partial_or_unknown_rows,
                "Expected at least one PARTIAL or UNKNOWN entry in the CSV register"
            )

    def test_no_invented_class_names_for_unverified_entries(self) -> None:
        with self.CSV_PATH.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row["api_verification_status"].strip() in {"PARTIAL", "UNKNOWN"}:
                    self.assertTrue(
                        row["xml_api_class"].strip() in {"UNKNOWN", ""} or row["xml_api_class"].startswith("UNKNOWN"),
                        f"Unverified entry must not claim a concrete xml_api_class: {row}"
                    )

    def test_no_duplicate_candidate_entries(self) -> None:
        seen = set()
        with self.CSV_PATH.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                key = (
                    row["category"].strip(),
                    row["statistic_name"].strip(),
                    row["exact_nfm_p_terminology"].strip(),
                )
                self.assertNotIn(
                    key,
                    seen,
                    f"Duplicate candidate entry found: {key}"
                )
                seen.add(key)

    def test_discovery_artifacts_do_not_require_live_nfmp(self) -> None:
        self.assertFalse(
            hasattr(self, "NFMP_CLIENT"),
            "Test must not require a live NFM-P client"
        )
