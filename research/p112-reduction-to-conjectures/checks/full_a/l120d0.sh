#!/usr/bin/env bash
# L120D0: ClassI kill of rows 302 [7^9,6] (s=5) and 398 [7^9,6,1] (s=6), d=8: Lemma-F need counts for the A_{p-1} pattern (impl A lf.py = impl B brute force),
# tight-count test (tight.py, impl A), sigma0-refined margins (tight2.py, impl A) and the independent impl B (implB.py); non-kill controls = the A7 classes.
. "$(dirname "$0")/lib.sh"; D="$WK/l120d0"; rm -rf "$D"; mkdir -p "$D"; cp "$FA"/l120d0/*.py "$D"/; cd "$D"
$PY -B lf.py 8 9 > lf.out 2>&1 &
$PY -B implB.py > implB.out 2>&1 &
$PY -B lab_run.py > lab_run.out 2>&1 &
wait
want L120D0_lf "$(tr '\n' ';' < lf.out)" "p=8 A7 class(perp lines=1): need hist [(0, 1), (2, 84), (4, 35)] total 308 cap 36*8=288;p=8 A7 class(perp lines=0): need hist [(1, 8), (2, 56), (3, 56)] total 288 cap 36*8=288;p=9 A8 class(perp lines=0): need hist [(2, 36), (3, 84)] total 324 cap 36*9=324;" "need counts: impl A g-vector formula asserted equal to impl B brute-force rank for all 120 lines (assert inside lf.py); A8 total 324 = 9*36 tight"
want L120D0_labrun "$(sort -u lab_run.out | grep 'max lines' | tr '\n' ';')" "max lines in 6-flat 20;max lines in 7-flat 36;" "lab_run.py: max lines in a 6-flat = 20, in a 7-flat = 36"
want L120D0_implB "$(sed -n 1,3p implB.out | tr '\n' ';')" "need hist (array([2, 3]), array([36, 84])) total 324;m (max |A_a cap 7-flat|) 21;distinct 6-flat line sets 777241 max lines 20;" "impl B (Bourbaki roots, A8 = alpha2-coeff in {0,+-3}): need hist, m = 21, 777241 distinct 6-flat line sets"
want L120D0_implB_margins "$(sed -n '4,$p' implB.out | tr '\n' ';')" "1 55;2 35;3 15;4 35;5 55;6 75;7 75;8 75;" "impl B min margin (H - relief) over all 6-flats by sigma0 = 1..8 (needs >0 for row 302, >6 for row 398)"
python3 -B - <<PYEOF
m=[int(l.split()[1]) for l in open('implB.out').read().strip().split('\n')[3:]]
print(('PASS' if len(m)==8 and min(m)>6 else 'FAIL')+' FULL-A L120D0_kill: min margin %d (parsed from implB.out) > 0 (row 302 ClassI dead) and > 6 (row 398 ClassI dead)'%min(m))
PYEOF
# impl A tight.py (3 lines) and sigma0-refined tight2.py, one process per (p, perp) class
( $PY -B tight.py > tight.out 2>&1 ) &
for t in 8,1 8,0 9,0; do ( TT=$t $PY -B tight2.py > "tight2_$t.out" 2>&1 ) & done
wait
want L120D0_tight "$(tr '\n' ';' < tight.out)" "7-flat line sets 43181 6-flat subspaces 788035;p=8 perp=1: TOT=308 cap=288 m_a=[15, 15, 15, 15, 15, 15, 15, 15] r=2.0 flexible=35 surviving 6-flats=1470 worst=(4.0, 20, 8, 40);p=8 perp=0: TOT=288 cap=288 m_a=[21, 21, 21, 21, 21, 21, 21, 21] r=0.6666666666666666 flexible=0 surviving 6-flats=58744 worst=(20.0, 60, 60, 60);p=9 perp=0: TOT=324 cap=324 m_a=[21, 21, 21, 21, 21, 21, 21, 21, 21] r=1.0 flexible=0 surviving 6-flats=0 worst=None;" "tight.py (impl A): A7 classes (rows 159) not killed (surviving 6-flats 1470 / 58744), A8 class (rows 302/398): TOT=324=cap, 0 surviving 6-flats"
want L120D0_t2_A8 "$(tail -1 tight2_9,0.out)" "p=9 perp=0: min margin r*H-beta by sigma0: [(1, 55.0), (2, 35.0), (3, 15.0), (4, 35.0), (5, 55.0), (6, 75.0), (7, 75.0), (8, 75.0)]" "tight2.py (impl A, all 788035 six-dim label subspaces): A8 min margins = impl B values; min 15 > 6, so rows 302 AND 398 ClassI dead"
want L120D0_t2_A7a "$(tail -1 tight2_8,1.out)" "p=8 perp=1: min margin r*H-beta by sigma0: [(1, 16.0), (2, -4.0), (3, 16.0), (4, 36.0), (5, 36.0), (6, 36.0), (7, 36.0)]" "control (non-kill): A7 class perp=1 has margin -4 at sigma0=2 (row 159 ClassI NOT killed), test is not vacuous"
want L120D0_t2_A7b "$(tail -1 tight2_8,0.out)" "p=8 perp=0: min margin r*H-beta by sigma0: [(1, 20.0), (2, 0.0), (3, -20.0), (4, 0.0), (5, 20.0), (6, 40.0), (7, 40.0)]" "control (non-kill): A7 class perp=0 has margin -20 at sigma0=3"
