#!/bin/bash
# Guided LNS of the fifth version (portable copy of the session's gloop.sh): repeated lns2.py guide steps toward one
# fixed class-level target GUIDE (a winlp.py ip JSON), each on a random fraction (0.08-0.3) of the differing classes.
# The first fifth-version checkpoint (kappa 0.001673373170972473) came from this loop; sloop.sh superseded it.
# usage: search/gloop.sh DIR START_OWNERS GUIDE_JSON NW SEED ITERS     (env RUN: optional command prefix)
# Needs uv, CPython 3.12, numpy and ortools. Run from the repository root.
H=$(cd "$(dirname "$0")" && pwd)
D=$1; mkdir -p "$D"; cp "$2" "$D/best.OWNERS.json.gz"; export OMP_NUM_THREADS=1
PY="uv run -q --no-project --python 3.12 --with numpy --with ortools python -I"
for n in $(seq 1 "$6"); do
  fr=$(python3 -c "import random; random.seed($5*1000+$n); print(random.choice([0.08,0.12,0.15,0.2,0.3]))")
  GUIDE=$3 GFRAC=$fr GMUL=2 NW=$4 DIV=0 TL2=30 $RUN $PY "$H/lns2.py" "$H" "$D/best.OWNERS.json.gz" "$D/t" 2 $(( $5*1000+n )) 120 guide 2>&1 \
    | grep -E "^it|^final" | cut -c1-330 | sed "s/^/$(date +%T) fr=$fr /"
  [ -f "$D/t.OWNERS.json.gz" ] && mv "$D/t.OWNERS.json.gz" "$D/best.OWNERS.json.gz"
done
