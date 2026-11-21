#!/bin/bash
# OPTIONAL (not run by verify.py or check.py): regenerate and re-check DRAT proofs of cubes.
# Needs: python3, kissat (we used 4.0.4) and drat-trim on PATH (or KISSAT=... DRAT_TRIM=...). Proofs are large (up to ~3 GB
# binary DRAT for the hardest cubes, tens of GB over all 1001 cubes); each proof is deleted after checking.
# Usage: ./run_drat.sh ID [ID ...]      cubes from cubes.txt, e.g.  ./run_drat.sh i3 f33 j8_6
#        ./run_drat.sh all              every cube (days of CPU; run in pieces)
# Env:   WORK=dir for CNF/proof scratch (default: a fresh mktemp dir), TIME=kissat seconds (default 1200).
# Per cube it prints: id, cnf sha256 check against hashes.tsv, kissat verdict, drat-trim verdict.
set -u
cd "$(dirname "$0")"
KISSAT=${KISSAT:-kissat}; DRAT_TRIM=${DRAT_TRIM:-drat-trim}; TIME=${TIME:-1200}
command -v "$KISSAT" >/dev/null || { echo "kissat not found"; exit 2; }
command -v "$DRAT_TRIM" >/dev/null || { echo "drat-trim not found"; exit 2; }
WORK=${WORK:-$(mktemp -d)}; mkdir -p "$WORK"
sha() { if command -v sha256sum >/dev/null; then sha256sum "$1" | cut -d' ' -f1; else shasum -a 256 "$1" | cut -d' ' -f1; fi; }
if [ "${1:-}" = "all" ]; then set -- $(grep -v '^#' cubes.txt | cut -f1); fi
[ $# -gt 0 ] || { sed -n 2,10p "$0"; exit 2; }
fail=0
for id in "$@"; do
  cnf="$WORK/$id.cnf"; prf="$WORK/$id.drat"
  python3 -B gen.py cube "$id" "$cnf" || { echo "$id GENFAIL"; fail=1; continue; }
  want=$(awk -F'\t' -v i="$id" '$1==i{print $2}' hashes.tsv)
  got=$(sha "$cnf")
  [ "$got" = "$want" ] && hs=HASH_OK || { hs=HASH_MISMATCH; fail=1; }
  "$KISSAT" --time="$TIME" -q "$cnf" "$prf" > "$WORK/$id.kout" 2>&1
  st=$(grep '^s ' "$WORK/$id.kout" | cut -c3-)
  if [ "$st" = "UNSATISFIABLE" ]; then
    "$DRAT_TRIM" "$cnf" "$prf" -t 40000 > "$WORK/$id.dlog" 2>&1
    if grep -aq 's NOT VERIFIED' "$WORK/$id.dlog"; then v=NOT_VERIFIED; fail=1
    elif grep -aq 's VERIFIED' "$WORK/$id.dlog"; then v=VERIFIED
    else v=NO_VERDICT; fail=1; fi
  else v=SKIPPED; fail=1; fi
  echo "$id $hs $st $v"
  rm -f "$prf" "$cnf" "$WORK/$id.kout" "$WORK/$id.dlog"
done
exit $fail
