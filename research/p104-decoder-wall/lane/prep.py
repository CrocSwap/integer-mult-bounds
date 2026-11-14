# FIVEROW prep (own code): export exact combinatorial data for the propagation enumerator.
# For R: labels, Q-cell masks, X_R/Y_R hyperplane flats (exact over Q: a port set has rank<4 iff it lies in one),
# and all rank-4 all-Q bicliques I x J (|I|=4 coset of a 2-dim W, J = common odd partners; exact flint rank).
import sys, itertools
sys.path.insert(0,'../FATROWS')
from lib import *
import flint
def qrank(M): return flint.fmpz_mat([[int(x) for x in r] for r in M]).rank() if len(M) else 0
def hypflats(Z):
    # all hyperplane flats of the row-vector matroid of Z (rank 4): closures of rank-3 sets
    nz=[t for t in P if Z[t].any()]
    dirs={}
    for t in nz:
        v=Z[t]; i=next(k for k in range(4) if v[k]); key=tuple(int(x)*int(v[i]) for x in v)  # sign-normalise (entries 0,+-1)
        dirs.setdefault(key,[]).append(t)
    keys=list(dirs); flats=set()
    for a,b,c in itertools.combinations(range(len(keys)),3):
        M=[keys[a],keys[b],keys[c]]
        if qrank(M)<3: continue
        fl=frozenset(t for t in P if qrank(M+[list(Z[t])])==3)
        flats.add(fl)
    return sorted(flats,key=lambda s:sorted(s))
def mask(S): return sum(1<<t for t in S)
def main(R):
    T=target2(R)
    XR=np.array([ROWS[j][0] for j in R]).T; YR=np.array([ROWS[j][1] for j in R]).T
    assert ((XR@YR.T)*Qm==T).all() and qrank(XR)==4 and qrank(YR)==4
    HX=hypflats(XR); HY=hypflats(YR)
    # sanity: a set has rank<4 iff inside some flat (spot check random sets)
    import random; rnd=random.Random(1)
    for _ in range(300):
        S=rnd.sample(P,rnd.randint(1,6))
        assert (qrank(YR[S])<4)==any(set(S)<=f for f in HY)
        assert (qrank(XR[S])<4)==any(set(S)<=f for f in HX)
    bics=[]
    seenW=set()
    for w1 in range(1,512):
        for w2 in range(w1+1,512):
            W=frozenset((0,w1,w2,w1^w2))
            if W in seenW: continue
            seenW.add(W); seen=set()
            for a in LAB:
                cos=frozenset(a^x for x in W)
                if cos in seen: continue
                seen.add(cos)
                I=[p for p in P if LAB[p] in cos]
                if len(I)<4: continue
                J=[s for s in P if all(Qm[t,s] for t in I)]
                if qrank(T[np.ix_(I,J)])==4: bics.append((I,J))
    name='R'+''.join(map(str,R))
    with open('data_%s.txt'%name,'w') as f:
        f.write('%d\n'%len(P)); f.write(' '.join(map(str,LAB))+'\n')
        for t in P: f.write('%x\n'%mask([s for s in P if Qm[t,s]]))
        f.write('%d\n'%len(HX)); [f.write('%x\n'%mask(h)) for h in HX]
        f.write('%d\n'%len(HY)); [f.write('%x\n'%mask(h)) for h in HY]
        f.write('%d\n'%len(bics)); [f.write('%x %x\n'%(mask(I),mask(J))) for I,J in bics]
    print(name,'HX',len(HX),'HY',len(HY),'rank4 bicliques',len(bics),flush=True)
for R in [(0,1,2,3),(0,1,3,5)]: main(R)
