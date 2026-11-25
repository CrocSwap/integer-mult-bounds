#!/bin/bash
# Re-run (7,5,2) s0 at T=7: all 8 rems for JREM=1 (never run) and JREM=0 rems 6,7 (unclear). 4 at a time, 20-min cap each.
cd "$(dirname "$0")"; D=data88.txt
jobs=(); for r in 0 1 2 3 4 5 6 7; do jobs+=("$r 1"); done; jobs+=("6 0" "7 0")
run(){ set -- $1; JMOD=2 JREM=$2 EXITCRACK=1 nice -n 10 timeout 1200 s3z $D 2 7 5 0 88 7 8 $1 > r$1j$2.out 2> r$1j$2.err; echo "rc=$?" >> r$1j$2.out; }
i=0; for j in "${jobs[@]}"; do run "$j" & i=$((i+1)); [ $((i%4)) -eq 0 ] && wait; done; wait; echo ALLDONE > done.flag
