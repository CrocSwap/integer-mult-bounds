#!/bin/bash
# drat1b.sh = drat1.sh with the 20-min hard cap (Mason, Oct 15); usage: drat1b.sh SCRIPT args... -- regenerates the CNF (last arg = cnf path, no 'solve'), runs kissat --no-binary with proof, then drat-trim; prints one line.
P=/Users/mason/repo_clones/intmult-work/venv/bin/python; DT=/Users/mason/repo_clones/intmult-work/tools_ext/drat-trim/drat-trim
cd /Users/mason/repo_clones/intmult-work/cards/STRAYS-H10
cnf="${@: -1}"; $P "$@" > /dev/null || { echo "$* GENFAIL"; exit; }
r=$(timeout 1200 kissat -q --no-binary "$cnf" "$cnf.drat" | head -1)
if [[ "$r" == *UNSAT* ]]; then v=$($DT "$cnf" "$cnf.drat" -t 1200 2>&1 | grep -a -m1 -o 'NOT VERIFIED\|VERIFIED\|TIMEOUT'); else v="-"; fi
echo "$* : $r : drat $v"; rm -f "$cnf" "$cnf.drat"
