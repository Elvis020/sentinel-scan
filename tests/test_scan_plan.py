import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from sentinel_scan.scan_plan import build_scan_plan, history_guardrail, normalize_mode


class ScanPlanTest(unittest.TestCase):
    def test_quick_scan_omits_git_history_and_artifacts(self):
        with TemporaryDirectory() as tmpdir:
            plan = build_scan_plan(tmpdir, mode="quick", available_tools={"gitleaks"})

            self.assertEqual(plan.mode, "quick")
            self.assertFalse(plan.include_git_history)
            self.assertEqual(plan.commit_scanner, "not-run")
            self.assertNotIn("**/*.map", plan.target_globs)

    def test_full_scan_selects_available_tools_and_artifacts(self):
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            (path / "package.json").write_text("{}", encoding="utf-8")

            plan = build_scan_plan(
                tmpdir,
                mode="full",
                commit_count=42,
                available_tools={"gitleaks", "trufflehog"},
            )

            self.assertEqual(plan.mode, "full")
            self.assertTrue(plan.include_git_history)
            self.assertEqual(plan.commit_scanner, "gitleaks")
            self.assertEqual(plan.optional_deep_scanners, ["trufflehog"])
            self.assertIn("node", plan.categories)
            self.assertIn("**/*.map", plan.target_globs)
            self.assertFalse(plan.guardrail.requires_confirmation)

    def test_git_history_scan_falls_back_without_gitleaks(self):
        with TemporaryDirectory() as tmpdir:
            plan = build_scan_plan(tmpdir, mode="git-history", available_tools=set())

            self.assertEqual(plan.commit_scanner, "fallback-git-log")
            self.assertGreater(len(plan.fallback_history_patterns), 0)
            self.assertIn(".env*", plan.deep_history_paths)

    def test_history_guardrails_match_commit_thresholds(self):
        self.assertFalse(history_guardrail(500).targeted_history_only)
        self.assertTrue(history_guardrail(501).targeted_history_only)
        self.assertFalse(history_guardrail(501).requires_confirmation)
        self.assertTrue(history_guardrail(2001).requires_confirmation)

    def test_rejects_unknown_mode(self):
        with self.assertRaises(ValueError):
            normalize_mode("everything")


if __name__ == "__main__":
    unittest.main()
