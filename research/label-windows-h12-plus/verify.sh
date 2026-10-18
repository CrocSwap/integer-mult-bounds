#!/usr/bin/env bash
# Verification of research/label-windows-h12-plus (no kappa claim).   usage: bash verify.sh [/fresh/output/dir]      FULL=1 bash verify.sh ... for the long runs
# Step 0  MANIFEST.sha256 + SOURCES.json pins (hard stop).
# Step 1  c1  Lemma C on all 144 exceptional pairs (clique inside R cap A, identity pattern, random fittings; omega recomputed in pure Python).
# Step 2  c2  census min omega = 5 over all 20,721,360 pairs: cen.cpp in full; mc.cpp (independent exact clique) on reps 43-46 + a stride sample (FULL=1: all pairs).
# Step 3  c3  Aut order, sections preserved, the 6 exceptional orbits = the 6 queried pairs (pynauty, optional; FULL=1 adds the 440,880-section orbit cover).
# Step 4  c4  networkx omega on the 144 exceptional pairs + random sample (optional).
# Step 5  c5  break-even table and the closure arithmetic under the INHERITED pricing model; X(112,40,h) for h = 15..200.
# Step 6  c6  accounting of the shipped SAT logs (re-runs nothing).
# Step 7  SAT regenerate CNFs with sat/hk3.py and re-solve with kissat 4.0.4 + drat-trim: 14-query sample (default, about a minute) or all 757 queries (FULL=1,
#         two chains, nice 10, per-query timeouts 1200 s kissat / 1500 s drat-trim; about 1.5-2 h).   c7 compares CNF sha256 with the shipped record.
# Step 8  c8  the cited #1212 Theorem 1 text is present in the repository tree.
# Python >= 3.11 with numpy (required); pynauty / networkx optional; a C++ compiler for c2; kissat and drat-trim for step 7 (KISSAT=, DRAT_TRIM=).  Never CaDiCaL.
# At most two processes at a time, all heavy ones under nice -n 10 and timeout; no unbounded wait loops.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/label-windows-h12-plus.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1; export PYTHON="$PY"
KS="${KISSAT:-kissat}"; DT="${DRAT_TRIM:-drat-trim}"; export KISSAT="$KS" DRAT_TRIM="$DT"; FULL=${FULL:-0}; export FULL
T0=$SECONDS
echo "== 0. manifest and provenance"
if ! "$PY" -B "$HERE/scripts/provenance.py" | tee "$OUT/provenance.log" | sed 's/^/   /' || grep -q '^FAIL' "$OUT/provenance.log" \
   || [ "$(grep -c '^PASS' "$OUT/provenance.log")" != 2 ]; then echo "step 0 FAILED"; exit 1; fi
echo "   tools: kissat=$(command -v "$KS" 2>/dev/null || echo none)  drat-trim=$(command -v "$DT" 2>/dev/null || echo none)  FULL=$FULL"
mkdir -p "$OUT/logs" "$OUT/work"; : > "$OUT/all.out"; export WORK="$OUT/work"
run() { echo "== $1"; ( cd "$HERE/checks" && timeout 3600 nice -n 10 "$PY" -B "$2" ${3:-} > "$OUT/logs/$2.log" 2>&1; echo $? > "$OUT/logs/$2.rc" )
  tee -a "$OUT/all.out" < "$OUT/logs/$2.log" | sed 's/^/   /'
  [ "$(cat "$OUT/logs/$2.rc")" = 0 ] || echo "FAIL $2 exit status $(cat "$OUT/logs/$2.rc")" | tee -a "$OUT/all.out"; }
run "c1 Lemma C on the 144 exceptional pairs" c1_lemma.py
run "c2 census (cen.cpp full, mc.cpp)" c2_census.py
run "c3 orbits (pynauty)" c3_orbits.py
run "c4 networkx omega" c4_networkx.py
run "c5 pricing arithmetic (inherited model)" c5_pricing.py
run "c6 accounting of the shipped SAT logs" c6_sat_logs.py
echo "== 7. SAT: regenerate CNFs, kissat 4.0.4, drat-trim"
if ! command -v "$KS" >/dev/null 2>&1 || ! command -v "$DT" >/dev/null 2>&1 || ! "$PY" -c "import networkx, numpy" >/dev/null 2>&1; then
  echo "SKIP c7.a  kissat, drat-trim or networkx (needed by sat/hk3.py) not found" | tee -a "$OUT/all.out"; echo "SKIP c7.b  kissat, drat-trim or networkx not found" | tee -a "$OUT/all.out"
else
  export PYTHON="$PY"
  if [ "$FULL" = 1 ]; then
    { cat "$HERE/sat/jobs61.txt"; awk 'NR%2==1' "$HERE/sat/jobs696.txt"; } > "$OUT/jobsA.txt"; awk 'NR%2==0' "$HERE/sat/jobs696.txt" > "$OUT/jobsB.txt"
    WORK="$OUT/work/A" nice -n 10 bash "$HERE/sat/chain.sh" "$OUT/jobsA.txt" "$OUT/chainA.log" > /dev/null 2>&1 &
    WORK="$OUT/work/B" nice -n 10 bash "$HERE/sat/chain.sh" "$OUT/jobsB.txt" "$OUT/chainB.log" > /dev/null 2>&1 &
    wait; cat "$OUT/chainA.log" "$OUT/chainB.log" > "$OUT/sat.log"; MODE=full
  else
    # sample: 8 of the 61 (h = 12, 13 and 14 queries) and 6 of the 696; each solved within seconds
    cat > "$OUT/sample.txt" <<'EOS'
RREF=1,ORTH=1,GAUGE=RA 12 0 6 4 X
RREF=1,ORTH=1,GAUGE=RA 12 1 5 4 X
RREF=1,ORTH=1,GAUGE=RA 12 2 4 4 X
RREF=1,ORTH=1,GAUGE=RA 12 0 6 0 X
RREF=1,ORTH=1,GAUGE=RA 12 6 0 5 X
RREF=1,ORTH=1,GAUGE=RA 13 0 8 4 X
RREF=1,ORTH=1,GAUGE=RA 13 1 7 4 X
RREF=1,ORTH=1,GAUGE=RA 14 0 9 4 X
RREF=1,ORTH=1,GAUGE=A 12 0 7 10 P46
RREF=1,ORTH=1,GAUGE=A 12 0 7 101 P46
RREF=1,ORTH=1,GAUGE=A 12 0 7 103 P46
RREF=1,ORTH=1,GAUGE=A 12 0 7 105 P46
RREF=1,ORTH=1,GAUGE=RA 12 7 0 3 P46
RREF=1,ORTH=1,GAUGE=RA 12 7 0 0 P46
EOS
    bash "$HERE/sat/chain.sh" "$OUT/sample.txt" "$OUT/sat.log" > /dev/null 2>&1; MODE=sample
  fi
  ( cd "$HERE/checks" && "$PY" -B c7_sat_compare.py "$OUT/sat.log" $MODE > "$OUT/logs/c7.log" 2>&1; echo $? > "$OUT/logs/c7.rc" )
  tee -a "$OUT/all.out" < "$OUT/logs/c7.log" | sed 's/^/   /'
fi
run "c8 cited #1212 Theorem 1 text" c8_cited.py
npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out"); nskip=$(grep -c '^SKIP' "$OUT/all.out")
EXPECT=$((23 - nskip))
echo "== done in $((SECONDS - T0))s: $((npass + 2)) PASS (2 in step 0), $nskip SKIP, $nfail FAIL; logs in $OUT"
if [ "$nfail" = 0 ] && [ "$npass" = "$EXPECT" ]; then echo "PASS: all expected assertions hold"; exit 0; fi
echo "FAIL: expected $EXPECT assertion PASS lines after step 0, got $npass PASS / $nfail FAIL / $nskip SKIP"; exit 1
