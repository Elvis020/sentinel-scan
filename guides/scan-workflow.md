# Sentinel-Scan Workflow

## 0) Pre-scan

1. Read `.sentinel-ignore` (if present).
2. Read `.codebase-indexer/docs/architecture.md` and `implementation.md` (if present).
3. Build a focused target list:
- `.env*`
- `**/*credentials*`
- `**/*secret*`
- AI and agent configs: `.mcp.json`, `.cursor/`, `.claude/`, `.codex/`, `.continue/`, `.aider*`, `.goose/`, `.opencode/`
- Package and release configs: `package.json`, `.npmrc`, `.pypirc`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle*`, `.github/workflows/*`
- Artifact hygiene targets: `dist/`, `build/`, `out/`, `coverage/`, `*.map`, `*.tgz`, `*.zip`, `*.vsix`, `*.whl`, `*.jar`
- files/dirs called out in index docs
4. Resolve commit scanner:
- If `gitleaks` exists locally, use it.
- If missing and internet/package access is available, attempt install.
- If install is not possible (offline/blocked) or execution fails, continue with fallback history scans and record `gitleaks skipped: <reason>`.
5. Resolve optional deep scanners:
- If `trufflehog` exists locally, use `--no-update --fail --json` style output when appropriate and keep raw output out of reports.
- If `titus` exists locally, use it for validation, binary/archive extraction, and SARIF-compatible review.
- If neither exists, continue with Sentinel's built-in targeted `rg` and `git log` workflow.

## 1) Quick scan (working tree)

Use executable commands (examples):

```bash
# target discovery
rg --files -g '**/.env*' -g '**/*config*' -g '**/*credentials*' -g '**/*secret*'
rg --files -g '**/.mcp.json' -g '**/.cursor/**' -g '**/.claude/**' -g '**/.codex/**' -g '**/.continue/**' -g '**/.aider*' -g '**/.goose/**' -g '**/.opencode/**'
rg --files -g '**/dist/**' -g '**/build/**' -g '**/out/**' -g '**/coverage/**' -g '**/*.map' -g '**/*.tgz' -g '**/*.zip' -g '**/*.vsix' -g '**/*.whl' -g '**/*.jar'

# critical token patterns (pcre2 for modern regex)
rg -n --pcre2 'sk-(proj-|svcacct-)?[A-Za-z0-9_-]{48,}'
rg -n --pcre2 'gh[pousr]_[A-Za-z0-9]{36}'
rg -n --pcre2 'AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}'
rg -n --pcre2 'AIza[0-9A-Za-z_-]{35}'
rg -n --pcre2 'sk_(live|test)_[A-Za-z0-9]{24}'
rg -n --pcre2 'lsv2_(pt|sk)_[A-Za-z0-9_-]{20,}'
rg -n --pcre2 'phx_[A-Za-z0-9_-]{20,}'
rg -n --pcre2 -- '-----BEGIN(?: [A-Z]+)? PRIVATE KEY-----'
```

## 2) Full scan additions

```bash
# broad but still file-based
rg -n --pcre2 '(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*["\'\`][^"\'\`]{8,}["\'\`]'
rg -n --pcre2 '(?i)(mcp|modelcontextprotocol|claude|cursor|codex|continue|aider|goose|opencode).{0,60}(api[_-]?key|secret|token|password)\s*[:=]\s*["\'\`][^"\'\`]{8,}["\'\`]'
rg -n --pcre2 '(?i)(VSCE_PAT|OVSX_PAT|NPM_TOKEN|NPM_RELEASE_TOKEN|PYPI_TOKEN|TWINE_PASSWORD|HUGGINGFACE_HUB_TOKEN)\s*[:=]\s*["\'\`]?[^"\'\`\s]{8,}'

# common connection strings
rg -n --pcre2 '(postgres|mysql|mongodb(?:\+srv)?|redis)://[^\s]+'

# 2026 provider/context additions
rg -n --pcre2 '(?i)(cloudflare|cf[_-]?(api|account|user)).{0,40}(api[_-]?token|global[_-]?api[_-]?key|api[_-]?key).{0,20}["\'\`][A-Za-z0-9_-]{32,}["\'\`]'
rg -n --pcre2 '(?i)(figma).{0,40}(scim|api[_-]?token|bearer).{0,20}["\'\`][A-Za-z0-9_-]{24,}["\'\`]'
rg -n --pcre2 '(?i)(langsmith|langchain).{0,40}(license[_-]?key|scim[_-]?(bearer[_-]?)?token).{0,20}["\'\`][A-Za-z0-9_.-]{20,}["\'\`]'
rg -n --pcre2 '(?i)(openvsx|ovsx).{0,30}(pat|access[_-]?token|token).{0,20}["\'\`][A-Za-z0-9_.-]{20,}["\'\`]'

# artifact hygiene signals
rg -n --pcre2 '(?i)(sourceMappingURL|sourcesContent|Authorization:\s*Bearer|BEGIN [A-Z]+ PRIVATE KEY)' -g '*.map' -g '*.html' -g '*.md'
```

## 3) Git history scan

```bash
# size guard
git rev-list --count HEAD

# preferred commit-history scanner (when available)
gitleaks git --verbose --redact --source .

# fallback targeted history search
git log --all -p -G 'sk-(proj-|svcacct-)?[A-Za-z0-9_-]{48,}'
git log --all -p -G 'gh[pousr]_[A-Za-z0-9]{36}'
git log --all -p -G 'AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}'
git log --all -p -G 'lsv2_(pt|sk)_[A-Za-z0-9_-]{20,}|phx_[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{35}'
git log --all -p -G '(VSCE_PAT|OVSX_PAT|NPM_TOKEN|NPM_RELEASE_TOKEN|PYPI_TOKEN|TWINE_PASSWORD|HUGGINGFACE_HUB_TOKEN)'

# optional deeper env history
git log --all -p --full-history -- '.env*'
git log --all -p --full-history -- '.mcp.json' '.cursor' '.claude' '.codex' '.continue' '.aider*' '.goose' '.opencode'
```

Guardrails:
- If commits `>500`: warn + prefer targeted history scans.
- If commits `>2000`: require explicit confirmation before full patch-history scan.
- If `gitleaks` is not available or fails (for example, offline install failure), do not fail the full scan. Continue with fallback `git log` scans and add a note to the report: `gitleaks skipped: <reason>`.

## 4) Result handling

For each finding:
- file path
- line number
- matched detector
- masked value (`first4...last4`)
- severity
- suppression status (`[suppressed]` when matched by `.sentinel-ignore`)
- source (`working-tree`, `git-history`, `artifact-hygiene`, `external-scanner`)
- provider when known (`github`, `aws`, `cloudflare`, `langsmith`, etc.)

## 5) Reporting

Write to `.sentinel/`:
- `security.md`
- `secrets-found.md` (if findings)
- `remediation.md` (if findings)
