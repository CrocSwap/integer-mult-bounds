#!/bin/bash
D=code/leanlinear
OL=<research-tree>/lean/decoder-duality/.lake/build/lib/lean/Nov15
$D/b.sh Nov15/LinCore.lean $OL/LinCore.olean
$D/b.sh Nov15/Doubling.lean $OL/Doubling.olean
$D/b.sh Nov15/LinFinal.lean $OL/LinFinal.olean
