#!/bin/sh
cd ../KILL-A8
for x in 0 1; do for i in 8 1 2 3 4 5 6 7; do k=0; while read a; do echo "type h$i x1=$x $(./pcf2 dat_h$i.txt $x fr_h$i.txt $k 2>/dev/null)"; k=$((k+1)); done < fr_h$i.txt; done; done > types.out
