"""Tight B-linear covering form: for x in L4=E8/4E8, t in P with <x,c_t> != 0 mod 4 must lie in U_z for some z with <x,z> != 0 mod 4.
Collect minimal row-masks R per port; cross-check against FE (allowed mask A feasible iff A hits every R)."""
from ncore import *
import pickle
FE=np.load('zfeas.npy')
Xall=np.array(list(itertools.product(range(4),repeat=8)),np.int64)   # coordinates in basis; inner product via G
IPc=(Xall@G@C.T)%4        # 65536 x 104
IPz=(Xall@G@Z.T)%4        # 65536 x 16
Rm=((IPz!=0)*(1<<np.arange(16))).sum(1)
CL={}
for t in range(n):
    Rs=set(Rm[IPc[:,t]!=0].tolist())
    Rs=sorted(Rs,key=lambda r:bin(r).count('1'))
    mins=[]
    for r in Rs:
        if not any((a&r)==a for a in mins): mins.append(r)
    CL[t]=mins
pickle.dump(CL,open('zclauses.pkl','wb'))
print('clauses per port min/max',min(len(v) for v in CL.values()),max(len(v) for v in CL.values()))
print('clause sizes',sorted(set(bin(r).count('1') for v in CL.values() for r in v)))
# cross-check on random masks
rng=np.random.default_rng(0); bad=0
for _ in range(20000):
    t=rng.integers(n); A=int(rng.integers(0,1<<16))
    hit=all(A&r for r in CL[t])
    bad+= hit!=bool(FE[t,A])
print('FE vs clause cross-check mismatches:',bad)
