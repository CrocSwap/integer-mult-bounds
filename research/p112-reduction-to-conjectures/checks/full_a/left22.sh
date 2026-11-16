#!/usr/bin/env bash
# LEFT22: minimal two-7-flat leftovers <=22 for a root and a norm-4 (D7-type) vector; impl A (A.c) and impl B (B.py) rerun, tables regenerated.
. "$(dirname "$0")/lib.sh"; D="$WK/left22"; mkdir -p "$D"; S="$FA/left22"; cd "$D"
cp "$S"/{A.c,B.py,mk.py,lines.txt} .
cc -O2 -o A A.c || { fail LEFT22_build "cc"; exit 1; }
./A 22 root > A_root22.txt 2>/dev/null & ./A 16 root > A_root16.txt 2>/dev/null & ./A 22 d7 > A_d7_22.txt 2>/dev/null &
$PY -B B.py 22 d7 > B_d7.log 2>&1 &
wait
eq LEFT22_A_root "$D/A_root22.txt" "$S/A_root22.txt" "impl A (A.c) minimal root leftovers <=22 = pinned table (9387 sets)"
eq LEFT22_A_root16 "$D/A_root16.txt" "$D/A_root22.txt" "impl A: K=16 and K=22 root tables identical (no minimal leftover of size 17-22)"
eq LEFT22_A_d7 "$D/A_d7_22.txt" "$S/A_d7_22.txt" "impl A minimal D7 leftovers <=22 = pinned table (6021 sets)"
want LEFT22_A_root_hist "$(cut -d' ' -f1 A_root22.txt | sort -n | uniq -c | awk '{printf "%s:%s ",$2,$1}')" "8:315 12:5040 16:4032 " "impl A root size histogram"
want LEFT22_A_d7_hist "$(cut -d' ' -f1 A_d7_22.txt | sort -n | uniq -c | awk '{printf "%s:%s ",$2,$1}')" "14:1 20:532 21:1344 22:4144 " "impl A D7 size histogram"
( $PY -B B.py 22 root > B_root.log 2>&1 ) # ~75 s
want LEFT22_B_root "$(grep 'minimal leftovers' B_root.log)" "minimal leftovers Counter({12: 5040, 16: 4032, 8: 315})" "impl B (B.py) root histogram"
want LEFT22_B_root_rank "$(grep '^size,rank' B_root.log | sed 's/^[^[]*//')" "[((8, 4), 315), ((12, 6), 5040), ((16, 6), 4032)]" "impl B root (size,rank) of label span"
want LEFT22_B_d7 "$(grep 'minimal leftovers' B_d7.log)" "minimal leftovers Counter({22: 4144, 21: 1344, 20: 532, 14: 1})" "impl B D7 histogram"
want LEFT22_B_d7_rank "$(grep '^size,rank' B_d7.log | sed 's/^[^[]*//')" "[((14, 8), 1), ((20, 8), 84), ((20, 9), 448), ((21, 9), 1344), ((22, 8), 420), ((22, 9), 3724)]" "impl B D7 (size,rank)"
want LEFT22_B_orbits "$(grep -h '^orbits under' B_root.log B_d7.log | tr '\n' ' ')" "orbits under Stab(h) by size {8: 1, 12: 4, 16: 3} orbits under Stab(h) by size {14: 1, 20: 2, 21: 2, 22: 4} " "impl B orbit counts under Stab(h)"
$PY -B - <<PYEOF
import pickle,sys
ok=all(pickle.load(open('$D/B_%s.pkl'%n,'rb'))==pickle.load(open('$S/B_%s.pkl'%n,'rb')) for n in ('root22','d722'))
print(('PASS' if ok else 'FAIL')+' FULL-A LEFT22_B_pkl: regenerated impl-B leftover pickles equal pinned B_root22.pkl / B_d722.pkl')
PYEOF
# regenerate the W-transported mask tables used by SERVE (impl A) and compare sha256 with the pinned hashes
$PY -B mk.py > mk.log 2>&1
want LEFT22_roots_bin "$(shasum -a 256 roots.bin | cut -c1-64)" cb34d775e7b3e22a35323bba6bf3fa1753038ff97fe8a071529fc2817cd090df "roots.bin (120 x 9387 masks) sha256"
want LEFT22_d7_bin "$(shasum -a 256 d7.bin | cut -c1-64)" 2e5cc3d2df46309f417d2d9715e6fb196ad44908e802cacd29788bb3222e8f55 "d7.bin (1080 x 6021 masks) sha256"
want LEFT22_counts "$(cat counts.txt)" "120 9387 1080 6021" "orbit/table counts"
