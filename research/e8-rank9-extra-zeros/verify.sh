#!/usr/bin/env bash
# Verification of research/e8-rank9-extra-zeros (no kappa claim).   usage: bash verify.sh [/fresh/output/dir]     PYTHON=  KISSAT=  DRAT_TRIM=  (FULL=1 for the fresh solves)
#   0  MANIFEST.sha256
#   1  exact finite facts: spans S1/S2/S3'/W2 and P-compatible frames (spans.py, spans3.py, pframes.py, as in #2819), clique spans (cliquespans.py), the bridge to the kappa-family / a2lib normal forms (bridge.py, 12 exact members),
#      span facts (spansminus.py), rigidity on E8 minus an A2 triangle (rigA2.py), frame choice (fchoice.py, lemex.py, hit.py), P-compatible frames on E8 minus a clique (pcompK.py, pcompK2.py)
#   2  CNF regeneration, byte-identical to the pinned sha256: s56 (56-line incidence problem), scope b (Theorem Z1 residue), scope z + NOPURE (Theorem R, <= 3 extra zeros per row and column),
#      rk8 and rk7 (Theorem RK: rank-8 rigidity with arbitrary extra zeros on E8 minus an 8- / 7-clique)
#   3  shipped DRAT proofs (xz) decompress to the pinned sha256 and are accepted by the standard drat-trim; s56 is re-solved with kissat and re-checked
#   FULL=1: fresh kissat solves of rk8, rk7, scope b, scope z + NOPURE (limit 1200 s each) each followed by drat-trim, and the negative control (rk8 without its goal clause must be SAT)
#   4  recorded logs of the original runs (asserted, not re-run)
# One heavy process at a time, run under nice 10, each external call under timeout 1200.  Missing numpy/sympy/kissat/drat-trim/xz => SKIP lines (never PASS) and exit 1.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/e8extrazeros.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; KISSAT="${KISSAT:-kissat}"; DT="${DRAT_TRIM:-drat-trim}"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1
NICE="nice -n 10"; TO="timeout 1200"; C="$HERE/checks"; EV="$HERE/evidence"; SAT="$HERE/sat"; W="$OUT/work"; mkdir -p "$W" "$OUT/logs"; : > "$OUT/all.out"; T0=$SECONDS
note() { echo "$@" | tee -a "$OUT/all.out"; }
sha() { shasum -a 256 "$1" 2>/dev/null | cut -d' ' -f1 || sha256sum "$1" | cut -d' ' -f1; }
pin() { awk -F'\t' -v n="$1" '$2==n{print $1}' "$EV/pins.tsv"; }
echo "== 0. manifest"
if ! "$PY" -B "$C/manifest_check.py" | tee -a "$OUT/all.out" | sed 's/^/   /' || grep -q '^FAIL' "$OUT/all.out"; then echo "step 0 FAILED"; exit 1; fi
HAVE=1
"$PY" -c "import numpy, sympy" 2>/dev/null || { note "SKIP python needs numpy and sympy"; HAVE=0; }
for t in "$KISSAT" "$DT" xz; do command -v "$t" >/dev/null 2>&1 || { note "SKIP tool missing: $t"; HAVE=0; }; done
[ "$HAVE" = 0 ] && { echo "INCOMPLETE: tools missing"; exit 1; }
# run SCRIPT [args] -> logs/NAME.log ; then every pattern in EXPECT must occur (fixed strings)
runchk() { local n=$1; shift; local expect=$1; shift
  ( cd "$W" && $NICE $TO "$PY" -B "$C/$1" "${@:2}" > "$OUT/logs/$n.log" 2>&1 ); local rc=$? ok=1
  [ $rc = 0 ] || ok=0
  while IFS= read -r pat; do [ -z "$pat" ] && continue; grep -qF -- "$pat" "$OUT/logs/$n.log" || { ok=0; note "   missing line: $pat"; }; done <<< "$expect"
  if [ $ok = 1 ]; then note "PASS ran $n"; else note "FAIL ran $n (exit $rc)"; tail -3 "$OUT/logs/$n.log" | sed 's/^/      /'; fi; }
echo "== 1. exact finite facts"
runchk spans "PASS spans E8" spans.py
runchk spans3 "PASS spans3: (S3prime) over 1512 pairs and (W2): 28 directions, no 3 in a 2-plane" spans3.py
runchk pframes "PASS pframes: all 2025 E8 frames are P-compatible; all 3780 orthogonal pairs lie in a frame" pframes.py
runchk cliquespans "maximal cliques: 44320 by size: [(3, 1120), (7, 34560), (8, 8640)]
orbit rep size 8 rank 8, orbit size 8640
orbit rep size 7 rank 7, orbit size 34560
S1-K/S2-K failures: 0
PASS cliquespans" cliquespans.py "$C"
runchk bridge "PASS bridge
dependent non-clique pairs found: 2" bridge.py "$C"
[ "$(grep -c 'root realisation True' "$OUT/logs/bridge.log")" = 12 ] && ! grep -q 'False' "$OUT/logs/bridge.log" && note "PASS bridge: 12 exact members, each with forced zeros, diagonal 1, rank 9, rank 8 off S and N[T,T] a root realisation" || note "FAIL bridge member count"
runchk spansminus "(S1-) failures: 0  (checked 7560 cases)
(S2-) failures: 0  (checked 241500 cases)
(C-A) failures: 0  (checked 3136 cases, all 28 pairs of frames()[0])" spansminus.py
runchk rigA2 "frames inside L': 1620  H-frames inside L': 1620
(C1) every line of L' in an H-frame: True  min count 90
(C2'') ordered non-orth pairs in L': 6390  failing: 0" rigA2.py
runchk lemex "cases 58016 failures 168" lemex.py
runchk fchoice "configs 974580 fails 0" fchoice.py
runchk hit "through line 135 through orth pair 15
line: per-line counts [(15, 63)]
pair: hitting number (lines != f1,f2) = 5" hit.py
runchk pcompK8 "frames inside L' 945 P-compatible w.r.t. L' 0" pcompK.py "$C" 8
runchk pcompK7 "frames inside L' 1080 P-compatible w.r.t. L' 450" pcompK.py "$C" 7
runchk pcompK2_8 "first frame of type (cls,pat)=(0, 1): frames(L)[0] = (1, 27, 44, 54, 58, 61, 83, 84), missing triple patterns [((27, 83, 84), (1, 1))]
Counter({(0, 1, (1, 1, 1, 1, 1, 1, 2)): 35, (0, 4, (2, 2, 2, 2)): 15})" pcompK2.py "$C" 8
runchk pcompK2_7 "first frame of type (cls,pat)=(0, 0): frames(L)[0] = (1, 26, 44, 55, 66, 69, 75, 76), missing triple patterns []" pcompK2.py "$C" 7
echo "== 2. CNF regeneration (byte-identical to the pinned sha256)"
gen() { # name, pin name, command...
  local n=$1 p=$2; shift 2; ( cd "$W" && $NICE $TO "$@" > "$OUT/logs/gen_$n.log" 2>&1 )
  [ "$(sha "$W/$n.cnf")" = "$(pin "$p")" ] && note "PASS $p regenerated: sha256 equals the pinned value ($(tail -1 "$OUT/logs/gen_$n.log"))" || note "FAIL $p sha256"; }
gen s56_0 s56_0.cnf "$PY" -B "$C/s56z.py" s56_0.cnf
gen zb zb.cnf "$PY" -B "$C/pinz.py" zb.cnf --scope b
gen np_z np_z.cnf "$PY" -B "$C/pinz2.py" np_z.cnf --scope z --nopure 1
gen rk8 rk8.cnf "$PY" -B "$C/rkz.py" "$C" 8 20 rk8.cnf "$SAT/rk8_final_extra.txt"
gen rk7 rk7.cnf "$PY" -B "$C/rkz.py" "$C" 7 20 rk7.cnf "$SAT/rk7_final_extra.txt"
echo "== 3. DRAT proofs"
dtcheck() { # label cnf drat log
  local r; r=$(cd "$W" && $NICE $TO "$DT" "$2" "$3" 2>&1 | tee "$OUT/logs/$4.log" | tr '\r' '\n' | grep -E '^s ')
  [ "$r" = "s VERIFIED" ] && note "PASS standard drat-trim: $1 VERIFIED ($(tr '\r' '\n' < "$OUT/logs/$4.log" | grep -E 'verification time' | tr -d '\n'))" || note "FAIL drat-trim on $1: '$r'"; }
for n in rk8 rk7 zb np_z; do
  xz -dc "$EV/proofs/$n.drat.xz" > "$W/$n.drat"
  [ "$(sha "$W/$n.drat")" = "$(pin $n.drat)" ] && note "PASS shipped proof $n.drat.xz decompresses to the pinned sha256" || note "FAIL shipped proof $n sha256"
  dtcheck "shipped $n proof" $n.cnf $n.drat dt_$n
  rm -f "$W/$n.drat"
done
r=$(cd "$W" && $NICE $TO "$KISSAT" -q --factor=false --preprocessfactor=false s56_0.cnf s56_0.drat --no-binary | head -1)
[ "$r" = "s UNSATISFIABLE" ] && note "PASS s56: kissat UNSAT" || note "FAIL s56 kissat: '$r'"
dtcheck "fresh s56 proof" s56_0.cnf s56_0.drat dt_s56; rm -f "$W/s56_0.drat"
if [ "${FULL:-0}" = 1 ]; then
  for n in rk8 rk7 zb np_z; do
    s=$SECONDS; r=$(cd "$W" && $NICE $TO "$KISSAT" -q --factor=false --preprocessfactor=false $n.cnf ${n}_fresh.drat --no-binary | head -1)
    if [ "$r" = "s UNSATISFIABLE" ]; then note "PASS fresh kissat solve of $n: UNSAT in $((SECONDS-s))s"; dtcheck "fresh $n proof" $n.cnf ${n}_fresh.drat dtf_$n
    else note "FAIL fresh kissat solve of $n: '$r'"; fi
    rm -f "$W/${n}_fresh.drat"
  done
  ( cd "$W" && NOGOAL=1 $NICE $TO "$PY" -B "$C/rkz.py" "$C" 8 20 rk8_nogoal.cnf "$SAT/rk8_final_extra.txt" > /dev/null 2>&1 )
  r=$(cd "$W" && $NICE $TO "$KISSAT" -q rk8_nogoal.cnf | head -1)
  [ "$r" = "s SATISFIABLE" ] && note "PASS negative control: rk8 without its goal clause is SAT (so the UNSAT is due to 'some extra zero')" || note "FAIL negative control: '$r'"
else note "SKIP-FULL fresh solves of rk8, rk7, scope b, scope z + NOPURE and the negative control (FULL=1); the shipped proofs are checked above"; fi
echo "== 4. recorded logs (not re-run here)"
crlf() { tr '\r' '\n' < "$1"; }
for n in rk8 rk7 zb np_z; do crlf "$EV/logs/dratrim_$n.log.txt" | grep -q '^s VERIFIED' && note "PASS recorded: drat-trim on the shipped $n proof: s VERIFIED" || note "FAIL recorded drat-trim log $n"; done
for n in rk8 rk7 zb np_z; do grep -q '^s UNSATISFIABLE' "$EV/logs/kissat_$n.log.txt" && note "PASS recorded: original kissat run on $n: s UNSATISFIABLE" || note "FAIL recorded kissat log $n"; done
grep -q '^s SATISFIABLE' "$EV/logs/kissat_rk8_nogoal.log.txt" && note "PASS recorded: negative control (rk8 without goal clause): s SATISFIABLE" || note "FAIL recorded negative control"
npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out"); nskip=$(grep -c '^SKIP' "$OUT/all.out")
echo "== done in $((SECONDS - T0))s: $npass PASS, $nskip SKIP, $nfail FAIL; logs in $OUT"
if [ "$nfail" = 0 ]; then [ "${FULL:-0}" = 1 ] && echo "PASS: all assertions hold (FULL)" || echo "PASS: all default assertions hold (fresh solves: FULL=1)"; exit 0; fi
echo "FAIL"; exit 1
