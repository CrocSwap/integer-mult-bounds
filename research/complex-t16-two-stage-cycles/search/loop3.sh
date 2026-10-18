#!/bin/bash
# Improvement loop used for the kappa search (portable copy of the session's loop3.sh; logic unchanged).
# Alternate: chain2.py (one/two-stage ejection cycles, depth D) while it finds a strictly improving step;
# when it finds none, run one CP-SAT plateau-diversification step of lns.py (DIV=1: keep the surrogate
# objective, then randomly maximise relocations) on a random neighbourhood mode, and continue from its output.
# Each accepted map is written as <OUT_PREFIX><n>.OWNERS.json.gz. Finite heuristic; no optimality claim.
# usage: search/loop3.sh START_OWNERS OUT_PREFIX     env: D (default 8), MAXN (default 200 steps),
#        RUN (optional command prefix, e.g. a memory-capped systemd scope; the session used MemoryMax=4G)
# Needs uv, CPython 3.12, numpy and ortools. Run from the repository root (lib.py reads the selected data there).
H=$(cd "$(dirname "$0")" && pwd)
cur=$1; P=$2; n=0; D=${D:-8}; MAXN=${MAXN:-200}
while [ $n -lt $MAXN ]; do
  n=$((n+1))
  out=$($RUN uv run -q --no-project --python 3.12 --with numpy python -I "$H/chain2.py" "$H" "$cur" "$P$n" "$D" 2>&1 | tail -1)
  if [ -f "$P$n.OWNERS.json.gz" ]; then cur=$P$n.OWNERS.json.gz; echo "chain2 $n $(echo "$out" | grep -o 'idle.*')"; continue; fi
  n=$((n+1)); modes=("set:0,1,2,3,4" "early8" "early15" "time" "fam"); md=${modes[$((RANDOM % 5))]}
  r=$(DIV=1 TL2=40 $RUN uv run -q --no-project --python 3.12 --with numpy --with ortools python -I "$H/lns.py" "$H" "$cur" "$P$n" 1 $((n+700+RANDOM)) 60 "$md" 2>&1 | grep "^it" | grep -o "status.*" | cut -c1-60; true)
  [ -f "$P$n.OWNERS.json.gz" ] && cur=$P$n.OWNERS.json.gz
  echo "div $n $md $r -> $cur"
done
