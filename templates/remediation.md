# Security Remediation Guide

> Steps to fix identified security issues. Generated: {timestamp}

## Immediate Actions Required

### For Each Critical Finding:

1. **Identify the service** using the secret type
2. **Login to the service dashboard**
3. **Navigate to API keys/credentials section**
4. **Revoke the exposed key immediately**
5. **Generate a new key**
6. **Update your configuration**

---

## By Secret Type

### OpenAI API Keys (`sk-...`)

1. Go to [platform.openai.com](https://platform.openai.com)
2. Navigate to API Keys section
3. Delete the exposed key
4. Create new key with appropriate permissions
5. Update `.env` file (DO NOT commit the new key to git)

### GitHub Personal Access Tokens (`ghp_...`)

1. Go to GitHub Settings > Developer settings
2. Navigate to Personal access tokens
3. Revoke the exposed token
4. Create new token with minimal required scopes
5. Update local credentials storage

### AWS Access Keys (`AKIA...`)

1. Go to AWS IAM Console
2. Find the access key under Users > Security credentials
3. Deactivate the exposed key
4. Create new access key
5. Update all configurations that use the old key

### Stripe Keys (`sk_live_...`)

1. Go to [dashboard.stripe.com](https://dashboard.stripe.com)
2. Navigate to Developers > API keys
3. Reveal and copy the restricted key
4. Rotate any exposed keys
5. Update your server configuration

### Google API Keys (`AIza...`)

1. Go to Google Cloud Console > APIs & Services > Credentials
2. Identify the exposed API key and review its usage
3. Restrict the key by API, application, referrer, IP, or service account binding where possible
4. Rotate or delete the exposed key
5. Update runtime configuration without committing the replacement

### LangSmith Keys (`lsv2_...`)

1. Go to LangSmith settings for the relevant organization or workspace
2. Revoke the exposed personal access token or service key
3. Create a replacement with the narrowest workspace scope
4. Prefer service keys for production services and PATs only for personal tooling
5. Update local env or managed secret storage

### Cloudflare API Tokens / Keys

1. Go to Cloudflare Dashboard > My Profile > API Tokens
2. Revoke the exposed token or rotate the exposed global API key
3. Replace broad global keys with scoped API tokens whenever possible
4. Update deployment secrets and local developer env files

### Figma SCIM Tokens

1. Open Figma Admin settings for the organization
2. Navigate to Login and provisioning > SCIM provisioning
3. Revoke or regenerate the exposed SCIM API token
4. Update the identity provider integration secret
5. Confirm provisioning still works after rotation

### PostHog Personal API Keys (`phx_...`)

1. Go to PostHog account settings > Personal API keys
2. Revoke the exposed personal key
3. Create a replacement with the minimum required scopes
4. Update the consuming integration or local environment

### Package Publishing Tokens (`VSCE_PAT`, `OVSX_PAT`, `NPM_TOKEN`, `PYPI_TOKEN`)

1. Revoke the exposed registry or marketplace token immediately
2. Audit recent package, extension, and release activity for unauthorized publishes
3. Reissue a scoped token with publish-only permissions where supported
4. Store the replacement only in CI secret storage or a local secret manager
5. Avoid exposing publish tokens to untrusted pull request workflows or package install scripts

---

## Git History Cleanup

### If secrets were committed:

**Option 1: BFG Repo-Cleaner (Recommended)**
```bash
# Install BFG
brew install bfg

# Remove files containing secrets
bfg --delete-files containing-secrets.txt

# Or replace secret content
bfg --replace-text secrets.txt

# Push changes
git gc --prune=now -- aggressive
```

**Option 2: git filter-branch (Manual)**
```bash
# Find the commit with the secret
git log --all -p -S "secret-pattern" --source --remotes
git log --all -p --full-history -- '.env*' '.mcp.json' '.cursor' '.claude' '.codex' '.continue' '.aider*' '.goose' '.opencode'

# Remove from history (CAREFUL - rewrites history)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/file" \
  --prune-empty --tag-name-filter cat -- --all
```

### ⚠️ Important Warnings:

- **Do NOT rewrite history if the repo has been shared with others**
- **Notify team members if history is rewritten**
- **After cleanup, force push with: `git push --force`**

---

## Prevention Measures

### 1. Update .gitignore

```bash
# Add to .gitignore
.env
.env.*
.env.local
.env.development
.env.production
credentials.json
*.pem
*.key
config/secrets.*
.mcp.json
.cursor/
.claude/
.codex/
.continue/
.aider*
.goose/
.opencode/
*.map
*.tgz
*.zip
*.vsix
*.whl
```

### 2. Create .env.example

```bash
# Create a template WITHOUT real values
cp .env .env.example

# Then edit .env.example to have placeholder values
OPENAI_API_KEY=your-api-key-here
AWS_ACCESS_KEY_ID=your-access-key
# etc.

# Commit .env.example, NOT .env
```

### 3. Setup Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Check for common secret patterns
if git diff --cached | grep -iE "(sk-|sk-ant-|ghp_|AKIA|ASIA|AIza|lsv2_|phx_|OVSX_PAT|VSCE_PAT|NPM_TOKEN|PYPI_TOKEN|api[_-]?key.*=.*['\"][a-zA-Z0-9]{20,})"; then
    echo "SECRETS DETECTED - commit blocked"
    exit 1
fi
```

### 4. Add to CI/CD Pipeline

For GitHub Actions, add to `.github/workflows/security.yml`:

```yaml
- name: Run Gitleaks
  uses: gitleaks/gitleaks-action@v2
```

---

## Quick Checklist

- [ ] Rotate all exposed API keys
- [ ] Clean git history (if applicable)
- [ ] Add sensitive files to .gitignore
- [ ] Create .env.example template
- [ ] Move AI/MCP secrets out of checked-in config files
- [ ] Remove source maps, archives, and generated bundles that expose source or credentials
- [ ] Setup pre-commit hooks
- [ ] Enable CI/CD secret scanning

---
*Generated by Sentinel-Scan Skill*
*For additional help, consult your security team*
