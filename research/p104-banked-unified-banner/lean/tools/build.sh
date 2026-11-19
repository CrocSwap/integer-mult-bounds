#!/bin/bash
# Sequential, memory-guarded build of every module in build-order.txt (one `lean` process at a time).
# A module is recompiled when its olean is missing, older than its source, or older than any imported olean.
# Env: RSS_CAP_KB (default 3500000; 0 = no guard); WAIT_IDLE=1 waits for no other `lean` process before each file.
cd "$(dirname "$0")/.." || exit 2
OUT=.lake/build/lib/lean/Nov15; mkdir -p "$OUT" logs
CAP=${RSS_CAP_KB:-3500000}; nb=0
while read -r m; do
  src=Nov15/$m.lean; ol=$OUT/$m.olean; need=0
  [ -f "$src" ] || { echo "FAIL missing source $src"; exit 1; }
  if [ ! -f "$ol" ] || [ "$src" -nt "$ol" ]; then need=1; fi
  if [ $need = 0 ]; then
    for d in $(grep -E '^\s*import Nov15\.' "$src" | sed -E 's/.*Nov15\.//'); do
      [ "$OUT/$d.olean" -nt "$ol" ] && { need=1; break; }; done
  fi
  [ $need = 0 ] && continue
  if [ "${WAIT_IDLE:-0}" = 1 ]; then w=0; while pgrep -x lean >/dev/null; do sleep 1; w=$((w+1)); [ $w -gt 3600 ] && { echo "WAIT TIMEOUT before $m"; exit 3; }; done; fi
  t0=$(date +%s); lake env lean -o "$ol" -i "$OUT/$m.ilean" "$src" > "logs/$m.log" 2>&1 & lp=$!; peak=0
  while kill -0 $lp 2>/dev/null; do
    r=$(ps -Ao ppid=,rss=,comm= | awk -v P=$lp '$1==P && $3 ~ /lean/ {print $2}' | head -1); r=${r:-0}
    [ "$r" -gt "$peak" ] && peak=$r
    if [ "$CAP" -gt 0 ] && [ "$r" -gt "$CAP" ]; then echo "RSS CAP hit on $m"; kill $lp; fi
    sleep 0.3
  done
  wait $lp; rc=$?; nb=$((nb+1))
  echo "$m rc=$rc $(( $(date +%s)-t0 ))s peak=$((peak/1024))MB"
  if [ $rc != 0 ] || grep -qE '(^|: )error' "logs/$m.log"; then echo "FAIL $m"; head -20 "logs/$m.log"; rm -f "$ol"; exit 1; fi
done < build-order.txt
for m in All; do   # root modules (cheap: imports only)
  if [ "${WAIT_IDLE:-0}" = 1 ]; then while pgrep -x lean >/dev/null; do sleep 1; done; fi
  lake env lean -o .lake/build/lib/lean/$m.olean -i .lake/build/lib/lean/$m.ilean $m.lean > logs/$m.log 2>&1 || { echo "FAIL $m"; head -20 logs/$m.log; exit 1; }
done
echo "BUILD OK ($nb modules compiled, rest up to date)"
