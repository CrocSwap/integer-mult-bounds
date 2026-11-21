from ortools.sat.python import cp_model
N={0:0,1:1,2:2,3:4,4:8,5:12,6:20,7:36,8:60,9:104}
m=cp_model.CpModel()
c={l:m.NewIntVar(0,60,f'c{l}') for l in range(1,10)}
n={b:c[b+1] for b in range(0,9)}   # wlog max depositors
for l in range(1,9):
    hits=sum(min(13,N[9-b])*n[b] for b in range(max(l,1),9))
    fl=m.NewIntVar(0,10**4,f'f{l}'); m.AddDivisionEquality(fl,hits,13)
    mn=m.NewIntVar(0,8,f'm{l}'); m.AddMinEquality(mn,[fl,8]); m.Add(c[l]>=8-mn)
m.Minimize(sum(c.values()))
s=cp_model.CpSolver(); s.parameters.num_workers=1
st=s.Solve(m); print(s.StatusName(st),s.ObjectiveValue(),[s.Value(c[l]) for l in range(1,10)])
