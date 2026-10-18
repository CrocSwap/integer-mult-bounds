#!/usr/bin/env bash
# One-command verification of research/format-limits-2 (no kappa claim): the erratum to #595 and the invoice calculus (sections 1-2),
# the censuses and cold-end gauges of the #656 word (3-4), the decoder floors and the spec/verifier requirements (5-6) and the centre
# barrier, fragmentation and ledger rows (7-9).  Step 0 checks the package against MANIFEST.sha256 and every vendored input against its
# pin in SOURCES.json (git blob ids / sha256) and stops hard on any mismatch; then each section group's checks run and print one PASS/FAIL
# line per assertion.  Exit status 0 only if every assertion passes.
#   usage: bash verify.sh [/fresh/output/dir]      (inside a checkout or `git archive` of the repository; nothing outside the package is read)
#   needs python3 >= 3.11 with numpy, scipy and sympy (requirements.txt) for sections 5-9; set PYTHON to choose the interpreter.
#   Sections 1-4 use the standard library only; a C++ compiler is used by E2 if present (otherwise E2 compares the shipped output).
#   About 1 minute wall on 4 cores (the four groups run at once).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/format-limits-2.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHON="$PY" PYTHONDONTWRITEBYTECODE=1
T0=$SECONDS
echo "== 0. manifest and provenance"
if ! "$PY" -B "$HERE/scripts/provenance.py" | tee "$OUT/provenance.log" | sed 's/^/   /' || grep -q '^FAIL' "$OUT/provenance.log" \
   || [ "$(grep -c '^PASS' "$OUT/provenance.log")" != 2 ]; then
  echo "step 0 FAILED"; exit 1
fi
echo "== 1-9. checks  [$((SECONDS - T0))s]"
G="s1-2-erratum-invoice s3-4-census-gauges s5-6-decoders-spec s7-9-centre-fragmentation"
for g in $G; do
  mkdir -p "$OUT/$g"
  ( PKG="$HERE/$g" OUT="$OUT/$g" bash "$HERE/$g/verify.part.sh" "$OUT/$g" > "$OUT/$g.log" 2>&1; echo $? > "$OUT/$g.rc" ) &
done
wait
status=0; npass=0; nfail=0
for g in $G; do
  echo "== $g"
  sed 's/^/   /' "$OUT/$g.log"
  p=$(grep -c '^ *PASS' "$OUT/$g.log"); f=$(grep -c '^ *FAIL' "$OUT/$g.log")
  npass=$((npass + p)); nfail=$((nfail + f))
  if [ "$(cat "$OUT/$g.rc")" != 0 ] || [ "$f" != 0 ] || [ "$p" = 0 ]; then echo "   FAILED: $g (exit $(cat "$OUT/$g.rc"), $f FAIL lines)"; status=1; fi
done
echo "== done in $((SECONDS - T0))s: $((npass + 2)) PASS (2 in step 0), $nfail FAIL; logs in $OUT"
exit $status
