import importlib.util
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


def load_prioritizer():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "pattern-prioritizer.py"
    spec = importlib.util.spec_from_file_location("pattern_prioritizer", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


prioritizer = load_prioritizer()


class PatternPrioritizerTest(unittest.TestCase):
    def test_detects_generic_when_no_project_markers(self):
        with TemporaryDirectory() as tmpdir:
            self.assertEqual(prioritizer.detect_project_type(tmpdir), ["generic"])

    def test_detects_ai_agent_config_and_package_publishing(self):
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            (path / ".mcp.json").write_text("{}", encoding="utf-8")
            (path / ".github" / "workflows").mkdir(parents=True)

            self.assertEqual(
                prioritizer.detect_project_type(tmpdir),
                ["ai_agent_config", "package_publishing"],
            )

    def test_detects_nested_artifact_hygiene(self):
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            (path / "packages" / "web" / "dist").mkdir(parents=True)
            (path / "packages" / "web" / "dist" / "app.js.map").write_text("{}", encoding="utf-8")

            self.assertEqual(prioritizer.detect_project_type(tmpdir), ["artifact_hygiene"])

    def test_merges_priorities_for_detected_categories(self):
        result = prioritizer.prioritize_patterns(["node", "ai_agent_config", "package_publishing"])

        self.assertIn("openai", result["critical"])
        self.assertIn("langsmith", result["critical"])
        self.assertIn("npm", result["critical"])
        self.assertIn("mcp_config", result["high"])
        self.assertIn("openvsx", result["high"])


if __name__ == "__main__":
    unittest.main()
