#!/bin/bash
# usage: runq.sh listfile ; runs each cnf with kissat 1200s, 2 parallel
cd code/tight55/ic
cat $1 | xargs -P 2 -I{} sh -c 'f={}; [ -s $f.out ] && grep -q "^s " $f.out && exit 0; kissat --time=1200 -q $f.cnf > $f.out 2>&1'
