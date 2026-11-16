#!/bin/sh
# frame-exempt + one free line (row 398 small flats {6},{1}); P=4
cd ../KILL-A8
for k in $(seq $1 $2); do ./pcf dat_4.txt 1 frames_rep.txt $k 2>&1 | grep -v "^pair"; done >> frames_P4_x1.out
