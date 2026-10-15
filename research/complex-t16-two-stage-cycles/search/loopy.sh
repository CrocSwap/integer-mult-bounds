#!/bin/bash
# Improvement loop of the fourth version (portable copy of the session's loopY.sh). Same as loopx.sh except the
# neighbourhood mode mix, which now includes the evac mode of lns.py (stranded cap-48 bins plus bins whose windows
# contain some of their calls, re-packed exactly; env NB = neighbourhood size, default 200). It alternates chain2.py
# (ejection cycles, depth 8) while it finds a strictly improving step with one CP-SAT plateau step of lns.py
# (DIV=1) on a random mode (evac, time, f3, early15). It keeps only the current map and the best one by exact
# kappa (score.py, compared as Decimal), and writes every new best as DIR/k_<kappa>.OWNERS.json.gz. Finite heuristic; no optimum.
# usage: search/loopy.sh DIR START_OWNERS NW SEED [MAXN]
#   NW = CP-SAT workers per lns.py solve; MAXN = steps (default 100000, stop by hand).
#   env RUN: optional command prefix, e.g. a memory-capped systemd scope (the session used MemoryMax=4G).
# Needs uv, CPython 3.12, numpy and ortools. Run from the repository root (lib.py reads the selected data there).
H=$(cd "$(dirname "$0")" && pwd)
D=$1; cur=$2; NW=$3; SEED=$4; MAXN=${5:-100000}; mkdir -p "$D"
PY="uv run -q --no-project --python 3.12 --with numpy --with ortools python -I"
bestk=$($RUN $PY "$H/score.py" "$H" "$cur" | awk '{print $2}')
cp "$cur" "$D/best.OWNERS.json.gz"; cp "$cur" "$D/cur.OWNERS.json.gz"; cur=$D/cur.OWNERS.json.gz
echo "start $bestk"
RANDOM=$SEED; n=0
gt() { python3 -c "import sys; from decimal import Decimal as D; sys.exit(0 if D('$1') > D('$2') else 1)"; }
newcur() { mv "$1" "$D/cur.OWNERS.json.gz"; k=$2
  if [ -n "$k" ] && gt "$k" "$bestk"; then bestk=$k; cp "$D/cur.OWNERS.json.gz" "$D/best.OWNERS.json.gz"
    cp "$D/cur.OWNERS.json.gz" "$D/k_$k.OWNERS.json.gz"; echo "$(date +%T) NEW BEST $k step $n"; fi; }
while [ $n -lt "$MAXN" ]; do
  n=$((n+1))
  out=$($RUN $PY "$H/chain2.py" "$H" "$cur" "$D/t" 8 2>&1 | tail -1)
  if [ -f "$D/t.OWNERS.json.gz" ]; then k=$(echo "$out" | grep -o 'kappa [0-9.]*' | awk '{print $2}')
    echo "$(date +%T) chain2 $n $(echo "$out" | grep -o 'idle.*')"; newcur "$D/t.OWNERS.json.gz" "$k"; continue; fi
  n=$((n+1)); modes=("evac" "evac" "time" "time" "f3" "f3" "evac" "early15" "time" "f3"); md=${modes[$((RANDOM % 10))]}
  r=$(NB=${NB:-200} NW=$NW DIV=1 TL2=40 $RUN $PY "$H/lns.py" "$H" "$cur" "$D/t" 1 $((SEED*100000+n+RANDOM)) 60 "$md" 2>&1 | grep "^it")
  k=$(echo "$r" | grep -o 'kappa [0-9.]*' | awk '{print $2}')
  [ -f "$D/t.OWNERS.json.gz" ] && newcur "$D/t.OWNERS.json.gz" "$k"
  echo "$(date +%T) div $n $md $(echo "$r" | grep -o "status.*" | cut -c1-50) k=$k"
done
