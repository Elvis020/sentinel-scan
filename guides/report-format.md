# Sentinel-Scan Report Format

`sentinel_scan.reporting` is the executable contract for finding fields, severity/status/source validation, detail rendering, and report output paths. Keep this guide aligned with that module.

## Required outputs

- `.sentinel/security.md`
- `.sentinel/secrets-found.md` (if findings)
- `.sentinel/remediation.md` (if findings)

## Masking rule (authoritative)

Always mask detected values as:
- `first4...last4`

Never print full raw secrets.

## Minimum finding fields

- `id`
- `severity`
- `file`
- `line`
- `detector`
- `provider` (`unknown` when not inferable)
- `source` (`working-tree` | `git-history` | `artifact-hygiene` | `external-scanner`)
- `masked_value`
- `status` (`active` | `suppressed`)

## Severity buckets

- `CRITICAL`
- `HIGH`
- `MEDIUM`
- `LOW`
