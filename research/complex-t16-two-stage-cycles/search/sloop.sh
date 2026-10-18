#!/bin/bash
# Improvement loop of the fifth version (portable copy of the session's sloop.sh / sloop2.sh; sloop2.sh only made the
# CP-SAT worker count of the realisation step an env setting, NW2). Each step:
#  1. winlp.py ip: re-solve the class-level model (pattern counts and flows per (capacity, window) class, R4
#     aggregate cuts) warm-started from the current map, with a random subset of 12, 18 or 24 classes free (drawn
#     from the classes that differ from TARGET, a full-model optimum JSON) and all others fixed; change penalty
#     PEN=1000, minimum surrogate gain GAIN=1;
#  2. lns2.py guide: realise that class target on concrete bins by two CP-SAT neighbourhood solves around the bins
#     whose class (call, width) count or pattern count must drop, maximising the surrogate exactly; a result is kept
#     only if the exact kappa rises (Decimal comparison).
# Finite heuristic; no optimum. Every new best is written as DIR/k_<step>.OWNERS.json.gz.
# usage: search/sloop.sh DIR START_OWNERS TARGET_JSON SEED ITERS
#   env RUN: optional command prefix, e.g. a memory-capped systemd scope (the session used MemoryMax=5G);
#   env NW2: CP-SAT workers of the realisation step (default 2).
# Needs uv, CPython 3.12, numpy, scipy and ortools. Run from the repository root (lib.py reads the selected data there).
H=$(cd "$(dirname "$0")" && pwd)
D=$1; mkdir -p "$D"; [ -f "$D/best.OWNERS.json.gz" ] || cp "$2" "$D/best.OWNERS.json.gz"
export OMP_NUM_THREADS=1
PY="uv run -q --no-project --python 3.12 --with numpy --with scipy --with ortools python -I"
for n in $(seq 1 "$5"); do
  sd=$(( $4*1000+n )); fr=$(( 12 + sd % 3 * 6 ))
  FREE=$fr SEED=$sd FREEFROM=$3 PEN=1000 GAIN=1 $RUN $PY "$H/winlp.py" "$H" "$D/best.OWNERS.json.gz" ip 120 1 2 "$D/s1.json" > "$D/s1.log" 2>&1
  st=$(grep -E "^(FEASIBLE|OPTIMAL|INFEASIBLE|UNKNOWN)" "$D/s1.log" | cut -c1-60)
  if ! echo "$st" | grep -qE "^(FEASIBLE|OPTIMAL)"; then echo "$(date +%T) $n s1 $st"; continue; fi
  GUIDE=$D/s1.json GFRAC=1 GMUL=2 NW=${NW2:-2} DIV=0 TL2=30 $RUN $PY "$H/lns2.py" "$H" "$D/best.OWNERS.json.gz" "$D/t" 2 $sd 150 guide 2>&1 \
    | grep -E "^it|^guide" | cut -c1-260 | sed "s/^/$(date +%T) $n [$st] /"
  [ -f "$D/t.OWNERS.json.gz" ] && mv "$D/t.OWNERS.json.gz" "$D/best.OWNERS.json.gz" && cp "$D/best.OWNERS.json.gz" "$D/k_$n.OWNERS.json.gz"
done
