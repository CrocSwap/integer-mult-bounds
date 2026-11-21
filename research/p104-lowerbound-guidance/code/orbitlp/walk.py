"""ORBITLP walk.py: random walk over mod-4 decoders (moves keep the odd-cell identity), tracking
slack = C - rankY - rankZ (test of [CONJ] HALFRANK) and rank(I+X). Moves: elementary GL_m(Z4) column ops,
split a row along a random support partition, add (x,2y)/(2x,y) or (x,y)/(x,-y) pairs, zero ports + trivial rows,
drop zero rows. Greedy-biased toward low slack."""
import numpy as np, sys
from geo import *
from carry import rk2
I=np.eye(104,dtype=int); Qb=Q.astype(bool)
def price1(w,v):
    D=np.nonzero(w%4)[0]; S=np.nonzero(v%4)[0]
    if len(D)==0 or len(S)==0: return 0
    return rk2(Q[np.ix_(D,S)])
def stats(W,V):
    W=W%4; V=V%4; m=W.shape[1]
    a=W%2; w2=(W//2)%2; b=V%2; v2=(V//2)%2
    Y=((w2@b.T)%2)*Q; Z=((a@v2.T)%2)*Q
    N=(a@b.T)*Q; X=((N//2)%2)
    C=sum(price1(W[:,k],V[:,k]) for k in range(m))
    return C, rk2(Y), rk2(Z), rk2((I+X)%2)
def ok(W,V):
    return not (((W@V.T-2*I)%4)*Q).any()
rng=np.random.default_rng(int(sys.argv[1]) if len(sys.argv)>1 else 0)
W=np.load('e8W.npy'); V=np.load('e8V.npy')
def inv4(g):
    from sympy import Matrix
    return np.array(Matrix(g).inv_mod(4)).astype(int)
def move(W,V):
    m=W.shape[1]; r=rng.random()
    if r<0.45 and m>=2:
        i,j=rng.choice(m,2,replace=False); c=int(rng.integers(1,4))
        W=W.copy(); V=V.copy(); W[:,j]=(W[:,j]+c*W[:,i])%4; V[:,i]=(V[:,i]-c*V[:,j])%4
    elif r<0.55:
        k=rng.integers(m); D=np.nonzero(W[:,k]%4)[0]
        if len(D)>1:
            part=rng.random(len(D))<0.5; w1=np.zeros(104,int); w1[D[part]]=W[D[part],k]
            W=np.hstack([W,(W[:,k]-w1)[:,None]%4]); W[:,k]=w1; V=np.hstack([V,V[:,k:k+1]])
    elif r<0.62:
        x=np.zeros(104,int); y=np.zeros(104,int)
        sx=rng.choice(104,rng.integers(1,20),replace=False); sy=rng.choice(104,rng.integers(1,20),replace=False)
        x[sx]=rng.integers(1,4,len(sx)); y[sy]=rng.integers(1,4,len(sy))
        if rng.random()<0.5: W=np.hstack([W,x[:,None],(2*x%4)[:,None]]); V=np.hstack([V,(2*y%4)[:,None],y[:,None]])
        else: W=np.hstack([W,x[:,None],x[:,None]]); V=np.hstack([V,y[:,None],(-y%4)[:,None]])
    elif r<0.70:
        h=rng.integers(104); W=W.copy(); V=V.copy()
        if rng.random()<0.5: W[h,:]=0; e=np.zeros((104,1),int); e[h]=1; W=np.hstack([W,e]); V=np.hstack([V,2*e])
        else: V[h,:]=0; e=np.zeros((104,1),int); e[h]=1; W=np.hstack([W,2*e]); V=np.hstack([V,e])
    elif r<0.80:
        # unit/2 scale swap on a row: (w,v)->(3w,3v)
        k=rng.integers(m); W=W.copy(); V=V.copy(); W[:,k]=3*W[:,k]%4; V[:,k]=3*V[:,k]%4
    else:
        # GL op restricted to random rows with general coefficient
        i,j=rng.choice(m,2,replace=False); c=2
        W=W.copy(); V=V.copy(); W[:,j]=(W[:,j]+c*W[:,i])%4; V[:,i]=(V[:,i]-c*V[:,j])%4
    keep=[k for k in range(W.shape[1]) if (W[:,k]%4).any() and (V[:,k]%4).any()]
    return W[:,keep],V[:,keep]
best=None; cur=(W,V); s=stats(W,V); curslack=s[0]-s[1]-s[2]
minsl=99; minIX=999
for it in range(int(sys.argv[2]) if len(sys.argv)>2 else 400):
    W2,V2=move(*cur)
    if W2.shape[1]>30: continue
    assert ok(W2,V2)
    s=stats(W2,V2); sl=s[0]-s[1]-s[2]
    if sl<minsl: minsl=sl
    if s[3]<minIX: minIX=s[3]; 
    if sl<0: print('COUNTEREXAMPLE',s,W2.shape); np.save('cex_W.npy',W2); np.save('cex_V.npy',V2); break
    # accept if slack not much worse and C bounded
    if sl<=curslack+1 and s[0]<=90 or rng.random()<0.1 and s[0]<=90:
        cur=(W2,V2); curslack=sl
    if it%100==0: print(it,'m',cur[0].shape[1],'C,rY,rZ,rIX',stats(*cur),'minslack',minsl,'min rank(I+X)',minIX,flush=True)
print('done minslack',minsl,'min rank(I+X)',minIX)
np.save('walk_W_%s.npy'%sys.argv[1],cur[0]); np.save('walk_V_%s.npy'%sys.argv[1],cur[1])
