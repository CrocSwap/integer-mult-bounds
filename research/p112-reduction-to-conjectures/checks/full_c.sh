#!/usr/bin/env bash
# FULL-C reruns: (1) SIXHEAVY Lemma GRRC-2 cover facts + the 12 kills, (2) row 424 E6 Dim-Cover (6,6,5,5,5,4)+1 on Phi\E6.
# usage: bash checks/full_c.sh [WORKDIR]   Writes only to WORKDIR (default $TMPDIR/full_c_work).  <=3 busy processes (xargs -P3), each job under timeout 1200.
# Needs python3 with numpy+networkx+sympy (override PYTHON=...), cc.  Prints "FULL-C: PASS|FAIL <name>: ..." lines.  Pins are the recorded values in the cards (cited in PROOF_MAP_c.md).
HERE=$(cd "$(dirname "$0")" && pwd); F="$HERE/full_c"
if [ -z "${PYTHON:-}" ]; then for p in python3; do "$p" -c 'import numpy,networkx,sympy' 2>/dev/null && PYTHON=$p && break; done; fi
WK=${1:-${TMPDIR:-/tmp}/full_c_work}; mkdir -p "$WK/six" "$WK/e6" "$WK/res"; WK=$(cd "$WK" && pwd)
export PYTHON F WK HERE FULLC_WORK="$WK/six" PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1
echo "FULL-C: python=$PYTHON work=$WK"
cc -O2 -o "$WK/audcov" "$F/aud2/cov.c" && cc -O2 -o "$WK/s" "$F/e6/s.c" && cc -O2 -o "$WK/six/covB" "$F/sixheavy/covB.c" || { echo "FULL-C: FAIL builds"; exit 1; }
# job(name, workdir, regex-required-in-output, cmd...) : runs under timeout 1200, prints PASS/FAIL
job() { n=$1; d=$2; req=$3; shift 3; ( cd "$WK/$d" && timeout 1200 "$@" > "$WK/$n.log" 2>&1 ); rc=$?
  if [ $rc = 0 ] && grep -Eq "$req" "$WK/$n.log"; then echo "FULL-C: PASS $n: $(grep -E "$req" "$WK/$n.log" | head -1 | cut -c1-150)"; else echo "FULL-C: FAIL $n (rc=$rc, need /$req/): $(tail -n 2 "$WK/$n.log" | tr '\n' ' ' | cut -c1-200)"; fi; }
export -f job
echo "== 0. impl-B label data regenerated and compared with the shipped B.json; flats tables (impl A)"
( cd "$WK/six" && $PYTHON -B "$F/sixheavy/labB.py" >/dev/null && cmp B.json "$F/sixheavy/B.json" && echo "FULL-C: PASS labB_B.json identical to shipped" || echo "FULL-C: FAIL labB B.json differs" )
( cd "$WK/six" && [ -f flats7.pkl ] || $PYTHON -B -c "
import sys; sys.path.insert(0,'$F/sixheavy')
from sa import *
for w in (1,2,3,4,5,6,7): print(w,len(flats(w)),flush=True)" ) | tail -n 7 | tr '\n' ' '; echo
# --- jobs (name | workdir | required regex | command).  A = sixheavy/verA.py (python), B = sixheavy/qB.py+covB.c (C), AUD2 = aud2/cov.c (own label build)
A_L="E7:7,7,1 E7:7,7 E7:6,6,5,5 E7:6,6,4,4,4 E7:6,6,4,4,3,1 D7:7,7,6,6 D7:6,6,6,4,4,1,1 D7:6,6,6,4,4,2 D7:6,6,6,5,4 E7:6,6,4,4,1 E7:6,6,4,4,1,1 E7:6,6,4,4,2 E7:6,6,5,3,1"
V="$PYTHON -B $F/sixheavy"; AC="$WK/audcov"; S="$WK/s"; LB="$F/e6/labs.txt"
cat > "$WK/jobs" <<EOT
SIX_A_D7_664443#six#^FACTS_OK#$V/verA.py D7:6,6,6,4,4,3 | $PYTHON -B $F/cmp.py facts
SIX_B_D7_664443#six#^FACTS_OK#$V/qB.py D7:6,6,6,4,4,3 | $PYTHON -B $F/cmp.py facts
E6_AUD2_unreduced_plus1#res#^NONE nodes=250733100#$AC e6 6 6 5 5 5 4 1
SIX_A_light#six#^FACTS_OK#$V/verA.py $A_L | $PYTHON -B $F/cmp.py facts
SIX_A_E7_6654#six#^FACTS_OK#$V/verA.py E7:6,6,5,4 | $PYTHON -B $F/cmp.py facts
SIX_B_light#six#^FACTS_OK#$V/qB.py $A_L | $PYTHON -B $F/cmp.py facts
SIX_B_E7_6654#six#^FACTS_OK#$V/qB.py E7:6,6,5,4 | $PYTHON -B $F/cmp.py facts
AUD2_root_6654#res#^NONE nodes=1478386#$AC root 6 6 5 4
AUD2_root_66442#res#^NONE nodes=4691896#$AC root 6 6 4 4 2
AUD2_root_664411#res#^NONE nodes=85998#$AC root 6 6 4 4 1 1
AUD2_root_66441#res#^NONE nodes=18410#$AC root 6 6 4 4 1
AUD2_root_66531#res#^NONE nodes=387938#$AC root 6 6 5 3 1
AUD2_root_77_ctl#res#^NONE nodes=337#$AC root 7 7
AUD2_root_771_ctl#res#^COVER witness ok=1#$AC root 7 7 1
AUD2_root_6655_ctl#res#^COVER witness ok=1 nodes=5\$#$AC root 6 6 5 5
AUD2_d7_66654#res#^NONE nodes=4208#$AC d7 6 6 6 5 4
AUD2_d7_666443#res#^NONE nodes=767660#$AC d7 6 6 6 4 4 3
AUD2_d7_666442#res#^NONE nodes=78#$AC d7 6 6 6 4 4 2
AUD2_d7_66644_11#res#^NONE nodes=3#$AC d7 6 6 6 4 4 1 1
SIX_chk2#six#^CHK2_OK#$V/chk2.py | $PYTHON -B $F/cmp.py chk2
SIX_chkgrrc#aud2#^ALL OK#$PYTHON -B $F/aud2/chkgrrc.py
SIX_chkJ#six#uncovered \[\]#$V/chkJ.py
E6_A0_orbit#e6#nodes=24325\$#env ROOTFILE=$F/e6/A0.root $S $LB 0 1 100000000000 6 6 5 5 5 4
E6_A1_orbit_plus1#e6#nodes=2261334\$#env ROOTFILE=$F/e6/A1.root $S $LB 1 1 100000000000 6 6 5 5 5 4
E6_C_ctl_66555_5#e6#^RESULT COVERABLE nodes=3431307#env ROOTFILE=$F/e6/C.root $S $LB 0 1 100000000000 6 6 5 5 5 5
E6_AUD2_unreduced#res#^NONE nodes=1581034#$AC e6 6 6 5 5 5 4
EOT
echo "== 1. jobs (<=3 procs)"
# the two heavy jobs first so they start early
tr '\n' '\0' < "$WK/jobs" | xargs -0 -n1 -P3 bash -c 'IFS="#" read -r n d req cmd <<< "$1"; mkdir -p "$WK/$d"; job "$n" "$d" "$req" bash -c "$cmd"' _ | sort
echo "== 2. GRRC-2 bookkeeping with impl-B oracle (fill.py, resumable cache; pass 1 and 2)"
for i in 1 2; do ( cd "$WK/six" && timeout 1200 $PYTHON -B "$F/sixheavy/fill.py" 30 > fill$i.out 2>&1 ; echo "fill pass $i rc=$?" ); [ -f "$WK/six/fill_res.json" ] && break; done
( cd "$WK/six" && $PYTHON -B - <<'X'
import json,sys
d=json.load(open('fill_res.json')); res=d['res']; used=set(d['used'])
killed=sorted(int(r) for r,v in res.items() if all(k for _,k in v)); opn=sorted(int(r) for r,v in res.items() if not all(k for _,k in v))
want_k=[169,312,316,332,333,418,420,426,427,430,435,464]; want_o=[303,315,400,401,402,409,411,417,424,425]
want_u={'D7:6,6,6,4,4,1,1','D7:6,6,6,4,4,2','D7:6,6,6,4,4,3','D7:6,6,6,5,4','E7:6,6,4,4,1','E7:6,6,4,4,1,1','E7:6,6,4,4,2','E7:6,6,5,3,1','E7:6,6,5,4'}
ok=killed==want_k and opn==want_o and used==want_u
print('FULL-C: %s SIX_fill_kills: killed=%s open=%s used=%d facts (== the 9 pinned: %s)'%('PASS' if ok else 'FAIL',killed,opn,len(used),used==want_u))
X
)
echo "FULL-C: done"
