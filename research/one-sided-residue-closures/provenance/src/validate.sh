#!/bin/bash
# Compiles s3z/s4z and reproduces one known crack and one known pass of the (6,6,4) s0 span (s4z with d=0 is the 3-flat case).
set -e; cd "$(dirname "$0")"; B=$(mktemp -d); trap 'rm -rf "$B"' EXIT
gcc -O2 -march=native -o $B/s4z s4z.c; gcc -O2 -march=native -o $B/s3z s3z.c
# crack: V1 rep 82, T=5 -> "CRACK? target 5 span 5 ... V2idx 103676"
for p in s3z s4z; do
  out=$(ONLY=82 EXITCRACK=1 timeout 100 $B/$p data88.txt 6 6 4 0 88 5 1 0 2>/dev/null)
  echo "$out" | grep -q "CRACK? target 5 span 5 rep 82 V2idx 103676" || { echo "FAIL crack $p"; exit 1; }
  echo "ok crack  $p"
done
# pass: slice 3 of 50 of rep 82 at T=6 -> no crack, max span 4 (equal for s3z and s4z)
for p in s3z s4z; do
  out=$(ONLY=82 JMOD=50 JREM=3 timeout 100 $B/$p data88.txt 6 6 4 0 88 6 1 0 2>/dev/null)
  echo "$out" | grep -q "CRACK?" && { echo "FAIL pass $p (crack)"; exit 1; }
  echo "$out" | grep OVERALL | grep -q "max span 4 " || { echo "FAIL pass $p"; exit 1; }
  echo "ok pass   $p"
done
echo VALIDATE OK
