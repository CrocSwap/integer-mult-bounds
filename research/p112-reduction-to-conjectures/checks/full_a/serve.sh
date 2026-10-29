#!/usr/bin/env bash
# SERVE / SERVE2 / SERVE3 (rows 596-601): exact max served(E) over unions of label-flats; K9 graphic tests.  Needs left22.sh to have run (tables in $WK/left22 and pickles).
. "$(dirname "$0")/lib.sh"; L="$WK/left22"; SA="$WK/serveA"; S="$FA/serve"; S2="$FA/serve2"; S3="$FA/serve3"
[ -f "$L/roots.bin" ] || { fail SERVE_prereq "run left22.sh first"; exit 1; }
rm -rf "$SA"; mkdir -p "$SA"; cd "$SA"; cp "$L"/{lines.txt,rootidx.txt,roots.bin,d7.bin} .; cp "$S"/{serve.c,serveB.py,k9.py,k9ctl.py} .
cc -O2 -o serveA serve.c || { fail SERVE_build cc; exit 1; }
mx() { awk '{for(i=1;i<=NF;i++) if($i=="max"&&$(i+1)=="served"){print $(i+2)}}' "$@" | sort -n | tail -1; }
# ---- impl A: flat family inventories
./serveA 0 5 > inv5.out 2>&1; ./serveA 0 6 > inv6.out 2>&1
eq SERVE_A_inv5 inv5.out "$S/inv5.out" "rank-5 flat family 2898178 sets / 19 W-orbits"
eq SERVE_A_inv6 inv6.out "$S/inv6.out" "rank-6 flat family 777241 sets / 17 W-orbits"
# ---- impl A: exhaustive maxima.  596: F4+F4 in 3 parallel chunks; others one process each
./serveA 1 4 4 0 5 2>/dev/null > c0 & ./serveA 1 4 4 5 10 2>/dev/null > c1 & ./serveA 1 4 4 10 15 2>/dev/null > c2 & wait
cat c0 c1 c2 > r596.out; cat "$S/r596_a.out" "$S/r596_b.out" > e596.out
eq SERVE_A_596 r596.out e596.out "row 596 (F4 u F4, all 15 orbit reps x all 1935706 second flats) = pinned r596_a+b.out"
want SERVE_A_596_max "$(mx r596.out)" 30 "row 596 exact max served (<36 required)"
./serveA 2 5 3 2>/dev/null > r597.out & ./serveA 1 5 3 2>/dev/null > r599.out & ./serveA 2 6 2 2>/dev/null > r600.out & wait
cat "$S/r597_a.out" "$S/r597_b.out" > e597.out
eq SERVE_A_597 r597.out e597.out "rows 597/598 (F5 u 3 lines, 19 orbit reps) = pinned r597_a+b.out"
want SERVE_A_597_max "$(mx r597.out)" 23 "rows 597/598 exact max served (<36)"
eq SERVE_A_599 r599.out "$S/r599.out" "row 599 (F5 u F3) = pinned r599.out"
want SERVE_A_599_max "$(mx r599.out)" 30 "row 599 exact max served (<36)"
eq SERVE_A_600 r600.out "$S/r600.out" "rows 600/601 (F6 u 2 lines, 17 orbit reps) = pinned r600.out"
want SERVE_A_600_max "$(mx r600.out)" 38 "rows 600/601 exact max served"
want SERVE_A_600_reps36 "$(awk '{for(i=1;i<=NF;i++) if($i=="max"&&$(i+1)=="served"&&$(i+2)>=36)n++}END{print n+0}' r600.out)" 1 "rows 600/601: number of orbit reps whose max served is >=36 (only the 20-line orbit rep, orbit size 40320)"
# ---- all served sets for E = F6 rep u 2 lines (7140 sets, served >=36); F = common part of the HIT lines
./serveA 2 6 2 11 12 36 2>/dev/null > hits600.txt
eq SERVE_A_hits600 hits600.txt "$S/hits600.txt" "7140 pairs (a,b) with served(F u {a,b}) >=36 for the 20-line orbit rep = pinned hits600.txt"
F=$($PY -B -c "
import sys
sets=[set(l.split()[5:]) for l in open('hits600.txt') if l.startswith('HIT')]
print(' '.join(sorted(set.intersection(*sets),key=int)))")
echo "$F" | ./serveA 5 36 2>/dev/null > all600.txt
eq SERVE_A_all600 all600.txt "$S/all600.txt" "7140 served sets (lists of served roots / norm-4 vectors) = pinned all600.txt"
# ---- phase 2: long jobs through a pool of at most 3 background processes
pool() { while [ "$(jobs -rp | wc -l)" -ge 3 ]; do sleep 2; done; "$@" & }
jb_serveB() { $PY -B serveB.py < "$S/ctl.txt" > ctlB.out 2>/dev/null; }
jb_k9A() { $PY -B k9.py all600.txt > k9A.out 2>/dev/null; $PY -B k9ctl.py > k9ctl.out 2>/dev/null; }
S2D="$WK/serve2"; rm -rf "$S2D"; mkdir -p "$S2D"; cp "$S2"/{setup2.py,k9b.py,s2.c,data.txt,k9chunk.py,k9ctl.py} "$S2D"/; cp all600.txt "$S2D"/
jb_k9b() { ( cd "$S2D" && $PY -B k9chunk.py "$2" "$1" 3 > "k9b.$2.$1.out" 2>&1 ); }   # args: chunk file
pool jb_serveB
pool jb_k9A
# SERVE2 setup (fast, inline): regenerate data.txt with setup2.py's own E8 build, compare with the shipped one
( cd "$S2D" && cp data.txt data_pinned.txt && $PY -B setup2.py > setup2.log 2>&1; cmp -s data.txt data_pinned.txt && echo DATA-OK > data.chk || echo DATA-BAD > data.chk
  cc -O2 -o s2 s2.c 2>/dev/null; ./s2 pair 4 4 1000 0 0 > s2inv4.out 2> s2inv4.err; ./s2 pair 5 3 1000 0 0 > /dev/null 2> s2inv5.err
  $PY -B k9ctl.py > k9ctl.out 2>&1 )
for c in 0 1 2; do pool jb_k9b $c all600.txt; done
# SERVE3: own labelling; fast tables rebuilt from LEFT22 impl-B pickles; every served count rechecked against the full table
S3D="$WK/serve3"; rm -rf "$S3D"; mkdir -p "$S3D"; cp "$S3"/{build.py,s3.c} "$S3D"/; cp "$S2"/{setup2.py,k9b.py,k9chunk.py} "$S3D"/; cp "$S2"/data.txt "$S3D"/data.txt; 
jb_s3() { cd "$S3D"
  $PY -B setup2.py > /dev/null 2>&1; cmp -s data.txt "$S2/data.txt" && echo DATA-OK > data.chk || echo DATA-BAD > data.chk
  $PY -B build.py > build.log 2>&1; shasum -a 256 tabs.bin | cut -d' ' -f1 > tabs.sha
  cc -O2 -o s3 s3.c
  ./s3 tpair 4 4 1000 0 10 > r596.out 2>/dev/null; ./s3 tlines 5 3 1000 > r597.out 2>/dev/null; ./s3 tpair 5 3 1000 > r599.out 2>/dev/null
  ./s3 tlines 6 2 36 0 14 emit > r600.out 2>/dev/null; ./s3 tcheck 4 500 > tcheck.out 2>/dev/null; }
pool jb_s3
wait
want SERVE_B_ctl "$(tr '\n' ' ' < ctlB.out)" "$(tr '\n' ' ' < "$S/ctlA.out")" "impl B (serveB.py, table-free, python) served() of the 7 control sets (Q, 596/597/599 argmax, F6, 600 argmax, hand 7) = pinned impl A values 12 30 23 30 36 38 7"
: > ctlA.re; while read -r line; do echo $line | ./serveA 3 2>/dev/null >> ctlA.re; done < "$S/ctl.txt"
eq SERVE_A_ctl ctlA.re "$S/ctlA.out" "impl A served() of the 7 control sets = pinned ctlA.out"
want SERVE_A_K9 "$(tail -1 k9A.out)" "sets with K9 embedding: 0 of 3571" "impl A K9 test (k9.py) on the 3571 distinct served sets of rows 600/601"
want SERVE_A_K9_ctl "$(tail -1 k9ctl.out)" CTL-OK "impl A K9 test controls: A8 root system embeds K9, E6 does not (36 lines each)"
want SERVE2_data "$(cat "$S2D/data.chk")" DATA-OK "setup2.py (own E8, labels, reflections, D7) regenerates the shipped data.txt"
want SERVE2_flats4 "$(head -1 "$S2D/s2inv4.err") $(sed -n 2p "$S2D/s2inv4.err")" "flats s=4: 1896435 orbits: 10" "s2.c own RREF flat enumeration + union-find orbits, rank 4, after its domination filter (impl A raw family: 1935706 / 15 orbits)"
want SERVE2_flats5 "$(head -1 "$S2D/s2inv5.err")" "flats s=5: 2854572" "s2.c own flat enumeration, rank 5, after domination filter (impl A raw family 2898178)"
want SERVE2_K9_ctl "$(tail -1 "$S2D/k9ctl.out")" CTL-OK "impl B K9 test (k9b.py) controls: A8 embeds K9, E6 does not"
kt() { cat "$1"/k9b.$2.[012].out | awk '{s+=$4; g+=$6; t=$8} END{print s, g, t}'; }
want SERVE2_K9 "$(kt "$S2D" all600.txt)" "3571 0 3571" "impl B (k9b.py, own labels + star coordinates) on impl A's regenerated served sets: sets, graphic, total"
# SERVE3 comparisons
n3() { sed 's/ n>=thr:[0-9]*//' "$1"; }
cat "$S3/r596_a.out" "$S3/r596_b.out" "$S3/r596_c.out" > "$S3D/e596.out"
want SERVE3_data "$(cat "$S3D/data.chk")" DATA-OK "SERVE3 regenerated data.txt equals the shipped one"
want SERVE3_tabs "$(cat "$S3D/tabs.sha")" 0fa7e9a6efab752117f9856075f8d9d788bc483eeced9a7e7d3940d6be95ccf8 "tabs.bin (impl-B tables mapped into SERVE2 labelling) sha256 = shipped"
want SERVE3_xcheck "$(grep -c ': True' "$S3D/build.log")" 2 "build.py cross-check: transported impl-B tables equal impl A roots.bin/d7.bin (roots as sets, D7 as multiset)"
want SERVE3_596 "$(n3 "$S3D/r596.out" | cksum)" "$(n3 "$S3D/e596.out" | cksum)" "row 596 maxima per orbit rep = pinned r596_a/b/c (md5 of lines without the thr counter)"
want SERVE3_597 "$(n3 "$S3D/r597.out" | cksum)" "$(n3 "$S3/r597.out" | cksum)" "rows 597/598 maxima per orbit rep = pinned r597.out"
want SERVE3_599 "$(n3 "$S3D/r599.out" | cksum)" "$(n3 "$S3/r599.out" | cksum)" "row 599 maxima per orbit rep = pinned r599.out"
eq SERVE3_600 "$S3D/r600.out" "$S3/r600.out" "rows 600/601: per-rep maxima and all 4950 served-set lines of the 14 reps = pinned r600.out"
want SERVE3_maxima "$(for f in r596 r597 r599 r600; do grep -o 'max [0-9]* (full' "$S3D/$f.out" | awk '{print $2}' | sort -n | tail -1; done | tr '\n' ' ')" "30 23 30 38 " "SERVE3 exact maxima for rows 596 / 597-598 / 599 / 600-601 (required 36)"
want SERVE3_tcheck "$(cat "$S3D/tcheck.out")" "tcheck bad=0" "fast served3 equals full-table served on 500 random E"
want SERVE3_recheck "$(grep -c 'max \([0-9]*\) (full-table recheck \1)' "$S3D/r596.out") $(grep -c . "$S3D/r596.out")" "10 10" "every reported max in r596 equals its full-table recheck"
# SERVE3 own served sets of rows 600/601 -> impl B K9 test (3 chunks)
cp "$S3D/r600.out" "$S3D/s3_600.txt"; grep '^E' "$S3D/r600.out" > "$S3D/s3_600.txt"
for c in 0 1 2; do ( cd "$S3D" && $PY -B k9chunk.py s3_600.txt $c 3 > "k9b.$c.out" 2>&1 ) & done; wait
want SERVE3_K9 "$(cat "$S3D"/k9b.[012].out | awk '{s+=$4; g+=$6; t=$8} END{print s, g, t}')" "3571 0 3571" "K9 test (k9b.py) on SERVE3's own regenerated served sets: sets, graphic, total"
