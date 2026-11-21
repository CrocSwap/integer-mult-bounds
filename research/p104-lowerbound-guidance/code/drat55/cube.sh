#!/bin/bash
# usage: cube.sh <cnf path>  ; kissat w/ DRAT proof, drat-trim check, log, delete proof
cd code/drat55
f=$1; b=$(basename $f .cnf)
grep -q "^$b	" results.tsv 2>/dev/null && exit 0
D=<research-tree>/tools_ext/drat-trim/drat-trim
p=work/$b.drat
s0=$(date +%s)
kissat --time=1200 -q $f $p > work/$b.kout 2>&1
s1=$(date +%s)
st=$(grep '^s ' work/$b.kout | cut -c3-)
sz=$(stat -f %z $p)
h=$(shasum -a 256 $p | cut -c1-16)
ch=$(shasum -a 256 $f | cut -c1-16)
if [ "$st" = "UNSATISFIABLE" ]; then
  $D $f $p -t 20000 > work/$b.dlog 2>&1
  if grep -aq 's NOT VERIFIED' work/$b.dlog; then v=NOT_VERIFIED; elif grep -aq 's VERIFIED' work/$b.dlog; then v=VERIFIED; else v=NO_VERDICT; fi
  vt=$(grep -a 'verification time' work/$b.dlog | awk '{print $4}')
else v=SKIPPED; vt=0; fi
printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" $b "$st" $((s1-s0)) $sz $h $ch "$v" "$vt" $(date +%H:%M) >> results.tsv
rm -f $p
gzip -c work/$b.dlog > logs/$b.dlog.gz 2>/dev/null; rm -f work/$b.dlog work/$b.kout
