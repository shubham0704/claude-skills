#!/usr/bin/env bash
#
# Pre-push audit for the claude skills repo.
#
# Greps for common leakage patterns before pushing to a public remote.
# Warns (does not block) — you decide whether each hit is a real
# problem or a false positive.
#
# Run manually before `git push`, or wire it up as a git pre-push hook
# by symlinking it into .git/hooks/pre-push.
#
# Exit code:
#   0 — no hits, safe to push
#   1 — hits found, review required
#
# Usage:
#   ./scripts/pre-push-audit.sh           # scan entire repo
#   ./scripts/pre-push-audit.sh --staged  # scan only staged files

set -u

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT" || exit 1

SCAN_TARGET="."
if [[ "${1:-}" == "--staged" ]]; then
  SCAN_TARGET=$(git diff --cached --name-only --diff-filter=ACM)
  if [[ -z "$SCAN_TARGET" ]]; then
    echo "No staged files to audit."
    exit 0
  fi
fi

hits=0

# Helper: report a pattern match with context.
scan() {
  local label="$1"
  local pattern="$2"
  local results
  # shellcheck disable=SC2086
  results=$(grep -rInE --include="*.md" --include="*.tex" --include="*.py" \
                  --include="*.sh" --include="*.json" --include="*.yaml" \
                  --include="*.yml" --include="*.txt" \
                  --exclude="pre-push-audit.sh" \
                  --exclude-dir=.git --exclude-dir=node_modules \
                  --exclude-dir=__pycache__ --exclude-dir=".mypy_cache" \
                  --exclude-dir=".ruff_cache" --exclude-dir=".pytest_cache" \
                  "$pattern" $SCAN_TARGET 2>/dev/null)
  if [[ -n "$results" ]]; then
    echo ""
    echo "⚠️  $label"
    echo "-------------------------------------------"
    echo "$results" | head -20
    local count
    count=$(echo "$results" | wc -l | tr -d ' ')
    if (( count > 20 )); then
      echo "... ($((count - 20)) more)"
    fi
    hits=$((hits + 1))
  fi
}

echo "Scanning $REPO_ROOT for leakage patterns..."

# Absolute home paths — reveals username, can reveal project structure
scan "Absolute /Users/... paths (macOS home)"  '/Users/[a-zA-Z0-9_.-]+'
scan "Absolute /home/... paths (Linux home)"   '/home/[a-zA-Z0-9_.-]+'

# API keys and common secret token formats
scan "OpenAI-style API keys (sk-...)"          'sk-[a-zA-Z0-9]{20,}'
scan "Anthropic API keys"                      'sk-ant-[a-zA-Z0-9_-]{20,}'
scan "AWS access keys"                         'AKIA[0-9A-Z]{16}'
scan "GitHub personal access tokens"           'gh[pousr]_[a-zA-Z0-9]{20,}'
scan "Google API keys"                         'AIza[0-9A-Za-z_-]{30,}'
scan "Slack tokens"                            'xox[baprs]-[a-zA-Z0-9-]{10,}'
scan "Generic 'api_key' / 'secret' assignments" '(api[_-]?key|secret|password|token)[[:space:]]*[:=][[:space:]]*["'"'"']?[a-zA-Z0-9_-]{16,}'

# Email addresses — often personal/professional contact
scan "Email addresses (excluding noreply@)"    '[a-zA-Z0-9._%+-]+@(?!noreply|example\.com)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

# Private IPs and internal hostnames
scan "Private 10.x IPs"                        '\b10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\b'
scan "Private 192.168.x IPs"                   '\b192\.168\.[0-9]{1,3}\.[0-9]{1,3}\b'
scan ".internal / .local / .corp hostnames"    '[a-zA-Z0-9-]+\.(internal|local|corp|intranet)\b'

# Common internal/client name leak spots — customize this list to YOUR projects
# This is a placeholder; add your own client/project names here once you
# notice them leaking. Example:
#   scan "Client name ACME"                      '\bACME\b'
scan "TODO/FIXME/XXX markers (review before publishing)" '\b(TODO|FIXME|XXX|HACK)\b'

echo ""
if (( hits == 0 )); then
  echo "✅ No leakage patterns found. Safe to push."
  exit 0
else
  echo "❌ $hits pattern(s) flagged. Review the matches above before pushing."
  echo ""
  echo "False positives are common — a match doesn't mean you must remove it."
  echo "Make the judgment yourself, then either fix and re-run, or proceed."
  exit 1
fi
