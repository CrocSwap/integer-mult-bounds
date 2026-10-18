"""CP-SAT: minimise a valid lower bound of sum_j beta_j / d over decoders B = W U^T on the A-orthogonality pattern.
cost_j >= f(D_j), D_j = A_j cap R_j:  f = 0 (empty), 1 (one line), 2 (2..L2 lines), 3 (in a hyperplane flat), w otherwise,
using the exact flat census.  usage: costlb.py <system> <cmax> <sym 0/1> <seconds>"""
import sys, time, pickle; sys.path.insert(0,sys.path[0])
from algebra_lines import *
from ortools.sat.python import cp_model
name, cmax, sym, secs = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
roots=e8_roots(); I8=np.eye(8,dtype=np.int64); Li,Lj,Lk=left_quat()
basis={'Gauss':[I8,Li],'Eisen':[I8,a2_rotation(roots)],'Hurwitz':[I8,Li,Lj,Lk]}[name]
reps,NO=lines_over(roots,basis); v=len(reps); w=arank(reps,basis,range(v))
# flats: hyperplanes = closures of rank w-1; rank-2 flats; computed exactly
def closure(idx):
    r=arank(reps,basis,idx); return frozenset(j for j in range(v) if j in idx or arank(reps,basis,list(idx)+[j])==r), r
cache='flats_%s.pkl'%name
try: fl=pickle.load(open(cache,'rb'))
except Exception:
    fl={1:{frozenset([i]) for i in range(v)}}
    for r in range(2,w):
        fl[r]=set()
        for F in fl[r-1]:
            bas=[]
            for i in sorted(F):
                if arank(reps,basis,bas+[i])>len(bas): bas.append(i)
                if len(bas)==r-1: break
            for j in range(v):
                if j not in F: fl[r].add(closure(bas+[j])[0])
    pickle.dump(fl,open(cache,'wb'))
L={r:max(len(F) for F in fl[r]) for r in fl}
print(name,'v',v,'w',w,'max flat sizes',L,flush=True)
m=cp_model.CpModel()
u=[[m.NewBoolVar('') for j in range(cmax)] for T in range(v)]
W=u if sym else [[m.NewBoolVar('') for j in range(cmax)] for T in range(v)]
def AND(a,b):
    if a is b: return a
    z=m.NewBoolVar(''); m.AddBoolAnd([a,b]).OnlyEnforceIf(z); m.AddBoolOr([a.Not(),b.Not()]).OnlyEnforceIf(z.Not()); return z
d=[[AND(W[T][j],u[T][j]) for j in range(cmax)] for T in range(v)]
for T in range(v): m.AddBoolXOr(d[T])                 # B_TT = 1
for T in range(v):
    for S in range(v):
        if NO[T,S] and (not sym or T<S):
            m.AddBoolXOr([AND(W[T][j],u[S][j]) for j in range(cmax)]+[m.NewConstant(1)])   # B_TS = 0
# cost levels: cost_j >= sum_{l} lev_{j,l}; lev_1 = nonempty, lev_2 = >=2 lines, lev_r (3..w-1) = not inside a rank-(r-1) flat
obj=[]
# precompute: for levels r>=3 use flats of rank r-1 with more than L[r-2] lines (smaller ones are covered by count)
for j in range(cmax):
    n=sum(d[T][j] for T in range(v))
    l1=m.NewBoolVar(''); m.Add(n>=1).OnlyEnforceIf(l1); m.Add(n==0).OnlyEnforceIf(l1.Not()); obj.append(l1)
    if w>=2:
        l2=m.NewBoolVar(''); m.Add(n>=2).OnlyEnforceIf(l2); m.Add(n<=1).OnlyEnforceIf(l2.Not()); obj.append(l2)
    prevL=1
    for r in range(3,w+1):
        # lev_r = 1 unless D_j inside some rank-(r-1) flat; sets of size <= L[r-2] are allowed free at this level (relaxation)
        lr=m.NewBoolVar(''); obj.append(lr)
        small=m.NewConstant(0)
        big=list(fl[r-1])
        sel=[m.NewBoolVar('') for F in big]
        for s_,F in zip(sel,big):
            for T in range(v):
                if T not in F: m.AddImplication(s_, d[T][j].Not())
        m.AddBoolOr(sel+[small,lr])
obj_expr=sum(obj)
# symmetry: totals ordered by count
cnt=[sum(d[T][j] for T in range(v)) for j in range(cmax)]
for j in range(cmax-1): m.Add(cnt[j]>=cnt[j+1])
m.Minimize(obj_expr)
sv=cp_model.CpSolver(); sv.parameters.max_time_in_seconds=secs; sv.parameters.num_workers=8
t=time.time(); st=sv.Solve(m)
print(name,'cmax',cmax,'sym',sym,sv.StatusName(st),'obj',sv.ObjectiveValue() if st in (cp_model.OPTIMAL,cp_model.FEASIBLE) else None,'bound',sv.BestObjectiveBound(),'x_K lb',sv.BestObjectiveBound()/v,round(time.time()-t,1),flush=True)
if st in (cp_model.OPTIMAL,cp_model.FEASIBLE):
    U=np.array([[sv.Value(u[T][j]) for j in range(cmax)] for T in range(v)]); Wv=np.array([[sv.Value(W[T][j]) for j in range(cmax)] for T in range(v)])
    tot=[ (arank(reps,basis,[T for T in range(v) if Wv[T,j] and U[T,j]]), int(U[:,j].sum())) for j in range(cmax)]
    print('totals (rank of D_j, |A_j|):',tot)
    np.savez('costlb_%s_%d_%d.npz'%(name,cmax,sym),U=U,W=Wv)
