#!/bin/bash
# Row 424 scenario assembly (RES116/AUDIT-RES asm.py): s = 7 gives the single scenario ClassI, which needs exactly the
# Dim-Cover E6 fact "(6,6,5,5,5,4)+1 line cannot cover the 84 lines outside E6" (checked twice in full_c.sh).
cd "$(dirname "$0")"; out=$(${PYTHON:-python3} -B asm.py 2>&1)
blk=$(echo "$out" | awk '/^ROW 424 /{f=1;print;next} /^ROW /{f=0} f')
n=$(echo "$blk" | grep -c '^   ')
echo "$blk" | grep -q "ClassI -> needs DimCover comp (6, 6, 5, 5, 5, 4, 1)" && [ "$n" = 1 ] && echo "PASS row 424 assembly: only scenario ClassI, needs (6,6,5,5,5,4)+1 Dim-Cover E6" || { echo "FAIL row 424 assembly"; echo "$blk"; }
