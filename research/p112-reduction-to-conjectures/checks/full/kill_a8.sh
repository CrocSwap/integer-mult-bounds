#!/usr/bin/env bash
# KILL-A8 impl C rerun in a scratch copy: usage kill_a8.sh WORKDIR PART   PART in: core | x1 | frames | framesx1 | types
set -u; PY="${PYTHON:-python3}"
HERE=$(cd "$(dirname "$0")/.." && pwd); W=$1; P=$2; D="$W/KILL-A8"; mkdir -p "$W"
if [ ! -d "$D" ]; then cp -R "$HERE/KILL-A8" "$D"; mkdir -p "$W/CARRIER"; cp -R "$HERE/CARRIER/." "$W/CARRIER/"; fi
cd "$D" || exit 2
[ -x pc ] || { cc -O2 -o pc pc.c && cc -O2 -o pcf pcf.c && cp pcf pcf2 || exit 2; }
[ -f dat_4.txt ] || { "$PY" -B gen.py 3 && "$PY" -B gen.py 4 || exit 2; }
same() { diff <(grep -v '^pair' "$1" | sed 's/ *$//') <(grep -v '^pair' "$2" | sed 's/ *$//') >/dev/null; }
case $P in
 core)  a=$(./pc dat_4.txt 0 | grep -c 'solutions=0\b'); b=$(./pc dat_3.txt 0 | grep -Eo 'solutions=[0-9]+'); echo "KILLA8 pc P=4 X1=0 solutions=0 lines=$a ; control P=3 $b"
        [ "$a" -ge 1 ] && [ "$b" != "solutions=0" ] && echo "STEP-OK KILL-A8 core" || echo "STEP-FAIL KILL-A8 core";;
 x1)    a=$(./pc dat_4.txt 1 | grep -c 'solutions=0\b'); b=$(./pc dat_3.txt 1 | grep -Eo 'solutions=[0-9]+'); echo "KILLA8 pc P=4 X1=1 zero-lines=$a ; control P=3 X1=1 $b (shipped note: 379)"
        [ "$a" -ge 1 ] && [ "$b" = "solutions=379" ] && echo "STEP-OK KILL-A8 x1" || echo "STEP-FAIL KILL-A8 x1";;
 frames) "$PY" -B frames.py > frames_regen.log 2>&1; sh runf.sh 4 > /dev/null 2>&1 ; same frames_P4.out "$HERE/KILL-A8/frames_P4.out" && echo "STEP-OK KILL-A8 frames (12 orbits, matches shipped frames_P4.out)" || echo "STEP-FAIL KILL-A8 frames";;
 framesx1) : > frames_P4_x1.out; sh runf1.sh 0 11 > /dev/null 2>&1; same frames_P4_x1.out "$HERE/KILL-A8/frames_P4_x1.out" && echo "STEP-OK KILL-A8 framesx1 (matches shipped)" || echo "STEP-FAIL KILL-A8 framesx1";;
 types) "$PY" -B types.py > types_regen.log 2>&1; sh runh.sh > /dev/null 2>&1; same types.out "$HERE/KILL-A8/types.out" && echo "STEP-OK KILL-A8 types (matches shipped types.out)" || echo "STEP-FAIL KILL-A8 types";;
esac
