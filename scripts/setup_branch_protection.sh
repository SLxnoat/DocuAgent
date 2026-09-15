#!/usr/bin/env bash
# ==============================================================================
# Script: setup_branch_protection.sh
# Description: Automates GitHub branch protection rule application via gh CLI
# Usage: ./scripts/setup_branch_protection.sh [OWNER/REPO]
# ==============================================================================

set -euo pipefail

REPO="${1:-}"

if [[ -z "$REPO" ]]; then
  # Try to detect repo from git remote
  REMOTE_URL=$(git config --get remote.origin.url || true)
  if [[ "$REMOTE_URL" =~ github.com[:/]([^/]+/[^/.]+)(\.git)?$ ]]; then
    REPO="${BASH_REMATCH[1]}"
  else
    echo "Usage: $0 <OWNER/REPO>"
    echo "Example: $0 organization/DocuAgent"
    exit 1
  fi
fi

echo "==> Configuring branch protection for: $REPO"

# Verify gh CLI is authenticated
if ! command -v gh &> /dev/null; then
  echo "Error: gh CLI is not installed. Visit https://cli.github.com"
  exit 1
fi

if ! gh auth status &> /dev/null; then
  echo "Error: gh CLI is not authenticated. Run 'gh auth login' first."
  exit 1
fi

echo "==> [1/2] Applying branch protection rules to 'main'..."
gh api -X PUT "/repos/${REPO}/branches/main/protection" \
  -H "Accept: application/vnd.github+json" \
  --input - <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "ci/lint",
      "ci/type-check",
      "ci/test-backend",
      "ci/test-frontend"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 2
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": true
}
EOF

echo "==> [2/2] Applying branch protection rules to 'develop'..."
gh api -X PUT "/repos/${REPO}/branches/develop/protection" \
  -H "Accept: application/vnd.github+json" \
  --input - <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "ci/lint",
      "ci/type-check",
      "ci/test-backend",
      "ci/test-frontend"
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": false
}
EOF

echo "==> Branch protection configured successfully for 'main' and 'develop'."
