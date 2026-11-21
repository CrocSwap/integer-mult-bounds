#!/bin/bash
cd <research-tree>/lean/decoder-duality
for h in 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19; do
  echo "h=$h"; bash ../../cards/WILD/LEANCERT/runlean.sh Nov15/PriceHI$h.lean .lake/build/lib/lean/Nov15/PriceHI$h.olean; head -3 <tmpdir> -c1-200
done
