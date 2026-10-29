#!/bin/bash
# Target completeness for SERVE (rows 596-601): only root (with r covered) and D7 directions have a two-7-flat leftover <= 22.
# Reruns pairmin.c over every pair of 7-flats for each non-root perp-type and asserts the minimum leftovers.
set -u; H=$(cd "$(dirname "$0")" && pwd); T=$(mktemp -d); cc -O2 -o "$T/pm" "$H/pairmin.c" || { echo "FAIL pairmin build"; exit 1; }
want(){ case $1 in D7) echo 14;; A7) echo 25;; A1A6) echo 31;; A1A2A4) echo 38;; A4A3) echo 36;; D5A2) echo 31;; E6A1) echo 23;; E7) echo 1;; D6) echo 26;; E6) echo 24;; esac; }; bad=0
while read n a b c d e f g h; do m=$(timeout 1100 "$T/pm" $a $b $c $d $e $f $g $h | sed -n 's/.*min leftover=\([0-9]*\).*/\1/p'); w=$(want $n); [ "$m" = "$w" ] || { echo "FAIL pairmin $n got $m want $w"; bad=1; }; done < "$H/types.txt"
[ $bad = 0 ] && echo "PASS pairmin: min two-7-flat leftovers D7 14, E6A1 23, E6 24, A7 25, D6 26, D5A2 31, A1A6 31, A4A3 36, A1A2A4 38 (E7 = root-type 1); only roots and D7 are <= 22"
