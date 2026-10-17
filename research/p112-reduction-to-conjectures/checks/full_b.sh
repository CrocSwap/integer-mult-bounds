#!/usr/bin/env bash
# FULL-B reruns (supplements verify.sh FULL=1; writes only under checks/full_b, evidence/full_b.log, PROOF_MAP_b.md).
# usage: bash checks/full_b.sh [WORKDIR]   (default WORKDIR=$TMPDIR/full_b_work).  <=3 busy processes (xargs -P3); every run under timeout 1200 (chunked).
# Needs: python3 with numpy (override with PYTHON=...), cc, g++, kissat.  Prints PASS/FAIL lines; also run  bash checks/full_b.sh | tee evidence/full_b.log
HERE=$(cd "$(dirname "$0")" && pwd); B="$HERE/full_b"
if [ -z "${PYTHON:-}" ]; then for p in python3 /usr/bin/python3; do "$p" -c 'import numpy' 2>/dev/null && PYTHON=$p && break; done; fi
export PYTHON; WK=${1:-${TMPDIR:-/tmp}/full_b_work}; mkdir -p "$WK"; export PYTHONHASHSEED=0
echo "== FULL-B: python=$PYTHON work=$WK"
st() { n=$1; shift; r=$(timeout 1200 "$@" 2>&1 | tail -n 3); if echo "$r" | grep -Eq 'STEP-OK|STEP-DONE|^OK'; then echo "PASS FULL-B $n: $(echo "$r" | grep -E 'STEP-OK|STEP-DONE|^OK' | head -1)"; else echo "FAIL FULL-B $n: $(echo "$r" | tr '\n' ' ' | cut -c1-300)"; fi; }
stl() { n=$1; shift; r=$(timeout 1200 "$@" 2>&1 | tail -n 3); if echo "$r" | grep -Eq 'STEP-OK'; then echo "PASS FULL-B $n: $(echo "$r" | grep -E 'STEP-OK' | head -1)"; else echo "FAIL FULL-B $n: $(echo "$r" | tr '\n' ' ' | cut -c1-300)"; fi; }
export -f st stl
S="bash $B/steps.sh $WK"; FN="bash $B/fin.sh $WK"; A="bash $B/aud1.sh $WK"
echo "== 0. builds"; if [ -z "${ONLY:-}" ] || [ ! -d "$WK/fin" ]; then $FN build; fi; $A build
{ echo "stl K579T_implA $S k579a"
  echo "stl JOINT2_satM bash $B/satm.sh $WK"
  for i in 0 1 2; do echo "st KILLALL7_kb_slice$i $S kb $i"; done
  for c in 0 1 2; do echo "st KILLA8_framesx1_chunk$c $S a8x1 $c"; done
  echo "stl TWOSIDE_f7r_rank $S two rank"; echo "stl TWOSIDE_f7r_cover $S two cover"; echo "stl TWOSIDE_bk1b_bk2b $S two bk1b"
  for k in 0 1 2 3 4 5 6 7; do echo "stl AUD1_cov_jobs_shard$k $A jobs $k 8"; done; echo "stl AUD1_cov_two_x0 $A file two_x0 'solutions 0\\|unordered 0'"; echo "stl AUD1_cov_two_x1 $A file two_x1 'solutions 0\\|unordered 0'"
  echo "stl AUD1_cov_p3_x0 $A file p3_x0 'solutions 1\$'"; echo "stl AUD1_cov_p3_x1 $A file p3_x1 'solutions 379'"; echo "stl AUD1_ps $A ps"
  echo "stl FINITE_alpha_t $FN chk t '7 4 0 7' FINITE/a1.out FINITE_alpha_t"; echo "stl FINITE2_alpha_f2 $FN chk f2 '7 4 0 7' FINITE2/a.out FINITE2_alpha_f2"
  echo "stl FINITE_ctl_S66_t $FN chk t '6 6 0 7' FINITE/c_s66.out FINITE_ctl_S66_t"; echo "stl FINITE2_ctl_S66_f2 $FN chk f2 '6 6 0 7' FINITE2/c_s66.out FINITE2_ctl_S66_f2"
  echo "stl FINITE_betaR6_p2_t $FN chk t '6 6 2 6' FINITE/b_p2_R6.out FINITE_betaR6_p2_t"; echo "stl FINITE2_betaR6_p2_f2 $FN chk f2 '6 6 2 6' FINITE2/b_p2_R6.out FINITE2_betaR6_p2_f2"
  for lo in $(seq 0 5 159); do echo "st b7_f2_$lo $FN chunk f2 $lo $((lo+5))"; done
  for lo in $(seq 0 10 159); do echo "st b7_t_$lo $FN chunk t $lo $((lo+10))"; done
} > "$WK/jobs1"
echo "== 1. phase 1 (<=3 procs)"; [ -n "${ONLY:-}" ] && grep -E "$ONLY" "$WK/jobs1" > "$WK/jobs1.f" && mv "$WK/jobs1.f" "$WK/jobs1"   # ONLY=regex reruns a subset of phase-1 jobs
tr "\n" "\0" < "$WK/jobs1" | xargs -0 -n1 -P3 bash -c 'eval "$1"' _ | grep -v "FULL-B b7_" 
echo "== 2. phase 2 (needs K579T regen)"; if [ -z "${ONLY:-}" ] || echo "$ONLY" | grep -q R579b; then bash -c "stl R579b_K5minus $S r579"; fi
echo "== 3. joins"
bash -c "st KILLALL7_kb_join $S kbjoin" ; bash -c "st KILLA8_framesx1_join $S a8x1join"
r=$(bash $B/fin.sh $WK join); echo "$r" | grep -v STEP | sed 's/^/   /'; if echo "$r" | grep -q 'STEP-OK'; then echo "PASS FULL-B FINITE_FINITE2_betaR7_p2: $(echo "$r" | grep STEP-OK)"; else echo "FAIL FULL-B FINITE_FINITE2_betaR7_p2: $(echo "$r" | tr '\n' ' ' | cut -c1-300)"; fi
