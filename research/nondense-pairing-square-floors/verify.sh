#!/usr/bin/env bash
# Verification of research/nondense-pairing-square-floors (no kappa claim).
#   usage: bash verify.sh [/fresh/output/dir]     PYTHON=python3 (numpy scipy sympy)  KISSAT=kissat  CC=cc   FULL=1 for the complete re-solve
# Default (about 6-12 minutes, <= 2 busy processes): 0 manifest; 1 build the pinned drat-trim from vendor/; 2 both orbit implementations (in parallel)
#   + recount agreement; 3 fixed 32-type sample re-solved at rank <= 8 by BOTH CNF writers with drat-trim VERIFIED; 4 brute force = both writers (60 instances);
#   5 E8 orthogonal-normal counterexample; 6 D4 (all 192 D-sets), D6 (scan |D|<=19), E7 counterexamples; 7 sharp decoders (E8 72, P112 64, P104 56).
# FULL=1 adds: all 4022 types re-solved by writer A and by writer B (4 chunks each, run 4 at a time, each chunk well under 20 min), every proof drat-trim VERIFIED,
#   plus the complete D6 scan. Missing tools => FAIL/SKIP and exit 1 (never PASS).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); C="$HERE/checks"
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/nondense.XXXXXX")}; mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export KISSAT="${KISSAT:-kissat}"; CCx="${CC:-cc}"; export DRAT_TRIM="$OUT/drat-trim"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1
NICE="nice -n 10"; mkdir -p "$OUT/logs"; : > "$OUT/all.out"; T0=$SECONDS; FAILS=0
note() { echo "$@" | tee -a "$OUT/all.out"; }
echo "== 0. manifest"; "$PY" -B "$C/manifest_check.py" | tee -a "$OUT/all.out" | sed 's/^/   /'; grep -q '^FAIL' "$OUT/all.out" && { echo "step 0 FAILED"; exit 1; }
"$PY" -c "import numpy, scipy, sympy" 2>/dev/null || { note "FAIL python needs numpy, scipy, sympy"; exit 1; }
command -v "$KISSAT" >/dev/null 2>&1 || { note "FAIL kissat missing (KISSAT=)"; exit 1; }
echo "== 1. drat-trim built from vendor/drat-trim/drat-trim.c"
$CCx -O2 -o "$DRAT_TRIM" "$HERE/vendor/drat-trim/drat-trim.c" 2>"$OUT/logs/cc.log" && note "PASS drat-trim built" || { note "FAIL drat-trim build"; tail -3 "$OUT/logs/cc.log"; exit 1; }
# chk NAME 'what' cmd... : PASS iff exit 0 and the last PASS/FAIL line of the log starts with PASS
chk() { local n=$1 what=$2; shift 2; ( cd "$C" && $NICE timeout 1500 "$@" > "$OUT/logs/$n.log" 2>&1 ); local rc=$?
  if [ $rc = 0 ] && grep -q '^PASS' "$OUT/logs/$n.log" && ! grep -q '^FAIL' "$OUT/logs/$n.log"; then note "PASS $what  [$(grep -h '^PASS' "$OUT/logs/$n.log" | tail -1 | cut -c1-150)]"; else note "FAIL $what (exit $rc)"; tail -3 "$OUT/logs/$n.log" | sed 's/^/      /'; FAILS=$((FAILS+1)); fi; }
echo "== 2. orbit recount, two implementations (440880 hyperplanes, 4022 nonorthogonal types, min |D| = 30)"
chk orbA "orbit implementation A (IDEAL: coweight orbits + union-find over W_J)" "$PY" -B orbits_a.py "$OUT/types_a.json.gz" &
P1=$!
chk orbB "orbit implementation B (finisher: ambient coordinates, all 120 reflections, scipy components)" "$PY" -B orbits_b.py "$OUT/types_b.json.gz" &
P2=$!
wait $P1 $P2
for n in orbA orbB; do grep -q "hyperplanes 440880 types 4340 nonorth 4022 orth 318 min|D| nonorth 30" "$OUT/logs/$n.log" && note "PASS $n: 440880 hyperplanes, 4022 nonorthogonal + 318 orthogonal types, min |D| = 30" || { note "FAIL $n counts"; FAILS=$((FAILS+1)); }; done
chk cmp "the two implementations agree type by type (node class, |D|, orthogonality degree sequence)" "$PY" -B compare_orbits.py "$OUT/types_a.json.gz" "$OUT/types_b.json.gz"
echo "== 3. fixed 32-type sample re-solved at rank <= 8, both CNF writers, DRAT VERIFIED"
chk solA "writer A (IDEAL CNF) on the sample" "$PY" -B solve_types.py "$OUT/types_a.json.gz" A 8 sample &
P1=$!
chk solB "writer B (independent chunked-XOR CNF) on the sample, types from implementation B" "$PY" -B solve_types.py "$OUT/types_b.json.gz" B 8 sample &
P2=$!
wait $P1 $P2
echo "== 4. brute force over all fitting B = both CNF writers (60 instances)"
chk brute "brute-force minrank vs both CNF writers" "$PY" -B brute_agree.py &
P1=$!
echo "== 5-6. counterexamples to the per-term claim"
chk e8orth "E8 orthogonal normals |D|=24 mr2=6" "$PY" -B counter_e8orth.py
wait $P1
chk d4 "D4: 192 D-sets, mr2 >= 3" "$PY" -B small.py D4
chk e7 "E7 type |D|=11 mr2=5" "$PY" -B small.py E7 "$OUT/types_b.json.gz.normals.npz"
chk d6 "D6 counterexamples (|D|<=19 scan)" "$PY" -B small.py D6 $([ "${FULL:-0}" = 1 ] && echo full)
echo "== 7. sharp decoders: E8 72, P112 64, P104 56"
chk dec "exact decoders" "$PY" -B decoders.py
if [ "${FULL:-0}" = 1 ]; then
  echo "== 8. FULL: all 4022 types, both writers (4 chunks at a time), every DRAT proof VERIFIED"
  for W in A B; do
    for i in 0 1 2 3; do ( cd "$C" && $NICE timeout 1200 "$PY" -B solve_types.py "$OUT/types_$(echo $W | tr AB ab).json.gz" $W 8 chunk:$i/4 > "$OUT/logs/full$W$i.log" 2>&1 ) & done; wait
    tot=0; okc=0; for i in 0 1 2 3; do t=$(grep -E '^writer' "$OUT/logs/full$W$i.log" | awk '{print $4}'); b=$(grep -E '^writer' "$OUT/logs/full$W$i.log" | awk '{print $6}'); tot=$((tot+${t:-0})); [ "${b:-1}" = 0 ] && okc=$((okc+1)); done
    [ $tot = 4022 ] && [ $okc = 4 ] && note "PASS FULL writer $W: all 4022 types UNSAT at rank <= 8, every proof VERIFIED" || { note "FAIL FULL writer $W (types $tot, clean chunks $okc/4)"; FAILS=$((FAILS+1)); }
  done
fi
note "== done in $((SECONDS-T0)) s; failures: $FAILS"
[ $FAILS = 0 ] && { echo "ALL PASS"; exit 0; } || { echo "SOME FAILED"; exit 1; }
