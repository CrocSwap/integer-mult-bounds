#!/bin/bash
cd <research-tree>/lean/decoder-duality
B=.lake/build/lib/lean/Nov15
for h in "$@"; do
 for f in Nov15/PriceHK${h}_*.lean; do
  n=$(basename $f .lean); echo "== $n"
  bash ../../cards/WILD/LEANCERT/runlean.sh $f $B/$n.olean 2>&1 | tail -4
  cat <tmpdir> | head -5
 done
 echo "== PriceHK$h"
 bash ../../cards/WILD/LEANCERT/runlean.sh Nov15/PriceHK$h.lean $B/PriceHK$h.olean 2>&1 | tail -4
 head -8 <tmpdir>
done
