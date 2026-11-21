import numpy as np,sys,itertools,collections,time
from lt import *
rng=np.random.default_rng(int(sys.argv[1]) if len(sys.argv)>1 else 0)
NB='../'
def inv4(P):
    m=P.shape[0]; A=np.concatenate([P%4,np.eye(m,dtype=np.int64)],1)
    for c in range(m):
        p=next((i for i in range(c,m) if A[i,c]%2),None)
        if p is None: return None
        A[[c,p]]=A[[p,c]]; A[c]=(A[c]*(1 if A[c,c]%4==1 else 3))%4
        for i in range(m):
            if i!=c: A[i]=(A[i]-A[i,c]*A[c])%4
    return A[:,m:]
def check(W,V): return not ((((W@V.T)-2*np.eye(104,dtype=np.int64))%4)*Q104).any()
stats=collections.defaultdict(list)
def rec(fam,W,V,nrand=4,tag=''):
    W=W%4;V=V%4; assert check(W,V),fam
    r=evaluate(Q104,W,V,rng,nrand=nrand)
    for o in ('fwd','mir'):
        x=r[o]; stats[fam+'/'+o].append((x['S'],x['D'],x['f2'],x['std'],x['sym'],tag))
        assert x['S']<=x['D'],('S>D',fam,o,x)
    return r
def summary():
    for k in sorted(stats):
        L=stats[k]; mS=min(L,key=lambda t:t[0]); mf=min(t[2] for t in L)
        print('%-28s n=%4d  minS=%3d (D=%3d, tag %s)  minS-D gap<=: maxS=%d  minF2floor=%d  minD=%d  #S<56=%d  #S<D=%d'%(k,len(L),mS[0],mS[1],mS[5],max(t[0] for t in L),mf,min(t[1] for t in L),sum(t[0]<56 for t in L),sum(t[0]<t[1] for t in L)),flush=True)
# A: E8
W8=np.load(NB+'orbitlp/e8W.npy');V8=np.load(NB+'orbitlp/e8V.npy'); rec('E8',W8,V8,nrand=20)
# B: transvection / split neighbours (double56 e8X,e8Y)
X=np.load(NB+'double56/e8X.npy'); Y=np.load(NB+'double56/e8Y.npy')
assert check(C104@X,C104@Y)
for i in range(8):
  for j in range(8):
    if i==j: continue
    for c in (1,2,3):
      X2=X.copy(); Y2=Y.copy(); X2[:,j]=(X2[:,j]+c*X2[:,i])%4; Y2[:,i]=(Y2[:,i]-c*Y2[:,j])%4
      rec('E8-transvection',C104@X2,C104@Y2,tag=(i,j,c))
for _ in range(60):
    k=int(rng.integers(8)); y1=rng.integers(0,4,8)
    X2=np.concatenate([X,X[:,[k]]],1); Y2=np.concatenate([Y,y1[:,None]],1); Y2[:,k]=(Y2[:,k]-y1)%4
    rec('E8-split',(C104@X2),(C104@Y2),tag=k)
print('E8 nbrs done',flush=True); summary()
# C: linear decoders: random factorisations W=C Xm, V=(C Gb) Ym
W0=C104%4; V0=(C104@Gb)%4
for t in range(150):
    m=int(rng.integers(8,17))
    while True:
        Xm=rng.integers(0,4,(8,m)); Pi=inv4(Xm[:,:8])
        if Pi is not None: break
    Ym=np.zeros((8,m),dtype=np.int64); Ym[:,:8]=Pi.T
    rec('linear-randfact',(W0@Xm),(V0@Ym),nrand=2,tag=m)
# sparse-ish linear: X = signed permutation-ish with few nonzeros (cheap rows) 
for t in range(100):
    m=int(rng.integers(8,13))
    while True:
        Xm=(rng.integers(0,4,(8,m))*(rng.random((8,m))<0.35)).astype(np.int64); Pi=inv4(Xm[:,:8])
        if Pi is not None: break
    Ym=np.zeros((8,m),dtype=np.int64); Ym[:,:8]=Pi.T
    rec('linear-sparse',(W0@Xm),(V0@Ym),nrand=2,tag=m)
# tight 8-row linear (m8tight): tight x-lifts from tightX.npy
T=np.load(NB+'linear56/tightX.npy'); tl={}
for x in T:
    kk=tuple(x%2)
    if kk not in tl: tl[kk]=x
keys=sorted(tl); subs=list(itertools.combinations(range(16),8)); rng.shuffle(subs)
n8=0
for sub in subs:
    Xm=np.array([tl[keys[i]] for i in sub]).T; Xi=inv4(Xm)
    if Xi is None: continue
    for Kn,K in (('G',Gb),('G+2B',Gb+2*(Gb%2))):
        Ym=((Xi@K)%4).T
        W=C104@Xm; V=C104@Ym
        if not check(W,V): continue
        rec('linear-tight8-'+Kn,W,V,nrand=2); n8+=1
    if n8>=120: break
print('linear done',flush=True); summary()
# D: Gibbs nonlinear decoders (stored)
for nm in ('2_4','3_8'):
    W=np.load(NB+'tau48/g_W_%s.npy'%nm);V=np.load(NB+'tau48/g_V_%s.npy'%nm); rec('gibbs-stored-'+nm,W,V,nrand=10,tag=W.shape)
summary()
import pickle; pickle.dump(dict(stats),open('stats_a.pkl','wb'))
