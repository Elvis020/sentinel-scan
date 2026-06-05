#!/usr/bin/env python3
"""
Validate regex snippets documented in guides/patterns.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sentinel_scan.catalog import iter_regex_patterns, validate_regex_patterns


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    patterns_file = repo_root / "guides" / "patterns.md"
    patterns = iter_regex_patterns(patterns_file)

    if not patterns:
        print(f"No regex patterns found in {patterns_file}", file=sys.stderr)
        return 1

    failures = validate_regex_patterns(patterns)
    if failures:
        for pattern, error in failures:
            print(f"Invalid regex: {pattern}", file=sys.stderr)
            print(error, file=sys.stderr)
        return 1

    print(f"Validated {len(patterns)} regex patterns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
