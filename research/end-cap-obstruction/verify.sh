#!/usr/bin/env bash
# One-command verification of research/end-cap-obstruction (no kappa claim): the end-cap wall of the E8 skeleton (k8 / #1018-type local word).
# Step 0 checks the package against MANIFEST.sha256 and every vendored input against its pin in SOURCES.json (git blob ids / sha256 / content
# sha256, plus the word hash published by #1018) and stops hard on any mismatch.  Then the gauge-forward words used below are REGENERATED from the
# vendored inputs, and seven check groups run at once and print one PASS/FAIL line per assertion.  Exit status 0 only if every assertion passes.
#   usage: bash verify.sh [/fresh/output/dir]      (inside a checkout or `git archive` of the repository; nothing outside the package is read)
#   needs python3 >= 3.11 with ortools (requirements.txt; the B251 solver step) and numpy (port geometry); set PYTHON to choose the interpreter.
#   About 8 minutes wall on 12 cores: the four exhaustive orderings searches of group G5 take 1 to 5 minutes each and run at once.
#   Author switch: EO_GROUPS="G1 G2" runs only the named groups (a partial run is never a verification).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/end-cap-obstruction.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1 PYTHONINTMAXSTRDIGITS=0
T0=$SECONDS
echo "== 0. manifest and provenance"
if ! "$PY" -B "$HERE/scripts/provenance.py" | tee "$OUT/provenance.log" | sed 's/^/   /' || grep -q '^FAIL' "$OUT/provenance.log" \
   || [ "$(grep -c '^PASS' "$OUT/provenance.log")" != 2 ]; then
  echo "step 0 FAILED"; exit 1
fi
# work tree: scripts write scratch files here, never into the package
export EO_ROOT="$OUT/tree"; mkdir -p "$EO_ROOT" "$OUT/logs"
cp -R "$HERE/cards" "$HERE/inputs" "$HERE/checks" "$HERE/evidence" "$EO_ROOT/"
export TMPDIR="$OUT/tmp"; mkdir -p "$TMPDIR"
WK="$EO_ROOT/work"; mkdir -p "$WK/ham" "$WK/in"
RP="$EO_ROOT/inputs/repo/research"
cp "$RP/static44-selective/vendor/pr531/inputs/hamming/PACKET-PROGRAMS.json.gz" "$RP/static44-selective/vendor/pr531/inputs/hamming/PROTOTYPE.json" \
   "$RP/gauge44-slots/construction/COMPLETION-PRIORITY.json" "$WK/ham/"
cp "$RP/gauge44-slots/construction/leaver/TRI-LEAVER-k8.json" "$WK/in/TRI.json"
cp "$RP/gauge44-slots/construction/leaver/CODED-CELLS-k8.json" "$WK/in/CODED-CELLS.json"
export XPARAM="$RP/gauge44-slots/construction/notri/PRIO6.json"
E_="$PY -B $EO_ROOT/checks/expect.py"
# run NAME DIR cmd...   (stdout+stderr -> logs/NAME.log, exit code -> logs/NAME.rc; DIR is a card directory under cards/, or a path under the work tree)
run() { local n=$1 d=$2; shift 2; case "$d" in /*) ;; *) d="$EO_ROOT/cards/$d";; esac; ( cd "$d" && "$@" > "$OUT/logs/$n.log" 2>&1; echo $? > "$OUT/logs/$n.rc" ); }
chk() { local l=$1 n=$2; shift 2; $E_ "$l" "$OUT/logs/$n.log" "$@"; }
# overlay DIR card...   (a scratch directory holding the scripts of several cards that import one another)
overlay() { local d="$WK/$1"; shift; rm -rf "$d"; mkdir -p "$d"; local c; for c in "$@"; do cp "$EO_ROOT/cards/$c"/*.py "$d/"; done; echo "$d"; }
DFS_TL=${EO_DFS_TL:-3000}   # author switch: time limit (s) of the exhaustive orderings search; a run that hits it fails
want() { case " ${EO_GROUPS:-G0 G1 G2 G3 G4 G5 G6} " in *" $1 "*) return 0;; *) return 1;; esac; }

# --- generator: the gauge-forward word of the k8 skeleton (card B252 cgx_y.py = the #1005 generator plus the deletion switches), 1 s per word
gen() {  # NAME ENV=VALUE...   -> $WK/o_NAME/FULL-WORD.json.gz, logs/gen-NAME.{log,rc}
  local n=$1; shift; rm -rf "$WK/o_$n"
  ( env "$@" "$PY" -B "$EO_ROOT/cards/B252/cgx_y.py" "$WK/ham" "$WK/o_$n" "$WK/in/TRI.json" > "$OUT/logs/gen-$n.log" 2>&1; echo $? > "$OUT/logs/gen-$n.rc" )
}
CF16=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
RR=10,11,12,13,16,17,18,19,26,27,28,29,34,35,36,37,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55
echo "== generating the gauge-forward words from the vendored inputs"
gen base  STAG=0 GLAZY=0
gen cf0   STAG=0 GLAZY=1 CF=0
gen all16 STAG=1 GLAZY=1 CF=$CF16
gen rr    STAG=0 GLAZY=1 RO=$RR
gen wr    STAG=0 GLAZY=1 WRC=Wr WR=all
gen rrss  STAG=1 GLAZY=1 CF=$CF16 RO=$RR
gen rrwr  STAG=0 GLAZY=1 RO=$RR WRC=Wr WR=all
gen all80 STAG=1 GLAZY=1 CF=$CF16 RO=$RR WRC=Wr WR=all
gen nogl  STAG=0 GLAZY=0 CF=0
for n in base cf0 all16 rr wr rrss rrwr all80; do [ "$(cat "$OUT/logs/gen-$n.rc")" = 0 ] || { echo "generator failed for $n"; tail -3 "$OUT/logs/gen-$n.log"; exit 1; }; done
W_() { echo "$WK/o_$1/FULL-WORD.json.gz"; }
B253="$EO_ROOT/cards/B253"; B258="$EO_ROOT/cards/B258"

g0() {  # G0 model, generator, word pins
  "$PY" -B "$EO_ROOT/checks/anchors.py"
  "$PY" -B "$EO_ROOT/checks/wordpins.py" "$EO_ROOT" "$WK"
}
g1() {  # G1 the obstruction in the deletion experiments: caps, profile, mechanism
  for n in base cf0 all16; do
    run caps-$n B253 "$PY" -B caps.py "$(W_ $n)"
    run prof-$n B253 "$PY" -B prof.py "$(W_ $n)"
  done
  run endcap B258 "$PY" -B endcap.py "$(W_ base)" "$(W_ cf0)" "$(W_ all16)" "$(W_ rr)" "$(W_ wr)" "$(W_ rrss)" "$(W_ rrwr)" "$(W_ all80)"
  run trace283 B253 "$PY" -B trace.py "$(W_ cf0)" 283
  run trace170 B253 "$PY" -B trace.py "$(W_ cf0)" 170
  chk G1.base-clean caps-base --has "^final cap violators \[\]$"
  chk G1.base-profile prof-base --has "^\{1: 1928, 2: 736, 3: 336, 4: 168, 5: 168, 6: 32, 8: 8\}$"
  chk G1.gen-base gen-base --has "CF 8 \[\] WIDEN \[\] NH 480 NVIOL 0 \[\] MASS \(6312, 6312\)"
  chk G1.cf0-deletion gen-cf0 --has "NH 479 NVIOL 0 \[\] MASS \(6307, 6303\)"
  chk G1.cf0-violators caps-cf0 --has "^final cap violators \[170, 171, 174, 175\]$" --has "^170 \('B', 945, \['add', 170, 591\]\)" --has "^171 \('B', 929, \['add', 171, 283\]\)" \
      --has "^174 \('B', 930, \['add', 174, 379\]\)" --has "^175 \('B', 946, \['add', 175, 598\]\)"
  chk G1.cf0-profile-fails prof-cf0 --has "^FAIL \('frame violation', 170, \(256, 128, 64, 32, 16, 8, 4, 2, 1\), \(258, 130, 66, 32, 16, 8, 6, 1\)\)"
  chk G1.all16-deletion gen-all16 --has "NH 464 NVIOL 0 \[\]"
  chk G1.all16-violators caps-all16 --has "^final cap violators \[160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175\]$"
  chk G1.all16-profile-fails prof-all16 --has "^FAIL \('frame violation', 160, "
  chk G1.drag-283 trace283 --has "^B 585 \['add', 591, 283, 1, 1\] dim 7 cur \[0, 7\]" --has "^B 929 \['add', 171, 283, -1, 2\] dim 9 cur \[7, 8\]"
  chk G1.cap-hit-170 trace170 --has "^B 945 \['add', 170, 591, -1, 2\] dim 9 cur \[7, 8\] inperp \[False\]"
  chk G1.violators-end-FULL endcap --has "^o_base R 480 viol 0 " --has "^o_cf0 R 479 viol 4 dim9 4 complement-hyperplane-possible\(u not in frame\) 0 sum\(dim-dim∩perp\) 4 " \
      --has "^o_all16 R 464 viol 16 dim9 16 complement-hyperplane-possible\(u not in frame\) 0 sum\(dim-dim∩perp\) 16 " \
      --has "^o_rr R 448 viol 48 dim9 48 complement-hyperplane-possible\(u not in frame\) 0 sum\(dim-dim∩perp\) 48 " \
      --has "^o_wr R 448 viol 48 dim9 48 complement-hyperplane-possible\(u not in frame\) 0 sum\(dim-dim∩perp\) 48 " \
      --has "^o_rrss R 432 viol 64 dim9 64 complement-hyperplane-possible\(u not in frame\) 0 sum\(dim-dim∩perp\) 64 " \
      --has "^o_rrwr R 416 viol 48 dim9 48 complement-hyperplane-possible\(u not in frame\) 0 sum\(dim-dim∩perp\) 48 " \
      --has "^o_all80 R 400 viol 64 dim9 64 complement-hyperplane-possible\(u not in frame\) 0 sum\(dim-dim∩perp\) 64 "
  for n in rr wr rrss rrwr all80; do chk G1.gen-$n gen-$n --has "NVIOL 0 \[\]"; done
  if [ "$(cat "$OUT/logs/gen-nogl.rc")" != 0 ] && grep -q "AssertionError: ('frame violation', 299, " "$OUT/logs/gen-nogl.log"; then
    echo "PASS G1.no-glazy-refused  without the lazy widening the deletion is refused by the generator: frame violation at register 299"
  else echo "FAIL G1.no-glazy-refused"; fi
  # the 32 single-copy deletions (16 copies, STAG = 0 and 1): every legal one violates exactly 4 caps, all four ending FULL
  local st cf ok=0 bad=0 four=0 refused=0
  for st in 0 1; do for cf in $(seq 0 15); do
    gen sw_${st}_$cf STAG=$st GLAZY=1 CF=$cf
    if [ "$(cat "$OUT/logs/gen-sw_${st}_$cf.rc")" = 0 ]; then
      ok=$((ok + 1)); "$PY" -B "$B258/endcap.py" "$(W_ sw_${st}_$cf)" > "$OUT/logs/sw-$st-$cf.log" 2>&1
      grep -q "R 479 viol 4 dim9 4 complement-hyperplane-possible(u not in frame) 0 " "$OUT/logs/sw-$st-$cf.log" && four=$((four + 1))
      grep -q "NVIOL 0" "$OUT/logs/gen-sw_${st}_$cf.log" || bad=$((bad + 1))
    else refused=$((refused + 1)); fi
  done; done
  [ "$ok $four $bad $refused" = "24 24 0 8" ] && echo "PASS G1.single-copies  24 legal single deletions, each: R 479, 4 violators, all dim 9 = FULL, NVIOL 0; 8 refused by the generator (STAG=0, CF>=8)" \
    || echo "FAIL G1.single-copies  ok=$ok four=$four nviol-bad=$bad refused=$refused"
}

g2() {  # G2 prices
  run units "$EO_ROOT/checks" "$PY" -B "$EO_ROOT/checks/units.py"
  run ceil B248 "$PY" -B ceil.py
  run step0 B248 "$PY" -B step0.py
  chk G2.base-kappa units --has "^base kappa 1\.671665283218770e-03$"
  chk G2.unit-price units --has "^\+1 rank-1 local units: kappa 1\.624537144e-03  -2\.819%  per unit -2\.8192%$" --has "^\+4 rank-1 local units: kappa 1\.483191993e-03  -11\.275%" \
      --has "^\+16 rank-1 local units: kappa 9\.183989999e-04  -45\.061%" --has "^\+32 rank-1 local units: kappa 1\.667976019e-04  -90\.022%" --has "^first k with no certificate: 35 "
  chk G2.break-even units --has "one unit costs 2\.819% per violating y -> a deletion pays only if it breaks <= 0\.0156 caps per copy"
  chk G2.ceiling ceil --has "^mass->H48 \{48: 1056\} \(0\.001730427469823602, 3\.5151885484925662\)$" --has "^S4 paid profile \{1: 384, 2: 64, 3: 32, 4: 24\} mass 704$"
  chk G2.helper-value step0 --has "^base 0\.00167166528321877$" --has "2 helpers gone, mass->idle rank48 \(27 H48\) +1\.676641807e-03 \+0\.298%"
}

g3() {  # G3 geometry of the ports and the copy census
  run portdims "$EO_ROOT/checks" "$PY" -B "$EO_ROOT/checks/portdims.py"
  for f in geo groups rd val cp anc merge pure; do run b260-$f B260 "$PY" -B $f.py; done
  run an1 B259 "$PY" -B an1.py "$(W_ cf0)"
  for f in an2 an3 an4 an6; do run $f B259 "$PY" -B $f.py; done
  run an5 B259 "$PY" -B an5.py "$(W_ cf0)" "$(W_ all16)"
  chk G3.port-dims portdims --has "^ports 112 distinct odd-weight, 14 blocks of 8, block ranks \[4\]$" --has "^cross-block pairs 5824 dim of common perp \[7\]$" \
      --has "^cross-block triples 186368 dim of common perp \[6\]$" --has "^cross-block quads 4100096 dim 5: 4080384 dim 6 \(zero-sum, rank 3\): 19712$"
  chk G3.geometry b260-geo --has "^self-dot all 1: True$" --has "^cap \(no 3 xor 0\): True$" --has "^zero-sum 4-sets \(span dim3 with 4 ports\): 24276$" \
      --has "^quad block patterns: Counter\(\{\(1, 1, 1\): 19712, \(1, 2\): 4368, \(3,\): 196\}\)$" --has "^orth degree \(excluding self\): Counter\(\{52: 112\}\)$" \
      --has "^pairs: #ports in perp\(u_a\)∩perp\(u_b\): \[\(20, 168\), \(22, 2688\), \(24, 672\), \(26, 2688\)\]$" \
      --has "\(0, 896\), \(4, 112\), \(6, 2688\), \(7, 14336\), \(8, 14560\), \(10, 40320\), \(11, 86016\), \(12, 44800\), \(14, 8960\), \(15, 14336\), \(16, 896\)\]$"
  chk G3.delivery-groups b260-groups --has "^pairs dot0 cross 2688 .*\[\(\(26, 25, 2\), 2688\)\]$" --has "^quads blocks\(1, 1, 2\) 0 " --has "^quads blocks\(1, 1, 1, 1\) 19712 " --has "^quads blocks\(4,\) 196 "
  chk G3.sharing-is-minimal-span b260-rd --has "^\('h', 2, 2, 1\) 13$" --has "^\('h', 2, 2, 2\) 41$" --has "^\('x', 2, 2, 2\) 25$" --has "^\('y', 2, 2, 1\) 8$" --has "^\('y', 2, 2, 2\) 16$" \
      --has "^\('h', 3, 3, 3\) 16$" --has "^\('x', 3, 3, 3\) 16$" --has "^\('h', 4, 3, 1\) 56$"
  chk G3.copy-census b260-anc --has "^copies 480 merge-union reader groups \(\|T\|,span dim\): \[\('one side unread', 232\), \(\(2, 2\), 200\), \(\(3, 3\), 33\), \(\(4, 4\), 15\)\]"
  chk G3.copy-at-instant-in-cap b260-merge --has "\(\(2, True, False, True\), 171\)" --has "\(\(2, True, True, True\), 29\)" --has "\(\(3, True, False, True\), 30\)" --has "\(\(3, True, True, True\), 3\)" \
      --has "\(\(4, True, False, True\), 12\)" --has "\(\(4, True, True, True\), 3\)" --absent "^  \(\([0-9], False,"
  chk G3.versions-and-drag b260-pure --has "\(\(False, False, False, True\), 3\)" --has "\(\(False, False, True, True\), 8\)" --has "\(\(False, True, False, False\), 5\)" --has "\(\(False, True, True, False\), 208\)" \
      --has "\(\(True, False, False, True\), 6\)" --has "\(\(True, False, True, True\), 13\)" --has "\(\(True, True, False, True\), 5\)"
  chk G3.copies-by-event b260-cp --has "^copy events \(helper written from zero\): 480 Counter\(\{\('A', 'x'\): 212, \('B', 'h'\): 212, \('B', 'x'\): 44, \('A', 'h'\): 12\}\)$"
  chk G3.violating-groups an1 --has "^violator targets \[58, 59, 62, 63\] blocks \[7\]$" --has "^dim ∩ over all violators 6$"
  chk G3.final-frames-exceed-cap an3 --has "^regs read directly by y of >=2 blocks: 136$" --has "\[\(\(2, 1\), 80\), \(\(2, 2\), 24\), \(\(3, 2\), 32\)\]$" --has "^dim ∩ distribution Counter\(\{7: 104, 6: 32\}\)$"
  chk G3.second-encoding-excess an4 --has "^n 136 sum excess per reg: min/median/max 1 3\.0 13$" --has "^regs with 0 excess 0$"
  chk G3.deleted-copy-excess an6 --has "^283 T \[12, 37, 59\] blocks \[1, 4, 7\] dimI 6 final 9 op-excess 22$" --has "^315 T \[59, 68, 109\] blocks \[7, 8, 13\] dimI 6 final 9 op-excess 14$" \
      --has "^379 T \[62, 76, 101\] blocks \[7, 9, 12\] dimI 6 final 9 op-excess 16$" --has "^591 T \[58\] blocks \[7\] dimI 8 final 9 op-excess 4$"
  if [ "$(grep -o 'op-excess [0-9]*' "$OUT/logs/an6.log" | awk '{s += $2} END {print s}')" = 103 ]; then echo "PASS G3.deleted-copy-total-excess  sum of op-excess over the registers whose frame changes: 103 mass"; else echo "FAIL G3.deleted-copy-total-excess"; fi
  chk G3.violator-sources an2 --has "^\|I\| 64 dim 6$" --has "^y 170 final dim 9 readers \[169, 197, 237, 427, 591, 594\]$"
  chk G3.violators-of-16 an5 --has "^work \[\(\[58, 59, 62, 63\], 24, 328, 207\)\]$" --has "^work \[\(\[48, 49, 50, 51\], 20, 243, 130\), \(\[52, 53, 54, 55\], 20, 231, 118\), \(\[56, 57, 58, 59\], 20, 284, 154\), \(\[60, 61, 62, 63\], 20, 287, 157\)\]$"
}

g4() {  # G4 frame conflicts, rematerialisation and the hoist/slide windows (cards B251, B254, B257 on the #1018 word, cards B249 sim)
  local D; D=$(overlay b251 B249 B251)
  run b251-chain "$D" bash -c "for s in graph vals proj inc; do $PY -B \$s.py || exit 1; done; $PY -B mis.py h 1 200 && $PY -B mis.py all 1 200 && $PY -B cls2.py && $PY -B fin.py"
  chk G4.decoupler-bound b251-chain --has "^Y events 926 Counter\(\{'B': 926\}\)$" --has "^592 incarnations; L not inside own cap: 54$" \
      --has "^status OPTIMAL MIS\(max pairwise-conflicting incarnations\) = 111\.0 bound 111\.0$" --has "^status OPTIMAL MIS\(max pairwise-conflicting incarnations\) = 124\.0 bound 124\.0$" \
      --has "^greedy chain cover \(UB on registers for this set under model\) 113$" --has "^chi hist Counter\(\{1: 548, 2: 22\}\)$" \
      --has "^cold0/endFULL 237 164 0 73 0$" --has "^cold0/endU 48 0 0 48 0$" --has "^enter1/endFULL 106 66 0 40 0$" --has "^enter1/endU 30 30 0 0 0$" --has "^enter4/endFULL 32 32 0 0 0$" --has "^enter5/endFULL 24 24 0 0 0$"
  D=$(overlay b254 B249 B251 B254)
  run b254-chain "$D" bash -c "for s in graph vals proj inc; do $PY -B \$s.py >/dev/null || exit 1; done; $PY -B mis.py h 1 200 >/dev/null; $PY -B set161.py && $PY -B rm161.py && $PY -B roles2.py && $PY -B sim161.py && $PY -B joint.py"
  chk G4.161-helpers b254-chain --has "^161$" --has "^algebra-ok 65 " --has "^49 \('cold0/endFULL', 'Cglue\+Arot\+Awr', 'rotlock'\) ex 225$" --has "^12 \('cold0/endFULL', 'Cglue\+Awr', 'algOK'\) ex 408$" \
      --has "^12 \('cold0/endFULL', 'Cglue\+Awr', 'rotlock'\) ex 402$" --has "^13 \('cold0/endU', 'Brelay', 'algOK'\) ex 500$" --has "^1 \('cold0/endU', 'Brelay\+Awr', 'rotlock'\) ex 498$" \
      --has "^34 \('cold0/endU', 'other\+Arot\+Awr', 'rotlock'\) ex 273$" --has "^40 \('enter1/endFULL', 'Brelay', 'algOK'\) ex 474$" --has "^baseline True 5586$" \
      --has "^Counter\(\{\('enter1/endFULL', False\): 40, \('cold0/endU', False\): 13, \('cold0/endFULL', False\): 12\}\)$" --has "^feasible single \[\]$" --has "^Counter\(\{'bail': 158, 'infeas': 3\}\)$" \
      --has "^all65 65 \(False, \"op \('B', 574\) reg 160 F dim 3 end dim 8 cur 0\"\)$" --has "^Brelay53 53 \(False, \"op \('B', 1432\) reg 139 F dim 9 end dim 8 cur 7\"\)$"
  D=$(overlay b257 B249 B257)
  run b257-hoist "$D" "$PY" -B hoist.py
  run b257-slide "$D" "$PY" -B slide.py
  run b257-cls "$D" "$PY" -B cls.py
  run b257-det "$D" "$PY" -B det.py
  chk G4.hoist b257-hoist --has "^W alg-ok 172; window-ok 64 frame-ok 0$" --has "^Counter\(\{'read-x': 108, \"frame:op \('B',\": 62, 'frame:target level': 2\}\)$"
  chk G4.slide b257-slide --has "^Counter\(\{'no-position': 86, 'window-ok': 86\}\) frame-ok 0 \[\]$"
  chk G4.slide-placements b257-cls --has "^not-placeable \(first blocking class\): \{'both': 86\}$" --has "169, \('target level y#', 'S'\): 3\}$"
  chk G4.hoist-first-violation b257-det --has "^Z Counter\(\{\"op \('B', #\) reg # F dim #\": 62, 'target level y2': 1, 'target level y42': 1\}\)$"
}

g5() {  # G5 version reconstruction and reordering of the CF=0 cluster (card B256), four absorption variants, exhaustive
  local D="$EO_ROOT/cards/B256" v
  run b256-plan B256 "$PY" -B plan.py
  run b256-pair B256 "$PY" -B pair.py
  run b256-cluster B256 "$PY" -B cluster.py
  run b256-cluster2 B256 "$PY" -B cluster2.py
  run b256-e1 B256 "$PY" -B e1.py
  run b256-e2 B256 "$PY" -B e2.py
  run b256-e6 B256 "$PY" -B e6.py
  run b256-leaves B256 "$PY" -B leaves.py
  for v in "pre pre" "post pre" "pre post" "post post"; do
    set -- $v
    ( cd "$D" && VA=$1 VB=$2 TL=$DFS_TL "$PY" -B dfs.py > "$OUT/logs/dfs-$1$2.log" 2>&1; echo $? > "$OUT/logs/dfs-$1$2.rc" ) &
  done
  wait
  run b256-e7 B256 "$PY" -B e7.py 20
  chk G5.expansion-no-floor b256-plan --has "^\[58\] 4 \[\]$" --has "^\[58, 63\] 4 \[\]$" --has "^\[\(283, 517, 2449, Fraction\(1, 1\)\), \(281, 515, 2450, Fraction\(1, 1\)\), \(299, 671, 2475, Fraction\(1, 1\)\), \(297, 669, 2476, Fraction\(1, 1\)\)\]$"
  chk G5.pair-alone b256-pair --has "^Counter\(\{.*\(True, True, True, True\): 128\b"
  chk G5.relaxation-has-orders b256-cluster --has "^340$" --has "^also perp63 340$"
  chk G5.precedence-kills b256-cluster2 --has "^solutions 0$"
  chk G5.absorb-at-once-fails b256-e2 --has "^ widened 33 caps \[124, 125, 126, 127, 149, 150, 170, 171, 174, 175\] FAIL \('frame violation', 124, " --count "valsame True" 4
  chk G5.hoist-readers-fails b256-e6 --has "^239 value True changed 46 caps \[124, 125, 126, 127, 148, 151, 171, 174\] FAIL " --count "value True" 4
  chk G5.leaves-all-written b256-leaves --has "^y 170 src 591 support 18 leaves: \[\]$" --has "^y 175 src 598 support 18 leaves: \[\]$"
  chk G5.relaxation-orders-in-word b256-e7 --count "caps \[(12[4-7]|14[89]|15[01])" 20 --absent "caps \[\]"
  for v in prepre postpre prepost postpost; do
    "$PY" -B "$EO_ROOT/checks/dfs_exhaustive.py" "G5.dfs-$v" "$OUT/logs/dfs-$v.log" "$DFS_TL"
  done
}

g6() {  # G6 cold-slot capacity, coded pairs and partner end caps (cards B244, B247, B248)
  local D; D=$(overlay b244 B240 B244)
  run b244-ev "$D" "$PY" -B ev.py
  run b244-classify "$D" "$PY" -B classify.py
  run b244-lift "$D" "$PY" -B lift.py
  chk G6.tail-reproduces b244-ev --has "^\{'1': 2412, '2': 418, '3': 432, '4': 142, '5': 82, '8': 8\} \{'1': 2412, '2': 418, '3': 432, '4': 142, '5': 82, '8': 8\}$" --has "^0\.00167166528321877$" --has "^0 non-lazy gates$"
  chk G6.splits-partner-end-cap b244-classify --has "^32 \('T->E', 'partner_end_cap', 1, 5\)$" --has "^22 \('T->E', 'partner_end_cap', 1, 1\)$" --has "^16 \('T->E', 'partner_end_cap', 2, 1\)$" --has "^8 \('T->E', 'partner_end_cap', 3, 1\)$" --has "^78$" --absent "partner_uncapped"
  chk G6.lift-gates b244-lift --has "^2 \[\(0\.0, 83, 8, " --has "\(0\.0, 104, 8, "
  chk G6.coded-pair-capacity gen-base --has "PROBE \{'pairs': 112, 'own_cold_T': 112, .*'warm_T': 0, .*'second_pair_prev_half_in_partner_hyper': 0, 'second_pair_cases': 224, 'second_pair_prev_bothkeys_in_partner': 0, 'second_pair_prev_selloads_in_partner': 0, 'raw_half_cases': 448, 'raw_half_in_partner': 0"
  mkdir -p "$WK/b248"; cp "$EO_ROOT/cards/B248/gen/ana1.py" "$WK/b248/"
  run b248-gen "$WK/b248" "$PY" -B "$EO_ROOT/cards/B248/gen/cgx_inst.py" "$WK/ham" "$WK/b248/out" "$WK/in/TRI.json"
  run b248-ana "$WK/b248" "$PY" -B ana1.py
  chk G6.noncoded-gate b248-ana --has "^pairs 168 selected 56$" --has "^nonselected raw-half frames inside hyper\(Pt\),hyper\(Pu\): \{\(True, True\): 112\}$" --has "^\{\(True, True, False\): 56, \(False, True, False\): 112\}$" \
      --has "^\{\(False, False\): 112\} \{\(7, 7\): 112\}$" --has "^\{'sel:False': 224, 'non:False': 224\}$" --has "^\{False: 896\}$"
}

for g in G0 G1 G2 G3 G4 G5 G6; do
  want $g || continue
  f=$(echo "$g" | tr 'G' 'g')
  ( $f > "$OUT/$g.out" 2>&1; echo $? > "$OUT/$g.rc" ) &
done
wait
status=0; npass=0; nfail=0
for g in G0 G1 G2 G3 G4 G5 G6; do
  want $g || continue
  echo "== $g"; sed 's/^/   /' "$OUT/$g.out"
  p=$(grep -c '^PASS' "$OUT/$g.out"); f=$(grep -c '^FAIL' "$OUT/$g.out")
  npass=$((npass + p)); nfail=$((nfail + f))
  if [ "$(cat "$OUT/$g.rc")" != 0 ] || [ "$f" != 0 ] || [ "$p" = 0 ]; then echo "   FAILED: $g (exit $(cat "$OUT/$g.rc"), $f FAIL lines)"; status=1; fi
done
echo "== done in $((SECONDS - T0))s: $((npass + 2)) PASS (2 in step 0), $nfail FAIL; logs in $OUT"
exit $status
