#!/usr/bin/env bash
# Verification of research/a2-family-decoder-floors (no kappa claim).  usage: bash verify.sh [/fresh/output/dir]     (Python >= 3.11, numpy, networkx; PYTHON=/path/to/python)
# One process at a time, no SAT solver.  Everything below is exact (rational arithmetic, F2 ranks) except where a step says "mod p" (ranks mod 2^61-1: lower bounds for the rank over Q, used only in the safe direction).
#   0  MANIFEST.sha256 (pins every shipped file, including the recorded logs)
#   1  units (E8 / P112 / P104, label dimension 9); survivor classes and survivor-pair ranks (inputs_check.py); spans S1, S2 (Theorem G inputs)
#   2  the A2 family: exact members with the iff pattern and rank 9 on all three units; the non-B-form certificate (a2cert.py)
#   3  census facts (A2COST sections 2, 5): unit census on the first triangle of each unit, replayed and compared line-for-line with the recorded logs; all 28 P104 orbit representatives; triangle-orbit counts
#   4  floors: P_k (exact duality B&B on P112 / P104, structural + arithmetic on E8) and the Case I / Case II arithmetic; Case II(b): the merged-class kill fact (mergedkill.py) and the exact class-level
#      min-cost relaxation (iib_check.py), on P112, E8 and all 28 P104 orbit representatives
#   5  sharpness: the tie decoders (64 on P112, 72 on E8), exact over Q, independent evaluator; the tie members are certified non-B-form; exact square optimum at fixed members (generic 65 / tie 64 on P112; 73 / 72 on E8)
#   6  m >= 10, factors in the realisation's spaces: the class-level relaxation (step 4, off the B-locus) and pair-cost tables at the checked members (corroboration)
#   7  recorded HUNT-A2 logs (robust CP-SAT / CEGAR; NOT re-run): headline lines asserted
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/a2fam.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1
C="$HERE/checks"; REC="$HERE/evidence/logs"; W="$OUT/work"; mkdir -p "$W" "$OUT/logs"; : > "$OUT/all.out"
export PYTHONPATH="$C"
T0=$SECONDS
note() { echo "$@" | tee -a "$OUT/all.out"; }
# run NAME UNIT SCRIPT ARGS...   (cwd = work dir; log -> logs/NAME.log; every PASS line is echoed)
run() { local n=$1 u=$2; shift 2; local s=$SECONDS
  ( cd "$W" && UNIT=$u "$PY" -B "$C/$1" "${@:2}" > "$OUT/logs/$n.log" 2>&1 ); local rc=$?
  grep '^PASS' "$OUT/logs/$n.log" | sed 's/^/   /' | tee -a "$OUT/all.out" >/dev/null
  if [ $rc = 0 ]; then note "PASS ran $n (UNIT=$u $1 ${*:2}) in $((SECONDS - s))s"; else note "FAIL ran $n exit $rc"; tail -3 "$OUT/logs/$n.log" | sed 's/^/      /'; fi; }
expectF() { if grep -qF -- "$2" "$OUT/logs/$1.log"; then note "PASS $1: $3"; else note "FAIL $1: expected '$2' ($3)"; fi; }
expect() { if grep -q -- "$2" "$OUT/logs/$1.log"; then note "PASS $1: $3"; else note "FAIL $1: expected '$2' ($3)"; fi; }
echo "== 0. manifest"
if ! "$PY" -B "$C/manifest_check.py" | tee -a "$OUT/all.out" | sed 's/^/   /' || grep -q '^FAIL' "$OUT/all.out"; then echo "step 0 FAILED"; exit 1; fi
echo "== 1. units and span facts"
run units E8 units_check.py
run inputs E8 inputs_check.py
expectF inputs "PASS P112: survivor-pair ranks" "P112: survivor-pair ranks computed and passing"
expectF inputs "] in [8] [8]" "P112: all survivor-pair ranks equal 8"
expectF inputs "PASS P104: survivor-pair ranks" "P104: survivor-pair ranks"
expectF inputs "ALL PASS" "survivors, survivor-pair ranks, 7-cliques on P112 and P104"
run spans E8 spans.py; expect spans "PASS spans E8" "S1 (rank r(O_u) = 7) and S2 (rank r(O_u cap O_u') = 6) on P112, P104, E8"
echo "== 2. the A2 family: exact members, non-B-form certificate"
for U in P112 P104 E8; do
  run a2fam_$U $U a2fam.py; expect a2fam_$U "PASS A2 family on $U" "3 exact rank-9 members with the iff pattern"
  run a2cert_$U $U a2cert.py; [ "$(grep -c '^PASS member\|not of B-form' "$OUT/logs/a2cert_$U.log")" = 3 ] && note "PASS a2cert_$U: 3 members certified not of B-form" || note "FAIL a2cert_$U"
done
echo "== 3. census facts and triangle orbits"
for U in P112 P104 E8; do
  run census_$U $U unitcensus.py; cmp -s "$OUT/logs/census_$U.log" "$REC/census/ucensus_$U.log.txt" && note "PASS census_$U identical to recorded log" || note "FAIL census_$U differs from recorded log"
  "$PY" -B "$C/census_facts.py" "$OUT/logs/census_$U.log" | tee -a "$OUT/all.out" | sed 's/^/   /'
done
REPS="0,3,22 0,5,24 0,60,103 0,61,102 1,3,31 1,5,33 1,44,96 1,45,95 1,46,94 1,47,93 1,49,92 1,50,91 1,51,90 5,44,101 5,45,100 5,48,97 5,53,93 5,56,91 7,44,102 7,46,100 7,48,98 7,52,95 7,54,93 9,44,103 9,47,100 9,49,98 9,50,97 9,53,95"
n=0; bad=0
for T in $REPS; do
  ( cd "$W" && UNIT=P104 A2TRI=$T "$PY" -B "$C/unitcensus.py" > "$OUT/logs/uc104_$T.log" 2>&1 )
  cmp -s "$OUT/logs/uc104_$T.log" "$REC/census/uc104_${T//,/_}.log.txt" || { bad=$((bad+1)); echo "   differs: $T"; }
  "$PY" -B "$C/census_facts.py" "$OUT/logs/uc104_$T.log" > "$OUT/logs/uc104_$T.facts" 2>&1 || { bad=$((bad+1)); echo "   facts fail: $T"; }
  n=$((n+1))
done
[ $bad = 0 ] && note "PASS census on all $n P104 orbit representatives: identical to the recorded logs, same structural facts" || note "FAIL P104 representatives: $bad problems"
run orbits_P112 P112 orbits.py;  expect orbits_P112 "P112 triangles 896 orbits(lower bound on merging) 1 " "all 896 A2 triangles of P112 form one orbit"
run orbits_E8 E8 orbits.py;      expect orbits_E8 "E8 triangles 1120 orbits(lower bound on merging) 1 " "all 1120 A2 triangles of E8 form one orbit"
run orbits_P104 P104 orbits104.py; expect orbits_P104 "triangles 704 orbits 28 " "the 704 A2 triangles of P104 fall into at most 28 orbits"
echo "== 4. floors and the case arithmetic"
for U in P112 P104 E8; do run floors_$U $U floors.py; done
expect floors_P112 "PASS case arithmetic P112: every square decoder of every A2-family member costs >= 64" "P112 >= 64"
expect floors_P104 "PASS case arithmetic P104: every square decoder of every A2-family member costs >= 56" "P104 >= 56"
expect floors_E8 "PASS case arithmetic E8: every square decoder of every A2-family member costs >= 72" "E8 >= 72"
run mk_P104 P104 mergedkill.py; expect mk_P104 "PASS merged-kill P104" "P104 (default triangle): two merged classes are co-killable only on gamma2 = gamma3"
run iib_P104 P104 iib_check.py; expect iib_P104 "PASS II(b) relaxation P104" "P104: II(b) >= 62 off the B-locus (63 on it); m >= 10 off the locus >= 64"
run mk_P112 P112 mergedkill.py; expect mk_P112 "PASS merged-kill P112" "P112: two merged classes are co-killable only on gamma2 = gamma3"
run mk_E8 E8 mergedkill.py;     expect mk_E8 "PASS merged-kill E8" "E8: two merged classes are co-killable only on gamma2 = gamma3"
run iib_P112 P112 iib_check.py; expect iib_P112 "PASS II(b) relaxation P112" "P112: II(b) >= 65 off the B-locus (66 on it); m >= 10 off the locus >= 68"
run iib_E8 E8 iib_check.py;     expect iib_E8 "PASS II(b) relaxation E8" "E8: II(b) >= 74 off the B-locus (75 on it); m >= 10 off the locus >= 77"
bad=0; n=0
for T in $REPS; do
  ( cd "$W" && UNIT=P104 A2TRI=$T "$PY" -B "$C/mergedkill.py" > "$OUT/logs/mk104_$T.log" 2>&1 && UNIT=P104 A2TRI=$T "$PY" -B "$C/iib_check.py" > "$OUT/logs/iib104_$T.log" 2>&1 ) || { bad=$((bad+1)); echo "   fail: $T"; }
  grep -q '^PASS merged-kill' "$OUT/logs/mk104_$T.log" && grep -q '^PASS II(b) relaxation' "$OUT/logs/iib104_$T.log" || bad=$((bad+1))
  n=$((n+1))
done
[ $bad = 0 ] && note "PASS merged-kill fact and II(b)/m>=10 relaxation on all $n P104 orbit representatives (II(b) >= 62 off the B-locus, 63 on it; m >= 10 off the locus >= 64)" || note "FAIL P104 representatives (merged-kill / relaxation): $bad problems"
echo "== 5. sharpness: tie decoders"
for U in P112 E8; do
  run tie_$U $U tie_check.py; expect tie_$U "PASS $U tie decoder: exact cost" "exact tie decoder"
  run tiecert_$U $U a2cert.py tie; expect tiecert_$U "PASS tie-decoder member $U: not of B-form" "the tie member is not of B-form"
done
run opt_P112_gen P112 exact_opt.py gen 70; expect opt_P112_gen "exact square optimum 65$" "P112 generic member: exact square optimum 65"
run opt_P112_tie P112 exact_opt.py tie 70; expect opt_P112_tie "exact square optimum 64$" "P112 tie member: exact square optimum 64"
run opt_E8_gen E8 exact_opt.py gen 80;     expect opt_E8_gen "exact square optimum 73$" "E8 generic member: exact square optimum 73"
run opt_E8_tie E8 exact_opt.py tie 80;     expect opt_E8_tie "exact square optimum 72$" "E8 tie member: exact square optimum 72"
echo "== 6. m >= 10 in the realisation's spaces"
run pt_P112_gen P112 pairtable.py gen 64; expect pt_P112_gen "PASS pair table P112 gen" "P112 generic member: m >= 10 relaxation >= 64"
run pt_P112_tie P112 pairtable.py tie 64; expect pt_P112_tie "PASS pair table P112 tie" "P112 tie member: m >= 10 relaxation >= 64"
run pt_P104_gen P104 pairtable.py gen 64; expect pt_P104_gen "PASS pair table P104 gen" "P104 generic member: m >= 10 relaxation >= 64"
run pt_E8_gen E8 pairtable.py gen 77;     expect pt_E8_gen "PASS pair table E8 gen" "E8 generic member: m >= 10 relaxation >= 77"
run pt_E8_tie E8 pairtable.py tie 77;     expect pt_E8_tie "PASS pair table E8 tie" "E8 tie member: m >= 10 relaxation >= 77"
echo "== 7. recorded logs (not re-run)"
"$PY" -B "$C/log_counts.py" 2>&1 | tee "$OUT/logs/log_counts.log" | sed 's/^/   /'; grep '^PASS\|^FAIL' "$OUT/logs/log_counts.log" >> "$OUT/all.out"
npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out")
echo "== done in $((SECONDS - T0))s: $npass PASS, $nfail FAIL; logs in $OUT"
[ "$nfail" = 0 ] && { echo "PASS: all assertions hold"; exit 0; }
echo "FAIL"; exit 1
