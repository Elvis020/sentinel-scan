# Sentinel-Scan Patterns (Curated)

This guide focuses on high-signal patterns with lower false-positive rates.

## Critical

```regex
# OpenAI / Anthropic style
sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{48,}
sk-ant-[A-Za-z0-9_-]{48,}

# GitHub tokens
gh[pousr]_[A-Za-z0-9]{36}

# AWS access keys
AKIA[0-9A-Z]{16}
ASIA[0-9A-Z]{16}

# Google API keys
AIza[0-9A-Za-z_-]{35}

# Stripe keys
sk_(?:live|test)_[A-Za-z0-9]{24}

# LangSmith API keys
lsv2_(?:pt|sk)_[A-Za-z0-9_-]{20,}

# PostHog personal API keys
phx_[A-Za-z0-9_-]{20,}

# Private key headers
-----BEGIN(?: [A-Z]+)? PRIVATE KEY-----
```

## High

```regex
# GitHub 2026 push-protection expansion, context anchored
(?i)(cloudflare|cf[_-]?(?:api|account|user)).{0,40}(?:api[_-]?token|global[_-]?api[_-]?key|api[_-]?key).{0,20}["\'\`][A-Za-z0-9_-]{32,}["\'\`]
(?i)(figma).{0,40}(?:scim|api[_-]?token|bearer).{0,20}["\'\`][A-Za-z0-9_-]{24,}["\'\`]
(?i)(langsmith|langchain).{0,40}(?:license[_-]?key|scim[_-]?(?:bearer[_-]?)?token).{0,20}["\'\`][A-Za-z0-9_.-]{20,}["\'\`]
(?i)(openvsx|ovsx).{0,30}(?:pat|access[_-]?token|token).{0,20}["\'\`][A-Za-z0-9_.-]{20,}["\'\`]
(?i)(posthog).{0,30}(?:personal[_-]?api[_-]?key|api[_-]?key|token).{0,20}["\'\`]phx_[A-Za-z0-9_-]{20,}["\'\`]

# Context-anchored AWS secret key
(?i)(aws|secret_access_key).{0,20}["\'\`][A-Za-z0-9/+=]{40}["\'\`]

# Slack / SendGrid
xox[baprs]-[0-9]{8,13}-[0-9]{8,13}-[A-Za-z0-9-]{20,}
SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}

# Connection strings
(postgres|mysql|mongodb(?:\+srv)?|redis)://[^\s]+

# JWT-like token
eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+
```

## Medium (context required)

```regex
(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*["\'\`][^"\'\`]{8,}["\'\`]
(?i)(mcp|modelcontextprotocol|claude|cursor|codex|continue|aider|goose|opencode).{0,60}(api[_-]?key|secret|token|password)\s*[:=]\s*["\'\`][^"\'\`]{8,}["\'\`]
(?i)(VSCE_PAT|OVSX_PAT|NPM_TOKEN|NPM_RELEASE_TOKEN|PYPI_TOKEN|TWINE_PASSWORD|HUGGINGFACE_HUB_TOKEN)\s*[:=]\s*["\'\`]?[^"\'\`\s]{8,}
```

Only raise medium findings when assignment context is clear and value is non-placeholder.

## Artifact hygiene signals

Treat these as exposure risks even when no token-shaped value is found:

```regex
# Browser/package artifacts that often expose source or embedded config
(?i)(^|/)(dist|build|out|coverage)/.*\.map$
(?i)\.(?:tar\.gz|tgz|zip|vsix|whl|jar|apk|ipa)$
(?i)(^|/)(npm-debug|yarn-error|pnpm-debug)\.log$
```

Raise as `MEDIUM` by default, or `HIGH` when the artifact is tracked and contains source, env names, auth headers, or connection-string context.

## False-positive controls

Treat as likely placeholder unless additional evidence exists:

```regex
(?i)(example|sample|placeholder|dummy|fake|test|changeme)
AKIAIOSFODNN7EXAMPLE
AIzaSyD-EXAMPLE0000000000000000000000000
```

## Suppression

Use `.sentinel-ignore` path matching. Suppressed findings remain visible with:
- severity downgraded to `LOW`
- `[suppressed]` label
