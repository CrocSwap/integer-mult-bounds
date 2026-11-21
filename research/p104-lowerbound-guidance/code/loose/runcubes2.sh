#!/bin/bash
# usage: runcubes.sh base.cnf masklist tag ; sequential, kissat <=1200s each, cube cnf deleted after run
cd code/loose
P=python3
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
for m in $(cat $2); do
  o=cubes/$3_$m.out
  if [ -s $o ] && grep -q "^s " $o; then continue; fi
  $P ${MK:-mkcube2.py} $1 $m cubes/tmp_$3.cnf
  s=$(date +%s); kissat --time=1200 -q cubes/tmp_$3.cnf > $o 2>&1; e=$(( $(date +%s)-s ))
  echo "$m $(grep '^s ' $o) ${e}s" >> cubes/$3.log
  rm -f cubes/tmp_$3.cnf
done
echo DONE >> cubes/$3.log
