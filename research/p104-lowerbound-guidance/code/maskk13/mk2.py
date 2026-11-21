"""MASKK13 mk2: stage-level (mask-only) feasibility of the face profile '2 full hubs + third role of degree d + (2k-5) degree-2 roles'
under two ORDER-FREE laws [P]:
 TRIPLE (every stage triple lies >=2 inside some NON-hub role: hubs are full so they always count, and TRIPLE needs >=3 roles) and
 SPARSE (dimension count: roles with mask inside U are independent vectors ah_r in {x supported on blocks U, block-sum 0}, dim 2|U|-2).
Unknowns: M3 (WLOG {0..d-1}), multiplicities m_uv in {0,1,2,...} of degree-2 roles, sum = 2k-5. CEGAR on SPARSE over all 2^k subsets."""
import sys,itertools,numpy as np
from ortools.sat.python import cp_model
def sparse_violation(k,d,m):
    # m: dict (u,v)->mult ; returns list of violating U (bitmask) , worst first
    N=1<<k;cnt=np.zeros(N,np.int32)
    W=np.zeros((k,k),np.int32)
    for (u,v),x in m.items():W[u,v]=W[v,u]=x
    pop=np.zeros(N,np.int32)
    for b in range(k):
        lo=np.arange(1<<b)
        # w[U'] = sum_{v in U'} W[b,v]
        w=np.zeros(1<<b,np.int32)
        for v in range(b):
            w[(lo>>v)&1==1]+=W[b,v]
        cnt[(1<<b):(1<<(b+1))]=cnt[:1<<b]+w
        pop[(1<<b):(1<<(b+1))]=pop[:1<<b]+1
    U=np.arange(N)
    m3=((U&((1<<d)-1))==((1<<d)-1)).astype(np.int32)
    tot=cnt+m3
    bad=np.nonzero((tot>2*pop-2)&(pop>=2))[0]
    return bad.tolist()
def solve(k,d,maxm=2,verbose=False):
    pairs=[(u,v) for u in range(k) for v in range(u+1,k)]
    M=cp_model.CpModel()
    m={p:M.NewIntVar(0,maxm,'m%d_%d'%p) for p in pairs}
    M.Add(sum(m.values())==2*k-5)
    # triples
    for T in itertools.combinations(range(k),3):
        if sum(1 for t in T if t<d)>=2:continue
        M.Add(sum(m[(a,b)] for a,b in itertools.combinations(T,2))>=1)
    def addU(U):
        S=[i for i in range(k) if U>>i&1]
        M.Add(sum(m[(a,b)] for a,b in itertools.combinations(S,2))+int(all(s<d for s in range(d)) and all(U>>s&1 for s in range(d)))<=2*len(S)-2)
    for r in range(2,5):
        for S in itertools.combinations(range(k),r):addU(sum(1<<s for s in S))
    it=0
    while True:
        s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=600
        st=s.Solve(M)
        if st==cp_model.INFEASIBLE:return 'INFEASIBLE',it
        if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):return 'UNKNOWN',it
        sol={p:s.Value(m[p]) for p in pairs if s.Value(m[p])}
        bad=sparse_violation(k,d,sol)
        if not bad:return 'FEASIBLE',sol
        for U in bad[:200]:addU(U)
        it+=1
if __name__=='__main__':
    for k in [int(a) for a in sys.argv[1:]]:
        for d in range(2,k):
            r=solve(k,d)
            print('k',k,'d',d,r[0],(r[1] if r[0]!='FEASIBLE' else r[1]),flush=True)
