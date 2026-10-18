# Spot check of the exact-rank formula (README INPUT-2): rank_F2 B[R,A] equals rank B[V\C(Z_R), V\C(Z_A)] (the label-span form) on random blocks, and
# r = 9 - d - tau with tau in {0,1} (tau = 0 if delta_A = 0) whenever delta_A <= 1.   usage: rank_formula_check.py (prints bad = 0 on success)
import sys, random
from setup9 import *
from common2 import B0rows, rank_f2
for unit in ['P112','P104']:
    L, v, G, frames, nbar, h, basis, cls = load(unit)
    full=(1<<v)-1; B0=B0rows(L); ks=sorted(cls)
    def rk(R,A):
        Rl=[t for t in range(v) if R>>t&1]; Al=[s for s in range(v) if A>>s&1]
        return rank_f2([sum(1<<i for i,s in enumerate(Al) if B0[t]>>s&1) for t in Rl])
    def Z(R): return [c for c in ks if not cls[c]&R]
    def CZ(z):
        x=0
        for c in z: x|=cls[c]
        return x
    random.seed(3); bad=0; n=0; hist={}
    for _ in range(3000):
        # random R: complement of union of a few classes + random deletions
        R=full
        for _ in range(random.randint(0,3)): R&=~cls[random.choice(ks)]
        for _ in range(random.randint(0,40)): R&=~(1<<random.randrange(v))
        A=full
        for _ in range(random.randint(0,2)): A&=~cls[random.choice(ks)]
        for _ in range(random.randint(0,30)): A&=~(1<<random.randrange(v))
        if not R or not A: continue
        zr, za = Z(R), Z(A)
        r1=rk(R,A); r2=rk(full^CZ(zr), full^CZ(za)); n+=1
        if r1!=r2: bad+=1
        d=(len(zr)+1).bit_length()-1; dA=(len(za)+1).bit_length()-1
        if dA<=1:
            # tau via exact: r = 9-d-tau
            tau=9-d-r1
            hist[(d,dA,tau)]=hist.get((d,dA,tau),0)+1
            if tau not in (0,1) or (dA==0 and tau!=0): bad+=1
    print(unit,'h',h,'tests',n,'bad',bad, sorted(hist.items())[:20])
    assert bad == 0
