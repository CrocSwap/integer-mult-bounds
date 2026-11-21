"""SCHERK sk3 (SIZING only, rows NOT proved): ms9 witness LP + DYADIC rows + DEEP row  #{roles with D >= f*k} >= beta*k.
Sizes what any crossing-type law (deep roles forced by rank of an off-diagonal block of G) could buy.  usage: sk3.py f beta k..."""
import os,sys
os.environ.setdefault('FAM','coord,pfix,shal')
sys.argv=[sys.argv[0]]+sys.argv[1:]
f,beta=float(sys.argv[1]),float(sys.argv[2])
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import sk2
from math import ceil,log2
sys.path.insert(0,sk2.BASE+'UNIMODEL/routes/mainscan');import ms9
class LP(ms9.LP):
    def __init__(s_,k):
        super().__init__(k)
        for J in range(1,ceil(log2(k))+1):s_.X.append((lambda D,c=2**(J+1):float(min(D,c)-1),lambda L:0.0,lambda D:0.0,0.0,float(sk2.RJ(k,J))))
        s_.X.append((lambda D,d0=ceil(f*k):float(D>=d0),lambda L:0.0,lambda D:0.0,0.0,beta*k))
for k in [int(a) for a in sys.argv[3:]]:
    res=LP(k).solve()
    if res is None:print('f',f,'beta',beta,'k',k,'INFEASIBLE',flush=True);continue
    B,p,sup=res;print('f',f,'beta',beta,'k',k,'cB',round(104*B/k,3),sup if os.environ.get('SUP') else '',flush=True)
