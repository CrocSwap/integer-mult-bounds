#!/usr/bin/env bash
# KILL-ALL7 rerun in a scratch copy: kill_all7.sh WORKDIR PART   PART: ps (ka2.c list + ka1.c PS+1, ~3 min) | t3 (t3p.c) | kbN (impl B kb.py slice N of 3, ~6 min each; N=0,1,2) | kbjoin
set -u; PY="${PYTHON:-python3}"
HERE=$(cd "$(dirname "$0")/.." && pwd); W=$1; P=$2; D="$W/KILL-ALL7"; mkdir -p "$W"
if [ ! -d "$D" ]; then cp -R "$HERE/KILL-ALL7" "$D"; mkdir -p "$W/CARRIER"; cp -R "$HERE/CARRIER/." "$W/CARRIER/"; fi
cd "$D" || exit 2
nrm() { sed 's/ *$//' "$1"; }
case $P in
 ps) "$PY" -B gen.py > gen.log 2>&1 || { echo "STEP-FAIL KILL-ALL7 gen"; exit 1; }
     cmp -s lab.in "$HERE/KILL-ALL7/lab.in" || { echo "STEP-FAIL KILL-ALL7 lab.in differs"; exit 1; }
     for f in ka ka1 ka2 t3p; do cc -O2 -o $f $f.c || exit 2; done
     ./ka2 > ka2.new; ./ka1 > ka1.new
     diff <(nrm ka2.new) <(nrm "$HERE/KILL-ALL7/ka2.out") >/dev/null && diff <(nrm ka1.new) <(nrm "$HERE/KILL-ALL7/ka1.out") >/dev/null && echo "STEP-OK KILL-ALL7 PS (ka2.c) and PS+1 (ka1.c) reproduce shipped ka2.out/ka1.out" || echo "STEP-FAIL KILL-ALL7 ps";;
 t3) [ -x t3p ] || cc -O2 -o t3p t3p.c; ./t3p > t3p.new 2>&1
     # expected (NOTES): types k=0..5 have 0 covering pairs (plain and +1 line); k=6 (E6A1) 6009 plain, 0 with an extra line
     if [ "$(grep -c 'with one extra line 0' t3p.new)" -ge 7 ] && [ "$(grep -c 'plain 0,' t3p.new)" = 6 ] && grep -q 'k=6 .*plain 6009,' t3p.new; then echo "STEP-OK KILL-ALL7 T3+1 (t3p.c): 6 types uncoverable, E6A1 6009 pairs, +1 line adds none"; else echo "STEP-FAIL KILL-ALL7 t3p"; fi;;
 kb[0-2]) n=${P#kb}; KB_NS=3 KB_SL=$n "$PY" -B kb.py plain > kb_$n.out 2>&1; grep -c '^rep' kb_$n.out | sed 's/^/KILL-ALL7 kb slice reps done: /';;
 kbjoin) cat kb_0.out kb_1.out kb_2.out | grep '^rep' | sort > kb_all.rep; grep '^rep' "$HERE/KILL-ALL7/kb_plain.out" | sort > kb_ship.rep
     cmp -s kb_all.rep kb_ship.rep && echo "STEP-OK KILL-ALL7 impl B kb.py plain (11 orbit reps) reproduces shipped kb_plain.out" || echo "STEP-FAIL KILL-ALL7 kb";;
esac
