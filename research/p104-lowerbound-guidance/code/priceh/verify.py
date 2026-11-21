# PRICEH verify.py: independent exact check of mol_h*.json (stdlib only): decomposition identity on all pairs, sep weight, nonnegativity.
import sys, json
from fractions import Fraction as Fr
def check(h):
    d=json.load(open(f'mol_h{h}.json')); assert d['h']==h
    betas={}
    for L in range(1,h):
        m=d['mol'][str(L)]; D,E,W=m['D'],m['E'],m['W']
        assert D>0 and E>=0 and all(w>0 for _,w in W)
        for i in range(h+1):
            for j in range(h+1):
                dec=sum(w for S,w in W if ((S>>i)&1)!=((S>>j)&1))
                dd=abs(i-j)
                assert dec==D*min(L,dd)+E*min(1,dd),(h,L,i,j)
        b=lambda S,i:(S>>i)&1
        sep=sum(w for S,w in W if (b(S,1) and b(S,h) and not b(S,0) and not b(S,h-1)) or ((not b(S,1)) and (not b(S,h)) and b(S,0) and b(S,h-1)))
        if L<=h-2: assert D+E<=2*sep,(h,L,sep,D,E)
        else: assert sep==0 and E==0
        betas[L]=Fr(E,D)
    return betas
if __name__=="__main__":
    for h in sys.argv[1:]:
        bt=check(int(h)); print('h',h,'OK betas',{L:str(b) for L,b in bt.items()})
