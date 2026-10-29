#!/usr/bin/env bash
# steps.sh WK NAME [args]  -- one self-contained rerun in its own scratch dirs under WK; last line printed: STEP-OK ... or STEP-FAIL ...
set -u; WK=$1; N=$2; shift 2; PY="${PYTHON:-python3}"
HERE=$(cd "$(dirname "$0")/.." && pwd)       # .../checks
nrm() { sed 's/ *$//' "$1"; }
cpd() { # cpd DEST SRC...: copy checks/SRC dirs into DEST (fresh)
  d=$1; shift; mkdir -p "$d"; for s in "$@"; do [ -d "$d/$s" ] || cp -R "$HERE/$s" "$d/$s"; done; }
case $N in
# ---- (1) K579T implA, harness fixed: (a) SIZEONLY=1 for the size-only run, (b) rep ids/slice split of a3e are labelling-dependent (mask order), so compare the
#      union of both slices as a multiset ignoring rep ids, plus the 958/291/A4=0 totals and ext.py tails
k579a) D="$WK/k579a"; rm -rf "$D"; mkdir -p "$D"; cp -R "$HERE/K579T" "$D/K579T"; cd "$D/K579T" || exit 2
  rm -f surv_28_*.txt masks.npy a3.txt
  "$PY" -B deficit.py > deficit.log 2>&1; "$PY" -B genA3.py > genA3.log 2>&1; cc -O2 -o a3e a3e.c -lm 2>/dev/null || cc -O2 -o a3e a3e.c
  ./a3e a3.txt 28 0 2 > run28_0.new; ./a3e a3.txt 28 1 2 > run28_1.new
  [ -f surv_28_0_2.txt ] && [ -f surv_28_1_2.txt ] || { echo "STEP-FAIL k579a (a3e produced no survivors; see $D/K579T)"; exit 1; }
  "$PY" -B ext.py 28 > ext28.new 2>&1
  SIZEONLY=1 "$PY" -B ext.py 28 28 > ext28_sizeonly.new 2>&1
  U() { cat "$@" | grep '^rep' | cut -d' ' -f4- | sort; }
  q=$(U run28_0.new run28_1.new | awk '{q+=$NF} END{print q}'); r=$(U run28_0.new run28_1.new | wc -l)
  ok=1; diff <(U run28_0.new run28_1.new) <(U "$HERE/K579T/run28_0.out" "$HERE/K579T/run28_1.out") >/dev/null || ok=0
  [ "$(tail -n 2 ext28.new | sed 's/ *$//')" = "$(tail -n 2 "$HERE/K579T/ext28.out" | sed 's/ *$//')" ] || ok=0
  [ "$(tail -n 2 ext28_sizeonly.new | sed 's/ *$//')" = "$(tail -n 2 "$HERE/K579T/ext28_sizeonly.out" | sed 's/ *$//')" ] || ok=0
  grep -q 'A3 coverable states 291' ext28.new || ok=0; grep -q 'A3 coverable states 958' ext28_sizeonly.new || ok=0
  [ $ok = 1 ] && echo "STEP-OK K579T implA (a3e+ext.py): $r reps, $q quads (958), 291 coverable, A4 states 0 (cover and size-only); union of slices equals shipped run28_*.out as a multiset" || echo "STEP-FAIL K579T implA";;
# ---- (4) R579b: needs the K579T regen (k579a) -- uses its surv_28_*_2.txt and masks.npy
r579) K="$WK/k579a"; D="$WK/r579b"; rm -rf "$D"; mkdir -p "$D"; cp -R "$HERE/R579b" "$D/R579b"; ln -sfn "$K/K579T" "$D/K579T"
  [ -f "$K/K579T/masks.npy" ] || { echo "STEP-FAIL R579b (run k579a first)"; exit 1; }
  cd "$D/R579b" || exit 2
  "$PY" -B km_a.py 28 > km_a28.new 2>&1
  "$PY" -B km_a2.py 28 2 > km2_n2.new 2>&1
  cc -O2 -o b5m b5m.c -lm 2>/dev/null || cc -O2 -o b5m b5m.c; cc -O2 -o b5m2 b5m2.c -lm 2>/dev/null || cc -O2 -o b5m2 b5m2.c
  ./b5m 28 nc > b5m_28_nc.new 2>&1
  NNR=2 ./b5m2 28 nc > b5m2_n2.new 2>&1
  ok=1
  [ "$(tail -n 1 km_a28.new)" = "$(tail -n 1 $HERE/R579b/km_a28.out)" ] || ok=0
  [ "$(tail -n 1 km2_n2.new)" = "$(tail -n 1 $HERE/R579b/km2_n2.out)" ] || ok=0
  [ "$(tail -n 1 b5m_28_nc.new)" = "$(tail -n 1 $HERE/R579b/b5m_28_nc.out)" ] || ok=0
  [ "$(tail -n 1 b5m2_n2.new)" = "$(tail -n 1 $HERE/R579b/b5m2_n2.out)" ] || ok=0
  [ $ok = 1 ] && echo "STEP-OK R579b: K5^- (km_a.py, b5m.c) and K5^-2 (km_a2.py 28 2, b5m2.c NNR=2): 0 solutions, min |U| 36, final lines equal shipped" || { echo "STEP-FAIL R579b"; tail -n 1 km_a28.new km2_n2.new b5m_28_nc.new b5m2_n2.new; };;
# ---- (2) KILL-ALL7 kb.py, slice i in its own scratch dir (no shared scratch copy)
kb) i=$1; W="$WK/kb$i"; rm -rf "$W"; bash "$HERE/full/kill_all7.sh" "$W" kb$i | tail -n 1 | sed 's/^/STEP-DONE /';;
kbjoin) for i in 0 1 2; do cat "$WK/kb$i/KILL-ALL7/kb_$i.out"; echo; done | grep '^rep' | sort > "$WK/kb_all.rep"; grep '^rep' "$HERE/KILL-ALL7/kb_plain.out" | sort > "$WK/kb_ship.rep"
  n=$(wc -l < "$WK/kb_all.rep"); cmp -s "$WK/kb_all.rep" "$WK/kb_ship.rep" && [ "$n" -ge 11 ] && echo "STEP-OK KILL-ALL7 impl B kb.py plain (3 separate-scratch slices, $n rep lines) equals shipped kb_plain.out" || echo "STEP-FAIL KILL-ALL7 kb ($n rep lines)";;
# ---- (3) KILL-A8 frames x1=1, 3 chunks of 4 orbits in separate scratch dirs
a8x1) c=$1; lo=$((c*4)); hi=$((c*4+3)); W="$WK/a8x1_$c"; rm -rf "$W"; mkdir -p "$W"; cp -R "$HERE/KILL-A8" "$W/KILL-A8"; mkdir -p "$W/CARRIER"; cp -R "$HERE/CARRIER/." "$W/CARRIER/"; cd "$W/KILL-A8" || exit 2
  cc -O2 -o pcf pcf.c; "$PY" -B gen.py 3 >/dev/null 2>&1; "$PY" -B gen.py 4 >/dev/null 2>&1; [ -f dat_4.txt ] || { echo "STEP-FAIL a8x1 gen"; exit 1; }
  : > frames_P4_x1.out; for k in $(seq $lo $hi); do ./pcf dat_4.txt 1 frames_rep.txt $k 2>&1 | grep -v "^pair"; done >> frames_P4_x1.out; echo "STEP-DONE chunk $c orbits $lo-$hi";;
a8x1join) cat "$WK/a8x1_0/KILL-A8/frames_P4_x1.out" "$WK/a8x1_1/KILL-A8/frames_P4_x1.out" "$WK/a8x1_2/KILL-A8/frames_P4_x1.out" > "$WK/a8x1_all.out"
  diff <(grep -v '^pair' "$WK/a8x1_all.out" | sed 's/ *$//' | sort) <(grep -v '^pair' "$HERE/KILL-A8/frames_P4_x1.out" | sed 's/ *$//' | sort) >/dev/null && [ "$(wc -l < "$WK/a8x1_all.out" | tr -d " ")" = 12 ] && echo "STEP-OK KILL-A8 framesx1 (12 x1=1 frame orbits in 3 chunks, equals shipped frames_P4_x1.out as a set of 12 lines, all solutions=0)" || echo "STEP-FAIL KILL-A8 framesx1";;
# ---- TWOSIDE heavy parts (data via ../../data)
two) m=$1; D="$WK/two"; mkdir -p "$D/checks" "$D/data"; [ -d "$D/checks/TWOSIDE" ] || cp -R "$HERE/TWOSIDE" "$D/checks/TWOSIDE"; cp -R "$HERE/../data/." "$D/data/"; cd "$D/checks/TWOSIDE" || exit 2
  case $m in
   rank) "$PY" -B f7r.py rank > f7r_rank.new 2>&1; tail -n 1 f7r_rank.new | grep -q "(0, 41431), (1, 1976), (2, 28)" && echo "STEP-OK TWOSIDE f7r.py rank: hist [(0,41431),(1,1976),(2,28)] = shipped f7rcover.out/f7a" || echo "STEP-FAIL TWOSIDE f7r rank: $(tail -n 1 f7r_rank.new)";;
   cover) "$PY" -B f7r.py cover > f7r_cover.new 2>&1; [ "$(tail -n 1 f7r_cover.new)" = "$(cat f7rcover.out)" ] && echo "STEP-OK TWOSIDE f7r.py cover: hist equals shipped f7rcover.out (0:41431 1:1976 2:28)" || echo "STEP-FAIL TWOSIDE f7r cover: $(tail -n 1 f7r_cover.new)";;
   bk1b) "$PY" -B bk1b.py > bk1b.new 2>&1; 
          "$PY" -B bk2b.py > bk2b.new 2>&1; if diff <(head -n 24 bk2b.new | sed 's/ *$//') <(sed 's/ *$//' bk2b.out) >/dev/null; then b2=1; else b2=0; fi
          # bk1b prints "b t nsurv N deficit D ..."; bk2b.out is "b t N flag" (deficit is defined differently in the two scripts): compare survivor counts N per cell
          if diff <(awk '{print $1,$2,$4}' bk1b.new) <(awk '{print $1,$2,$3}' bk2b.out) >/dev/null; then b1=1; else b1=0; fi
          [ $b1 = 1 ] && [ $b2 = 1 ] && echo "STEP-OK TWOSIDE bk1b.py and bk2b.py: 24 cells (b=5..8, t=1..6) both equal shipped bk2b.out (survivor counts per cell; the deficit column is defined differently in the two scripts and is not compared)" || echo "STEP-FAIL TWOSIDE bk1b/bk2b (bk1b==shipped:$b1 bk2b==shipped:$b2)";;
  esac;;
*) echo "unknown step $N"; exit 2;;
esac
