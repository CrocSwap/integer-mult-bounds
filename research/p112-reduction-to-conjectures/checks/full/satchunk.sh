#!/usr/bin/env bash
# usage: satchunk.sh WORKDIR NAME EXPECT(UNSAT|SAT) GENERATOR-CMD...   (generator must write WORKDIR/NAME.cnf)
# regenerates the CNF, runs kissat with a DRAT proof (UNSAT) and verifies it with drat-trim; prints one result line.
W=$1; N=$2; EXP=$3; shift 3
DT="${DRAT_TRIM:-drat-trim}"; mkdir -p "$W"; cd "$W" || exit 2
"$@" > "$N.gen.log" 2>&1 || { echo "GENFAIL $N"; exit 1; }
if [ "$EXP" = UNSAT ]; then
  kissat -q "$N.cnf" "$N.drat" > "$N.sat.log" 2>&1
  grep -q '^s UNSATISFIABLE' "$N.sat.log" || { echo "CHUNKFAIL $N expected UNSAT"; exit 1; }
  "$DT" "$N.cnf" "$N.drat" > "$N.chk.log" 2>&1
  grep -q 's VERIFIED' "$N.chk.log" && echo "CHUNK-OK $N UNSAT DRAT-VERIFIED" || { echo "CHUNKFAIL $N drat"; exit 1; }
  rm -f "$N.drat"
else
  kissat -q "$N.cnf" > "$N.sat.log" 2>&1
  grep -q '^s SATISFIABLE' "$N.sat.log" && echo "CHUNK-OK $N SAT (control)" || { echo "CHUNKFAIL $N expected SAT"; exit 1; }
fi
rm -f "$N.cnf"
