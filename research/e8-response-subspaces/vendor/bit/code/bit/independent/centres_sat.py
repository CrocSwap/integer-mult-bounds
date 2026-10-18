"""Dylan Crow, with Anthropic Claude assistance, Apache-2.0.  usage: centres_sat.py k seconds   (k = 8: INFEASIBLE, k = 9: feasible)
Is there an F2 decoder of rank k (k centres) for the bit-E8 labels?  Need w_S, u_t in F2^k with
<u_t,w_t>=1 and <u_t,w_S>=0 for every neighbour S (|<r_t,r_S>|=1).  CP-SAT."""
import sys, time
import os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','producer')); os.environ.pop('E8COORD',None)
import e8lib as E
from ortools.sat.python import cp_model
V=E.V; k=int(sys.argv[1]); tl=float(sys.argv[2])
clique=[0, 2, 6, 8, 56, 57, 64, 65]
assert all(abs(E.G[a][b])==1 for a in clique for b in clique if a!=b), 'clique of pairwise neighbours'
# WLOG normalization: A restricted to a neighbour clique is the identity, so w and u of the clique are dual bases;
# GL(k, 2) acts on (w, u) preserving every <u, w>, so they may be taken to be the standard basis.
m=cp_model.CpModel()
w=[[m.NewBoolVar('w%d_%d'%(s,i)) for i in range(k)] for s in range(V)]
u=[[m.NewBoolVar('u%d_%d'%(s,i)) for i in range(k)] for s in range(V)]
for j,c in enumerate(clique[:k]):
    for i in range(k):
        m.Add(w[c][i]==(1 if i==j else 0)); m.Add(u[c][i]==(1 if i==j else 0))
for t in range(V):
    for S in [t]+E.NEIGH[t]:
        ps=[]
        for i in range(k):
            p=m.NewBoolVar('')
            m.AddBoolAnd([u[t][i],w[S][i]]).OnlyEnforceIf(p)
            m.AddBoolOr([u[t][i].Not(),w[S][i].Not()]).OnlyEnforceIf(p.Not())
            ps.append(p)
        if S==t: m.AddBoolXOr(ps)               # odd
        else: m.AddBoolXOr(ps+[m.NewConstant(1)])  # even
sol=cp_model.CpSolver(); sol.parameters.max_time_in_seconds=tl; sol.parameters.num_workers=2
t0=time.time(); r=sol.Solve(m)
print('k',k,'status',sol.StatusName(r),'%.0fs'%(time.time()-t0))
if r in (cp_model.OPTIMAL,cp_model.FEASIBLE):
    W=[[sol.Value(w[s][i]) for i in range(k)] for s in range(V)]
    U=[[sol.Value(u[s][i]) for i in range(k)] for s in range(V)]
