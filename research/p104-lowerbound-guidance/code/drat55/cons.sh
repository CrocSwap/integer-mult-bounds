#!/bin/bash
# consumer loop: picks work/*.ready, regenerates cube cnf if needed, runs drat-trim, appends to results.tsv, deletes proof.
cd code/drat55
D=<research-tree>/tools_ext/drat-trim/drat-trim
PY=python3
id=$1   # consumer id 0/1 : takes alternating? use mkdir lock
while true; do
  r=$(ls work/*.ready 2>/dev/null | head -20 | while read x; do b=$(basename $x .ready); if mkdir work/$b.lock 2>/dev/null; then echo $b; break; fi; done)
  if [ -z "$r" ]; then [ -e work/STOP ] && exit 0; sleep 15; continue; fi
  b=$r; IFS=$'\t' read -r nm st secs sz h ch e < work/$b.ready
  p=work/$b.drat
  case $e in F*) m=${e#F}; f=work/$b.cnf; $PY mkcube.py $m $f;; *) f=$e;; esac
  if [ "$st" = "UNSATISFIABLE" ]; then
    $D $f $p -t 20000 > work/$b.dlog 2>&1
    if grep -aq 's NOT VERIFIED' work/$b.dlog; then v=NOT_VERIFIED; elif grep -aq 's VERIFIED' work/$b.dlog; then v=VERIFIED; else v=NO_VERDICT; fi
    vt=$(grep -a 'verification time' work/$b.dlog | awk '{print $4}')
  else v=SKIPPED; vt=0; touch work/$b.dlog; fi
  cch=$(shasum -a 256 $f | cut -c1-16)
  [ "$cch" = "$ch" ] || v="${v}_CNFHASH_MISMATCH"
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" $b "$st" $secs $sz $h $ch "$v" "$vt" $(date +%H:%M) >> results.tsv
  case $e in F*) rm -f $f;; esac
  rm -f $p; gzip -c work/$b.dlog > logs/$b.dlog.gz; rm -f work/$b.dlog work/$b.kout work/$b.ready; rmdir work/$b.lock
done
