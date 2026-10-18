#!/usr/bin/env bash
# Verification of research/one-sided-decoders-all-m (no kappa claim).   usage: bash verify.sh [/fresh/output/dir]
# Needs: Python >= 3.11 with numpy, scipy, sympy (PYTHON=/path/to/python to choose), and a C compiler `cc`.  No SAT solver.
# Every exact check of the README is re-run here (about 12-15 minutes on a laptop with two processes; nice 10).  Nothing is skipped: the
# only things taken on trust are the CONDITIONAL [verify] inputs listed in README section 2 (they are cited, not computed here).
#   0  MANIFEST.sha256
#   1  geometry and tables:  data.json regenerated and compared; labels; g(5..8); weight-8 hyperplanes; direction lists; flats of the root system;
#      cover facts (cover.py is the slow one, ~6 min)
#   2  the ε-free theorem:  DP, multiset enumeration, LP with exact integer dual certificates (lp3.py) and the independent symmetrised LP (symlp.py)
#   3  Theorem U' / cost-65 / cost-66 classification inputs: eq, eq2, land, c65, c66, coloop, coloop2, rootswap (+ independent audit)
#   4  Lemma N: exact counts (ncount, ncount2), upper bound over |L| <= 4 (mu76) and an independent implementation (lnprep + lemmaN.c)
#   5  check_logs.py: every assertion of the README as a PASS/FAIL line
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/one-sided.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1
TMO=""; command -v timeout >/dev/null 2>&1 && TMO="timeout 1500"; command -v gtimeout >/dev/null 2>&1 && TMO="gtimeout 1500"
W="$OUT/work"; LOG="$OUT/logs"; mkdir -p "$W" "$LOG"; : > "$OUT/all.out"; T0=$SECONDS
echo "== 0. manifest"
"$PY" -B "$HERE/checks/manifest_check.py" | tee -a "$OUT/all.out" | sed 's/^/   /'; grep -q '^FAIL' "$OUT/all.out" && { echo "step 0 FAILED"; exit 1; }
cp "$HERE"/checks/*.py "$HERE"/checks/*.c "$HERE"/data/* "$W"/
cd "$W"
# run NAME CMD...  (cwd = work dir, log -> logs/NAME.log, nice 10)
run() { local n=$1; shift; local s=$SECONDS; $TMO nice -n 10 "$@" > "$LOG/$n.log" 2>&1; local rc=$?; echo "ran $n rc=$rc in $((SECONDS - s))s" >> "$OUT/times.out"; return 0; }
echo "== 1-4. computations (two parallel streams, at most 2 processes)"
streamA() {
  mkdir -p gen && ( cd gen && cp ../*.py ../*.json . && "$PY" -B dump.py > "$LOG/dump.log" 2>&1 && cmp data.json ../data.json && echo "data.json regenerated: identical" >> "$LOG/dump.log" )
  run chk1 "$PY" -B chk1.py; run w8 "$PY" -B w8.py; run g78 "$PY" -B g78.py; run flats_classify "$PY" -B flats_classify.py
  run dp3 "$PY" -B dp3.py P112
  for d in 1 2 3 4 5 6 7 8; do run enum_$d "$PY" -B enum.py $d $((8*d)); done
  run lp2 "$PY" -B lp2.py; run lp3 "$PY" -B lp3.py; run symlp "$PY" -B symlp.py
  run eq "$PY" -B eq.py; run eq2 "$PY" -B eq2.py 2 6,7,8; run land "$PY" -B land.py 2 1,2,3,4,5,6,7,8
  run c65 "$PY" -B c65.py; run c66 "$PY" -B c66.py; run coloop "$PY" -B coloop.py; run coloop2 "$PY" -B coloop2.py
  run rootswap "$PY" -B rootswap.py; run rootswap_audit "$PY" -B rootswap_audit.py
  run symcheck "$PY" -B symcheck.py; run d7 "$PY" -B d7.py; run gT "$PY" -B gT.py; run cover6 "$PY" -B cover6.py
  run gsmall "$PY" -B gsmall.py
}
streamB() {
  run cover "$PY" -B cover.py; run cover761 "$PY" -B cover761.py
  for p in ncount ncount2 mu76 lemmaN; do cc -O2 -o "$p" "$p.c" 2> "$LOG/cc_$p.log" || echo "cc failed for $p" >> "$LOG/cc_$p.log"; done
  run lnprep "$PY" -B lnprep.py
  run lemmaN ./lemmaN; run ncount ./ncount; run mu76 ./mu76; run ncount2 ./ncount2
}
# targets*.txt / labs.txt are written by gen_targets.py / gen_t3.py (stream A) and read by ncount*/mu76/coloop/rootswap: generate them first, serially
run gen_targets "$PY" -B gen_targets.py; run gen_t3_76 "$PY" -B gen_t3.py 76
streamA & PA=$!
streamB & PB=$!
wait $PA; wait $PB
cat "$OUT/times.out" | sed 's/^/   /'
echo "== 5. assertions (check_logs.py)"
"$PY" -B "$HERE/checks/check_logs.py" "$LOG" | tee -a "$OUT/all.out" | sed 's/^/   /'
npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out")
echo "== done in $((SECONDS - T0))s: $npass PASS, $nfail FAIL; logs in $OUT"
[ "$nfail" = 0 ] && { echo "PASS: all assertions hold"; exit 0; }
echo "FAIL"; exit 1
