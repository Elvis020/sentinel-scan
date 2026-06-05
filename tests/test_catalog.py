import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from sentinel_scan.catalog import iter_regex_patterns


class CatalogTest(unittest.TestCase):
    def test_iter_regex_patterns_reads_only_regex_blocks(self):
        with TemporaryDirectory() as tmpdir:
            patterns_file = Path(tmpdir) / "patterns.md"
            patterns_file.write_text(
                "\n".join(
                    [
                        "# Patterns",
                        "```regex",
                        "# comment",
                        "gh[pousr]_[A-Za-z0-9]{36}",
                        "",
                        "AKIA[0-9A-Z]{16}",
                        "```",
                        "```bash",
                        "rg -n 'not-a-catalog-pattern'",
                        "```",
                    ]
                ),
                encoding="utf-8",
            )

            self.assertEqual(
                iter_regex_patterns(patterns_file),
                ["gh[pousr]_[A-Za-z0-9]{36}", "AKIA[0-9A-Z]{16}"],
            )


if __name__ == "__main__":
    unittest.main()
