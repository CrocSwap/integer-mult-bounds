"""MASKK13 mk2b: as mk2 but with the sharper LEMMA-A form for every role set S_U = {roles inside U} (any f):
   |S_U| <= sum_{t in U} min(2,c_t(S_U)) - max_{t in U} min(2,c_t(S_U)),  c_t = #S_U roles containing t   [P, dimension count of ah_r]
 plus NH: S = all roles except the two full hubs:  sum_t max(0,2-c_t) <= 2  (c_t = non-hub roles through t).
 Ranks A_t|S <= min(2, c_t) since A_t|S has c_t nonzero columns in R^2.  TRIPLE as in mk2."""
import sys,itertools,numpy as np
from ortools.sat.python import cp_model
def check(k,d,m):
    N=1<<k;W=np.zeros((k,k),np.int32)
    for (u,v),x in m.items():W[u,v]=W[v,u]=x
    U=np.arange(N,dtype=np.int64)
    inU=[((U>>t)&1).astype(bool) for t in range(k)]
    m3=((U&((1<<d)-1))==((1<<d)-1))
    # c_t(S_U)
    c=np.zeros((k,N),np.int32)
    for t in range(k):
        acc=np.zeros(N,np.int32)
        for v in range(k):
            if v!=t and W[t,v]:acc+=W[t,v]*inU[v]
        if t<d:acc+=m3
        c[t]=np.where(inU[t],acc,0)
    r=np.minimum(c,2)
    size=np.zeros(N,np.int32)
    for t in range(k):
        for v in range(t+1,k):
            if W[t,v]:size+=W[t,v]*(inU[t]&inU[v])
    size+=m3
    rhs=r.sum(0)-r.max(0)
    pop=sum(inU[t].astype(np.int32) for t in range(k))
    bad=np.nonzero((size>rhs)&(pop>=2))[0]
    return bad.tolist()
def solve(k,d,maxm=2,tl=900):
    pairs=[(u,v) for u in range(k) for v in range(u+1,k)]
    M=cp_model.CpModel()
    m={p:M.NewIntVar(0,maxm,'m%d_%d'%p) for p in pairs}
    M.Add(sum(m.values())==2*k-5)
    for T in itertools.combinations(range(k),3):
        if sum(1 for t in T if t<d)>=2:continue
        M.Add(sum(m[(a,b)] for a,b in itertools.combinations(T,2))>=1)
    # NH
    c=[]
    for t in range(k):
        ct=M.NewIntVar(0,2*k,'c%d'%t);M.Add(ct==sum(m[(min(t,u),max(t,u))] for u in range(k) if u!=t)+(1 if t<d else 0));c.append(ct)
    sl=[]
    for t in range(k):
        s=M.NewIntVar(0,2,'s%d'%t);M.Add(s>=2-c[t]);sl.append(s)
    M.Add(sum(sl)<=2)
    ctr=[0]
    def addU(U):
        S=[i for i in range(k) if U>>i&1];ctr[0]+=1;q=ctr[0]
        size=sum(m[(a,b)] for a,b in itertools.combinations(S,2))+(1 if all(U>>s&1 for s in range(d)) else 0)
        zs=[]
        for t in S:
            ct=sum(m[(min(t,u),max(t,u))] for u in S if u!=t)+(1 if (t<d and all(U>>s&1 for s in range(d))) else 0)
            cv=M.NewIntVar(0,2*k,'');M.Add(cv==ct)
            z=M.NewIntVar(0,2,'');M.AddMinEquality(z,[cv,2]);zs.append(z)
        mx=M.NewIntVar(0,2,'');M.AddMaxEquality(mx,zs)
        M.Add(size<=sum(zs)-mx)
    for r in range(2,4):
        for S in itertools.combinations(range(k),r):addU(sum(1<<s for s in S))
    it=0
    while True:
        s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=tl
        st=s.Solve(M)
        if st==cp_model.INFEASIBLE:return 'INFEASIBLE',it
        if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):return 'UNKNOWN',it
        sol={p:s.Value(m[p]) for p in pairs if s.Value(m[p])}
        bad=check(k,d,sol)
        if not bad:return 'FEASIBLE',sol
        for U in bad[:60]:addU(U)
        it+=1
if __name__=='__main__':
    for k in [int(a) for a in sys.argv[1:]]:
        for d in range(2,k):
            r=solve(k,d)
            print('k',k,'d',d,r[0],r[1],flush=True)
