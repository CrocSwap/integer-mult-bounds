#!/usr/bin/env bash
# Verification of research/a2-family-b-locus (no kappa claim).  usage: bash verify.sh [/fresh/output/dir]   (Python >= 3.11, numpy, networkx; PYTHON=/path/to/python)
# At most 6 processes at a time (the 28 P104 triangle representatives run 6-way), every process under `timeout 1200`; no SAT solver; no unbounded loops.
#   0  MANIFEST.sha256 pins every shipped file (including the recorded logs)
#   1  bcheck.py facts (a)-(e) and the floor line: P112, E8 (UNIT=...), and the 28 P104 triangle representatives (A2TRI=...); re-run output compared byte-for-byte with the recorded logs
#      (d) includes Q_XX, the square inside lower bound with the triangle X deleted on both sides, by the opt3u duality branch-and-bound
#   3  qxx.py partial punctures of Q_XX (P112; 6-way) and inrelax.py (inside relaxation alone)
#   2  relax.py: the class-level relaxation WITH the e9 row and e9 column; prints its optimum (62 / 58 / 70 at |supp beta| = 1, m = 10) and the configuration whose infeasibility THEORY.md Sec. 2 proves
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/blocus.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1
C="$HERE/checks"; REC="$HERE/evidence/logs"; mkdir -p "$OUT/logs"; : > "$OUT/all.out"
T0=$SECONDS
note() { echo "$@" | tee -a "$OUT/all.out"; }
echo "== 0. manifest"
if ! "$PY" -B "$C/manifest_check.py" | tee -a "$OUT/all.out" | sed 's/^/   /' || grep -q '^FAIL' "$OUT/all.out"; then echo "step 0 FAILED"; exit 1; fi
# one(NAME UNIT TRI RECORDED): run bcheck.py, compare with the recorded log, require (a)-(e) lines and the floor line
export PY C OUT REC
one() { local n=$1 u=$2 t=$3 rec=$4
  ( cd "$OUT" && UNIT=$u A2TRI=$t timeout 1200 "$PY" -B "$C/bcheck.py" > "$OUT/logs/$n.log" 2>&1 ); local rc=$?
  if [ $rc = 0 ] && cmp -s "$OUT/logs/$n.log" "$REC/$rec" && grep -q '^(a) ok' "$OUT/logs/$n.log" && grep -q '^(e) ok' "$OUT/logs/$n.log" && grep -q '^FLOOR B-locus' "$OUT/logs/$n.log"
  then echo "PASS bcheck $n: $(grep '^FLOOR' "$OUT/logs/$n.log")"; else echo "FAIL bcheck $n (exit $rc; log differs from recorded or a fact failed)"; fi; }
export -f one
echo "== 1. bcheck.py facts (a)-(e)"
# P112 and E8 use the default triangle of the unit (A2TRI unset: pass the empty string, which a2lib treats as unset)
{ one P112 P112 "" bcheck_P112.log.txt; one E8 E8 "" bcheck_E8.log.txt; } 2>&1 | tee -a "$OUT/all.out"
REPS="0,3,22 0,5,24 0,60,103 0,61,102 1,3,31 1,5,33 1,44,96 1,45,95 1,46,94 1,47,93 1,49,92 1,50,91 1,51,90 5,44,101 5,45,100 5,48,97 5,53,93 5,56,91 7,44,102 7,46,100 7,48,98 7,52,95 7,54,93 9,44,103 9,47,100 9,49,98 9,50,97 9,53,95"
echo $REPS | tr ' ' '\n' | xargs -P 6 -I{} bash -c 'T={}; one "P104_${T//,/_}" P104 "$T" "b104_${T//,/_}.log.txt"' 2>&1 | sort | tee -a "$OUT/all.out"
n=$(echo $REPS | wc -w | tr -d " "); np=$(grep -c '^PASS bcheck P104_' "$OUT/all.out")
if [ "$np" = "$n" ] && [ "$n" = 28 ]; then note "PASS all 28 P104 triangle representatives: B-locus floor line reproduced"; else note "FAIL P104 representatives: $np of $n passed"; fi
grep -h '^FLOOR' "$OUT"/logs/P104_*.log | sort | uniq -c | sed 's/^/   /' | tee -a "$OUT/all.out" >/dev/null
nf=$(grep -h '^FLOOR B-locus m>=10: 58 ' "$OUT"/logs/P104_*.log | wc -l | tr -d " "); [ "$nf" = 28 ] && note "PASS P104: FLOOR 58 on 28 of 28 representatives" || note "FAIL P104: FLOOR 58 on $nf of 28"
grep -q '^FLOOR B-locus m>=10: 64 ' "$OUT/logs/P112.log" && note "PASS P112: B-locus floor 64" || note "FAIL P112 floor"
grep -q '^FLOOR B-locus m>=10: 72 ' "$OUT/logs/E8.log" && note "PASS E8: B-locus floor 72" || note "FAIL E8 floor"
grep -q '^(d) Q_XX 62$' "$OUT/logs/P112.log" && grep -q '^(d) Q_XX 70$' "$OUT/logs/E8.log" && grep -q '^(d) Q_XX 56$' "$OUT/logs/P104_0_3_22.log" && note "PASS Q_XX (square inside lower bound, triangle deleted on both sides): 62 / 56 / 70" || note "FAIL Q_XX"
echo "== 2. the relaxation optimum (slack) with e9 row and e9 column"
for U in P112 P104 E8; do
  ( cd "$OUT" && UNIT=$U timeout 1200 "$PY" -B "$C/relax.py" > "$OUT/logs/relax_$U.log" 2>&1 )
  cmp -s "$OUT/logs/relax_$U.log" "$REC/relax_$U.log.txt" && note "PASS relax $U identical to the recorded log" || note "FAIL relax $U differs from the recorded log"
done
grep -q 'suppbeta 1 m 10 cost 62$' "$OUT/logs/relax_P112.log" && grep -q 'suppbeta 1 m 10 cost 58$' "$OUT/logs/relax_P104.log" && grep -q 'suppbeta 1 m 10 cost 70$' "$OUT/logs/relax_E8.log" \
  && note "PASS relaxation optimum at m = 10, |supp beta| = 1: 62 / 58 / 70 (P112, E8: not attainable by a decoder, README Sec. 3; P104: equals the proven floor)" || note "FAIL relaxation optimum"
echo "== 3. auxiliary: partial punctures of Q_XX (P112, 6-way) and the inside relaxation alone (inrelax.py)"
export -f one
q() { local n=$1; shift; ( cd "$OUT" && UNIT=P112 timeout 1200 "$PY" -B "$C/qxx.py" "$@" > "$OUT/logs/qxx_$n.log" 2>&1 ); cmp -s "$OUT/logs/qxx_$n.log" "$REC/qxx_$n.log.txt" && echo "PASS qxx $n identical to recorded: $(cat "$OUT/logs/qxx_$n.log")" || echo "FAIL qxx $n"; }
export -f q
printf '%s\n' "1_1 1 1" "2_2 2 2" "2_2_alt 2 2 alt" "3_0 3 0" "3_1 3 1" "3_3 3 3" | xargs -P 6 -I{} bash -c 'set -- {}; q "$@"' 2>&1 | sort | tee -a "$OUT/all.out"
for U in P112 P104 E8; do
  ( cd "$OUT" && UNIT=$U timeout 1200 "$PY" -B "$C/inrelax.py" > "$OUT/logs/inrelax_$U.log" 2>&1 )
  cmp -s "$OUT/logs/inrelax_$U.log" "$REC/inrelax_$U.log.txt" && note "PASS inrelax $U identical to the recorded log" || note "FAIL inrelax $U"
done
npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out")
echo "== done in $((SECONDS - T0))s: $npass PASS, $nfail FAIL; logs in $OUT"
[ "$nfail" = 0 ] && { echo "PASS: all assertions hold"; exit 0; }
echo "FAIL"; exit 1
