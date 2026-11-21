#!/bin/bash
# regenerate Nov15/BlockComplete.lean: python3 gen_block.py <tmpdir> 64 ; then ./asm.sh OUT
cd code/leanblock
python3 - "$1" <<'PY'
import sys
h=open('head.lean').read().replace('\nend BlockComplete\n','\n')
m=open('mid.lean').read()
d=open('<tmpdir>').read()
t=open('<tmpdir>').read()
tl=open('tail.lean').read()
i=d.index('def wt0'); open(sys.argv[1],'w').write(h+d[:i]+m+d[i:]+'\n'+t+tl)
PY
