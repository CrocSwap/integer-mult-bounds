#!/bin/bash
cd code/drat55
D=<research-tree>/tools_ext/drat-trim/drat-trim; PY=python3
while true; do
  r=$(ls work/*.readyL 2>/dev/null | head -20 | while read x; do b=$(basename $x .readyL); if mkdir work/$b.lockL 2>/dev/null; then echo $b; break; fi; done)
  if [ -z "$r" ]; then [ -e work/STOPL ] && exit 0; sleep 15; continue; fi
  b=$r; [ -e work/$b.readyL ] || { rmdir work/$b.lockL; continue; }
  IFS=$'\t' read -r nm st secs sz h ch e < work/$b.readyL; set -- $e; base=$1; m=$2; fx=$3
  f=work/$b.cnf; $PY mkcube3.py ../loose/$base.cnf $m $f "$fx" > /dev/null
  if [ "$st" = "UNSATISFIABLE" ]; then
    $D $f work/$b.drat -t 20000 > work/$b.dlog 2>&1
    if grep -aq 's NOT VERIFIED' work/$b.dlog; then v=NOT_VERIFIED; elif grep -aq 's VERIFIED' work/$b.dlog; then v=VERIFIED; else v=NO_VERDICT; fi
    vt=$(grep -a 'verification time' work/$b.dlog | awk '{print $4}')
  else v=SKIPPED; vt=0; touch work/$b.dlog; fi
  cch=$(shasum -a 256 $f | cut -c1-16); [ "$cch" = "$ch" ] || v="${v}_CNFHASH_MISMATCH"
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" $b "$st" $secs $sz $h $ch "$v" "$vt" $(date +%H:%M) >> results.tsv
  rm -f $f work/$b.drat; gzip -c work/$b.dlog > logs/$b.dlog.gz; rm -f work/$b.dlog work/$b.kout work/$b.readyL; rmdir work/$b.lockL
done
