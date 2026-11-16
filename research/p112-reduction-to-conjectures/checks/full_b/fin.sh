#!/usr/bin/env bash
# fin.sh WK MODE [args] -- FINITE (t.c) and FINITE2 (f2.cpp) reruns in a scratch dir WK/fin (layout FINITE, FINITE2, SIX/gens.txt as f2.cpp expects)
# MODES: build | chk TOOL "d1 d2 p R" SHIPPED_FILE LABEL | chunk TOOL lo hi | join
set -u; WK=$1; M=$2; shift 2; HERE=$(cd "$(dirname "$0")/.." && pwd); F="$WK/fin"
rl() { grep '^rep' "$1" | sed 's/ *$//'; }
case $M in
build) rm -rf "$F"; mkdir -p "$F/SIX" "$F/ch"; cp -R "$HERE/FINITE" "$F/FINITE"; cp -R "$HERE/FINITE2" "$F/FINITE2"; cp "$HERE/FINITE/gens.txt" "$F/SIX/gens.txt"
  (cd "$F/FINITE" && rm -f t && cc -O2 -o t t.c -lm 2>&1 | grep -c error); (cd "$F/FINITE2" && rm -f f2 && g++ -std=c++17 -O2 -o f2 f2.cpp 2>&1 | grep -c error); ls "$F/FINITE/t" "$F/FINITE2/f2" >/dev/null && echo built;;
chk) T=$1; A=$2; SH=$3; LB=$4; if [ $T = t ]; then cd "$F/FINITE" && ./t $A > "../chk_$LB.t" 2>/dev/null; o="$F/chk_$LB.t"; else cd "$F/FINITE2" && ./f2 $A > "../chk_$LB.f" 2>/dev/null; o="$F/chk_$LB.f"; fi
  # per-rep comparison: t prints "rep N lines L orbit O active A maxrank R"; f2 prints "rep N lines L witnesses W maxrank R maxdirs D"; compare to shipped file of the same tool
  if diff <(rl "$o") <(rl "$HERE/$SH") >/dev/null && [ "$(grep OVERALL "$o" | sed 's/reps .*max real/max real/;s/ *$//')" = "$(grep OVERALL "$HERE/$SH" | sed 's/reps .*max real/max real/;s/ *$//')" ]; then echo "STEP-OK $LB ($T $A): per-rep lines and OVERALL equal shipped $SH: $(grep OVERALL "$o" | sed 's/.*max real/max real/')"; else echo "STEP-FAIL $LB ($T $A) differs from shipped $SH"; fi;;
chunk) T=$1; lo=$2; hi=$3; run() { l=$1; h=$2; out="$F/ch/$T.$l.$h.out"
    if [ $T = t ]; then (cd "$F/FINITE" && timeout 1200 ./t 6 6 2 7 $l $h > "$out" 2>/dev/null); else (cd "$F/FINITE2" && timeout 1200 ./f2 6 6 2 7 $l $h > "$out" 2>/dev/null); fi
    rc=$?; if [ $rc = 124 ]; then rm -f "$out"; if [ $((h-l)) -gt 1 ]; then m=$(((l+h)/2)); run $l $m; run $m $h; else echo "TIMEOUT1200 $T rep $l" > "$F/ch/$T.$l.$h.timeout"; fi; fi; }
  run $lo $hi; echo "STEP-DONE chunk $T $lo $hi";;
join) fail=0; for T in t f2; do rm -f "$F/b7_$T.reps"; cat "$F"/ch/$T.*.out 2>/dev/null | grep '^rep' | sort -n -k2,2 -u > "$F/b7_$T.reps"; n=$(wc -l < "$F/b7_$T.reps"); to=$(ls "$F"/ch/$T.*.timeout 2>/dev/null | wc -l); echo "b7 $T: $n rep lines, $to single-rep timeouts"; done
  # shipped
  for f in "$HERE"/FINITE2/rem_*.out "$HERE"/FINITE2/one_*.out "$HERE"/FINITE2/b7_a.out "$HERE"/FINITE2/b7_b.out; do cat "$f"; echo; done | grep '^rep' | sed 's/ *$//' | sort -n -k2,2 -u > "$F/ship_f2.reps"; grep '^rep' "$HERE/FINITE/b_p2_R7.out" | sed 's/ *$//' | sort -n -k2,2 -u > "$F/ship_t.reps"
  # shipped logs are gappy for f2 (155 of 160 reps: boundary reps lost), so: every shipped line must occur in the rerun, and the rerun must be complete
  for T in t f2; do miss=$(comm -13 <(sed 's/ *$//' "$F/b7_$T.reps" | sort) <(sort "$F/ship_$T.reps") | wc -l | tr -d " "); n=$(wc -l < "$F/b7_$T.reps" | tr -d " "); if [ "$miss" = 0 ] && [ "$n" -ge 159 ]; then echo "b7 $T: rerun has $n reps and contains every shipped rep line (shipped has $(wc -l < "$F/ship_$T.reps" | tr -d " "))"; else echo "b7 $T: shipped lines missing from rerun: $miss, reps $n"; fail=1; fi; done
  mx=$(awk '{for(i=1;i<=NF;i++) if($i=="maxrank" && $(i+1)>m) m=$(i+1)} END{print m+0}' "$F/b7_t.reps"); mf=$(awk '{for(i=1;i<=NF;i++) if($i=="maxrank" && $(i+1)>m) m=$(i+1)} END{print m+0}' "$F/b7_f2.reps")
  mm() { awk '{l="";r="";for(i=1;i<=NF;i++){if($i=="lines")l=$(i+1);if($i=="maxrank")r=$(i+1)} print l,r}' "$1" | sort; }; mm "$F/b7_t.reps" > "$F/mt.txt"; mm "$F/b7_f2.reps" | grep -v '^0 0$' > "$F/mf.txt"; diff "$F/mt.txt" "$F/mf.txt" > "$F/rdiff.txt"
  [ ! -s "$F/rdiff.txt" ] && echo "b7: multiset of per-rep (lines,maxrank) of t.c and f2.cpp agree on all 159 nonempty reps (rep numbering differs by the empty rep 0; index-free comparison)" || { echo "b7: t.c/f2.cpp per-rep (lines,maxrank) DISAGREE"; fail=1; }
  [ $fail = 0 ] && echo "STEP-OK FINITE/FINITE2 beta R=7 p=2: both implementations rerun in chunks, per-rep lines equal shipped, max span t=$mx f2=$mf" || echo "STEP-FAIL FINITE/FINITE2 beta R=7 p=2";;
esac
