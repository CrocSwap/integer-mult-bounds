#!/usr/bin/env bash
# One-command verification of research/three-total-decoders (no kappa claim): reductions, partial theorems, the sharp example tied_min and the
# lift route for three-total root-unit decoders under #446 Theorem C.  Step 0 checks the package against MANIFEST.sha256 and every pin of SOURCES.json and
# stops hard on any mismatch.  Then C sources are compiled and seven check groups run one after the other (single process; python-sat and a C compiler only),
# printing one PASS/FAIL line per assertion.  Exit status 0 only if every assertion passes.
#   usage: bash verify.sh [/fresh/output/dir]     (inside a checkout or `git archive` of the repository; nothing outside the package is read)
#   needs python3 >= 3.11 with python-sat (requirements.txt) and cc; set PYTHON to choose the interpreter, CC for the compiler.  No external solver binary is run.
# Not re-run here: the Hesse experiment itself (README, Outcome X2), the G1 provers, the CP-SAT solve behind the multi-copy certificate (its certificate IS verified), #2031.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/three-total-decoders.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; CC="${CC:-cc}"; export PYTHONDONTWRITEBYTECODE=1
T0=$SECONDS
echo "== 0. manifest and provenance"
if ! "$PY" -B "$HERE/scripts/provenance.py" | tee "$OUT/provenance.log" | sed 's/^/   /' || grep -q '^FAIL' "$OUT/provenance.log" \
   || [ "$(grep -c '^PASS' "$OUT/provenance.log")" != 2 ]; then
  echo "step 0 FAILED"; exit 1
fi
# work tree: scripts and binaries live here, never in the package
R="$OUT/tree"; mkdir -p "$R" "$OUT/logs" "$R/bin"
cp -R "$HERE/checks" "$HERE/lib" "$HERE/data" "$HERE/c" "$R/"
export TMPDIR="$OUT/tmp"; mkdir -p "$TMPDIR"; export TTD_BIN="$R/bin"
E_="$PY -B $R/checks/expect.py"
run() { local n=$1; shift; ( cd "$R/checks" && "$@" > "$OUT/logs/$n.log" 2>&1; echo $? > "$OUT/logs/$n.rc" ); }
chk() { local l=$1 n=$2; shift 2; $E_ "$l" "$OUT/logs/$n.log" "$@" | tee -a "$OUT/all.out"; }

echo "== G0 compile the five C programs from source"
ok=1; for p in enumall tusign jsign mas brutetu; do "$CC" -O2 -o "$R/bin/$p" "$R/c/$p.c" > "$OUT/logs/cc_$p.log" 2>&1 || ok=0; done
if [ "$ok" = 1 ]; then echo "PASS G0.compile  enumall tusign jsign mas brutetu" | tee -a "$OUT/all.out"; else echo "FAIL G0.compile  see $OUT/logs/cc_*.log" | tee -a "$OUT/all.out"; fi

echo "== G1 tied_min: cost = v = 12 (exchange proof, 217 optima, lifts)"
run tied_min $PY -B tied_min.py
chk G1.structure tied_min --has '^TM structure: v=12 points all full support with entries \+-1: True; q two-support: True; \|D\(t\)\|=2 for every line \(tied\): True; incidences 72; block row sets all 12 rows: True$' \
    --has '^TM classes \(missing coordinate of q\): sizes \[4, 4, 4\]; distinct points 4, distinct q-lines 6$' --has '^TM H strongly connected \(Lemma SCC\): True$'
chk G1.step-a tied_min --has '^TM step \(a\): MAS\(G\[D_j\]\) for j=0,1,2: \[3, 3, 3\]$'
chk G1.step-b tied_min --count '^TM step \(b\) j=[012]: block rank <= 3 fillings of its 8 columns: 1; \(dim S_k, dim S_l, dim\(S_k\+S_l\), class-[012] rows vanish\) = \[\(\(3, 3, 3\), True\)\]$' 3
chk G1.step-c tied_min --has '^TM step \(c\): B\[T_j,C_j\] is 4x4 with \(free entries, minimum F2 rank over all fillings\) = \[\(8, 2\), \(8, 2\), \(8, 2\)\]$'
chk G1.cnf tied_min --has '^TM CNF cost<=11: UNSAT$' --has '^TM CNF cost<=12: SAT, block ranks recomputed by elimination \[4, 4, 4\]$'
chk G1.optima tied_min --has '^TM optima: B with block ranks <= \(4,4,4\) enumerated to exhaustion: 217$' --has '^TM optima: block-rank triples \[\(4, 4, 4\)\], costs \[12\]$' \
    --has "^TM optimum kind: class-diagonal: dim S_k \(2, 2, 2\), rank B 6, w \(2, 2, 2\), class-block ranks \(2, 2, 2\) -> 216 matrices$" \
    --has "^TM optimum kind: cross-class entries 24: dim S_k \(4, 4, 4\), rank B 4, w \(0, 0, 0\), class-block ranks None -> 1 matrices$" \
    --has '^TM special optimum B0: S_0 = S_1 = S_2 = W \(column spaces equal, dim 4\): True$'
chk G1.f2s-identity tied_min --has '^TM F2S identity cost = 3\*rho - sum_j w_j .*holds for 217 of 217 optima$'
chk G1.lifts tied_min --has '^TM lifts: .*\(4,4,4\): 217 of 217; whole 12x12 B TU-signable: 217 of 217$'
chk G1.subconfigurations tied_min --has '^TM every one-line deletion has cost >= 12 \(cost <= 11 UNSAT\): 12 of 12$' \
    --has '^TM first tight 10-line subconfiguration \(cost <= 9 UNSAT, cost <= 10 SAT\): \(0, 1, 2, 3, 4, 5, 6, 7, 9, 10\)$' --absent 'Traceback'

echo "== G2 lift route: v = 9 whole-TS counterexample, joint block-TU counterexamples (X1 evidence), Theorem 9.3"
run g1_cex $PY -B g1_cex.py
run lifts $PY -B lifts.py
chk G2.w9-instance g1_cex --has '^W9 v=9 f=13 mincost=18 minimisers=16 block ranks \[\(7, 4, 7\)\] offdiag-ones 8..12$' \
    --has '^W9 the 8-ones minimiser of PROOF section 6 occurs: True \(number of 8-ones minimisers 1\)$' \
    --has '^W9 degeneracy: lines 1,2 equal True; lines 4,6 equal True; lines 7,8 same projective line True; points 4,5 coincide True$'
chk G2.w9-no-whole-TS g1_cex --has '^W9 whole-matrix TU-signable: 0 of 16; all three blocks TU-signable: 16 of 16; jointly block-TU signable: 16 of 16; python Camion agrees: True$'
chk G2.w9-lift g1_cex --has '^W9 joint signing has exact Q block ranks equal to the F2 ranks for 16 of 16 minimisers; \(A\) 18 >= v = 9: True$'
chk G2.j7-no-joint g1_cex --has '^J7 v=7 f=11 mincost=12 minimisers=4 off-diagonal ones \[7, 8, 9, 10\] block ranks \[\(4, 4, 4\)\]$' \
    --has '^J7 submatrix rows 0,2,3,4 x cols 0,3,4,6 .*: \[\(7, False\), \(8, False\), \(9, False\), \(10, False\)\]$' \
    --has '^J7 jointly block-TU signable: 0 of 4; whole-matrix TU-signable: 0; block 2 TU-signable: 0; blocks 0,1 TU-signable: 4,4; python Camion agrees: True; \(A\) 12 >= v = 7: True$'
chk G2.j7-lift g1_cex --has '^J7 lift: the printed rational 7x7 matrix has the support of a minimiser: True; exact Q block ranks \[4, 4, 4\], F2 block ranks \[4, 4, 4\]$' \
    --has '^J7 block 2 has 4 nonzero rows of 6 '
chk G2.j10-no-joint g1_cex --has '^J10 v=10 f=19 mincost=14 minimisers=2 block ranks \[\(5, 4, 5\)\] jointly block-TU signable 0; block-wise TU-signable \(b0 b1 b2\) \[\(1, 1, 0\), \(1, 1, 0\)\]; \(A\) True$'
chk G2.failure-modes g1_cex --has '^C8 v=8 f=11 mincost=16 minimisers=320; minimisers with all blocks TU-signable but NO joint signing \(Cech, F2\): 1; jointly signable: 318$' \
    --has '^C8 python Camion agrees on the Cech minimisers: True$' \
    --has '^S8 v=8 f=12 mincost=14 minimisers=2 ones \[9, 9\] block ranks \[\(4, 5, 5\)\]; whole-TU \[1, 0\]; block TU flags \[\(1, 1, 1\), \(0, 1, 1\)\]; jointly signable 1$' \
    --has '^S8 the two minimisers differ by one swap of ones: True$'
chk G2.obstructions g1_cex --has '^L91 TU-signable: J2 True, odd 3-cycle True, F7 submatrix \[110,011,101,111\] False$' --has '^L91 odd theta of supmin_fail_v8 \(rows 0,1,2,6 x cols 0,3,4,6\): TU-signable False$'
chk G2.theorem-9.3 g1_cex --has '^T93 Camion system \(jsign.c\) vs exhaustive signings x exhaustive minors \(brutetu.c\): 53 instances, 53 agree on \(J,b0,b1,b2\), 0 skipped as out of range$' \
    --has '^T93 outcome classes seen: J=0 b=011 x2, J=0 b=100 x1, J=0 b=101 x2, J=0 b=110 x4, J=0 b=111 x2, J=1 b=111 x42$' \
    --has '^T93 Cech case \(every block signable, no joint signing\) confirmed by the exhaustive oracle: True$'
chk G2.nojoint14 g1_cex --has '^NJ14 instances nojoint_21_1..14 \(v 7-10\): minimisers without a joint block-TU signing: 14 of 14 instances \(joint signings in total 0\); \(A\) cost >= v in 14;'
chk G2.nojoint-lifts lifts --has '^NL lifts: 102 stored \(16 configurations: .*minimiser 102, support equal 102, diagonal nonzero 102, exact Q block ranks <= F2 ranks 102 \(equal 102\) of 102$' --has '^NL cex_joint_v7 minimisers lifted: 4 of 4$' --absent 'Traceback'
chk G2.gadget g1_cex --has '^GAD v=10 f=29 .*: 11 off-diagonal ones, block ranks \[6, 6, 7\] sum 19 = 19: True; block TU-signable flags \[True, False, False\]; whole B TU-signable False$' --absent 'Traceback'

echo "== G3 cex_min_1: the one-copy certificate stops at 18, the multi-copy certificate (verified, not solved) reaches 20"
run mcc_cex $PY -B mcc_cex.py
chk G3.cex-structure mcc_cex --has '^CX v=19 entries in \{-1,0,1\}: True; \|D\(t\)\| odd for 8 lines \(set G\), even \(=2, tied\) for 11$' \
    --has '^CX D-types \{\(0,\): 4, \(0, 1\): 3, \(0, 1, 2\): 1, \(0, 2\): 5, \(1,\): 1, \(1, 2\): 3, \(2,\): 2\}$'
chk G3.parity-lemmas mcc_cex --has '^CX Lemma 1.1: every incidence t->s has \|pi\(t\) & sigma\(s\)\| in \{0,2\}: True \(114 incidences\)$' \
    --has '^CX Lemma 1.2: tied lines of the same \(D, eps\) are never incident: True \(6 classes\)$' \
    --has '^CX pool: 121 primitive pairs \(p,q\) in \{-1,0,1\}\^3 with p.q != 0 \(13 vectors up to sign\); Lemma 1.1 on all incidences of the pool: True$'
chk G3.mcc-certificate mcc_cex --has '^CX MCC: stored solution has 20 copies on 17 lines \(up to 2 per line\); .*forward: True$' --has '^CX MCC: 20 copies >= v = 19: True$'
chk G3.lemma-MC mcc_cex --has '^CX Lemma MC on 60 admissible B \(incl. B = I\): N unit upper triangular for 60 of 60; sum_j rank B_j >= 20 for 60 of 60 ' \
    --has '^CX stored B of cost <= 22: admissible True; block ranks \[10, 6, 6\] sum 22; so 20 <= cost\(cex_min_1\) <= 22$' --absent 'Traceback'

echo "== G4 partial theorems and reductions: M1, U, SCC, Peel"
run thm $PY -B thm.py
chk G4.M1 thm --has '^M1 80 random configurations with every point having a zero coordinate \(v 6-14\): violations of MAS-sum >= sum_t c\(t\) >= v/2: 0; ' \
    --has '^M1 sharpness digon: v=2, sum_t c\(t\) = 1, MAS-sum 1, exact cost 2 '
chk G4.U thm --has '^U cex_min_1: certificate sizes for the three special coordinates \[\(15, 8, 11\), \(15, 8, 11\), \(15, 8, 11\)\] ' --has '^U 121-line pool: sizes \[106, 106, 106\]; best 106 of v = 121$' \
    --has '^U 250 random unit-world configurations \(4-60 lines, forced incidences\): every scheme valid; smallest best-certificate/v = .*\(>= 1/2: True\)$'
chk G4.SCC thm --has '^SCC block upper-triangularity in topological order of the strong components of H: 300 of 300 random configurations ' --has '^SCC component sizes: tied_min \[12\], cex_min_1 \[19\]$'
chk G4.PP thm --has '^PP lone tied lines of tied_min cost \[2\]; lines 0 and 3 \(different point, different line: True\) together cost 2, so no group X '
chk G4.Peel thm --has '^PEEL 36 configurations with a unit-support point or line: exact cost\(config\) >= cost\(config - t\) \+ 1 violated in 0$' --has '^MONO exact cost\(sub-configuration\) <= cost\(config\) violated in 0 of 36$' --absent 'Traceback'

echo "== G5 F2S rowspace identity"
run f2s $PY -B f2s.py
chk G5.identity f2s --has '^F2S identity cost = 3 rho - sum_j w_j on 179 .*: holds in 179; cost >= 2 rho in 179; sum_j w_j <= rho \(direct sum\) in 179$' --has '^F2S 8 random F2S configurations \(v 6-8\): cost <= v-1 UNSAT \(cost >= v\) in 8$' --absent 'Traceback'

echo "== G6 non-degenerate admissible B that is not TU-signable (aff14)"
run nondeg $PY -B nondeg.py
chk G6.aff14 nondeg --has '^NG aff14: n=14 admissible True; points pairwise distinct True; lines pairwise distinct True; off-diagonal ones 24; K22 \(L6 pattern, 4 distinct indices\) present: False$' \
    --has '^NG aff14: blocks R_j x A_j equal to the whole matrix for j in \[2\]; block ranks \[9, 11, 11\]; whole B TU-signable \(Camion\): False$' --absent 'Traceback'

echo "== G7 Hesse harness (smoke only; the experiment is described in README, Outcome X2)"
run hesse_smoke $PY -B hesse_smoke.py
chk G7.hesse hesse_smoke --has '^HS Hesse configuration over Z\[w\] \(w\^2\+w\+1=0\): 9 points, 12 lines, points per line \[3\], lines per point \[4\]; intersection points of the lines 21$' \
    --has '^HS every pair of the 9 points lies on one of the 12 lines \(no ordinary line\): True$' \
    --has '^HS smoke sample: 16 random configurations .*: smallest cost - v = 0, cost = v in 1, cost < v in 0$' --absent 'Traceback'
# X2 hook: if the Hesse experiment ends BELOW-v FOUND, the configuration(s) go to data/hesse_below_*.json (README, Outcome X2) and are evaluated exactly here.
EXPECT=34
nb=$(ls "$HERE"/data/hesse_below_*.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$nb" -gt 0 ]; then
  echo "== G7b Hesse configurations below v (data/hesse_below_*.json)"
  run hesse_below $PY -B hesse_below.py
  chk G7.below hesse_below --has '^HB all [1-9][0-9]* configurations have exact minimum cost below v$' --absent 'Traceback' --absent '>= v'
  EXPECT=$((EXPECT+1))
fi

npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out")
echo "== done in $((SECONDS - T0))s: $((npass + 2)) PASS (2 in step 0), $nfail FAIL; logs in $OUT"
[ "$nfail" = 0 ] && [ "$npass" = "$EXPECT" ] || { echo "FAILED: expected $EXPECT assertion PASS lines after step 0, got $npass PASS / $nfail FAIL"; exit 1; }
