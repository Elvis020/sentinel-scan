from __future__ import annotations

import subprocess
from pathlib import Path


AI_AGENT_PATHS = (
    ".mcp.json",
    ".cursor",
    ".claude",
    ".codex",
    ".continue",
    ".goose",
    ".opencode",
)

ARTIFACT_DIRS = {"dist", "build", "out", "coverage"}
ARTIFACT_SUFFIXES = (".map", ".tgz", ".zip", ".vsix", ".whl", ".jar")

PRIORITY_MAP = {
    "node": {
        "critical": ["openai", "anthropic", "github", "aws", "gcp", "stripe", "langsmith", "posthog"],
        "high": ["database", "slack", "sendgrid", "package_publishing", "artifact_hygiene"],
    },
    "python": {
        "critical": ["openai", "anthropic", "github", "aws", "gcp", "stripe", "langsmith"],
        "high": ["database", "slack", "sendgrid", "pypi"],
    },
    "go": {"critical": ["github", "aws", "stripe"], "high": ["database", "docker", "kubernetes"]},
    "rust": {"critical": ["github", "aws"], "high": ["database", "env"]},
    "java": {"critical": ["github", "aws", "azure"], "high": ["database", "docker"]},
    "docker": {"critical": ["aws", "gcp", "dockerhub"], "high": ["private_key", "registry_auth"]},
    "terraform": {"critical": ["aws", "azure", "gcp"], "high": ["digitalocean", "cloudflare"]},
    "env": {"critical": ["openai", "github", "aws", "stripe", "database"], "high": ["generic_assignment"]},
    "ai_agent_config": {
        "critical": ["openai", "anthropic", "github", "gcp", "langsmith", "posthog"],
        "high": ["mcp_config", "generic_assignment", "tool_auth"],
    },
    "package_publishing": {
        "critical": ["github", "npm", "pypi", "gcp", "aws"],
        "high": ["vsce", "openvsx", "registry_auth", "ci_cd"],
    },
    "artifact_hygiene": {
        "critical": ["private_key", "source_map_secrets"],
        "high": ["source_map", "archive", "generated_bundle"],
    },
    "generic": {"critical": ["openai", "github", "aws", "stripe"], "high": ["database", "generic_assignment"]},
}


def detect_project_type(project_path: str | Path) -> list[str]:
    categories: list[str] = []
    path = Path(project_path)

    if (path / "package.json").exists():
        categories.append("node")
    if (path / "requirements.txt").exists() or (path / "setup.py").exists() or (path / "pyproject.toml").exists():
        categories.append("python")
    if (path / "Cargo.toml").exists():
        categories.append("rust")
    if (path / "go.mod").exists():
        categories.append("go")
    if (path / "pom.xml").exists() or (path / "build.gradle").exists() or (path / "build.gradle.kts").exists():
        categories.append("java")
    if any((path / f).exists() for f in ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"]):
        categories.append("docker")
    if (path / "terraform").is_dir() or any(path.glob("*.tf")):
        categories.append("terraform")
    if any((path / f).exists() for f in [".env", ".env.local", ".env.production", ".env.development"]):
        categories.append("env")
    if any((path / f).exists() for f in AI_AGENT_PATHS) or any(path.glob(".aider*")):
        categories.append("ai_agent_config")
    if (path / ".github" / "workflows").is_dir() or (path / ".npmrc").exists() or (path / ".pypirc").exists():
        categories.append("package_publishing")
    if has_artifact_hygiene_signals(path):
        categories.append("artifact_hygiene")

    return sorted(set(categories)) if categories else ["generic"]


def has_artifact_hygiene_signals(path: Path) -> bool:
    for child in path.rglob("*"):
        if child.is_dir() and child.name in ARTIFACT_DIRS:
            return True
        if child.is_file() and child.name.endswith(ARTIFACT_SUFFIXES):
            return True
    return False


def prioritize_patterns(categories: list[str]) -> dict:
    critical: set[str] = set()
    high: set[str] = set()

    for category in categories:
        config = PRIORITY_MAP.get(category)
        if not config:
            continue
        critical.update(config.get("critical", []))
        high.update(config.get("high", []))

    if not critical and not high:
        base = PRIORITY_MAP["generic"]
        critical.update(base["critical"])
        high.update(base["high"])

    return {
        "critical": sorted(critical),
        "high": sorted(high),
    }


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


def validate_regex_with_rg(pattern: str) -> tuple[bool, str]:
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


def validate_regex_patterns(patterns: list[str]) -> list[tuple[str, str]]:
    failures: list[tuple[str, str]] = []
    for pattern in patterns:
        ok, error = validate_regex_with_rg(pattern)
        if not ok:
            failures.append((pattern, error))
    return failures
