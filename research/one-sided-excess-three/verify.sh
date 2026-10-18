#!/usr/bin/env bash
# Verification of research/one-sided-excess-three (no kappa claim).   usage: bash verify.sh [/fresh/output/dir]
# Needs: Python >= 3.11 with numpy >= 2.0 and scipy (PYTHON=/path/to/python to choose), and a C compiler `cc` (128-bit integers: gcc/clang). No SAT solver.
# Everything runs under `nice -n 10`, at most 3 processes at a time, each under `timeout 1200`; the chunked stages run as 3 fixed lanes (a single `wait` on the lanes, no wait loops). Expected: about 35-45 minutes.
#   0  MANIFEST.sha256
#   1  data regeneration (gen.py 80, gen3.py) compared byte for byte with data/; land3.py 3 (slack-3 landscape); carrier3.py (finite inputs of the Carrier and Parity Lemmas)
#   2  compile s6x.c (implementation A, written for #2826 and extended) and k3.c (implementation B, written independently)
#   3  the kills of the 8 slack-3 survivors and the controls, both implementations, chunked
#   4  check_logs.py: every assertion of the README as a PASS/FAIL line
# Inherited inputs of #2816 / #2826 (flat caps, |Off| >= 70 off the roots and frame, DP/LP/Pencil/triple rules, Lemma B, direction list) are cited, not recomputed, except land3.py, which re-runs the DP/LP/Pencil/triple/Basis stages at slack <= 3.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/excess-three.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1
TMO=""; command -v timeout >/dev/null 2>&1 && TMO="timeout 1200"; command -v gtimeout >/dev/null 2>&1 && TMO="gtimeout 1200"
[ -n "$TMO" ] || { echo "need timeout or gtimeout"; exit 2; }
WK="$OUT/work"; LOG="$OUT/logs"; mkdir -p "$WK" "$LOG"; : > "$OUT/all.out"; T0=$SECONDS
echo "== 0. manifest"
"$PY" -B "$HERE/checks/manifest_check.py" | tee -a "$OUT/all.out" | sed 's/^/   /'; grep -q '^FAIL' "$OUT/all.out" && { echo "step 0 FAILED"; exit 1; }
cp "$HERE"/checks/*.py "$HERE"/checks/*.c "$HERE"/data/* "$WK"/
cd "$WK"
cat > runone.sh <<'RUN'
#!/usr/bin/env bash
# usage: runone.sh name cmd args...   (cwd = work dir; output in $LOG/name.out / name.err; at most 3 attempts)
n=$1; shift
export PYTHONDONTWRITEBYTECODE=1
for attempt in 1 2 3; do   # a job that dies (signal from outside, timeout) is run once more; check_logs.py fails on a missing summary line
  $TMO nice -n 10 "$@" > "$LOG/$n.out" 2> "$LOG/$n.err" && break
done
exit 0
RUN
chmod +x runone.sh; export TMO LOG PYTHONDONTWRITEBYTECODE
echo "== 1. data regeneration, land3, carrier3 (3 processes)"
mkdir -p g80 g3; cp gen.py g80/; cp gen3.py g3/
( cd g80 && ../runone.sh gen80 "$PY" -B gen.py 80 ) &
( cd g3  && ../runone.sh gen3  "$PY" -B gen3.py ) &
( ./runone.sh land3 "$PY" -B land3.py 3 ) &
wait
for p in "g80/data80.txt data80.txt" "g80/gens.txt gens.txt" "g3/data3.txt data3.txt"; do set -- $p; cmp -s "$1" "$2" && echo "IDENTICAL $2" || echo "DIFFERENT $2"; done > "$LOG/gen_cmp.log"
$TMO nice -n 10 "$PY" -B carrier3.py data80.txt > "$LOG/carrier3.out" 2> "$LOG/carrier3.err"
echo "== 2. compile"
cc -O2 -o s6x s6x.c 2> "$LOG/cc_s6x.log" || { echo "cc s6x failed"; exit 1; }
cc -O2 -o k3 k3.c 2> "$LOG/cc_k3.log" || { echo "cc k3 failed"; exit 1; }
echo "== 3. kills and controls, both implementations (3 lanes)"
reps() { seq -s, "$1" "$2" 158; }
: > jobs.txt
# implementation A (s6x): args  data dimA dimB s lim [rep list] [RT]   (RT = 8: exact refinement over all 161,420 third flats for relaxed rank 8)
for c in $(seq 0 23); do echo "A_664_c$c ./s6x data80.txt 6 6 4 80 $(reps $c 24) 8" >> jobs.txt; done
echo "A_ctl77 ./s6x data80.txt 7 7 0 76" >> jobs.txt
for c in 0 1 2; do echo "A_662_c$c ./s6x data80.txt 6 6 2 78 $(reps $c 3)" >> jobs.txt; done
echo "A_740 ./s6x data80.txt 7 4 0 80" >> jobs.txt
echo "A_660 ./s6x data80.txt 6 6 0 76" >> jobs.txt
# implementation B (k3): args  data A B s lim chunk nchunk [refine]
for c in 0 1 2 3; do echo "B_664_c$c ./k3 data3.txt 6 6 4 80 $c 4 1" >> jobs.txt; done
echo "B_ctl77 ./k3 data3.txt 7 7 0 76 0 1" >> jobs.txt
for c in 0 1; do echo "B_662_c$c ./k3 data3.txt 6 6 2 78 $c 2" >> jobs.txt; done
echo "B_740 ./k3 data3.txt 7 4 0 80 0 1" >> jobs.txt
echo "B_660 ./k3 data3.txt 6 6 0 76 0 1" >> jobs.txt
# three fixed lanes (jobs dealt round-robin), each lane runs its jobs one after the other: at most 3 processes at a time
for k in 0 1 2; do awk -v k=$k 'NR % 3 == k' jobs.txt > lane$k.txt; done
for k in 0 1 2; do ( while read -r line; do ./runone.sh $line; done < lane$k.txt ) & done
wait
echo "== 4. assertions (check_logs.py)"
"$PY" -B "$HERE/checks/check_logs.py" "$LOG" | tee -a "$OUT/all.out" | sed 's/^/   /'
npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out")
echo "== done in $((SECONDS - T0))s: $npass PASS, $nfail FAIL; logs in $OUT"
[ "$nfail" = 0 ] && { echo "PASS: all assertions hold"; exit 0; }
echo "FAIL"; exit 1
