#!/bin/bash
# prodL.sh <base> <mask> <fixes>  ; entry name l<base>_<mask>[_fixes]
cd code/drat55
base=$1; m=$2; fx=$3; PY=python3
b=L${base}_${m}; [ -n "$fx" ] && b=${b}_$(echo $fx | tr ':,' 'xy')
grep -q "^$b	" results.tsv 2>/dev/null && exit 0
[ -e work/$b.readyL ] && exit 0
while [ $(ls work/*.readyL 2>/dev/null | wc -l) -ge 4 ] || [ $(df -k . | tail -1 | awk '{print int($4/1048576)}') -lt 7 ]; do sleep 20; done
f=work/$b.cnf; $PY mkcube3.py ../loose/$base.cnf $m $f "$fx" > /dev/null
s0=$(date +%s); kissat --time=1200 -q $f work/$b.drat > work/$b.kout 2>&1; s1=$(date +%s)
st=$(grep '^s ' work/$b.kout | cut -c3-); ch=$(shasum -a 256 $f | cut -c1-16); rm -f $f
sz=$(stat -f %z work/$b.drat); h=$(shasum -a 256 work/$b.drat | cut -c1-16)
echo "$b	$st	$((s1-s0))	$sz	$h	$ch	$base $m $fx" > work/$b.meta; mv work/$b.meta work/$b.readyL
