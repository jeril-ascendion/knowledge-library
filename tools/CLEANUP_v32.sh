#!/usr/bin/env bash
# CLEANUP_v32.sh — run from the root of the knowledge-library repo.
#
# v32 (Observability group) added 5 new pages under content/observability/.
# The slugs (incident-response, logs, metrics, sli-slo, traces) were
# already pre-registered in TAXONOMY, so no orphan stubs are expected.
#
# This script is idempotent: it scans content/observability/ for any
# subdirectory that is NOT in the expected slug list and removes it.
# Safe to re-run. After this script runs, commit any deletions:
#   git add -A
#   git commit -m "chore: remove orphan observability subdirs (v32 observability group)"
#   git push origin main

set -e

if [ ! -d "content" ]; then
  echo "ERROR: run this script from the root of the knowledge-library repo"
  echo "(expected to find a content/ directory)"
  exit 1
fi

if [ ! -d "content/observability" ]; then
  echo "No content/observability/ directory found — nothing to check."
  exit 0
fi

EXPECTED="incident-response logs metrics sli-slo traces"
REMOVED=0

for sub in $(ls content/observability/ 2>/dev/null); do
  case " $EXPECTED " in
    *" $sub "*)
      ;; # expected, keep
    *)
      echo "  removing orphan content/observability/$sub/"
      git rm -rf "content/observability/$sub" 2>/dev/null || rm -rf "content/observability/$sub"
      REMOVED=$((REMOVED + 1))
      ;;
  esac
done

if [ $REMOVED -eq 0 ]; then
  echo "No orphan directories found under content/observability/ — already clean."
  echo "(Expected slugs: $EXPECTED — all present.)"
else
  echo
  echo "Removed $REMOVED orphan director(y/ies). Next:"
  echo "  git add -A"
  echo "  git commit -m 'chore: remove orphan observability subdirs (v32 observability group)'"
  echo "  git push origin main"
fi
