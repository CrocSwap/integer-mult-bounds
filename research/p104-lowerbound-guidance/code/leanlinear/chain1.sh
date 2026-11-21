#!/bin/bash
D=code/leanlinear
OL=<research-tree>/lean/decoder-duality/.lake/build/lib/lean/Nov15
$D/b.sh Nov15/LinRado.lean $OL/LinRado.olean
$D/b.sh Nov15/LinCore.lean
