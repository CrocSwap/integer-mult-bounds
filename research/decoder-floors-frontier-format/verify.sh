#!/usr/bin/env bash
# One-command verification of research/decoder-floors-frontier-format (no kappa claim).  Recomputes every CHECKED item of the README:
#   c1 Theorem R (rigidity of the minimal-rank label table): CNF regeneration + hashes, shipped DRAT proofs, kissat re-solve + drat-trim;
#   c2 Lemma 1.1 census, survivors and pair ranks (Theorem P);  c3 batching premises and an O(9) chart with 64 rank-7 cross pairs;
#   c4 #1180's nine-term identity (65), co-star dead sets;  c5 decoders attaining the floors;  c6 EDGE E1a block minrank and puncture clique-hitting bounds;
#   c7 the P111 bit unit.
# Step 0 checks the package against MANIFEST.sha256 and every pin of SOURCES.json and stops hard on any mismatch.
# Single process at a time; standard-library Python only.  kissat 4.0.4 (KISSAT=/path or on PATH) and drat-trim (DRAT_TRIM=/path or on PATH) are OPTIONAL:
# without them the lines that need them are SKIP lines (never PASS).  HIT_FULL=1 re-solves three slow clique-hitting instances (kissat only, no proof).
#   usage: bash verify.sh [/fresh/output/dir]     (inside a checkout or `git archive` of the repository)
#   set PYTHON to choose the interpreter (>= 3.11).  Prints PASS / FAIL; exit status is nonzero on any FAIL.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/decoder-floors-frontier-format.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1
T0=$SECONDS
echo "== 0. manifest and provenance"
if ! "$PY" -B "$HERE/scripts/provenance.py" | tee "$OUT/provenance.log" | sed 's/^/   /' || grep -q '^FAIL' "$OUT/provenance.log" \
   || [ "$(grep -c '^PASS' "$OUT/provenance.log")" != 2 ]; then
  echo "step 0 FAILED"; exit 1
fi
echo "   tools: kissat=$(command -v "${KISSAT:-kissat}" 2>/dev/null || echo none)  drat-trim=$(command -v "${DRAT_TRIM:-drat-trim}" 2>/dev/null || echo none)"
mkdir -p "$OUT/logs"; : > "$OUT/all.out"
run() {  # name script
  echo "== $1"
  ( cd "$HERE/checks" && "$PY" -B "$2" > "$OUT/logs/$2.log" 2>&1; echo $? > "$OUT/logs/$2.rc" )
  cat "$OUT/logs/$2.log" | tee -a "$OUT/all.out" | sed 's/^/   /'
  [ "$(cat "$OUT/logs/$2.rc")" = 0 ] || echo "FAIL $2 exit status $(cat "$OUT/logs/$2.rc")" | tee -a "$OUT/all.out"
}
run "c1 Theorem R: rigidity of the minimal-rank label table (30 SAT instances)" c1_rigidity.py
run "c2 Lemma 1.1 census, survivors and pair ranks" c2_support_propagation.py
run "c3 batching premises (P112 labels, normals, frame lemma, O(9) chart)" c3_batch_premises.py
run "c4 #1180 identity, co-star dead sets, survivor cliques" c4_masked_costar.py
run "c5 decoders attaining the floors" c5_attaining_decoders.py
run "c6 coordinate-block minrank under every B; puncture clique hitting" c6_block_minrank_punctures.py
run "c7 the P111 bit unit" c7_p111_unit.py
npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out"); nskip=$(grep -c '^SKIP' "$OUT/all.out")
EXPECT=$((72 - nskip))
echo "== done in $((SECONDS - T0))s: $((npass + 2)) PASS (2 in step 0), $nskip SKIP, $nfail FAIL; logs in $OUT"
if [ "$nfail" = 0 ] && [ "$npass" = "$EXPECT" ]; then echo "PASS: all expected assertions hold"; exit 0; fi
echo "FAIL: expected $EXPECT assertion PASS lines after step 0, got $npass PASS / $nfail FAIL / $nskip SKIP"; exit 1
