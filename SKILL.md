---
name: sentinel-scan
description: Scan codebase for leaked secrets, API keys, and sensitive data. Use for security scans and secret detection. Outputs reports to .sentinel/ and uses .codebase-indexer/docs/ as optional scan context.
---

# Sentinel-Scan

Scan the current project for leaked secrets, API keys, and sensitive data, then generate actionable reports.

## Scope and Paths

- **Report output path (authoritative):** `.sentinel/`
- **Optional scan context input:** `.codebase-indexer/docs/`

Sentinel writes only to `.sentinel/`. It may read `.codebase-indexer/docs/` to target high-value files.

## Modes

| Mode | Trigger | Behavior |
|---|---|---|
| `full` | "scan for secrets", "security audit", "rescan" | Working tree + high-value paths + optional git history |
| `quick` | "quick scan", "fast scan" | High-value files only |
| `git-history` | "scan commits", "check git history" | Commit-history focused scan |

## Required Rules

1. Check for `.sentinel-ignore` first and apply suppressions.
2. Read `.codebase-indexer/docs/architecture.md` + `implementation.md` when present.
3. Prefer targeted scanning over full-repo file reads.
4. Never print full secret values; mask as `first4...last4`.
5. Use executable/valid regex search commands (e.g., `rg --pcre2`).
6. Run git history scan only with commit-count guardrails.
7. For commit-history leaks, attempt `gitleaks` first when available.
8. If `gitleaks` cannot run (missing binary, install blocked, offline, execution failure), continue with fallback `git log` scans and explicitly report that `gitleaks` was skipped and why.
9. Treat AI-agent and MCP configuration files as high-value targets (`.mcp.json`, `.cursor/`, `.claude/`, `.codex/`, `.continue/`, `.aider*`, `.goose/`, `.opencode/`).
10. Include artifact hygiene checks for generated packages, source maps, exported docs, archives, and extension bundles.
11. When optional scanners such as `trufflehog` or `titus` are already available, use them for validation, decoding, and binary/archive extraction; do not make the scan fail when they are absent.

## Scan Workflow

1. Pre-scan setup
- Read `.sentinel-ignore` (if present).
- Determine mode (`full`, `quick`, `git-history`).
- If `.codebase-indexer/docs/` exists, collect high-value targets from docs.

2. Targeted file scan
- Always scan `.env*`, known config/credential files, and indexer-identified sensitive paths.
- Also scan AI/MCP configs, package publishing configs, CI workflows, generated source maps, and release artifacts.
- Run critical patterns first, then high-confidence contextual patterns.
- Include 2026 provider additions: Cloudflare, Figma SCIM, Google API keys, LangSmith, OpenVSX, and PostHog.

3. Git history scan (mode-dependent)
- `git rev-list --count HEAD` first.
- If `gitleaks` is missing, attempt install only when network access is available.
- Try `gitleaks git --verbose --redact --source .` for commit-history scanning.
- If `gitleaks` is unavailable or fails, run fallback targeted history scans (including `.env*`) and record skip reason.
- Include deleted-file history for `.env*` and AI/MCP configuration paths.
- If `>500`, warn and default to targeted `-G`/`-S` scans.
- If `>2000`, require explicit user confirmation before full patch-history scan.

4. Report generation (`.sentinel/`)
- `security.md`
- `secrets-found.md` (only if findings > 0)
- `remediation.md` (only if findings > 0)

## Severity Guidance

- `CRITICAL`: active secret in tracked file or deploy config
- `HIGH`: secret found in git history or likely-active credential artifact
- `MEDIUM`: unverified credential-like string requiring manual review
- `LOW`: suppressed or placeholder-like hit

## Integration with Codebase Indexer

Use `.codebase-indexer/docs/` only for scan targeting:
- `architecture.md`: config/env locations
- `implementation.md`: modules where credentials are handled
- `patterns.md`: project conventions that affect false positives

Do not write Sentinel reports into `.codebase-indexer/docs/`.
