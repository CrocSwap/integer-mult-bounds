#!/bin/bash
# usage: sweep.sh nh no "L list" extra
nh=$1; no=$2; shift 2; Ls=$1; extra=$2
for L in $Ls; do
  echo "== R=2 Q5 nh=$nh no=$no L=$L $extra"
  python3 enc4.py --case Q5 --R 2 --L $L --nh $nh --no $no --timeout 1200 $extra | head -6
done
