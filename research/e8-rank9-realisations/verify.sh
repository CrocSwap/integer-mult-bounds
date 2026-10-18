#!/usr/bin/env bash
# Verification of research/e8-rank9-realisations (no kappa claim).   usage: bash verify.sh [/fresh/output/dir]     PYTHON=  KISSAT=  DRAT_TRIM=  CC=
#   0  MANIFEST.sha256
#   1  exact finite facts: both families exist on E8 (a2e8.py); span facts S1/S2 (spans.py), S3' and W2 (spans3.py); P-compatible frames and orthogonal-pair coverage (pframes.py)
#   2  Theorem S finite step (56-line incidence problem): CNF regenerated (sha256 pinned for f1 = 0), kissat UNSAT, standard drat-trim VERIFIED, auxiliary rupc VERIFIED;  f1 = 0..15 (FULL=1: all 120 lines)
#   3  Theorem R finite step (pin.py ratio-equality model): CNF regenerated, sha256 equal to the pinned one (byte-identical to the working card's CNF); shipped DRAT (xz) decompresses to the pinned sha256.
#      FULL=1 additionally: standard drat-trim on the shipped proof (about 2-3 min), then a fresh kissat solve (flags as for the shipped proof; limit 1200 s) and drat-trim on the fresh proof.
#   4  soundness test of the pin.py rules on true data (A2 family: 5 parameter/triangle draws; B-form), and a mutation control (one flipped sign in the TRI row-column rule must be caught)
#   5  recorded logs (not re-run): the audit's drat-trim VERIFIED on pin3, the working card's rupc runs
# One heavy process at a time, run under nice 10.  Missing numpy/sympy/kissat/drat-trim/cc/xz => SKIP lines (never PASS) and exit 1.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/e8rank9.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; KISSAT="${KISSAT:-kissat}"; DT="${DRAT_TRIM:-drat-trim}"; CC="${CC:-cc}"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1
NICE="nice -n 10"; C="$HERE/checks"; EV="$HERE/evidence"; W="$OUT/work"; mkdir -p "$W" "$OUT/logs"; : > "$OUT/all.out"; T0=$SECONDS
note() { echo "$@" | tee -a "$OUT/all.out"; }
sha() { shasum -a 256 "$1" 2>/dev/null | cut -d' ' -f1 || sha256sum "$1" | cut -d' ' -f1; }
pin() { awk -F'\t' -v n="$1" '$2==n{print $1}' "$EV/pins.tsv"; }
echo "== 0. manifest"
if ! "$PY" -B "$C/manifest_check.py" | tee -a "$OUT/all.out" | sed 's/^/   /' || grep -q '^FAIL' "$OUT/all.out"; then echo "step 0 FAILED"; exit 1; fi
HAVE=1
"$PY" -c "import numpy, sympy" 2>/dev/null || { note "SKIP python needs numpy and sympy"; HAVE=0; }
for t in "$KISSAT" "$DT" "$CC" xz; do command -v "$t" >/dev/null 2>&1 || { note "SKIP tool missing: $t"; HAVE=0; }; done
[ "$HAVE" = 0 ] && { echo "INCOMPLETE: tools missing"; exit 1; }
runpy() { local n=$1; shift; ( cd "$W" && $NICE "$PY" -B "$C/$1" "${@:2}" > "$OUT/logs/$n.log" 2>&1 ); local rc=$?
  grep '^PASS' "$OUT/logs/$n.log" | sed 's/^/   /' | tee -a "$OUT/all.out" >/dev/null
  if [ $rc = 0 ] && grep -q '^PASS' "$OUT/logs/$n.log"; then note "PASS ran $n"; else note "FAIL ran $n (exit $rc)"; tail -3 "$OUT/logs/$n.log" | sed 's/^/      /'; fi; }
echo "== 1. exact finite facts"
runpy a2e8 a2e8.py; runpy spans spans.py; runpy spans3 spans3.py; runpy pframes pframes.py
echo "== 2. Theorem S finite step: 56-line incidence problem"
$CC -O2 -o "$W/rupc" "$C/rupc.c" 2>/dev/null || note "FAIL compile rupc.c"
if [ "${FULL:-0}" = 1 ]; then F1S=$(seq 0 119); else F1S=$(seq 0 15); fi
ok=0; n=0
for f in $F1S; do
  n=$((n+1)); ( cd "$W" && $NICE "$PY" -B "$C/s56.py" s56_$f.cnf $f > /dev/null )
  if [ $f = 0 ]; then [ "$(sha "$W/s56_0.cnf")" = "$(pin s56_0.cnf)" ] && note "PASS s56_0.cnf regenerated: sha256 equals the pinned value" || note "FAIL s56_0.cnf sha256"; fi
  r=$(cd "$W" && timeout 1200 $NICE "$KISSAT" -q --factor=false --preprocessfactor=false s56_$f.cnf s56_$f.drat --no-binary | head -1)
  d=$(cd "$W" && timeout 1200 $NICE "$DT" s56_$f.cnf s56_$f.drat 2>&1 | tr '\r' '\n' | grep -E '^s ')
  a=$("$W/rupc" "$W/s56_$f.cnf" "$W/s56_$f.drat" 2>&1 | grep -c '^VERIFIED')
  if [ "$r" = "s UNSATISFIABLE" ] && [ "$d" = "s VERIFIED" ] && [ "$a" = 1 ]; then ok=$((ok+1)); else note "FAIL s56 f1=$f: kissat '$r' drat-trim '$d' rupc $a"; fi
  rm -f "$W/s56_$f.cnf" "$W/s56_$f.drat"
done
[ $ok = $n ] && note "PASS Theorem S finite step: $n/$n choices of f1: kissat UNSAT, standard drat-trim VERIFIED, rupc VERIFIED" || note "FAIL Theorem S finite step: $ok/$n"
echo "== 3. Theorem R finite step: pinning model"
( cd "$W" && $NICE "$PY" -B "$C/pin.py" pin3.cnf > "$OUT/logs/pin_gen.log" 2>&1 )
[ "$(sha "$W/pin3.cnf")" = "$(pin pin3.cnf)" ] && note "PASS pin3.cnf regenerated: sha256 equals the pinned value ($(cat "$OUT/logs/pin_gen.log"))" || note "FAIL pin3.cnf sha256"
[ "$(xz -dc "$EV/proofs/pin3.drat.xz" | shasum -a 256 | cut -d' ' -f1)" = "$(pin pin3.drat)" ] && note "PASS shipped proof decompresses to the pinned sha256 (pin3.drat)" || note "FAIL shipped proof sha256"
if [ "${FULL:-0}" = 1 ]; then
  xz -dc "$EV/proofs/pin3.drat.xz" > "$W/pin3_shipped.drat"
  r=$(cd "$W" && timeout 1200 $NICE "$DT" pin3.cnf pin3_shipped.drat 2>&1 | tee "$OUT/logs/dt_shipped.log" | tr '\r' '\n' | grep -E '^s ')
  [ "$r" = "s VERIFIED" ] && note "PASS standard drat-trim: shipped pin3 proof VERIFIED" || note "FAIL drat-trim on shipped pin3 proof: '$r'"
  rm -f "$W/pin3_shipped.drat"
  s=$SECONDS; r=$(cd "$W" && timeout 1200 $NICE "$KISSAT" -q --factor=false --preprocessfactor=false pin3.cnf pin3_fresh.drat --no-binary | head -1)
  if [ "$r" = "s UNSATISFIABLE" ]; then
    note "PASS fresh kissat solve: UNSAT in $((SECONDS-s))s"
    r=$(cd "$W" && timeout 1200 $NICE "$DT" pin3.cnf pin3_fresh.drat 2>&1 | tee "$OUT/logs/dt_fresh.log" | tr '\r' '\n' | grep -E '^s ')
    [ "$r" = "s VERIFIED" ] && note "PASS standard drat-trim: fresh pin3 proof VERIFIED" || note "FAIL drat-trim on fresh pin3 proof: '$r'"
  else note "FAIL fresh kissat solve of pin3.cnf: '$r'"; fi
  rm -f "$W/pin3_fresh.drat"
else note "SKIP-FULL pin3 re-solve and drat-trim (set FULL=1; shipped proof, its sha256 and the recorded checker logs are checked in steps 3 and 5)"; fi
echo "== 4. soundness test of the pin.py rules"
mkdir -p "$W/mut"; cp "$C"/*.py "$W/mut/"
( cd "$W" && $NICE "$PY" -B "$C/soundtest.py" 0 3 > "$OUT/logs/soundtest.log" 2>&1 )
grep -q '^TOTAL violated 0$' "$OUT/logs/soundtest.log" && [ "$(grep -c '^A2 seed' "$OUT/logs/soundtest.log")" = 5 ] && note "PASS soundtest: 0 clause violations on true data (5 A2 draws on 5 triangles, 2 B-form instances, 3 random frames each)" || note "FAIL soundtest"
sed -i.bak 's/else: cl.append(\[-o\[0\],-o\[1\],-vs\[k\]\])/else: cl.append([-o[0],-o[1],vs[k]])/' "$W/mut/pin.py"
if cmp -s "$W/mut/pin.py" "$W/mut/pin.py.bak"; then note "FAIL mutation control: pattern not found"; else
  ( cd "$W/mut" && $NICE "$PY" -B soundtest.py 0 1 > "$OUT/logs/soundtest_mut.log" 2>&1 )
  v=$(grep '^TOTAL violated' "$OUT/logs/soundtest_mut.log" | awk '{print $3}')
  [ -n "$v" ] && [ "$v" -gt 0 ] && note "PASS mutation control: flipping the TRI row-column sign is caught ($v violated clauses)" || note "FAIL mutation control: not caught"; fi
echo "== 5. recorded logs (not re-run here)"
crlf() { tr '\r' '\n' < "$1"; }
crlf "$EV/logs/dratrim_shipped_pin3.log.txt" | grep -q '^s VERIFIED' && note "PASS recorded: drat-trim on the decompressed shipped proof: s VERIFIED" || note "FAIL recorded shipped-proof drat-trim log"
crlf "$EV/logs/audit_dratrim_pin3.log.txt" | grep -q '^s VERIFIED' && grep -q '56784 variables and 3513012 clauses' "$EV/logs/audit_dratrim_pin3.log.txt" && note "PASS recorded: independent audit's standard drat-trim run on pin3: s VERIFIED (3513012 clauses)"  || note "FAIL recorded audit drat-trim log"
grep -q 'VERIFIED: top-level conflict after 2382724 lemmas' "$EV/logs/kstar_cert2_E8_pin3_rupc.log.txt" && note "PASS recorded: working card's rupc run on pin3: VERIFIED after 2382724 lemmas" || note "FAIL recorded rupc log"
[ "$(grep -c 'VERIFIED: empty clause derived by RUP' "$EV/logs/kstar_s56_E8_f1_0-15.log.txt")" = 16 ] && note "PASS recorded: s56 for f1 = 0..15 all UNSAT + RUP-VERIFIED" || note "FAIL recorded s56 log"
npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out"); nskip=$(grep -c '^SKIP' "$OUT/all.out")
echo "== done in $((SECONDS - T0))s: $((npass + 2)) PASS (2 in step 0), $nskip SKIP, $nfail FAIL; logs in $OUT"
if [ "$nfail" = 0 ]; then [ "${FULL:-0}" = 1 ] && echo "PASS: all assertions hold (FULL)" || echo "PASS: all default assertions hold (pin3 re-solve / drat-trim: FULL=1)"; exit 0; fi
echo "FAIL"; exit 1
