#!/bin/bash
# usage: drat1.sh SCRIPT args... -- regenerates the CNF (last arg = cnf path, no 'solve'), runs kissat --no-binary with proof, then drat-trim; prints one line.
P=/Users/mason/repo_clones/intmult-work/venv/bin/python; DT=/Users/mason/repo_clones/intmult-work/tools_ext/drat-trim/drat-trim
cd /Users/mason/repo_clones/intmult-work/cards/STRAYS-H10
cnf="${@: -1}"; $P "$@" > /dev/null || { echo "$* GENFAIL"; exit; }
r=$(timeout 2400 kissat -q --no-binary "$cnf" "$cnf.drat" | head -1)
if [[ "$r" == *UNSAT* ]]; then v=$($DT "$cnf" "$cnf.drat" -t 3000 2>&1 | grep -a -m1 -o 'NOT VERIFIED\|VERIFIED\|TIMEOUT'); else v="-"; fi
echo "$* : $r : drat $v"; rm -f "$cnf" "$cnf.drat"
