# AUDIT-TS: independent F7 check. Directions = all 1200 E8 lines-of-vectors with norm 2 or 4 (roots; r+s, r.s=0), computed here.
# Qualify(h,V) <=> rank_F2(labels of Off(h) outside Lambda(V)) <= 7 <=> annihilator of those labels has >=3 nonzero functionals.
import json, numpy as np, os
from collections import Counter, defaultdict
D=json.load(open('../../data/bx_data.json'))
LAB=np.array([int(x) for x in D['LAB']]); L=np.rint(np.array(D['L'])*2).astype(int); E=np.rint(np.array(D['E8'])*2).astype(int)
R=np.vstack([E,-E]); assert len({tuple(r) for r in R})==240
n2=R[0]@R[0]; assert all(r@r==n2 for r in R)
def cn(v):
    v=np.array(v); i=np.nonzero(v)[0][0]; return tuple(v if v[i]>0 else -v)
Lset={cn(x) for x in L}; Eset={cn(x) for x in E}; assert len(Lset)==112 and Lset<=Eset
G=R@R.T; ii,jj=np.nonzero(G==0)
n4={cn(R[i]+R[j]) for i,j in zip(ii,jj) if i<j}; assert len(n4)==1080
dirs=[('frame',np.array(x)) for x in Eset-Lset]+[('root',np.array(x)) for x in Lset]+[('n4',np.array(x)) for x in n4]
par=np.vectorize(lambda x: bin(int(x)).count('1')&1)
U=np.arange(1,512); P=par(U[:,None]&LAB[None,:]).astype(np.float32)   # 511 x 112
# all 2-dim functional spaces {a,b,a^b}; V = common kernel (7-dim)
sp=set()
for a in range(1,512):
    for b in range(a+1,512): sp.add(tuple(sorted((a,b,a^b))))
sp=sorted(sp); assert len(sp)==43435
A=np.array([s[0] for s in sp]); B=np.array([s[1] for s in sp])
outV=(par(A[:,None]&LAB[None,:])|par(B[:,None]&LAB[None,:])).astype(np.float32)  # 43435 x 112, 1 = line outside Lambda(V)
inV=1-outV; print('max |Lambda(V)| over 7-spaces', int(inV.sum(1).max()))
cnt=defaultdict(lambda: np.zeros(len(sp),int)); offsz=Counter()
for typ,h in dirs:
    off=(L@h!=0).astype(np.float32); offsz[(typ,int(off.sum()))]+=1
    O=outV*off[None,:]
    z=((O@P.T)==0).sum(1)          # nonzero functionals vanishing on all outside labels
    cnt[typ]+= (z>=3)
for t in cnt: print(t,'qualifying per V hist',sorted(Counter(cnt[t].tolist()).items()))
tot=sum(cnt.values()); print('total hist',sorted(Counter(tot.tolist()).items())); print('Off sizes',sorted(offsz.items()))
