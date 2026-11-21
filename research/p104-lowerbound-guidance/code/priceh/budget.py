# PRICEH budget.py [C float, double precision]: kappa0 = sup of kappa in (0,0.2] where bud_h(1-kappa) < 0 (bud >= 0 above kappa0)
import json
from fractions import Fraction as Fr
def bud(h,betas,s):
    g=lambda d: float(d)**s
    cc=lambda L: 2*g(L)-g(L-1)-g(L+1)
    return cc(1)-sum(betas[L]*cc(L) for L in range(2,h-1))
for h in range(4,20):
    d=json.load(open(f'mol_h{h}.json'))
    betas={int(L):float(Fr(m['E'],m['D'])) for L,m in d['mol'].items()}
    N=20000; k0=0.0
    for i in range(N,0,-1):
        k=0.2*i/N
        if bud(h,betas,1-k)<0: k0=k; break
    print(h,'kappa0 ~',round(k0,5),' bud(.0093454):',round(bud(h,betas,1-0.0093454),6),' bud(.0339):',round(bud(h,betas,1-0.0339),6),flush=True)
