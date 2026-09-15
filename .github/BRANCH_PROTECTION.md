# Branch Protection & Governance Policy

**Document ID:** GOV-001  
**Version:** 1.0.0  
**Effective Date:** September 2026  
**Audience:** All Contributors, Maintainers, DevOps

---

## 1. Branch Hierarchy

The repository maintains two long-lived protected branches:

```
[feature/*, fix/*, chore/*]
          │
          ▼  (PR + 1 Approval + CI Green)
      [develop]  ── Integration branch (staging environment)
          │
          ▼  (PR + 2 Approvals + Full Test Suite)
       [main]    ── Production branch (live deployment)
```

| Branch      | Purpose                          | Protection Level          | Deployment Target  |
| ----------- | -------------------------------- | ------------------------- | ------------------ |
| `main`      | Production-ready stable release  | Maximum (Strict)          | Production         |
| `develop`   | Integration & continuous testing | Standard Protected        | Staging / Pre-prod |
| `feature/*` | Feature development              | Unprotected (short-lived) | Local / Preview    |
| `fix/*`     | Defect resolution                | Unprotected (short-lived) | Local / Preview    |
| `release/*` | Release stabilization            | Protected                 | Staging Freeze     |

---

## 2. Protection Rules for `main`

The following GitHub branch protection rules are mandatory for `main`:

1. **Require a Pull Request before merging:**
   - Require minimum **2 peer approvals** from code owners.
   - Dismiss stale pull request approvals when new commits are pushed.
   - Require review from Code Owners (`CODEOWNERS`).
2. **Require status checks to pass before merging:**
   - Require branches to be up to date before merging (`Strict`).
   - Required status checks:
     - `ci/lint` (Ruff, ESLint, Prettier)
     - `ci/type-check` (Mypy strict, TSC strict)
     - `ci/test-backend` (Pytest unit & integration)
     - `ci/test-frontend` (Vitest component tests)
     - `security/audit` (pip-audit & npm audit)
3. **Require signed commits:**
   - All commits in PR must be cryptographically signed (GPG/SSH).
4. **Require linear history:**
   - Enforce **Squash and Merge** or **Rebase and Merge**. Merge commits disallowed on `main`.
5. **Disallow force pushes & branch deletions:**
   - Force pushes: **Disabled**.
   - Deletion of `main`: **Disabled**.
6. **Include administrators:**
   - Policy applies to repository administrators and bots.

---

## 3. Protection Rules for `develop`

1. **Require a Pull Request before merging:**
   - Require minimum **1 peer approval**.
   - Dismiss stale pull request approvals on push.
2. **Require status checks to pass:**
   - `ci/lint`
   - `ci/type-check`
   - `ci/test-backend`
   - `ci/test-frontend`
3. **Disallow force pushes & branch deletions:**
   - Force pushes: **Disabled**.
   - Deletion of `develop`: **Disabled**.

---

## 4. Automated Configuration via GitHub CLI

Run the included setup script to apply these rules to your GitHub remote:

```bash
chmod +x scripts/setup_branch_protection.sh
./scripts/setup_branch_protection.sh <OWNER>/<REPO>
```

Or execute via `gh` CLI directly:

```bash
# Enable protection on main
gh api -X PUT /repos/:owner/:repo/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  --input - <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "ci/lint",
      "ci/type-check",
      "ci/test-backend",
      "ci/test-frontend",
      "security/audit"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 2
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": true
}
EOF
```
