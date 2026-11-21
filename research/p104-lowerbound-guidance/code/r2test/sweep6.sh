#!/bin/bash
nh=$1; no=$2; Ls=$3; extra=$4
for L in $Ls; do echo "== init0 R=2 Q5 nh=$nh no=$no L=$L $extra"; python3 enc6.py --case Q5 --R 2 --L $L --nh $nh --no $no --timeout 1200 --init0 $extra | head -4; done
