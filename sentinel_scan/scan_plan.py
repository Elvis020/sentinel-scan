from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from sentinel_scan.catalog import detect_project_type, prioritize_patterns


ScanMode = Literal["quick", "full", "git-history"]

BASE_TARGET_GLOBS = (
    "**/.env*",
    "**/*config*",
    "**/*credentials*",
    "**/*secret*",
)

AI_AGENT_TARGET_GLOBS = (
    "**/.mcp.json",
    "**/.cursor/**",
    "**/.claude/**",
    "**/.codex/**",
    "**/.continue/**",
    "**/.aider*",
    "**/.goose/**",
    "**/.opencode/**",
)

PACKAGE_TARGET_GLOBS = (
    "package.json",
    ".npmrc",
    ".pypirc",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle*",
    ".github/workflows/*",
)

ARTIFACT_TARGET_GLOBS = (
    "**/dist/**",
    "**/build/**",
    "**/out/**",
    "**/coverage/**",
    "**/*.map",
    "**/*.tgz",
    "**/*.zip",
    "**/*.vsix",
    "**/*.whl",
    "**/*.jar",
)

FALLBACK_HISTORY_PATTERNS = (
    r"sk-(proj-|svcacct-)?[A-Za-z0-9_-]{48,}",
    r"gh[pousr]_[A-Za-z0-9]{36}",
    r"AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}",
    r"lsv2_(pt|sk)_[A-Za-z0-9_-]{20,}|phx_[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{35}",
    r"(VSCE_PAT|OVSX_PAT|NPM_TOKEN|NPM_RELEASE_TOKEN|PYPI_TOKEN|TWINE_PASSWORD|HUGGINGFACE_HUB_TOKEN)",
)

DEEP_HISTORY_PATHS = (
    ".env*",
    ".mcp.json",
    ".cursor",
    ".claude",
    ".codex",
    ".continue",
    ".aider*",
    ".goose",
    ".opencode",
)


@dataclass(frozen=True)
class HistoryGuardrail:
    commit_count: int | None
    targeted_history_only: bool
    requires_confirmation: bool
    note: str


@dataclass(frozen=True)
class ScanPlan:
    mode: ScanMode
    project_path: str
    categories: list[str]
    priorities: dict
    target_globs: list[str]
    include_git_history: bool
    commit_scanner: str
    optional_deep_scanners: list[str]
    fallback_history_patterns: list[str]
    deep_history_paths: list[str]
    guardrail: HistoryGuardrail


def normalize_mode(mode: str) -> ScanMode:
    normalized = mode.strip().lower()
    if normalized not in {"quick", "full", "git-history"}:
        raise ValueError(f"Unsupported scan mode: {mode}")
    return normalized  # type: ignore[return-value]


def build_scan_plan(
    project_path: str | Path,
    mode: str = "full",
    *,
    commit_count: int | None = None,
    available_tools: set[str] | None = None,
) -> ScanPlan:
    scan_mode = normalize_mode(mode)
    tools = available_tools or set()
    categories = detect_project_type(project_path)
    include_git_history = scan_mode in {"full", "git-history"}

    return ScanPlan(
        mode=scan_mode,
        project_path=str(project_path),
        categories=categories,
        priorities=prioritize_patterns(categories),
        target_globs=target_globs_for_mode(scan_mode),
        include_git_history=include_git_history,
        commit_scanner=select_commit_scanner(tools, include_git_history),
        optional_deep_scanners=select_optional_deep_scanners(tools),
        fallback_history_patterns=list(FALLBACK_HISTORY_PATTERNS if include_git_history else ()),
        deep_history_paths=list(DEEP_HISTORY_PATHS if include_git_history else ()),
        guardrail=history_guardrail(commit_count),
    )


def target_globs_for_mode(mode: ScanMode) -> list[str]:
    globs = [*BASE_TARGET_GLOBS, *AI_AGENT_TARGET_GLOBS, *PACKAGE_TARGET_GLOBS]
    if mode in {"full", "git-history"}:
        globs.extend(ARTIFACT_TARGET_GLOBS)
    return sorted(set(globs))


def select_commit_scanner(available_tools: set[str], include_git_history: bool) -> str:
    if not include_git_history:
        return "not-run"
    if "gitleaks" in available_tools:
        return "gitleaks"
    return "fallback-git-log"


def select_optional_deep_scanners(available_tools: set[str]) -> list[str]:
    return sorted(tool for tool in ("trufflehog", "titus") if tool in available_tools)


def history_guardrail(commit_count: int | None) -> HistoryGuardrail:
    if commit_count is None:
        return HistoryGuardrail(
            commit_count=None,
            targeted_history_only=False,
            requires_confirmation=False,
            note="commit count not evaluated",
        )
    if commit_count > 2000:
        return HistoryGuardrail(
            commit_count=commit_count,
            targeted_history_only=True,
            requires_confirmation=True,
            note="requires confirmation before full patch-history scan",
        )
    if commit_count > 500:
        return HistoryGuardrail(
            commit_count=commit_count,
            targeted_history_only=True,
            requires_confirmation=False,
            note="prefer targeted history scans",
        )
    return HistoryGuardrail(
        commit_count=commit_count,
        targeted_history_only=False,
        requires_confirmation=False,
        note="full history scan allowed",
    )
