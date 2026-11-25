#!/usr/bin/env bash
# sc_rerun.sh OUTDIR FULL : compile s3z.c, rerun chunks, write OUTDIR/<name>.out (same names as evidence/sc_runs).  At most 3 busy processes, each under timeout 1200.
# default: all of (7,5,2) [10 jobs: j1 of every rem + j0 of rems 6,7] + (7,5,1) j1 + 3 sample chunks of (7,4,3) and (6,6,2); FULL=1: every chunk of (7,4,3) and (6,6,2) too.
set -u; HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../.." && pwd); O=$1; FULL=${2:-0}; mkdir -p "$O"; cp "$ROOT/data/sc/gens.txt" "$O/"; cd "$O"
cc -O3 -o s3z "$HERE/s3z.c" || exit 1; D="$ROOT/data/sc/data88.txt"
job() { # cfg a b c T M r J j
  local DD="$D" LIM=88; case $1 in 6-6-2*) DD="$D80"; LIM=80;; esac
  local n="$1_M$6r$7J$8j$9"; JMOD=$8 JREM=$9 EXITCRACK=1 timeout 1200 nice -n 10 ./s3z "$DD" $2 $3 $4 0 $LIM $5 $6 $7 > "$n.tmp" 2>/dev/null; echo "rc=$?" >> "$n.tmp"; sed 's#OVERALL [^ ]*data\(88\|80\).txt#OVERALL data\1.txt#' "$n.tmp" > "$n.out"; rm -f "$n.tmp"; }
export D80="$ROOT/data/sc/data80.txt"; export -f job; export D
{ for r in 0 1 2 3 4 5 6 7; do echo "7-5-2-s0 2 7 5 7 8 $r 2 1"; done; echo "7-5-2-s0 2 7 5 7 8 6 2 0"; echo "7-5-2-s0 2 7 5 7 8 7 2 0"; echo "7-5-1-s0 1 7 5 6 1 0 2 1"
  for r in 0 14 29; do echo "7-4-3-s0 3 7 4 6 30 $r 1 0"; done; for r in 0 40 79; do echo "6-6-2-s0 6 6 2 4 80 $r 1 0"; done
  if [ "$FULL" = 1 ]; then for r in $(seq 0 29); do echo "7-4-3-s0 3 7 4 6 30 $r 1 0"; done; for r in $(seq 0 79); do echo "6-6-2-s0 6 6 2 4 80 $r 1 0"; done; fi; } | sort -u > jobs.txt
xargs -P 3 -L 1 bash -c 'job "$@"' _ < jobs.txt
