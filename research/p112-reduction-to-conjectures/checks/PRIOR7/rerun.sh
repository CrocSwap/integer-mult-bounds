#!/bin/bash
# FULL=1 helper: independent s3z rerun of the (6,6,5) s0 span at target 7 (48 rems x JMOD 4 slices, <=20 min each, 3 parallel).
# PASS iff every slice prints OVERALL with no "CRACK?" (=> span <= 6), which kills the 7 rows 381, 384, 576, 577, 578, 580, 581 (d = 8 >= 7).
set -u; H=$(cd "$(dirname "$0")" && pwd); W=$(mktemp -d); cd "$W"; cp "$H/s3z.c" "$H/gens.txt" .; gunzip -c "$H/data88.txt.gz" > data88.txt; cc -O2 -o s3z s3z.c
for r in $(seq 0 47); do for j in 0 1 2 3; do echo "$r $j"; done; done | xargs -P 3 -L 1 sh -c 'JMOD=4 JREM=$1 timeout 1150 ./s3z data88.txt 6 6 5 0 88 7 48 $0 > s$0_$1.out 2>/dev/null'
inc=$(for f in s*_*.out; do grep -q "^OVERALL" $f || echo $f; done | wc -l); cr=$(grep -l "CRACK?" s*_*.out | wc -l)
[ "$inc" = 0 ] && [ "$cr" = 0 ] && echo "PASS prior7: (6,6,5) s0 span <= 6 at target 7 (192 slices, 0 cracks)" || echo "FAIL prior7: incomplete=$inc cracks=$cr"
