#!/usr/bin/env bash
# One-command verification of research/overcomplete-and-realisation-floors (no kappa claim): exact recomputation of every CHECKED item of the README --
#   c1 Lemma OC instances and the D5 floor data; c2 the 6,728-term decoder of the 120-line frame unit (cost 72); c3 the frame-intersection
#   certificate on nine units and the P104 / P112 pair-rank tables; c4 the E6 deficient-direction tables and the exhaustive search over 5,504,660
#   seven-sets; c5 the decoders attaining the floors; c6 regeneration of all 1,473 SAT instances, hash comparison, model and DRAT re-checks.
# Step 0 checks the package against MANIFEST.sha256 and every pin of SOURCES.json and stops hard on any mismatch.
# Single process at a time; standard library Python only.  drat-trim is optional (DRAT_TRIM=/path, or `drat-trim` on PATH, or buildable with `cc`
# from the vendored sibling package research/p111-minrank-proof-reconciliation/vendor/drat-trim/drat-trim.c); without it the DRAT re-check is a SKIP line.
#   usage: bash verify.sh [/fresh/output/dir]     (inside a checkout or `git archive` of the repository)
#   set PYTHON to choose the interpreter (>= 3.11); KISSAT_RESOLVE=n re-solves n shared-B instances (needs kissat and drat-trim).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/overcomplete-and-realisation-floors.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1
T0=$SECONDS
echo "== 0. manifest and provenance"
if ! "$PY" -B "$HERE/scripts/provenance.py" | tee "$OUT/provenance.log" | sed 's/^/   /' || grep -q '^FAIL' "$OUT/provenance.log" \
   || [ "$(grep -c '^PASS' "$OUT/provenance.log")" != 2 ]; then
  echo "step 0 FAILED"; exit 1
fi
if [ -z "${DRAT_TRIM:-}" ] && ! command -v drat-trim >/dev/null 2>&1; then
  SRC="$HERE/../p111-minrank-proof-reconciliation/vendor/drat-trim/drat-trim.c"
  if [ -f "$SRC" ] && command -v cc >/dev/null 2>&1 && cc -O2 -o "$OUT/drat-trim" "$SRC" >/dev/null 2>&1; then export DRAT_TRIM="$OUT/drat-trim"; echo "   built drat-trim from the vendored source"; fi
fi
mkdir -p "$OUT/logs"; : > "$OUT/all.out"
run() {  # name script
  echo "== $1"
  ( cd "$HERE/checks" && "$PY" -B "$2" > "$OUT/logs/$2.log" 2>&1; echo $? > "$OUT/logs/$2.rc" )
  cat "$OUT/logs/$2.log" | tee -a "$OUT/all.out" | sed 's/^/   /'
  [ "$(cat "$OUT/logs/$2.rc")" = 0 ] || echo "FAIL $2 exit status $(cat "$OUT/logs/$2.rc")" | tee -a "$OUT/all.out"
}
run "c1 Lemma OC instances, D5 data and floor core" c1_overcomplete_d5.py
run "c2 free terms: the 120-line frame unit has a decoder of cost 72" c2_free_terms_frame120.py
run "c3 frame-intersection certificate and realisation-free floors" c3_realisation_free_floors.py
run "c4 E6: deficient directions, pair ranks, exhaustive seven-term search" c4_e6_overcomplete.py
run "c5 decoders attaining the floors" c5_known_decoders.py
run "c6 SAT / DRAT replay" c6_sat_replay.py
npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out"); nskip=$(grep -c '^SKIP' "$OUT/all.out")
EXPECT=$((55 - nskip))
echo "== done in $((SECONDS - T0))s: $((npass + 2)) PASS (2 in step 0), $nskip SKIP, $nfail FAIL; logs in $OUT"
[ "$nfail" = 0 ] && [ "$npass" = "$EXPECT" ] || { echo "FAILED: expected $EXPECT assertion PASS lines after step 0, got $npass PASS / $nfail FAIL / $nskip SKIP"; exit 1; }
