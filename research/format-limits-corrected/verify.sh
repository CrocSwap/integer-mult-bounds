#!/usr/bin/env bash
# One-command verification of research/format-limits (no kappa claim): the format ceiling (rev. 2), the spec versus
# convention census, the structural lemmas with their exact toys, the design-free helper bounds and the complex helper
# prices.  Step 0 checks the package against MANIFEST.sha256, the vendored inputs against the git blob ids of their PR
# commits (SOURCES.json) and the files of main it reads (DEPENDS.json); steps A-E recompute every checked claim and
# print one PASS/FAIL line per claim.  Exit status 0 only if every claim passes.
#   usage: bash verify.sh [/fresh/output/dir]        (run inside a checkout or `git archive` of the whole repository)
#   needs python3 >= 3.11 with numpy, scipy, sympy, python-sat and ortools (requirements.txt); set PYTHON to
#   choose the interpreter and JOBS (default 6) for the number of checks run at once.  About 2 minutes on 12 cores.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/format-limits.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"
export PYTHONDONTWRITEBYTECODE=1 FORMAT_LIMITS_REPO="$REPO"
T0=$SECONDS
echo "== 0. manifest, vendored inputs (git blob ids), files of main (sha256)"
if ! "$PY" -B "$HERE/scripts/provenance.py" | tee "$OUT/provenance.log" | sed 's/^/   /'; then :; fi
if grep -q '^FAIL' "$OUT/provenance.log" || ! grep -q '^PASS 0.depends' "$OUT/provenance.log"; then
  echo "step 0 FAILED"; exit 1
fi
echo "== A-E. checks  [$((SECONDS - T0))s]"
status=0
"$PY" -B "$HERE/scripts/run_all.py" "$OUT" "${JOBS:-6}" || status=$?
echo "== done in $((SECONDS - T0))s; logs and RECEIPT.json in $OUT"
exit $status
