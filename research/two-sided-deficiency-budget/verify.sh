#!/usr/bin/env bash
# Verification of research/two-sided-deficiency-budget (no kappa claim).   usage: bash verify.sh      PYTHON=/path/to/python (needs numpy >= 2)
# Two chains run concurrently (at most 2 busy processes): chain A = the audit scripts (checks/audit), chain B = dbounds + the budget optimiser + the R-B scripts (checks/rb).
#  0 manifest   1 dbounds.py  2 chk1  3 chk2  4 chk3 (+budget/opt3.py)  5 chk5  6 chk6  7 chk8 A/B80/B78/C   8 chk4   9 R-B: sym e6t flats2 opt5 opt6 opt7 kill46b indepB
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); C="$HERE/checks"; PY="${PYTHON:-python3}"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1
"$PY" -c "import numpy,sys; assert int(numpy.__version__.split('.')[0])>=2" 2>/dev/null || { echo "FAIL python needs numpy>=2 (PYTHON=...)"; exit 1; }
OUT=$(mktemp -d "${TMPDIR:-/tmp}/bxver.XXXXXX"); mkdir -p "$OUT/a" "$OUT/rb"; cp "$C"/rb/*.py "$OUT/rb/"
export BX_DATA="$HERE/data/data.json" BX_WORK="$OUT/a"; T0=$SECONDS
echo "== 0. manifest"; "$PY" -B "$C/manifest_check.py" | tee "$OUT/m.out" | sed 's/^/   /'; grep -q '^FAIL' "$OUT/m.out" && { echo FAIL; exit 1; }
# chk NAME TIMEOUT 'regex' 'label' cmd...   : PASS iff exit 0 and the log matches the regex
chk() { local n=$1 to=$2 re=$3 lab=$4; shift 4; timeout "$to" nice -n 10 "$@" > "$OUT/$n.log" 2>&1; local rc=$?
  if [ $rc = 0 ] && grep -Eq "$re" "$OUT/$n.log"; then echo "PASS $lab"; else echo "FAIL $lab (exit $rc)"; tail -3 "$OUT/$n.log"; fi; }
chainA() { cd "$OUT/a"
 chk chk1 900 "frame lines per E6 \[\(2, 896\), \(4, 224\)\] => max P112 lines in an E6 = 34" "[1] 1120 E6 each with 2 or 4 frame lines, max 34 P112 lines (=> d_2 = 78)" "$PY" -B "$C/audit/chk1.py"
 for p in "labels distinct True" "common bit set \[0\]|common bit set \[[0-9]\]" "root Off sizes Counter\(\{53: 112, 56: 8\}\)" "norm4 Off sizes Counter\(\{73: 896, 70: 128, 76: 56\}\)" "\(\(53, 52, 32\), 112\), \(\(56, 56, 32\), 8\), \(\(70, 56, 32\), 128\), \(\(73, 60, 36\), 896\), \(\(76, 64, 36\), 56\)" "global g\(8\),g\(7\) 64 36" "#codim1 511 #codim2 43435"; do
   grep -Eq "$p" "$OUT/chk1.log" && echo "PASS [1] chk1 line: $p" || echo "FAIL [1] chk1 line: $p"; done
 chk chk2 900 "codim 3 .*g\(6\)= 20" "[2] g(6) = 20 over all 788035 codim-3 functional spaces (enumerator validated)" "$PY" -B "$C/audit/chk2.py"
 grep -Eq "codim 4 .*g\(5\)= 12" "$OUT/chk2.log" && echo "PASS [2] g(5) = 12 over all 3309747 codim-4 spaces" || echo "FAIL [2] g(5)"
 chk chk3 300 "t=1 \[0, 0, 0, 0, 1, 2, 3, 4\]" "[3] size-only deletion-lemma optimiser (d_2=76) reproduces the BUDGET-X deficit table" "$PY" -B "$C/audit/chk3.py"
 for p in "t=2 \[0, 0, 0, 0, 2, 4, 6, 8\]" "t=3 \[0, 0, 0, 0, 2, 4, 6, 8\]" "t=4 \[0, 0, 0, 1, 3, 5, 7, 9\]" "t=5 \[0, 0, 0, 1, 3, 5, 7, 10\]" "t=6 \[0, 0, 1, 2, 4, 6, 8, 10\]"; do grep -Eq "$p" "$OUT/chk3.log" && echo "PASS [3] table row $p" || echo "FAIL [3] table row $p"; done
 chk opt3 300 "t=6 deficit 6b-minSigma for b=1..8: \[0, 0, 1, 2, 4, 6, 8, 10\]" "[3b] second implementation of the optimiser (budget/opt3.py)" "$PY" -B "$C/budget/opt3.py"
 chk chk5 300 "\(3, 6\) #feasible below 6b: 0 deficit 0 CLOSED by size" "[5] size-only closure with d_2 = 78 and cap_7 = 32: (3,5),(3,6),(4,1..4) closed; (4,5),(4,6) leave named candidates for the exact oracle" "$PY" -B "$C/audit/chk5.py"
 for p in "\(4, 4\) #feasible below 6b: 0 deficit 0 CLOSED" "\(4, 5\) #feasible below 6b: 1 deficit 1 needs exact oracle" "\(4, 6\) #feasible below 6b: 4 deficit 1 needs exact oracle"; do grep -Eq "$p" "$OUT/chk5.log" && echo "PASS [5] $p" || echo "FAIL [5] $p"; done
 chk chk6 1200 "\(\(78, 32, 20, 12\), 5376\), \(\(80, 32, 20, 12\), 1344\)" "[6] all 1120 level-2 targets P112 minus E6: per-target caps (cap7,cap6,cap5) = (32,20,12)" "$PY" -B "$C/audit/chk6.py"
 for m in A B80 B78 C; do chk chk8$m 1500 "COVERS FOUND 0" "[7] exact level-2 cover search, mode $m: no cover found" "$PY" -B "$C/audit/chk8.py" $m
   grep -q "^control: |S|=.*covering triples [1-9]" "$OUT/chk8$m.log" && grep -q "^control: 20-line pieces in P112 [1-9].*triple found 1" "$OUT/chk8$m.log" && grep -Eq "pieces enumerated [1-9]" "$OUT/chk8$m.log" && echo "PASS [7] mode $m: positive control found and pieces enumerated > 0" || echo "FAIL [7] mode $m non-vacuity"; done
 chk chk4 900 "max 2 => kill" "[8] (4,6) survivor killed: all 112 non-frame roots as r_1, no orbit reduction, compatible roots have rank <= 2 < 4" "$PY" -B "$C/audit/chk4.py"; }
chainB() { cd "$OUT/rb"
 chk dbounds 300 "PASS rank-6 flats with >= 35 lines" "[1] N_r = 0,1,3,6,12,20,36,63 (d_b bounds); rank-7 flats with >= 40 lines are E7/D7 = the 1200 directions; E6: 1120" "$PY" -B "$C/dbounds.py"
 grep -c '^PASS' "$OUT/dbounds.log" | grep -q '^3$' && echo "PASS [1] dbounds: 3 assertions" || echo "FAIL [1] dbounds"
 for s in sym e6t flats2; do chk $s 600 "orbits" "[9] R-B $s.py ran" "$PY" -B "$s.py"; done
 grep -q "E6 targets 1120 sizes \[78, 80\]" "$OUT/e6t.log" && echo "PASS [9] e6t: 1120 level-2 E6 targets of sizes 78, 80 (second implementation of d_2 = 78)" || echo "FAIL e6t"
 grep -q "targets |S|<=94 88516" "$OUT/flats2.log" && echo "PASS [9] flats2: 92380 parabolic flats, 88516 level-2 targets |S|<=94, 58 orbit reps" || echo "FAIL flats2"
 chk opt5 1200 "4 4 deficit 0 None" "[9] opt5 (level 1 exact oracle): (3,t<=6) and (4,t<=4) closed" "$PY" -B opt5.py
 grep -q "3 6 deficit 0 None" "$OUT/opt5.log" && echo "PASS [9] opt5: (3,6) deficit 0" || echo "FAIL opt5 (3,6)"
 chk opt6 1200 "4 5 deficit 0 None" "[9] opt6 (+ level 2 E6 exact, d_2 = 78): (4,5) closed" "$PY" -B opt6.py
 grep -q "4 6 deficit 1 (0, 0, 0, 0, 0, 3, 5, 5, 5, 5)" "$OUT/opt6.log" && echo "PASS [9] opt6: (4,6) leaves the single survivor (5,5,5,5,3,0^5)" || echo "FAIL opt6 (4,6)"
 chk opt7 1200 "4 6 deficit 1 \(0, 0, 0, 0, 0, 3, 5, 5, 5, 5\)" "[9] opt7 (all |S|<=94 level-2 targets): the same single survivor" "$PY" -B opt7.py
 chk kill46b 1200 "rep 56 .*survivors 0" "[9] kill46b: the survivor is killed (R-B implementation A)" "$PY" -B kill46b.py
 grep -q "rep 2 .*survivors 0" "$OUT/kill46b.log" && ! grep -q SURVIVOR "$OUT/kill46b.log" && echo "PASS [9] kill46b: 0 survivors at both root orbit reps" || echo "FAIL kill46b"
 chk indepB 1200 "Sm with >=4 independent compatible roots 0" "[9] indepB (R-B implementation B): cap_7 = 32 on root targets, (4,6) kill, 0 survivors" "$PY" -B indepB.py; }
( chainA > "$OUT/chainA.txt" 2>&1 ) & pA=$!
( chainB > "$OUT/chainB.txt" 2>&1 ) & pB=$!
wait $pA; wait $pB
echo "== audit chain"; cat "$OUT/chainA.txt"; echo "== budget / R-B chain"; cat "$OUT/chainB.txt"
cat "$OUT/chainA.txt" "$OUT/chainB.txt" > "$OUT/all.txt"
npass=$(grep -c '^PASS' "$OUT/all.txt"); nfail=$(grep -c '^FAIL' "$OUT/all.txt")
echo "== done in $((SECONDS - T0))s: $npass PASS, $nfail FAIL; logs in $OUT"
[ "$nfail" = 0 ] && [ "$npass" -gt 20 ] && { echo "PASS: all assertions hold"; exit 0; }
echo FAIL; exit 1
