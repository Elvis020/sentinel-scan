# Emerging Secret-Scanning Risks: 2026 Refresh

Use this guide when updating Sentinel-Scan detectors and workflow defaults.

## Signals Incorporated

- GitHub expanded secret scanning and push protection coverage in April 2026 with Cloudflare detectors and default blocking for Cloudflare, Figma SCIM, Google bound-service-account API keys, LangSmith, OpenVSX, and PostHog secret types.
- GitGuardian's 2026 State of Secrets Sprawl reporting highlighted rapid AI-service leakage growth, MCP configuration leaks, and collaboration-tool exposure outside normal source files.
- Recent TruffleHog release notes emphasized decoded HTML coverage, deleted-file diff scanning, detector verification fixes, and safer command execution.
- Praetorian's Titus release emphasized validation, binary/archive extraction, SARIF output, and a broad long-tail SaaS rule set from Nosey Parker plus Kingfisher.
- AI-generated-code security research highlighted artifact hygiene, package drift, source-map exposure, hardcoded secrets, and supply-chain risk as gaps beyond classic regex scanning.

## Sentinel Updates To Keep

1. Treat AI/MCP configuration paths as high-value scan targets.
2. Include package publishing tokens (`VSCE_PAT`, `OVSX_PAT`, `NPM_TOKEN`, `PYPI_TOKEN`, `TWINE_PASSWORD`) in contextual scanning.
3. Add provider-specific coverage for stable prefixes (`AIza`, `lsv2_`, `phx_`) and context-anchored patterns where public docs name the token type but not a reliable token regex.
4. Flag source maps, generated bundles, archives, and extension packages as artifact hygiene signals.
5. Prefer optional external scanners for validation, decoding, and binary/archive extraction when already installed, while keeping Sentinel's built-in fallback path dependency-light.
6. Scan deleted-file history for `.env*` and AI/MCP config paths during `git-history` mode.

## Review Cadence

Refresh this guide when GitHub changelog posts announce new push-protection defaults, when gitleaks/TruffleHog/Titus add major detector families, or when incident reports show a repeated leak path that Sentinel does not target.
