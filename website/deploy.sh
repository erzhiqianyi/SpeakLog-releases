#!/usr/bin/env bash
# Default: offline validation and temporary build. Only --production publishes.
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
MODE=${1:---dry-run}
if [[ $# -gt 1 || ( "$MODE" != "--dry-run" && "$MODE" != "--production" && "$MODE" != "--help" ) ]]; then
  echo "Usage: website/deploy.sh [--dry-run|--production|--help]" >&2
  exit 2
fi
if [[ "$MODE" == "--help" ]]; then
  echo "Usage: website/deploy.sh [--dry-run|--production]"
  echo "No argument / --dry-run: offline checks and an allowlisted temporary build; no upload."
  echo "--production: after checks, publish a clean main-branch commit to Cloudflare Pages."
  exit 0
fi
export PYTHONDONTWRITEBYTECODE=1
"$ROOT/scripts/check_website.sh"
OUT=$(mktemp -d "${TMPDIR:-/tmp}/speaklog-site.XXXXXX")
trap 'rm -rf "$OUT"' EXIT
python3 "$ROOT/scripts/build_website.py" "$OUT" --source "$ROOT/website"
python3 "$ROOT/scripts/validate_website.py" "$OUT"
WRANGLER_VERSION=$(tr -d '\r\n' < "$ROOT/scripts/wrangler-version.txt")
if [[ ! "$WRANGLER_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Wrangler must be pinned to an exact stable version" >&2
  exit 1
fi
if [[ "$MODE" == "--dry-run" ]]; then
  echo "Dry run passed. Nothing was uploaded; Wrangler was not downloaded or invoked."
  echo "Production target: Cloudflare Pages project speaklog, branch main, Wrangler $WRANGLER_VERSION."
  echo "To publish deliberately after review: website/deploy.sh --production"
  exit 0
fi
command -v npm >/dev/null 2>&1 || { echo "npm is required for an explicit production deploy" >&2; exit 1; }
command -v git >/dev/null 2>&1 || { echo "git is required for an explicit production deploy" >&2; exit 1; }
[[ "$(git -C "$ROOT" branch --show-current)" == "main" ]] || { echo "Production deploy requires the main branch" >&2; exit 1; }
[[ -z "$(git -C "$ROOT" status --porcelain)" ]] || { echo "Production deploy requires a clean, reviewed commit (including no untracked files)" >&2; exit 1; }
COMMIT=$(git -C "$ROOT" rev-parse --verify HEAD)
cd "$ROOT"
# CI=1 prevents an unattended login flow; use an existing authorized login/token.
export CI=1 WRANGLER_SEND_METRICS=false
npm exec --yes --package="wrangler@$WRANGLER_VERSION" -- wrangler whoami
npm exec --yes --package="wrangler@$WRANGLER_VERSION" -- wrangler pages deploy "$OUT" \
  --project-name speaklog --branch main --commit-hash "$COMMIT" --commit-dirty=false
# Verification is read-only and deliberately separate from publication.
echo "Upload completed. Verify its returned deployment URL with:"
echo "python3 scripts/smoke_website.py --base-url https://<deployment>.speaklog.pages.dev"
echo "Then verify the production domain with the same command."
