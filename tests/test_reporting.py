import unittest

from sentinel_scan.reporting import (
    Finding,
    report_output_paths,
    render_finding_entry,
    render_secrets_found,
    severity_counts,
    validate_finding_dict,
)


class ReportingTest(unittest.TestCase):
    def test_finding_validates_contract_fields(self):
        finding = Finding(
            id="SEN-001",
            severity="CRITICAL",
            file="app.py",
            line=12,
            detector="openai",
            provider="openai",
            source="working-tree",
            masked_value="sk-a...1234",
        )

        self.assertEqual(finding.status, "active")

    def test_rejects_unmasked_values(self):
        with self.assertRaises(ValueError):
            Finding(
                id="SEN-002",
                severity="HIGH",
                file="app.py",
                line=1,
                detector="github",
                provider="github",
                source="git-history",
                masked_value="ghp_rawvalue",
            )

    def test_validate_finding_dict_reports_missing_fields(self):
        errors = validate_finding_dict({"id": "SEN-003"})

        self.assertIn("missing field: severity", errors)
        self.assertIn("missing field: status", errors)

    def test_rendering_groups_counts_and_keeps_masked_value(self):
        finding = Finding(
            id="SEN-004",
            severity="MEDIUM",
            file="settings.py",
            line=7,
            detector="generic_assignment",
            provider="unknown",
            source="artifact-hygiene",
            masked_value="abcd...wxyz",
            secret_type="generic token",
        )

        self.assertEqual(severity_counts([finding])["MEDIUM"], 1)
        self.assertIn("abcd...wxyz", render_finding_entry(finding))
        rendered = render_secrets_found([finding])
        self.assertIn("| Medium | 1 |", rendered)
        self.assertIn("## Medium Findings", rendered)

    def test_report_output_paths_include_details_only_when_findings_exist(self):
        self.assertEqual([path.name for path in report_output_paths(".sentinel", [])], ["security.md"])

        finding = Finding(
            id="SEN-005",
            severity="LOW",
            file="example.env",
            line=1,
            detector="placeholder",
            provider="unknown",
            source="working-tree",
            masked_value="exam...hold",
            status="suppressed",
        )
        self.assertEqual(
            [path.name for path in report_output_paths(".sentinel", [finding])],
            ["security.md", "secrets-found.md", "remediation.md"],
        )


if __name__ == "__main__":
    unittest.main()
