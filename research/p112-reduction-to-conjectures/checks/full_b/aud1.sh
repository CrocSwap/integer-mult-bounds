#!/usr/bin/env bash
# aud1.sh WK MODE [args]: AUD-1 cov.c / ps.c reruns.  MODES: build | job NAME (cov on one generated job, byte-compare with shipped out/NAME.out) | file NAME (job file shipped as jobs_NAME; prints solutions line) | ps
set -u; WK=$1; M=$2; shift 2; PY="${PYTHON:-python3}"; HERE=$(cd "$(dirname "$0")/.." && pwd); D="$WK/aud1"; export PYTHONHASHSEED=0
case $M in
build) rm -rf "$D"; mkdir -p "$D"; cp -R "$HERE/AUD-1/." "$D/"; cd "$D"; rm -rf out jobs fm.pkl base.txt; mkdir out; "$PY" -B prep.py >/dev/null 2>&1; "$PY" -B jobs.py >/dev/null 2>&1; "$PY" -B psprep.py >/dev/null 2>&1
  cc -O2 -o cov cov.c && cc -O2 -o ps ps.c -lm && [ "$(ls jobs | wc -l | tr -d " ")" = 137 ] && cmp -s ps.in "$HERE/AUD-1/ps.in" && echo built;;
job) cd "$D"; j=$1; timeout 1200 ./cov base.txt jobs/$j > out/$j.out 2>/dev/null; rc=$?; if [ $rc = 0 ] && cmp -s out/$j.out "$HERE/AUD-1/out/$j.out"; then echo "OK $j"; else echo "BAD $j rc=$rc"; fi;;
jobs) cd "$D"; K=$1; NS=$2; bad=0; n=0; i=0; for j in $(cat joblist); do i=$((i+1)); [ $((i % NS)) = $K ] || continue; r=$(bash "$0" "$WK" job $j); n=$((n+1)); case "$r" in OK*) ;; *) bad=$((bad+1)); echo "$r";; esac; done
  [ $bad = 0 ] && echo "STEP-OK AUD-1 cov.c shard $K/$NS: $n generated jobs (a_/c_/t3_/ctl) byte-identical to shipped out/*.out" || echo "STEP-FAIL AUD-1 cov.c shard $K/$NS: $bad of $n jobs differ";;
file) cd "$D"; n=$1; exp="$2"; timeout 1200 ./cov base.txt jobs_$n > "out_$n.txt" 2>/dev/null; rc=$?; r=$(tail -n 1 "out_$n.txt" | sed 's/^.*|//'); if [ $rc = 0 ] && grep -q "$exp" "out_$n.txt"; then echo "STEP-OK AUD-1 cov.c jobs_$n: $(tail -n 1 out_$n.txt)"; else echo "STEP-FAIL AUD-1 cov.c jobs_$n rc=$rc (124=timeout 1200s): $(tail -n 1 out_$n.txt)"; fi;;
ps) cd "$D"; timeout 1200 ./ps base.txt ps.in > ps.new 2>/dev/null; rc=$?
  # shipped record = ps_a.out + ps_b.out (two halves; ps.out is a 2-line stub): per-rep lines equal as a set, and the Q histogram of NOTES (0:350740 1:95322 2:21326 3:5112 4:2272 5:45 6:144 7:9 8:21)
  if [ $rc = 0 ] && diff <(grep '^rep' ps.new | sed 's/ *$//' | sort) <(cat "$HERE/AUD-1/ps_a.out" "$HERE/AUD-1/ps_b.out" | grep '^rep' | sed 's/ *$//' | sort -u) >/dev/null && grep -q '^hist Q: 0:350740 1:95322 2:21326 3:5112 4:2272 5:45 6:144 7:9 8:21' ps.new; then echo "STEP-OK AUD-1 ps.c (Lemma PS/PS+1): all $(grep -c '^rep' ps.new) rep lines equal ps_a.out+ps_b.out, Q histogram equal NOTES"; else echo "STEP-FAIL AUD-1 ps.c rc=$rc"; fi;;
esac
