#!/usr/bin/env bash
# CLEANUP_v29.sh — run from the root of the knowledge-library repo.
#
# Removes the three orphan stub directories under content/security/ that
# rendered as duplicate Application Security / Cloud Security / Vulnerability
# Management entries on the deployed site. Safe to re-run; idempotent.
#
# After this script runs, commit the deletions and push:
#   git add -A
#   git commit -m "chore: remove security/* orphan stubs (v29 strict build)"
#   git push origin main
set -e

if [ ! -d "content/security" ]; then
  echo "ERROR: run this script from the root of the knowledge-library repo"
  echo "(expected to find a content/security/ directory)"
  exit 1
fi

REMOVED=0
for orphan in appsec cloud vulnerability; do
  if [ -d "content/security/$orphan" ]; then
    echo "  removing content/security/$orphan/"
    git rm -rf "content/security/$orphan" 2>/dev/null || rm -rf "content/security/$orphan"
    REMOVED=$((REMOVED + 1))
  fi
done

if [ $REMOVED -eq 0 ]; then
  echo "No orphan directories found — your repo is already clean."
else
  echo
  echo "Removed $REMOVED orphan director(y/ies). Next:"
  echo "  git add -A"
  echo "  git commit -m 'chore: remove security/* orphan stubs (v29 strict build)'"
  echo "  git push origin main"
fi
