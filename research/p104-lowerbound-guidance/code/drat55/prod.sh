#!/bin/bash
# producer: prod.sh <entry>  entry = path to cnf  OR  F<mask>.  kissat -> proof; leaves work/<b>.ready for the consumer.
cd code/drat55
e=$1
case $e in F*) m=${e#F}; b=f$m; f=work/$b.cnf; PY=python3;; *) f=$e; b=$(basename $f .cnf);; esac
grep -q "^$b	" results.tsv 2>/dev/null && exit 0
[ -e work/$b.ready ] && exit 0
# backpressure: <=3 unchecked proofs and >=7GB free
while [ $(ls work/*.ready 2>/dev/null | wc -l) -ge 5 ] || [ $(df -k . | tail -1 | awk '{print int($4/1048576)}') -lt 7 ]; do sleep 20; done
case $e in F*) $PY mkcube.py $m $f;; esac
p=work/$b.drat
s0=$(date +%s)
kissat --time=1200 -q $f $p > work/$b.kout 2>&1
s1=$(date +%s)
st=$(grep '^s ' work/$b.kout | cut -c3-)
ch=$(shasum -a 256 $f | cut -c1-16)
case $e in F*) rm -f $f;; esac
sz=$(stat -f %z $p)
h=$(shasum -a 256 $p | cut -c1-16)
echo "$b	$st	$((s1-s0))	$sz	$h	$ch	$e" > work/$b.meta
mv work/$b.meta work/$b.ready
