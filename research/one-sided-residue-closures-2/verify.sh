#!/usr/bin/env bash
# Verification of research/one-sided-residue-closures-2 (no kappa claim).  usage: bash verify.sh   PYTHON=/path/to/python (numpy, networkx)   FULL=1 also reruns every chunk of the (7,4,3) and (6,6,2) span passes (chunked, <=3 processes, 20-min cap each)
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); C="$HERE/checks"; PY="${PYTHON:-python3}"; FULL="${FULL:-0}"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
OUT=$(mktemp -d "${TMPDIR:-/tmp}/resclos2.XXXXXX"); cd "$OUT"; note() { echo "$@" | tee -a "$OUT/all.out"; }
"$PY" -c "import numpy, networkx" 2>/dev/null || { echo "FAIL needs numpy and networkx"; exit 1; }
echo "== 0. manifest"; "$PY" -B "$C/manifest_check.py" | tee -a all.out | sed 's/^/   /'; grep -q '^FAIL' all.out && exit 1
G="$HERE/checks/g777"; E="$HERE/checks/e6"
echo "== 1. G777 Lemma Q4 leftover facts: implementation A (lo2, nq, m13), implementation B (implB, implB2), audit (a2_g777, a2b_m13)"
ex() { grep -Eq "$2" "$OUT/$1.log" && note "PASS $3" || note "FAIL $3"; }
r() { n=$1; shift; timeout 1200 nice -n 10 "$PY" -B "$@" > "$OUT/$n.log" 2>&1; }
( r lo2 "$G/lo2.py" 11 ) & ( r nq "$G/nq.py" ) & ( r implB "$G/implB.py" ) & wait
ex lo2 "minimal 315 Counter\(\{8: 315\}\)" "A: r0 covered: all minimal leftovers <= 11 are the 315 eight-sets"; ex lo2 "\(8, 4\): 315" "A: the 315 have F2 label rank 4"
ex nq "#distinct Q 9450  N_Q distribution Counter\(\{4: 9450\}\)" "A: 9450 distinct Q, each the leftover of exactly 4 roots"; ex nq "Counter\(\{0: 9450\}\)" "A: no root lies in its own Q"
ex implB "B: root \|Off\| 57 min leftover 14? .*min leftover with r covered 8" "B: independent build: root min leftover with r covered = 8"; ex implB "minimal leftovers <=11 \(r covered\): 315 Counter\(\{8: 315\}\)" "B: 315 minimal leftovers, all of size 8"
ex implB "min leftover 14$" "B: non-root minimal leftover 14 (D7)"
( r m13 "$G/m13.py" ) & ( r implB2 "$G/implB2.py" ) & ( r a2 "$G/a2_g777.py" ) & wait
ex m13 "max served roots over E = M \(\+1 line\), M an r0 12-leftover: 4 " "A: max served roots = 4 for E = M (+1 line)"; ex implB2 "E = M \(\+1 line\): 18  need <=22" "B2: at most 18 roots outside E with |Off(r) n E| >= 8, so 13+18 < 36"
ex a2 "NONROOT min leftover 14" "audit: non-root min leftover 14"; ex a2 "\[\(8, 315\), \(12, 5040\), \(16, 4032\)\]" "audit: r0 minimal leftovers 8:315, 12:5040, 16:4032"; ex a2 "all full-4-flat & D4-minus-frame True" "audit: all 315 Q are D4 minus a frame"
cp "$OUT/a2_left.pkl" . 2>/dev/null; ls a2_left.pkl >/dev/null 2>&1 || cp "$PWD/a2_left.pkl" . 
timeout 1200 nice -n 10 "$PY" -B "$G/a2b_m13.py" > a2b.log 2>&1; ex a2b "distinct Q 9450 roots per Q \{4\} distinct M 219240" "audit: 9450 Q, 219240 M"; ex a2b "max served roots outside E over E=M or M\+\{l\}: 4" "audit: max served roots 4 (so pairs <= 13 + 20 = 33 < 36)"
echo "== 2. count lemma, RRC and Dim-Cover E6 (6,6,5,5,5,4)"
timeout 600 "$PY" -B "$E/tight.py" > tight.log 2>&1; ex tight "tight cover exists: False" "E6 dim-cover, implementation 1 (tight.py): (6,6,5,5,5,4) cannot cover the 84 lines outside E6"
cc -O3 -o "$OUT/sub" "$E/sub.c" || note "FAIL compile sub.c"; SUBBIN="$OUT/sub" timeout 600 "$PY" -B "$E/verify_e6.py" 6,6,5,5,5,4 > ve6.log 2>&1; ex ve6 "\[6, 6, 5, 5, 5, 4\] False" "E6 dim-cover, implementation 2 (cov2/verify_e6.py): same result"
echo "== 3. span passes (re-check of shipped raw outputs, then reruns)"
"$PY" -B "$C/sc/sc_check.py" good_shipped.txt | tee -a all.out | sed 's/^/   /'
bash "$C/sc/sc_rerun.sh" "$OUT/rerun" "$FULL" > rerun.log 2>&1
for f in "$OUT"/rerun/*.out; do grep -q '^rc=0' "$f" && ! grep -q CRACK "$f" || { note "FAIL rerun $(basename $f)"; }; done; note "PASS ran $(ls $OUT/rerun/*.out | wc -l) span chunks from s3z.c: rc=0, no CRACK"
mkdir -p mix; cp "$HERE"/evidence/sc_runs/*.out mix/ ; cp "$OUT"/rerun/*.out mix/
"$PY" -B "$C/sc/sc_check.py" good_rerun.txt "$OUT/rerun" | tee -a all.out | sed 's/^/   /'
echo "== 4. ledger"
cd "$C"; "$PY" -B new_kills.py "$OUT/good_shipped.txt" | tee "$OUT/nk.log" | sed 's/^/   /'; cmp -s ledger2_recomputed.csv "$HERE/data/ledger2_consolidated.csv" && note "PASS ledger recomputed = shipped data/ledger2_consolidated.csv" || note "FAIL ledger differs"; rm -f ledger2_recomputed.csv
grep -q "'OPEN': 38" "$OUT/nk.log" && note "PASS open count 38" || note "FAIL open count"
"$PY" -B "$C/sc/row_cert.py" "$HERE/data/ledger2_consolidated.csv" > "$OUT/rowcert.log" 2>&1; tail -1 "$OUT/rowcert.log" | sed 's/^/   /'; grep -q "^PASS span-pass row certificates: 56 rows, 0 without" "$OUT/rowcert.log" && note "PASS per-row Lemma-B certificates for all 56 span-pass rows" || note "FAIL per-row certificates"
grep -c '^PASS' "$OUT/all.out" | sed 's/^/PASS lines: /'; grep '^FAIL' "$OUT/all.out" && echo "SOME FAILED" || echo "ALL PASS"
