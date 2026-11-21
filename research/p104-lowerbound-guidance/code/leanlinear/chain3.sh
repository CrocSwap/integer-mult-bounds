#!/bin/bash
D=code/leanlinear
OL=<research-tree>/lean/decoder-duality/.lake/build/lib/lean/Nov15
$D/b.sh Nov15/LinFinal.lean $OL/LinFinal.olean
$D/b.sh Nov15/LinToy.lean
$D/b.sh Nov15/LinP104.lean
