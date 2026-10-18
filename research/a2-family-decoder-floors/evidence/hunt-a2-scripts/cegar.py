# HUNT-A2: CEGAR over parameter-dependent duality products.  Robust CP-SAT (cost <= CAP) -> realize params ->
# exact catalogue/ILP at that point.  Infeasible equation sets become no-good cuts (minimal infeasible subsets).
import sys, pickle, os, itertools, sympy as sp
from ortools.sat.python import cp_model
from a2lib import *
import realize
k=sys.argv[1]; CAP=int(sys.argv[2]); NT=9
rd,cd,f=pickle.load(open(f'tab_{k}.pkl','rb')); nr,nc=len(rd),len(cd)
FREE=pickle.load(open(f'free_{k}.pkl','rb')); EX=pickle.load(open(f'expr_{k}.pkl','rb'))
PZ=[[(None if (i,j) in FREE else dot(rd[i],cd[j])==0) for j in range(nc)] for i in range(nr)]
def circuits(vecs):
    out=[]; n=len(vecs)
    for kk in range(2,min(n,10)+1):
        for S in itertools.combinations(range(n),kk):
            if any(set(C)<=set(S) for C in out): continue
            if rank([vecs[i] for i in S],9)<kk: out.append(S)
    return out
cr=circuits(rd); cc=circuits(cd)
syms=sp.symbols('al2 be2 al3 be3 z1 z2 z3')
def numer(key): return sp.fraction(sp.together(EX[key]))[0]
def infeasible(E):
    return not sp.solve([numer(e) for e in E],syms,dict=True) if E else False
def mis(E):
    E=list(E)
    for e in list(E):
        T=[x for x in E if x!=e]
        if infeasible(T): E=T
    return E
cuts=[]
for it in range(200):
    m=cp_model.CpModel()
    x={(i,j):m.NewIntVar(0,NT if (i==nr and j==nc) else 1,f'x{i}_{j}') for i in range(nr+1) for j in range(nc+1)}
    m.Add(sum(x.values())==NT)
    ur=[m.NewBoolVar('') for i in range(nr)]; uc=[m.NewBoolVar('') for j in range(nc)]
    for i in range(nr): m.Add(sum(x[i,j] for j in range(nc+1))==ur[i])
    for j in range(nc): m.Add(sum(x[i,j] for i in range(nr+1))==uc[j])
    zz={}
    for i in range(nr):
        for j in range(nc):
            if PZ[i][j] is True: m.Add(x[i,j]==0)
            elif PZ[i][j] is False: m.Add(ur[i]+uc[j]-x[i,j]<=1)
            else:
                b=m.NewBoolVar(''); m.Add(b>=ur[i]+uc[j]-x[i,j]-1); zz[i,j]=b
    for C in cr: m.Add(sum(ur[i] for i in C)<=len(C)-1)
    for C in cc: m.Add(sum(uc[j] for j in C)<=len(C)-1)
    for E in cuts: m.Add(sum(zz[e] for e in E)<=len(E)-1)
    obj=sum(f[i][j]*x[i,j] for i in range(nr+1) for j in range(nc+1)); m.Add(obj<=CAP); m.Minimize(obj)
    s=cp_model.CpSolver(); s.parameters.num_workers=1; s.parameters.max_time_in_seconds=600
    st=s.Solve(m)
    if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        print(k,'it',it,'status',s.StatusName(st),'-> no robust assignment <=',CAP,'cuts',len(cuts),flush=True); break
    terms=[(i,j) for (i,j),var in x.items() for _ in range(s.Value(var))]
    E=[e for e,b in zz.items() if s.Value(b)]
    print(k,'it',it,'cost',s.ObjectiveValue(),'needs zero',E,'terms',terms,flush=True)
    if infeasible(E):
        M=mis(E); cuts.append(M); print('  cut',M,[str(numer(e)) for e in M],flush=True); continue
    r,pt=realize.solve_point(k,terms,verbose=False)
    print('  realize',r,pt,flush=True)
    if r=='ok':
        pickle.dump((terms,pt),open(f'cand_{k}_{it}.pkl','wb')); print('  CANDIDATE saved',flush=True); break
    else:
        cuts.append(E); print("  NEQ-CUT (review)",E,flush=True)
