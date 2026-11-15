"""ARMTREE ilp2.py [N/P-sketch]: necessary mask conditions from the normalised Gram  G~ = S(x)I2 - diag(Q_a), Q_a invertible 2x2,
S_ac = +1 (a>=c), -1 (a<c)  (time order).  Role r contributes a rank-1 term on (M_r cap A)x(M_r cap B) => for all stage sets A,B:
#{r : M_r meets A and B} >= min_Q rank G~[A,B]  (min over a sample of Q: I,2I,-I,.5I, 6 randoms).
Min header sum|Z_k| over mask multisets (ILP, HiGHS).  Also optional layout check."""
import sys, itertools, numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
rng=np.random.default_rng(1)
def Gt(L,Qs):
    G=np.zeros((2*L,2*L))
    for a in range(L):
        for c in range(L):
            G[2*a:2*a+2,2*c:2*c+2]=(1 if a>=c else -1)*np.eye(2)
        G[2*a:2*a+2,2*a:2*a+2]-=Qs[a]
    return G
def samples(L):
    S=[]
    for s in (1,2,-1,.5): S.append([s*np.eye(2)]*L)
    for _ in range(6): S.append([rng.normal(size=(2,2)) for _ in range(L)])
    for _ in range(4): S.append([np.array([[1,rng.normal()],[0,1]])*rng.choice([1,2,-1]) for _ in range(L)])
    return [Gt(L,q) for q in S]
def minrank(Gs,A,B):
    idx=lambda X:[2*a+j for a in X for j in (0,1)]
    return min(np.linalg.matrix_rank(G[np.ix_(idx(A),idx(B))],tol=1e-9) for G in Gs)
if __name__=='__main__':
    L=int(sys.argv[1]); Gs=samples(L); masks=list(range(1,1<<L)); pc=lambda m:bin(m).count('1')
    rows=[];rhs=[]; seen=set()
    for lab in itertools.product(range(4),repeat=L):   # 0 none,1 A only,2 B only,3 both
        ma=sum(1<<i for i in range(L) if lab[i] in(1,3)); mb=sum(1<<i for i in range(L) if lab[i] in(2,3))
        if not ma or not mb: continue
        k=minrank([G for G in Gs],[i for i in range(L) if ma>>i&1],[i for i in range(L) if mb>>i&1])
        if k==0: continue
        rows.append([1.0 if (m&ma and m&mb) else 0.0 for m in masks]); rhs.append(k)
    A_=np.array(rows); c=np.array([pc(m) for m in masks],float)
    res=milp(c,constraints=LinearConstraint(A_,np.array(rhs),np.inf),integrality=np.ones(len(masks)),bounds=Bounds(0,60),options={'time_limit':900})
    print('L',L,'status',res.status,'min header',res.fun); x=np.round(res.x).astype(int)
    print('Z',[int(sum(x[i] for i,m in enumerate(masks) if m>>k&1)) for k in range(L)],'n',x.sum())
    for i,m in enumerate(masks):
        if x[i]: print(x[i],'x',''.join('1' if m>>k&1 else '.' for k in range(L)))
