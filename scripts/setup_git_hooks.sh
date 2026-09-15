#!/usr/bin/env bash
# ==============================================================================
# Script: setup_git_hooks.sh
# Description: Installs pre-commit tool and configures Git hooks for the repo
# Usage: ./scripts/setup_git_hooks.sh
# ==============================================================================

set -euo pipefail

echo "==> Setting up Git hooks and Pre-commit environment..."

# Detect or install pre-commit
if ! command -v pre-commit &> /dev/null; then
  echo "==> Installing pre-commit using pip..."
  if command -v pip3 &> /dev/null; then
    pip3 install --user pre-commit || pip3 install pre-commit
  elif command -v pip &> /dev/null; then
    pip install --user pre-commit || pip install pre-commit
  else
    echo "Error: pip3 / pip is not available. Please install pre-commit manually:"
    echo "  pip install pre-commit  OR  brew install pre-commit"
    exit 1
  fi
fi

echo "==> Verifying pre-commit installation..."
pre-commit --version

echo "==> Installing pre-commit hook..."
pre-commit install --hook-type pre-commit

echo "==> Installing commit-msg hook (Conventional Commits linter)..."
pre-commit install --hook-type commit-msg

echo "==> Git hooks successfully installed and active!"
echo "    - pre-commit: runs Ruff, Prettier, and sanity checks on staged files"
echo "    - commit-msg: validates commit message adheres to Conventional Commits"
