# HUNT-A2: exact square-decoder optimum over a catalogue as a CP-SAT model (1 worker).
# Exact for fixed parameters (pairwise duality + independence = completable, see NOTES §1); with ROBUST=1 the
# theta/zX-variable products (free_*.pkl) are unconstrained -> lower bound over all parameters.
import sys, pickle, os, itertools
from ortools.sat.python import cp_model
from a2lib import *
cat=sys.argv[1]; NT=int(os.environ.get('NT','9'))
rd,cd,f=pickle.load(open(cat.replace('cat_','tab_'),'rb'))
nr,nc=len(rd),len(cd)
FREE=pickle.load(open(cat.replace('cat_','free_'),'rb')) if os.environ.get('ROBUST') else set()
PZ=[[(None if (i,j) in FREE else dot(rd[i],cd[j])==0) for j in range(nc)] for i in range(nr)]
def circuits(vecs):
    out=[]; n=len(vecs)
    for k in range(2,min(n,10)+1):
        for S in itertools.combinations(range(n),k):
            if any(set(C)<=set(S) for C in out): continue
            if rank([vecs[i] for i in S],9)<k: out.append(S)
    return out
cr=circuits(rd); cc=circuits(cd)
m=cp_model.CpModel()
x={(i,j):m.NewIntVar(0,NT if (i==nr and j==nc) else 1,f'x{i}_{j}') for i in range(nr+1) for j in range(nc+1)}
m.Add(sum(x.values())==NT)
ur=[m.NewBoolVar(f'ur{i}') for i in range(nr)]; uc=[m.NewBoolVar(f'uc{j}') for j in range(nc)]
for i in range(nr): m.Add(sum(x[i,j] for j in range(nc+1))==ur[i])
for j in range(nc): m.Add(sum(x[i,j] for i in range(nr+1))==uc[j])
for i in range(nr):
    for j in range(nc):
        if PZ[i][j] is True: m.Add(x[i,j]==0)
        elif PZ[i][j] is False: m.Add(ur[i]+uc[j]-x[i,j]<=1)
for C in cr: m.Add(sum(ur[i] for i in C)<=len(C)-1)
for C in cc: m.Add(sum(uc[j] for j in C)<=len(C)-1)
m.Minimize(sum(f[i][j]*x[i,j] for i in range(nr+1) for j in range(nc+1)))
s=cp_model.CpSolver(); s.parameters.num_workers=1; s.parameters.max_time_in_seconds=float(os.environ.get('TL','900'))
st=s.Solve(m)
print(cat,'ROBUST' if FREE else 'exact','NT',NT,'status',s.StatusName(st),'opt',s.ObjectiveValue() if st in (cp_model.OPTIMAL,cp_model.FEASIBLE) else None,'bound',s.BestObjectiveBound(),'circuits',len(cr),len(cc))
if st in (cp_model.OPTIMAL,cp_model.FEASIBLE):
    terms=[(i,j) for (i,j),var in x.items() for _ in range(s.Value(var))]
    print('terms',terms)
    pickle.dump(terms,open(cat.replace('cat_','ilp_'),'wb'))
