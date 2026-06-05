#!/usr/bin/env python3
"""
Validate regex snippets documented in guides/patterns.md.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def iter_regex_patterns(patterns_file: Path) -> list[str]:
    patterns: list[str] = []
    in_regex_block = False

    for raw_line in patterns_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == "```regex":
            in_regex_block = True
            continue
        if line == "```" and in_regex_block:
            in_regex_block = False
            continue
        if not in_regex_block or not line or line.startswith("#"):
            continue
        patterns.append(line)

    return patterns


def validate_with_rg(pattern: str) -> tuple[bool, str]:
    result = subprocess.run(
        ["rg", "--pcre2", "--", pattern],
        input="",
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 2:
        return False, result.stderr.strip()
    return True, ""


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    patterns_file = repo_root / "guides" / "patterns.md"
    patterns = iter_regex_patterns(patterns_file)

    if not patterns:
        print(f"No regex patterns found in {patterns_file}", file=sys.stderr)
        return 1

    failures: list[tuple[str, str]] = []
    for pattern in patterns:
        ok, error = validate_with_rg(pattern)
        if not ok:
            failures.append((pattern, error))

    if failures:
        for pattern, error in failures:
            print(f"Invalid regex: {pattern}", file=sys.stderr)
            print(error, file=sys.stderr)
        return 1

    print(f"Validated {len(patterns)} regex patterns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
