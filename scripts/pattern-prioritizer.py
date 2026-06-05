#!/usr/bin/env python3
"""
Sentinel-Scan Pattern Prioritizer
Analyzes project shape to prioritize detector categories.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sentinel_scan.catalog import detect_project_type, prioritize_patterns


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python pattern-prioritizer.py <project_path>")
        sys.exit(1)

    project_path = sys.argv[1]
    categories = detect_project_type(project_path)
    priorities = prioritize_patterns(categories)

    result = {
        "project_path": project_path,
        "detected_categories": categories,
        "priorities": priorities,
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
