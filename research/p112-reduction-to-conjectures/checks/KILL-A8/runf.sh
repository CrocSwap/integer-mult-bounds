#!/bin/sh
cd ../KILL-A8
for k in 0 1 2 3 4 5 6 7 8 9 10 11; do ./pcf dat_$1.txt 0 frames_rep.txt $k 2>&1 | grep -v "^pair"; done > frames_P$1.out
