"""B14 satlift: CP-SAT over F3 (ternary symmetric terms d_k d_k^T summing to 2G mod 3), Thm-C cost <= BOUND via
rank-factor encoding (u_i (S+M_k) u_j^T = 0 on R_k x R_k, rank M_k <= rho_k).  Hits are lifted to Z by fitting + exact check.
usage: satlift.py n bound timelimit workers [control]"""
import sys, time, numpy as np
from ortools.sat.python import cp_model
import model as m
n=int(sys.argv[1]); BOUND=int(sys.argv[2]); TL=float(sys.argv[3]); W=int(sys.argv[4]); control=len(sys.argv)>5
NP=112; U=m.Ln; S=m.S9; DOT=m.DOT; G2=2*m.G
RHO=8
M=cp_model.CpModel()
p=[[M.NewBoolVar(f"p{k}_{i}") for i in range(NP)] for k in range(n)]
q=[[M.NewBoolVar(f"m{k}_{i}") for i in range(NP)] for k in range(n)]
r=[[M.NewBoolVar(f"r{k}_{i}") for i in range(NP)] for k in range(n)]
for k in range(n):
    for i in range(NP):
        M.AddBoolOr([p[k][i].Not(),q[k][i].Not()])
        M.Add(r[k][i]==p[k][i]+q[k][i])
    M.Add(sum(p[k][i]+q[k][i] for i in range(NP))>=1)
# symmetry breaking: terms ordered by support size (weak)
for k in range(n-1):
    M.Add(sum(r[k])>=sum(r[k+1]))
# products
Z={}
for k in range(n):
    for i in range(NP):
        Z[k,i,i]=r[k][i]
        for j in range(i+1,NP):
            a=M.NewBoolVar(""); b=M.NewBoolVar(""); c=M.NewBoolVar(""); d=M.NewBoolVar("")
            for v,x,y in ((a,p[k][i],p[k][j]),(b,q[k][i],q[k][j]),(c,p[k][i],q[k][j]),(d,q[k][i],p[k][j])):
                M.AddBoolOr([x.Not(),y.Not(),v]); M.AddImplication(v,x); M.AddImplication(v,y)
            Z[k,i,j]=(a,b,c,d)
for i in range(NP):
    for j in range(i,NP):
        s=M.NewIntVar(-(n//3+2),n//3+2,"")
        if i==j: expr=sum(Z[k,i,i] for k in range(n))
        else: expr=sum(Z[k,i,j][0]+Z[k,i,j][1]-Z[k,i,j][2]-Z[k,i,j][3] for k in range(n))
        M.Add(expr-int(G2[i,j])==3*s)
# cost
costs=[]
for k in range(n):
    used=[M.NewBoolVar(f"u{k}_{c}") for c in range(RHO)]
    for c in range(RHO-1): M.AddImplication(used[c+1],used[c])
    costs.append(sum(used))
    Pi=[[M.NewBoolVar("") for _ in range(9)] for c in range(RHO)]
    Sg=[[M.NewBoolVar("") for _ in range(9)] for c in range(RHO)]
    for c in range(RHO):
        for t in range(9):
            M.AddImplication(Pi[c][t],used[c]); M.AddImplication(Sg[c][t],used[c])
    Mm=[[None]*9 for _ in range(9)]
    for a_ in range(9):
        for b_ in range(9):
            ands=[]
            for c in range(RHO):
                v=M.NewBoolVar("")
                M.AddBoolOr([Pi[c][a_].Not(),Sg[c][b_].Not(),v]); M.AddImplication(v,Pi[c][a_]); M.AddImplication(v,Sg[c][b_])
                ands.append(v)
            mv=M.NewBoolVar(""); M.AddBoolXOr(ands+[mv.Not()]) ; Mm[a_][b_]=mv   # mv = xor(ands)
    # c_iq = (u_i M)_q
    Cq=[[None]*9 for _ in range(NP)]
    for i in range(NP):
        for qq in range(9):
            lits=[Mm[pp][qq] for pp in range(9) if U[i,pp]]
            cv=M.NewBoolVar(""); M.AddBoolXOr(lits+[cv.Not()]); Cq[i][qq]=cv
    for i in range(NP):
        for j in range(NP):
            if j<i: continue
            # need u_i (S+M) u_j^T = 0 for pairs in R (both orders). ordered (i,j): DOT_ij + sum_q c_iq u_jq
            for (a_,b_) in ((i,j),(j,i)) if i!=j else ((i,j),):
                lits=[Cq[a_][qq] for qq in range(9) if U[b_,qq]]
                w=M.NewBoolVar(""); par=int(DOT[a_,b_])
                # w = par xor XOR(lits)
                M.AddBoolXOr(lits+[w.Not()] if par==0 else lits+[w])
                M.AddBoolOr([r[k][i].Not(),r[k][j].Not(),w.Not()])
M.Add(sum(costs)<=BOUND)
if control:
    X=m.X
    for k in range(8):
        for i in range(NP):
            M.Add(p[k][i]==(1 if X[i,k]>0 else 0)); M.Add(q[k][i]==(1 if X[i,k]<0 else 0))
    # (n==8 control with hints only; bound 64)
sv=cp_model.CpSolver(); sv.parameters.max_time_in_seconds=TL; sv.parameters.num_workers=W; sv.parameters.log_search_progress=False
class CB(cp_model.CpSolverSolutionCallback):
    def __init__(s): super().__init__(); s.t0=time.time()
    def on_solution_callback(s): print(f"[{time.time()-s.t0:.0f}s] solution found",flush=True)
t0=time.time(); st=sv.Solve(M,CB())
print("status",sv.StatusName(st),"wall %.0fs"%(time.time()-t0),flush=True)
if st in (cp_model.OPTIMAL,cp_model.FEASIBLE):
    D=np.array([[sv.Value(p[k][i])-sv.Value(q[k][i]) for k in range(n)] for i in range(NP)])
    np.save(f"satlift_sol_n{n}_b{BOUND}_{int(time.time())}.npy",D)
    print("F3 solution; cost(sym terms)=",m.cost(D,D),"; exact over Z(2G)?",m.exact(D,D,1),flush=True)
    # lift: least squares on fixed supports
    from scipy.optimize import least_squares
    supp=(D!=0)
    def res(x):
        Dx=np.zeros((NP,n)); Dx[supp]=x
        return (Dx@Dx.T-m.M4).ravel()
    sol=least_squares(res,D[supp].astype(float),method="lm",max_nfev=200)
    print("lift residual",np.abs(sol.fun).max(),flush=True)
