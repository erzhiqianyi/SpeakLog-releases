#!/usr/bin/env bash
# Offline validation only. Never downloads tools or publishes anything.
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
export PYTHONDONTWRITEBYTECODE=1
for tool in python3 node; do
  command -v "$tool" >/dev/null 2>&1 || { echo "Required tool is missing: $tool" >&2; exit 1; }
done
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else "Python 3.10+ is required")'
node -e 'if (Number(process.versions.node.split(".")[0]) < 22) { console.error("Node.js 22+ is required"); process.exit(1); }'
python3 "$ROOT/scripts/validate_website.py" "$ROOT/website"
python3 -m unittest discover -s "$ROOT/tests" -p 'test_*.py' -v
node --check "$ROOT/website/assets/site.js"
node --check "$ROOT/website/assets/analytics.js"
node --test "$ROOT/tests/site-behavior.test.cjs"
bash -n "$ROOT/website/deploy.sh" "$ROOT/scripts/check_website.sh"
