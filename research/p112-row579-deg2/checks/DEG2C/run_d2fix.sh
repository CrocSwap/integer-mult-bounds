#!/usr/bin/env bash
# DEG2 impl C driver (d2fix.c = the FIXED oracle; see NOTES.md "Oracle bug").  usage: run_d2fix.sh WORKDIR [ctl|deg2]
#   ctl  : controls (all-root MODE 1: a triple and a quad are FOUND; K=3/4 DEG2 stages for the type D7), ~minutes
#   deg2 : DEG2 proper, ./d2fix 6 0 TYPE 1 SHARD 8 for TYPE 1..5 (D7,A7,E6A1,E6,D6) and SHARD 0..7; each job under timeout 1150, <= 3 at a time.
#          A job that hits the timeout prints rc=124 = INCOMPLETE (no verdict); a verdict needs every shard rc=0 and "final 0".
set -u; H=$(cd "$(dirname "$0")" && pwd); W=${1:-$(mktemp -d)}; M=${2:-ctl}; mkdir -p "$W"; cd "$W" || exit 2
cp "$H/d2fix.c" .; cc -O2 -o d2fix d2fix.c 2>/dev/null || cc -O2 -o d2fix d2fix.c || { echo "FAIL build d2fix"; exit 1; }
if [ "$M" = ctl ]; then
  FIRST=1 timeout 1150 ./d2fix 3 1 0 1 2>&1 | grep -E 'FOUND|final' | head -3 | sed 's/^/ctl K=3 MODE1: /'
  FIRST=1 timeout 1150 ./d2fix 4 1 0 1 2>&1 | grep -E 'FOUND|final' | head -3 | sed 's/^/ctl K=4 MODE1: /'
  echo "controls done (a root-only configuration must be FOUND for K=3 and K=4)"
else
  for t in 1 2 3 4 5; do for s in 0 1 2 3 4 5 6 7; do echo "$t $s"; done; done | xargs -P3 -L1 sh -c 'mkdir -p j$0_$1; cd j$0_$1; cp ../LM.bin . 2>/dev/null; timeout 1150 ../d2fix 6 0 $0 1 $1 8 > out 2>/dev/null; echo "rc=$? type $0 shard $1/8: $(grep -E "^TYPE" out | tail -n 1)"'
  echo "SLOT-C6-IMPL-C (filled by the author after the fixed rerun): six-set count = ?, controls = ?"
fi
