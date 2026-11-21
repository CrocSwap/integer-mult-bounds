#!/bin/bash
cd code/drat55
m=$1
grep -q "^f$m	" results.tsv 2>/dev/null && exit 0
python3 mkcube.py $m work/f$m.cnf
./cube.sh work/f$m.cnf
rm -f work/f$m.cnf
