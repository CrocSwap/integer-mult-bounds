"""TAU48 gibbs.py: exact validity-preserving port resampling. For port t, W[t] is redrawn uniformly-ish from
{w in Z4^m : w.V[p] = 2 delta_tp mod 4 for all p with Q[t,p]=1} (likewise V rows). Produces NONLINEAR decoders.
Reports rho (GF(2^16) rank, Rado ub), lemma bound, K bound, tau-rank at greedy Rado sets."""
import sys,json,numpy as np; sys.path.insert(0,'../orbitlp'); sys.path.insert(0,'../double56')
from geo import Q, D56
from rho import *
from e8xy_lib import xy_spaces
from lin import inv4
n=104
def f2solve(A,c,rng):
    """random solution of A x = c over F2, or None. A: r x m"""
    A=A%2; c=c%2; r,m=A.shape; M=np.concatenate([A,c[:,None]],1).astype(np.int64); piv=[]; row=0
    for col in range(m):
        p=next((i for i in range(row,r) if M[i,col]),None)
        if p is None: continue
        M[[row,p]]=M[[p,row]]
        for i in range(r):
            if i!=row and M[i,col]: M[i]^=M[row]
        piv.append(col); row+=1
    if M[row:,m].any(): return None
    free=[j for j in range(m) if j not in piv]; x=np.zeros(m,np.int64)
    x[free]=rng.integers(0,2,len(free))
    for i,col in enumerate(piv): x[col]=(M[i,m]+M[i,free]@x[free])%2
    return x
def kernel_f2(A):
    A=A%2; r,m=A.shape; M=A.copy().astype(np.int64); piv=[]; row=0
    for col in range(m):
        p=next((i for i in range(row,r) if M[i,col]),None)
        if p is None: continue
        M[[row,p]]=M[[p,row]]
        for i in range(r):
            if i!=row and M[i,col]: M[i]^=M[row]
        piv.append(col); row+=1
    free=[j for j in range(m) if j not in piv]; out=[]
    for f in free:
        x=np.zeros(m,np.int64); x[f]=1
        for i,col in enumerate(piv): x[col]=M[i,f]
        out.append(x)
    return out
def resample(W,V,t,rng,side):
    if side=='V': V,W=W,V
    P=np.nonzero(Q[t])[0]; A=V[P]%4; c=np.array([2 if p==t else 0 for p in P])
    K=kernel_f2(A); opts=[]
    for _ in range(40):
        w0=np.zeros(A.shape[1],np.int64)
        for kv in K:
            if rng.random()<0.5: w0=(w0+kv)%2
        rhs=((c-A@w0)%4)//2
        w1=f2solve(A,rhs,rng)
        if w1 is not None: opts.append((w0+2*w1)%4); break
    if opts:
        W=W.copy(); W[t]=opts[0]
    if side=='V': W,V=V,W
    return W,V
def check(W,V): return not ((((W@V.T)-2*np.eye(n,dtype=np.int64))%4)*Q).any()
def rk(M): return f2rank([toint(r) for r in M%2]) if len(M) else 0
def report(W,V,tag):
    a=W%2;b=V%2;N=(a@b.T)*Q;X=(N//2)%2;I=np.eye(n,dtype=int)
    RB=spaces_B(W,V,Q);RA=spaces_A(W,V,Q); rb=trank(RB,n,2); ra=trank(RA,n,2)
    vb,J=rado_ub(RB,n); va,Jp=rado_ub(RA,n); Xs,Ys,_,_=xy_spaces(RB,RA,n)
    tr=rk(Xs@Ys.T) if len(Xs) and len(Ys) else 0
    exact=(vb==rb and va==ra)
    print(tag,'C',cost(W,V,Q),'rho',ra,rb,'Rado-exact',exact,'|J|',len(J),len(Jp),'dims',len(Xs),len(Ys),'tau-rank',tr,'lemma',n-tr,
          'nonlin',nonlin(W,V),flush=True)
    return tr,exact,ra+rb
E=json.load(open(D56+'e8base.json')); Cc=np.array(E['C'])[:104]; Gb=np.array(E['Gb'])
Lab=np.array([[int(c) for c in format(x,'09b')] for x in [int(y) for y in open(D56+'labels.txt').read().split()]])
def nonlin(W,V):
    # number of a_k, b_k columns NOT in the label code C (colspace of Q mod 2)
    base=f2rank([toint(r) for r in Lab.T]); cnt=0
    for M in (W%2,V%2):
        for k in range(M.shape[1]):
            if f2rank([toint(r) for r in Lab.T]+[toint(M[:,k])])>base: cnt+=1
    return cnt
if __name__=='__main__':
    seed=int(sys.argv[1]) if len(sys.argv)>1 else 0; steps=int(sys.argv[2]) if len(sys.argv)>2 else 300
    m=int(sys.argv[3]) if len(sys.argv)>3 else 12
    rng=np.random.default_rng(seed); W0=Cc%4; V0=(Cc@Gb)%4
    while True:
        Xm=rng.integers(0,4,(8,m)); Pi=inv4(Xm[:,:8])
        if Pi is not None: break
    Ym=np.zeros((8,m),dtype=np.int64); Ym[:,:8]=Pi.T
    W=(W0@Xm)%4; V=(V0@Ym)%4; assert check(W,V); report(W,V,'start')
    for s in range(steps):
        t=int(rng.integers(n)); W,V=resample(W,V,t,rng,'W' if rng.random()<0.5 else 'V'); assert check(W,V)
        if (s+1)%(steps//6)==0: report(W,V,'step%d'%(s+1))
