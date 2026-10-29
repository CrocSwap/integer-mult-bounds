# TWOSIDE f7: for every 7-dim label space V (kernel of a 2-dim functional space on F2^9), count frame directions f with
# rank_F2 l(Off(f) \ Lambda(V)) <= 7.  Mode 'rank' (impl 1: Gaussian elimination) / mode 'cover' (impl 2: explicit 7-flat G with
# Off(f) subset Lambda(V) u Lambda(G), restricted to V,G holding >=24 lines of Off(f) -- forced since a 7-flat holds <=32 of 56).
import json, sys, numpy as np, itertools
from collections import Counter
D=json.load(open('../../data/bx_data.json'))
LAB=[int(x) for x in D['LAB']]; L=np.rint(np.array(D['L'])*2).astype(int); E=np.rint(np.array(D['E8'])*2).astype(int)
def canon(v):
    i=np.nonzero(v)[0][0]; return tuple(v if v[i]>0 else -v)
Ls=set(canon(x) for x in L); fr=[np.array(x) for x in set(canon(x) for x in E)-Ls]; assert len(fr)==8 and len(Ls)==112
OFF=[[i for i in range(112) if L[i]@f!=0] for f in fr]; assert all(len(o)==56 for o in OFF)
par=lambda x: bin(x).count('1')&1
spaces=set()
for a in range(1,512):
    for b in range(a+1,512):
        spaces.add(frozenset([a,b,a^b]))
spaces=sorted(tuple(sorted(s)) for s in spaces); assert len(spaces)==43435
def inV(s,l): return par(s[0]&l)==0 and par(s[1]&l)==0
def rank(vs):
    basis=[]
    for v in vs:
        for bb in basis: v=min(v,v^bb)
        if v: basis.append(v)
    return len(basis)
mode=sys.argv[1]
hist=Counter(); worst=0
if mode=='rank':
    for s in spaces:
        c=sum(1 for o in OFF if rank([LAB[i] for i in o if not inV(s,LAB[i])])<=7)
        hist[c]+=1
else:
    # own subspace membership: V = {x : M x = 0} using the 2 functionals as rows; precompute per space the 112-bit line mask
    lab=np.array(LAB,dtype=np.int64)
    bits=((lab[:,None]>>np.arange(9))&1)                       # 112x9
    S=np.array([[ (s[0]>>k)&1 for k in range(9)]+[(s[1]>>k)&1 for k in range(9)] for s in spaces])
    M1=(bits@S[:,:9].T)%2; M2=(bits@S[:,9:].T)%2               # 112 x 43435
    IN=((M1==0)&(M2==0))                                       # line i in Lambda(space j)
    cnt=np.zeros(len(spaces),dtype=int)
    for o in OFF:
        oset=np.zeros(112,bool); oset[o]=True
        hit=IN[oset].sum(0)                                    # lines of Off in each flat
        big=np.nonzero(hit>=24)[0]
        sub=IN[oset][:,big]                                    # 56 x nb
        ok=np.zeros(len(spaces),bool)
        for jj,j in enumerate(big):
            un=sub[:,jj][:,None]|sub                           # union with every big G
            if un.all(0).any(): ok[j]=True
        cnt+=ok
    hist=Counter(cnt.tolist())
print(mode,'hist #qualifying frames per 7-space:',sorted(hist.items()))
