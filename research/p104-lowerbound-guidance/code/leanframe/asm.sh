#!/bin/bash
# usage: asm.sh N out.lean [chunk]
cd code/leanframe
python3 -I gen.py $1 <tmpdir> $3 >/dev/null
cat head.lean <tmpdir> tail_a.lean <tmpdir> tail_b.lean > $2
