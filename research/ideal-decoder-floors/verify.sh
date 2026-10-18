#!/usr/bin/env bash
# One-command verification of research/ideal-decoder-floors (no kappa claim): exact recomputation of every CHECKED number of the README -- label ranks and the
# E8 block-rank law (c1), explicit decoders E8 72 / P112 64 / P104 56 / E7 49 / E7-F 42 / D4 12 / D5 20 / D6 30 (c2), Theorem 4 types, r_min, omega and
# sharpness (c3), D5/E6 deficient directions, incidences and N-space (c4), place-bound survivors and the tropical ceiling (c5), rank-44 witnesses, 2-adic
# carry and forced minors (c6).  Step 0 checks the package against MANIFEST.sha256 and every pin of SOURCES.json and stops hard on any mismatch.
# Single process at a time; standard library Python only (no compiler, no SAT, no third-party packages).
#   usage: bash verify.sh [/fresh/output/dir]     (inside a checkout or `git archive` of the repository; nothing outside the package is read)
#   set PYTHON to choose the interpreter (>= 3.11).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/ideal-decoder-floors.XXXXXX")}
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
run "c1 labels and the dense polar law (E8 block ranks 9/8/8/7)" c1_polar.py
run "c2 explicit exact decoders and their dense-B cost" c2_decoders.py
run "c3 Theorem 4: types, r_min, omega, sharpness" c3_floor.py
run "c4 D5 and E6: deficient directions, incidences, N-space" c4_coupling.py
run "c5 place bound: survivors and the tropical ceiling" c5_place.py
run "c6 rank-44 witnesses, 2-adic carry, forced minors" c6_beyond.py
EXPECT=64
npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out")
echo "== done in $((SECONDS - T0))s: $((npass + 2)) PASS (2 in step 0), $nfail FAIL; logs in $OUT"
[ "$nfail" = 0 ] && [ "$npass" = "$EXPECT" ] || { echo "FAILED: expected $EXPECT assertion PASS lines after step 0, got $npass PASS / $nfail FAIL"; exit 1; }
