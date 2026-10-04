#!/bin/bash
# Publish the site to Cloudflare Pages (project "speaklog" → https://speak.erzhiqian.cc).
# Only the files the site serves are uploaded; docs and generator scripts stay local.
set -euo pipefail
cd "$(dirname "$0")"
OUT=$(mktemp -d)
trap 'rm -rf "$OUT"' EXIT
rsync -a --exclude README.md --exclude deploy.sh --exclude make-og.swift --exclude .DS_Store ./ "$OUT/"
npx -y wrangler@4 pages deploy "$OUT" --project-name speaklog --branch main --commit-dirty=true
