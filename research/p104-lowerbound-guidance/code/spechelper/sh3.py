import sys, io, contextlib
sys.path.insert(0,'<research-tree>/cards/WILD/UNIMODEL/runggen')
with contextlib.redirect_stdout(io.StringIO()): import rg1
from rg1 import add, ceiling, fm, nat, C7113, D
print('control X112+HS (Lean .0093454):',fm(ceiling(add((1,C7113),(-1,nat(112,0))))))
for S in ('60.982','200','799.010'):
    print('S',S,'max form',fm(ceiling(add((1,C7113),(-1,nat(112,D(S),False))))),'| +HS additive [CONJ]',fm(ceiling(add((1,C7113),(-1,nat(112,D(S),True))))))
