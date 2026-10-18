#!/usr/bin/env bash
# One-command verification of research/line-system-saturation (no kappa claim): exact recomputation of every CHECKED item of the README -- the polar law and Lagrangian bound on
# D4/D5/D6/E6/E7/E8, generic-frame and blow-up constructions (c1), Theorem E ingredients and Theorem F constants (c2), the two-point point X* for k' = 2..5 (c3), descent
# E7 -> D6 -> D4 and E8 -> E7 (c4), the 14 saved L1_CONS systems (c5), the exact Delsarte dual certificate, uniform-angle arithmetic and signed-graph counts (c6).
# Step 0 checks the package against MANIFEST.sha256 and every pin of SOURCES.json and stops hard on any mismatch.
# Single process at a time; standard library Python only (no compiler, no SAT, no third-party packages).
#   usage: bash verify.sh [/fresh/output/dir]     (inside a checkout or `git archive` of the repository; nothing outside the package is read)
#   set PYTHON to choose the interpreter (>= 3.11).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/line-system-saturation.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1
T0=$SECONDS
echo "== 0. manifest and provenance"
if ! "$PY" -B "$HERE/scripts/provenance.py" | tee "$OUT/provenance.log" | sed 's/^/   /' || grep -q '^FAIL' "$OUT/provenance.log" \
   || [ "$(grep -c '^PASS' "$OUT/provenance.log")" != 2 ]; then
  echo "step 0 FAILED"; exit 1
fi
mkdir -p "$OUT/logs"; : > "$OUT/all.out"
run() {  # name script
  echo "== $1"
  ( cd "$HERE/checks" && "$PY" -B "$2" > "$OUT/logs/$2.log" 2>&1; echo $? > "$OUT/logs/$2.rc" )
  cat "$OUT/logs/$2.log" | tee -a "$OUT/all.out" | sed 's/^/   /'
  [ "$(cat "$OUT/logs/$2.rc")" = 0 ] || echo "FAIL $2 exit status $(cat "$OUT/logs/$2.rc")" | tee -a "$OUT/all.out"
}
run "c1 polar law, Lagrangian bound, ladder, generic frames, blow-up" c1_ladder.py
run "c2 norm-2 systems (Theorem E ingredients) and Theorem F constants" c2_normtwo.py
run "c3 two-point point X* on W(2k-1,2), k = 2..5" c3_twopoint.py
run "c4 descent E7 -> D6 -> D4, E8 -> E7" c4_descent.py
run "c5 the 14 saved L1_CONS systems" c5_l1cons.py
run "c6 Delsarte dual certificate, uniform-angle arithmetic, signed-graph counts" c6_delsarte_uniform.py
run "c7 PR2222 rank correction: binom(50,3) = 19,600 < 19,648 (maintainer review)" pr2222_rank.py

# Optional (needs GAP >= 4.12 with ctbllib; set GAP=/path/to/gap): smallest nontrivial degree of Sp(10,2) = 155
if [ -n "${GAP:-}" ]; then
  echo "== c8 GAP: smallest nontrivial ordinary degrees of Sp(6,2), Sp(8,2), Sp(10,2) = 7, 35, 155 (ATLAS tables)"
  "$GAP" -q -b "$HERE/checks/gap/sp2n2_degrees.g" < /dev/null 2>&1 | grep -v '^#I' | tee "$OUT/logs/gap.log" | sed 's/^/   /'
  grep -q GAP_SP2N2_PASS "$OUT/logs/gap.log" || { echo "FAIL c8 GAP check"; exit 1; }
else
  echo "== c8 GAP check SKIPPED (set GAP=/path/to/gap); recorded output: checks/gap/sp2n2_degrees.out.txt"
fi
EXPECT=87
npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out")
echo "== done in $((SECONDS - T0))s: $((npass + 2)) PASS (2 in step 0), $nfail FAIL; logs in $OUT"
[ "$nfail" = 0 ] && [ "$npass" = "$EXPECT" ] || { echo "FAILED: expected $EXPECT assertion PASS lines after step 0, got $npass PASS / $nfail FAIL"; exit 1; }
