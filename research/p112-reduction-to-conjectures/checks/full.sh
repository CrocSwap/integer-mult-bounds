#!/usr/bin/env bash
# FULL=1 reruns.  usage (from verify.sh): full.sh OUTDIR.  At most 4 processes at a time, every step under timeout 1200.
# Needs: kissat, a C compiler, PYTHON with numpy (default python3); drat-trim is compiled from checks/full/drat-trim.c.
OUT=${1:-.}; HERE=$(cd "$(dirname "$0")" && pwd); F="$HERE/full"; export PYTHON="${PYTHON:-python3}"
WK="$OUT/fullwork"; mkdir -p "$WK"; cc -O2 -o "$WK/drat-trim" "$F/drat-trim.c" 2>/dev/null; export DRAT_TRIM="$WK/drat-trim"
st() { # label cmd... : run under timeout, echo FULL-PASS/FULL-FAIL based on the step's own STEP-OK/CHUNK-OK line
  n=$1; shift; r=$(timeout 1200 "$@" 2>&1 | tail -n 3); if echo "$r" | grep -Eq 'STEP-OK|CHUNK-OK'; then echo "PASS FULL $n: $(echo "$r" | grep -E 'STEP-OK|CHUNK-OK' | head -1)"; else echo "FULL-FAIL $n: $r"; fi; }
export -f st
G="python3 -B $F/gen_satP.py"; SP="$HERE/KILL-SMALL/p262/satP1.py"; SC="bash $F/satchunk.sh $WK"
cat > "$WK/jobs" <<EOT
st SAT_joint2_p4_113_262x0 $SC joint2_p4 UNSAT $PYTHON -B $F/gen_satP.py $WK/joint2_p4.cnf 3 0 4
st SAT_262_f0 $SC f0 UNSAT $PYTHON -B $SP 3 1 4 o 0 $WK/f0.cnf
st SAT_262_f20 $SC f20 UNSAT $PYTHON -B $SP 3 1 4 o 20 $WK/f20.cnf
st SAT_262_f30 $SC f30 UNSAT $PYTHON -B $SP 3 1 4 o 30 $WK/f30.cnf
st SAT_262_f42 $SC f42 UNSAT $PYTHON -B $SP 3 1 4 o 42 $WK/f42.cnf
st SAT_ctl_p3_x0 $SC ctl3 SAT $PYTHON -B $F/gen_satP.py $WK/ctl3.cnf 3 0 3
st SAT_ctl_262_p3x1 $SC ctl3b SAT $PYTHON -B $SP 3 1 3 o 0 $WK/ctl3b.cnf
st KILLA8_core bash $F/kill_a8.sh $WK core
st KILLA8_x1 bash $F/kill_a8.sh $WK x1
st KILLA8_types bash $F/kill_a8.sh $WK types
st KILLA8_frames bash -c "bash $F/kill_a8.sh $WK frames; bash $F/kill_a8.sh $WK framesx1"
st K579T_implA bash $F/k579t.sh $WK A
st K579T_implB bash $F/k579t.sh $WK B
st K579T_types bash $F/k579t.sh $WK T
st KILLALL7_ps bash $F/kill_all7.sh $WK ps
st KILLALL7_t3 bash $F/kill_all7.sh $WK t3
st KILLALL7_kb bash -c "for i in 0 1 2; do bash $F/kill_all7.sh $WK kb\$i & done; wait; bash $F/kill_all7.sh $WK kbjoin"
EOT
tr "\n" "\0" < "$WK/jobs" | xargs -0 -n1 -P4 bash -c 'eval "$1"' _
# Supplementary FULL reruns (each script <= 3 busy processes, every process under timeout 1200; sequential, each with its own log in OUT).
bash "$HERE/full_a.sh" "$OUT/full_a.log" > /dev/null 2>&1; tail -n 1 "$OUT/full_a.log" | sed 's/^/FULL-A log: /'
bash "$HERE/full_b.sh" "$WK/b" > "$OUT/full_b.log" 2>&1; grep -c '^PASS FULL-B' "$OUT/full_b.log" | sed 's/^/FULL-B passes: /'; grep '^FAIL FULL-B' "$OUT/full_b.log"
bash "$HERE/full_c.sh" "$WK/c" > "$OUT/full_c.log" 2>&1; grep -c 'FULL-C: PASS' "$OUT/full_c.log" | sed 's/^/FULL-C passes: /'; grep 'FULL-C: FAIL' "$OUT/full_c.log"
bash "$HERE/full_c/res/asm_check.sh" 2>&1 | tee "$OUT/full_c_asm.log"
bash "$HERE/AUD-2/pairmin_check.sh" 2>&1 | tee "$OUT/pairmin.log"
bash "$HERE/CONJG2/lists_check.sh" 2>&1 | tee "$OUT/conjg2_lists.log"
bash "$HERE/PRIOR7/rerun.sh" 2>&1 | tee "$OUT/prior7.log"
bash "$HERE/full_d.sh" "$WK/d" > "$OUT/full_d.log" 2>&1; grep -c 'FULL-D: PASS' "$OUT/full_d.log" | sed 's/^/FULL-D passes: /'; grep 'FULL-D: FAIL' "$OUT/full_d.log"
