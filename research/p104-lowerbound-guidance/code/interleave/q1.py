import sys,signal; signal.alarm(600)
sys.path.insert(0,'<research-tree>/cards/WILD/UNIMODEL/runggen')
import io,contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import rg1
from rg1 import *
T2={1:D(2),2:D(-1)}  # 2-2^s : min price of one stop (climb-2 register)
for S in ('0','865.58','1029.6','1189'):
    for hs in (True,False):
        f=add((1,C7113),(-1,nat(112,D(S),hs)))
        print(f'#7113 X112 S={S} HS={hs}:',fm(ceiling(f)))
print('per-port CC floor 104(2-2^s) vs 104h at .99:',float(104*ev(T2,s99)),float(104*ev(H,s99)))
