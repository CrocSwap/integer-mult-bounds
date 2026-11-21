#!/bin/bash
D=code/leanlinear
OL=<research-tree>/lean/decoder-duality/.lake/build/lib/lean/Nov15
$D/b.sh Nov15/LinP104Base.lean $OL/LinP104Base.olean
for k in 0 1 2 3 4 5 6 7; do
  $D/b.sh Nov15/LinP104Pat$k.lean $OL/LinP104Pat$k.olean
done
$D/b.sh Nov15/LinP104Fin.lean
