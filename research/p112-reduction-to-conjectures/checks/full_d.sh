#!/usr/bin/env bash
# FULL-D reruns of the former "recorded only" items: (1) SEVEN Lemma T3 / D7R, (2) AUDIT-IMP WALL 8.2/8.3, (3) RES116 count lemma + scenario margins
# (cross-checked with full_c/res/asm.py), (4) E6SLACK2 orbit-rep pipeline, (5) TWOSIDE bk1/bk2/f7.
# usage: bash checks/full_d.sh [WORKDIR]   Writes only to WORKDIR.  Sequential: one busy process at a time, each under timeout 1200.
# Needs: python3 with numpy+sympy+networkx (override PYTHON=...), cc.  Prints "FULL-D: PASS|FAIL <name>: ..." lines.
HERE=$(cd "$(dirname "$0")" && pwd); PY=${PYTHON:-python3}; export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1
WK=${1:-${TMPDIR:-/tmp}/full_d_work}; mkdir -p "$WK"; WK=$(cd "$WK" && pwd); echo "FULL-D: python=$PY work=$WK"
res() { if [ "$2" = 1 ]; then echo "FULL-D: PASS $1: $3"; else echo "FULL-D: FAIL $1: $3"; fi; }
T() { timeout 1200 "$@"; }
# ---- 1. SEVEN: Lemma T3 (A = tri7.c, B = triB.c) and Lemma D7R (A = d7in6.c, B = d7B.c / d7B2.c)
S="$WK/seven"; rm -rf "$S"; mkdir -p "$S"; cp "$HERE"/SEVEN/*.in "$HERE"/SEVEN/*.c "$S/"; cd "$S" || exit 2
for f in tri7 triB d7B d7B2 d7in6; do cc -O2 -o $f $f.c || echo "FULL-D: FAIL build $f"; done
T ./tri7 > tri7.out; T ./triB > triB.out; T ./d7in6 > d7A.out; T ./d7B > d7B.out; T ./d7B2 > d7B2.out
A=$(sed -E 's/.*\|Off\|=([0-9]+).*pairs.*: ([0-9]+) +\(min.*/\1:\2/' tri7.out | tr '\n' ' ')
B=$(sed -E 's/.*\|Off\|=([0-9]+).*pairs: ([0-9]+)$/\1:\2/' triB.out | tr '\n' ' ')
# A has 8 types (|Off| = 78 92 98 106 104 97 83 57); B has the same 8 plus a control type (|Off| = 84).  Coverable types must agree.
ca=$(echo $A | tr ' ' '\n' | awk -F: '$2>0{print $1}' | sort -n | tr '\n' ' '); cb=$(echo $B | tr ' ' '\n' | awk -F: '$2>0 && $1!=84{print $1}' | sort -n | tr '\n' ' ')
res SEVEN_T3_implA_B $([ "$ca" = "57 83 " ] && [ "$cb" = "57 83 " ] && echo 1 || echo 0) "coverable by two 7-flats: A (|Off|:#flat-pairs) [$A]; B (|Off|:#pairs) [$B]; coverable |Off| sets A=[$ca] B=[$cb]; D7(78) A7(92) A1A6(98) D5A2(97) A4A3(104) A1A2A4(106) not coverable in A and B; E6A1(83), E6(57) coverable (A,B)"
res SEVEN_D7R_implA_B $(grep -q 'leftover<=20 and rank<=6: 0  (min leftover rank 8, min leftover 14)' d7A.out && grep -q 'leftover<=20 in a <=7-flat: 0 ' d7B.out && grep -q 'in a <=7-flat: 0 (min #ann 1, min leftover 14)' d7B2.out && echo 1 || echo 0) "A d7in6: 0 pairs, min leftover rank 8, min leftover 14; B d7B / d7B2: no leftover <=20 in a <=7-flat, min leftover 14 (NOTES S4)"
# ---- 2. AUDIT-IMP: WALL 8.2/8.3 (pc2.c) + independent catalogue checks
I="$WK/audimp"; rm -rf "$I"; cp -R "$HERE/AUDIT-IMP" "$I"; cd "$I" || exit 2; cp dirs.txt dirs.shipped
T $PY -B ind_e8.py > ind_e8.out 2>&1; T $PY -B ind_coloop.py > ind_coloop.out 2>&1
res AUDITIMP_ind_e8 $(cmp -s dirs.txt dirs.shipped && grep -q 'catalogue violations (<=11 not of type 0-frame/1-rootswap): \[\]' ind_e8.out && grep -q 'complement rank<=7: 8 = frame classes: True' ind_e8.out && echo 1 || echo 0) "regenerated dirs.txt identical to shipped; catalogue Thm 6.1 / L3.1: no violations, 8 frame hyperplanes"
res AUDITIMP_ind_coloop $(grep -q 'root targets with coloop set != {itself}: 0' ind_coloop.out && grep -q 'frame targets Off(f_i)\\{v} not spanning W_i: 0' ind_coloop.out && grep -q 'beta(z_i,z_j)==1 all i,j: True' ind_coloop.out && echo 1 || echo 0) "$(grep -E 'coloop set|not spanning' ind_coloop.out | tr '\n' ';')"
cc -O2 -o pc2 pc2.c && T ./pc2 > pc2.out
res AUDITIMP_pc2_WALL82_83 $(grep -q '^targets 248; pair-coverable: roots 0, N70 0, frame 8; min part rank over frame 7+7 covers 7; frame covers with a <=6-dim part 0' pc2.out && echo 1 || echo 0) "$(tail -n 1 pc2.out) (REPORT.md item 1)"
# ---- 3. RES116: count lemma + per-scenario margins, cross-checked with full_c/res/asm.py
R="$WK/res116"; rm -rf "$R"; mkdir -p "$R"; cp -R "$HERE/RES116" "$HERE/AUDIT-SC" "$R/"; cd "$R/RES116" || exit 2
T $PY -B countm.py > countm.new; T $PY -B scenmargin.py > scenmargin.new
res RES116_countm_448_449 $(grep -E '^(448|449) ' countm.new | grep -c "count-margin(>0 kills) (6, 'ClassI', 2)" | grep -q '^2$' && echo 1 || echo 0) "$(grep -E '^(448|449) ' countm.new | sed 's/\[.*\]//' | tr '\n' ';') (margin 6 > 0 kills)"
res RES116_scenmargin $(cmp -s scenmargin.new scenmargin.out && cmp -s scenmargin.json "$HERE/RES116/scenmargin.json" && echo 1 || echo 0) "scenmargin.py output and scenmargin.json identical to shipped scenmargin.out / .json"
T $PY -B "$HERE/full_c/res/asm.py" > asm.new 2>&1
$PY -B - <<'PYEOF' > xcheck.out 2>&1
import re
rows={168,324,325,328,457,448,449}; sm={}
for l in open('scenmargin.out'):
    p=l.split()
    if len(p)>5 and p[2]=='rrc': sm[(int(p[0]),p[1])]=(int(p[3]),int(p[5]))
cur=None; n=0; bad=0
for l in open('asm.new'):
    m=re.match(r'ROW (\d+) ',l)
    if m: cur=int(m.group(1)); continue
    if cur in rows and l.startswith('   '):
        t=l.split()[0]; t={'beta1':'base'}.get(t,t); m=re.search(r'cap=?\s*(\d+)',l)
        if not m: continue
        cap=int(m.group(1)); k=sm.get((cur,t)); n+=1
        if k is None or k[1]!=cap or (('needs DimCover' in l) and k[0]!=0) or (('KILLED by COUNT' in l) and cap>=84): bad+=1; print('MISMATCH',cur,t,cap,k)
print('XCHECK scenarios with cap compared:',n,'mismatches:',bad)
PYEOF
res RES116_vs_asm $(grep -q 'mismatches: 0$' xcheck.out && ! grep -q 'compared: 0 ' xcheck.out && echo 1 || echo 0) "$(tail -n 1 xcheck.out): scenmargin caps/DimCover (rrc 0) agree with asm.py for rows 168 324 325 328 457 448 449"
# ---- 4. E6SLACK2: orbit-rep pipeline grp.py -> reps.py, regenerated .root compared with shipped (kissat NOT rerun; B2/C candidates are not shipped)
E="$WK/e6slack2"; rm -rf "$E"; mkdir -p "$E"; cp -R "$HERE/CARRIER" "$HERE/SC-B2" "$HERE/E6SLACK2" "$E/"; cd "$E/E6SLACK2" || exit 2
T $PY -B grp.py > grp.out 2>&1; ok=1; sh=""
for n in A0 A1 B0 B1; do T $PY -B reps.py $n.cand $n.new > $n.reps.out 2>&1; if cmp -s $n.new $n.root; then sh="$sh $n=$(shasum -a 256 $n.root | cut -c1-12)"; else ok=0; fi; done
res E6SLACK2_orbit_reps $([ $ok = 1 ] && grep -q 'order mod +- 311040' grp.out && echo 1 || echo 0) "grp.py group order/2 = 311040; regenerated A0 A1 B0 B1 .root byte-identical to shipped (sha256 prefix:$sh); B2.root/C.root not regenerable (candidate files not shipped; covered by the unreduced AUD-2 run in full_c)"
# ---- 5. TWOSIDE: F7 (f7.py rank/cover), Basis-kill tables bk1.py / bk2.py
W="$WK/twoside"; rm -rf "$W"; mkdir -p "$W/checks" "$W/data"; cp -R "$HERE/TWOSIDE" "$W/checks/"; cp -R "$HERE/../data/." "$W/data/"; cd "$W/checks/TWOSIDE" || exit 2
T $PY -B f7.py rank > f7_rank.out 2>&1; T $PY -B f7.py cover > f7_cover.out 2>&1
res TWOSIDE_f7 $(grep -q '\[(0, 41431), (1, 1976), (2, 28)\]' f7_rank.out && [ "$(tail -n 1 f7_cover.out)" = "$(cat f7cover.out)" ] && echo 1 || echo 0) "f7.py rank and cover: $(tail -n 1 f7_cover.out | sed 's/.*: //') (= shipped f7cover.out)"
T $PY -B bk1.py > bk1.out 2>&1; T $PY -B bk2.py > bk2.out 2>&1
b1=$(awk '$1==5 && $2<=6{printf "%s ",$4}' bk1.out); b2=$(awk '{printf "%s ",$3}' bk2.out)
res TWOSIDE_bk1_bk2 $([ "$b1" = "0 0 4 15 38 77 " ] && [ "$b2" = "0 0 4 " ] && echo 1 || echo 0) "bk1.py survivors for b=5, t=1..6: [$b1] (NOTES table 0 0 4 15 38 77); bk2.py (independent) b=5, t=1..3: [$b2]; (5,1),(5,2) closed by both"
