#!/usr/bin/env bash
# One-command verification of research/helper-minimality (no kappa claim): minimality of the shipped helper layers of the #656 / #799
# words for their fixed op multiset.  Step 0 checks the package against MANIFEST.sha256 and every vendored input against its pin in
# SOURCES.json (git blob ids / sha256 / content sha256) and stops hard on any mismatch.  Then four check groups run at once and print
# one PASS/FAIL line per assertion.  Exit status 0 only if every assertion passes.
#   usage: bash verify.sh [/fresh/output/dir]     (inside a checkout or `git archive` of the repository; nothing outside the package is read)
#   needs python3 >= 3.11 with numpy and ortools (requirements.txt); set PYTHON to choose the interpreter.
#   HM_FULL=1 also regenerates the 36,501-pair pre-read table (about 5 min on 2 cores) and compares it with the stored one.
#   About 52 s wall on 12 cores (the S1 solver run takes about 50 s).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/helper-minimality.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1
T0=$SECONDS
echo "== 0. manifest and provenance"
if ! "$PY" -B "$HERE/scripts/provenance.py" | tee "$OUT/provenance.log" | sed 's/^/   /' || grep -q '^FAIL' "$OUT/provenance.log" \
   || [ "$(grep -c '^PASS' "$OUT/provenance.log")" != 2 ]; then
  echo "step 0 FAILED"; exit 1
fi
# work tree: scripts write their scratch files (iface.pkl, inst4567.json, ...) here, never into the package
export HM_ROOT="$OUT/tree"; mkdir -p "$HM_ROOT" "$OUT/logs"
cp -R "$HERE/cards" "$HERE/inputs" "$HERE/checks" "$HERE/evidence" "$HM_ROOT/"
E_="$PY -B $HM_ROOT/checks/expect.py"
# run NAME CARDDIR cmd...   (stdout+stderr -> logs/NAME.log, exit code -> logs/NAME.rc)
run() { local n=$1 d=$2; shift 2; ( cd "$HM_ROOT/cards/$d" && "$@" > "$OUT/logs/$n.log" 2>&1; echo $? > "$OUT/logs/$n.rc" ); }
chk() { local l=$1 n=$2; shift 2; $E_ "$l" "$OUT/logs/$n.log" "$@"; }
W656=$HM_ROOT/inputs/words/656-layers-FULL-WORD.json.gz
W799=$HM_ROOT/inputs/words/799-X4-FULL-WORD.json.gz
AL=$HM_ROOT/inputs/pr799/independent/audit_local.py

g1() {  # S1 Hall lemma and extensions (#656 canonical word)
  run iface B98b $PY -B iface.py
  run blockscan B167 $PY -B blockscan.py
  run scan01b B171 $PY -B scan01b.py
  run extract B167 $PY -B extract.py
  run level B167 $PY -B level.py --drop 433 --time 900
  run val B176 $PY -B val.py
  run gate B179 $PY -B gate.py
  run gate2 B179 $PY -B gate2.py
  chk S1.hall blockscan --count "'scratch', 16, 'wide', 8, 'plane-stoppers', 8, 'distinct', True, 'matching', 8" 11 --count "'cols', 56\)" 3 --count "'cand-eq-wide', True\)" 11
  chk S1.solver-drop433 level --has "^STATUS INFEASIBLE" --has "drop \(433,\)"
  chk S1.slack-01x scan01b --has "^matching 21$" --has "scratch-only partners matching 15 of 21" --has "col-only partners matching 21 of 21" --count "stoppers 7 scratch-only matching 5" 3
  chk S1.twins val --has "value-exact twins 0 of 38"
  chk S1.replayA gate --has "end rows mismatch vs rows0: 0 \[\]"
  chk S1.stoppers88 gate2 --has "stoppers 88 with jump found 88" --has "count ok>0: 0 holders>0: 0 low>0: 0 of 88" --has "all columns have a pure point holder: 0 inside plane: 0 no-climb \(frame>=z frame\): 0 of 88"
}
g2() {  # Lawler S3/S4, bridges and holders
  run law656 B171 $PY -B lawler799.py $HM_ROOT/inputs/words/656-CANONICAL-WORD.json.gz
  run law799 B171 $PY -B lawler799.py
  run pair656 B171 $PY -B pair799.py $HM_ROOT/inputs/words/656-CANONICAL-WORD.json.gz
  run pair799 B171 $PY -B pair799.py
  run lawcheck B171 $PY -B $HM_ROOT/checks/lawler_check.py
  run b182 B182 $PY -B b182.py
  chk S2.lawler-656 law656 --has "^ops 5287 copies Counter\(\{'S3': 156, 'S4': 112\}\)" --has "\('S3', 'FAIL', 'chains-alone-ok'\) 156" --has "\('S4', 'FAIL', 'chains-alone-ok'\) 112" --has "^passing copies 0$"
  chk S2.lawler-799 law799 --has "^ops 5687 copies Counter\(\{'S3': 156, 'S4': 112\}\)" --has "\('S3', 'FAIL', 'chains-alone-ok'\) 156" --has "\('S4', 'FAIL', 'chains-alone-ok'\) 112" --has "^passing copies 0$"
  chk S2.skipzero-656 law656 --has "^value-zero adds skipped 1921$" --has "^skip-zero \{\('S3', 'FAIL', 'chains-alone-ok'\): 156, \('S4', 'FAIL', 'chains-alone-ok'\): 112\}$" --has "^skip-zero passing copies 0$"
  chk S2.skipzero-799 law799 --has "^value-zero adds skipped 2317$" --has "^skip-zero \{\('S3', 'FAIL', 'chains-alone-ok'\): 156, \('S4', 'FAIL', 'chains-alone-ok'\): 112\}$" --has "^skip-zero passing copies 0$"
  chk S2.pair-656 pair656 --has "Counter\(\{\('S3', 'pair-conflict'\): 156, \('S4', 'pair-conflict'\): 112\}\)"
  chk S2.pair-799 pair799 --has "Counter\(\{\('S3', 'pair-conflict'\): 156, \('S4', 'pair-conflict'\): 112\}\)"
  sed 's/^\(PASS\|FAIL\) /\1 S2.oracle-/' "$OUT/logs/lawcheck.log"
  [ "$(cat "$OUT/logs/lawcheck.rc")" = 0 ] || echo "FAIL S2.oracle run exited nonzero"
  chk S3.bridges-holders b182 --has "\('BR', 'FAIL', 'chains-alone-ok'\) 12" --has "\('S3', 'FAIL', 'chains-alone-ok'\) 94" --has "^passing \[\]" --has "distinct 12 of 12 \[8(, 8){11}\]"
}
g3() {  # cut >= 8 centres, verifier model
  run cut656 B174 $PY -B check.py $W656
  run cut799 B174 $PY -B check.py $W799
  run clique B174 $PY -B clique.py $W656 $W799
  run al656 B174 $PY -B $AL --word $W656 --output $OUT/logs/al656.json
  run al799 B174 $PY -B $AL --word $W799 --output $OUT/logs/al799.json
  run toymake B174 $PY -B $HM_ROOT/checks/make_toy.py $W799 $OUT/logs/toy-FULL-WORD.json.gz
  run altoy B174 $PY -B $AL --word $OUT/logs/toy-FULL-WORD.json.gz --output $OUT/logs/altoy.json
  run cuttoy B174 $PY -B check.py $OUT/logs/toy-FULL-WORD.json.gz
  run anchors B174 $PY -B $HM_ROOT/checks/anchors.py
  for w in 656 799; do
    chk C.cut-$w cut$w --has "H-CUT: all cut ops add target<-centre: True \| centres disjoint from targets: True \| #centres 8 distinct 8 \| \|K\| read 8" \
      --has "^F == I: True" --has "odd nnz in F0 0" --has "rank\(F-F0\) = 8 <= \|K\| = 8" --has "omega\(odd graph\) = 8" --has "principal submatrix of F-F0 on clique is I: True" \
      --has "centre-frame lemma .*: True" --absent ": False"
    chk C.audit-$w al$w --has '"status": "PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES"' --has '"R": '$([ $w = 656 ] && echo 492 || echo 504)
  done
  chk C.clique clique --count "omega 8 \[0, 3, 45, 46, 69, 70, 104, 107\]" 2 --count "distinct 112" 2
  chk C.gap-AL-accepts-toy altoy --has '"status": "PASS_INDEPENDENT_EXACT_FORWARD'
  chk C.gap-H-CUT-detected cuttoy --has "H-CUT: all cut ops add target<-centre: False"
  cat "$OUT/logs/anchors.log"; [ "$(cat "$OUT/logs/anchors.rc")" = 0 ] || echo "FAIL C.anchors run exited nonzero"
}
g4() {  # pre-read layer, model fidelity
  run ilp B159 $PY -B ilp.py
  run pairs B159 $PY -B $HM_ROOT/checks/pairs_sample.py
  run b128 B128 $PY -B retest.py base
  run b128tab B128 $PY -B $HM_ROOT/checks/b128_table.py
  chk P.min66 ilp --has "^bundles 46 legal 38" --has "^touched targets 66 preads 118" --absent "Traceback"
  ( cd "$HM_ROOT/cards/B159" && $PY -B -c "
import ilp
r=ilp.solve('full'); print('RESULT',r[0],r[1],r[2])" > "$OUT/logs/ilp2.log" 2>&1; echo $? > "$OUT/logs/ilp2.rc" )
  chk P.cpsat-optimal ilp2 --has "RESULT OPTIMAL 66 66.0"
  sed 's/^\(PASS\|FAIL\) /\1 /' "$OUT/logs/pairs.log" | grep -E '^(PASS|FAIL)'
  [ "$(cat "$OUT/logs/pairs.rc")" = 0 ] || echo "FAIL P.pairs run exited nonzero"
  chk M.fidelity b128 --has "^frame map bad 0 5726$" --has "^endpoint forward PASS" --has "^endpoint dual PASS" --has '"status": "PASS_INDEPENDENT_EXACT_FORWARD' --has "REAL VERIFIER: ACCEPT"
  cat "$OUT/logs/b128tab.log"; [ "$(cat "$OUT/logs/b128tab.rc")" = 0 ] || echo "FAIL M.table run exited nonzero"
  if [ "${HM_FULL:-0}" = 1 ]; then
    run regen B159 env PAIRS_OUT=$OUT/logs/pairs-regen.json.gz $PY -B mdl.py
    ( cd "$HM_ROOT/cards/B159" && $PY -B -c "
import os
from pairsio import load_pairs
a=load_pairs(os.environ['HM_ROOT']+'/inputs/derived/pairs.json.gz'); b=load_pairs('$OUT/logs/pairs-regen.json.gz')
print('REGEN-EQUAL', a==b)" > "$OUT/logs/regen2.log" 2>&1; echo $? > "$OUT/logs/regen2.rc" )
    chk P.table-regenerated regen2 --has "REGEN-EQUAL True"
  fi
}
for g in g1 g2 g3 g4; do ( $g > "$OUT/$g.out" 2>&1; echo $? > "$OUT/$g.rc" ) & done
wait
status=0; npass=0; nfail=0
for g in g1 g2 g3 g4; do
  echo "== $g"; sed 's/^/   /' "$OUT/$g.out"
  p=$(grep -c '^PASS' "$OUT/$g.out"); f=$(grep -c '^FAIL' "$OUT/$g.out")
  npass=$((npass + p)); nfail=$((nfail + f))
  if [ "$(cat "$OUT/$g.rc")" != 0 ] || [ "$f" != 0 ] || [ "$p" = 0 ]; then echo "   FAILED: $g (exit $(cat "$OUT/$g.rc"), $f FAIL lines)"; status=1; fi
done
echo "== done in $((SECONDS - T0))s: $((npass + 2)) PASS (2 in step 0), $nfail FAIL; logs in $OUT"
exit $status
