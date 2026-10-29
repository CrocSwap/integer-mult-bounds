#!/bin/zsh
# $1 = fwd|rev ; each target run once (log file = claim)
cd ../AUDIT-SC
if [ "$1" = rev ]; then L=$(grep '^non' targets.txt | tail -r); else L=$(grep '^non' targets.txt); fi
echo "$L" | while read n lo hi k f; do
  [ -e log_$n.txt ] && continue
  echo start > log_$n.txt
  /usr/bin/time -p nice -n 10 ./cov $lo $hi $k 9 $f left_$n.txt.tmp 2>> log_$n.txt && mv left_$n.txt.tmp left_$n.txt
done
