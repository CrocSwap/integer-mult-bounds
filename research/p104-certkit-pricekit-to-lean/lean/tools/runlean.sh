#!/bin/bash
# usage: tools/runlean.sh Nov15/File.lean [olean-out]   (run from lean/; one file, RSS guard RSS_CAP_KB, default 3500000)
cd "$(dirname "$0")/.." || exit 2
f=$1; o=$2; CAP=${RSS_CAP_KB:-3500000}; mkdir -p logs; log=logs/runlean_$$.log
if [ -n "$o" ]; then lake env lean -j1 -o "$o" "$f" > "$log" 2>&1 & else lake env lean -j1 "$f" > "$log" 2>&1 & fi
lp=$!; peak=0; t0=$(date +%s)
while kill -0 $lp 2>/dev/null; do
  r=$(ps -Ao ppid=,rss=,comm= | awk -v P=$lp '$1==P && $3 ~ /lean/ {print $2}' | head -1); r=${r:-0}
  [ "$r" -gt "$peak" ] && peak=$r
  if [ "$CAP" -gt 0 ] && [ "$r" -gt "$CAP" ]; then kill $lp; echo "KILLED over RSS cap"; fi
  sleep 0.2
done
wait $lp; rc=$?
echo "rc=$rc time=$(( $(date +%s) - t0 ))s peak=$((peak/1024))MB"
grep -E "error|sorry" "$log" | head -20
grep -c "error" "$log"
