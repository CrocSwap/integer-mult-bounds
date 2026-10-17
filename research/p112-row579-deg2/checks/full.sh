#!/usr/bin/env bash
# FULL=1 heavy reruns. usage: full.sh OUTDIR.  <= 3 busy processes, every process under timeout 1150, chunked. Prints PASS/FAIL (FULL-FAIL on failure).
#  (a) AUD-2 pairmin.c: minimum two-7-flat leftovers per non-root type (D7 14, E6A1 23, E6 24, A7 25, D6 26, ...).
#  (b) DEG2 impl A quad stage, all 10 La-orbit reps, in chunks (rep: number of chunks): compared with the recorded DONE lines (survivor counts).
#  (c) DEG2 impl C (d2fix.c, fixed oracle): see checks/DEG2C/run_d2fix.sh; prints the counts only. SLOT: the verdict line for impl C is filled by the author after the rerun.
set -u; H=$(cd "$(dirname "$0")" && pwd); OUT=${1:-$(mktemp -d)}; W="$OUT/full"; mkdir -p "$W"
echo "== FULL (a) pairmin"; bash "$H/AUD-2/pairmin_check.sh" 2>&1 | sed 's/^FAIL/FULL-FAIL/'
echo "== FULL (b) DEG2A quad stage"
A="$W/A"; mkdir -p "$A"; cp "$H"/DEG2A/{quad.c,e8.h} "$A/"; ( cd "$A" && cc -O2 -o quad quad.c -lm ) || { echo "FULL-FAIL DEG2A build"; exit 1; }
# rep:nch:recorded-prefix  (S1 = rep 1 in 40 chunks, ...). The recorded prefix names the files in checks/DEG2A/rec.
plan="0:16:T0 1:40:S1 2:12:R2 3:2:T3 4:12:R4 5:1:Q 6:12:T6 7:4:T7 8:12:T8 9:1:T9"
jobs=""; for p in $plan; do r=${p%%:*}; rest=${p#*:}; n=${rest%%:*}; pre=${rest#*:}; for c in $(seq 0 $((n-1))); do jobs="$jobs $r:$n:$c:$pre"; done; done
run1() { IFS=: read r n c pre <<< "$1"; f="$2/rec/${pre}_${c}.out"; [ "$pre" = Q ] && f="$2/rec/Q_5.out"
  got=$(cd "$3" && timeout 1150 ./quad 28 $r $c $n 2>/dev/null | grep -o -E '(^SURV.*|DONE rep.*)' | sed 's/ tri.*surv/ surv/' | sort); want=$(grep -o -E '(^SURV.*|DONE rep.*)' "$f" | sed 's/ tri.*surv/ surv/' | sort)
  [ -n "$got" ] && [ "$got" = "$want" ] && echo "PASS-CHUNK rep $r $c/$n" || echo "FULL-FAIL DEG2A chunk rep $r $c/$n"; }
export -f run1
printf '%s\n' $jobs | xargs -P3 -I{} bash -c 'run1 {} "$0" "$1"' "$H/DEG2A" "$A" | sort > "$W/chunks.out"
nfail=$(grep -c FULL-FAIL "$W/chunks.out"); npass=$(grep -c PASS-CHUNK "$W/chunks.out"); grep FULL-FAIL "$W/chunks.out"
[ "$nfail" = 0 ] && echo "PASS FULL DEG2A quad stage: $npass chunks equal the recorded DONE/SURV lines (4-seven survivors only in reps 1 and 8)" || echo "FULL-FAIL DEG2A quad stage ($nfail chunk failures)"
echo "== FULL (c) DEG2C impl C (fixed oracle)"; bash "$H/DEG2C/run_d2fix.sh" "$W/C" 2>&1 | tail -n 40
