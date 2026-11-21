from math import comb
from ortools.sat.python import cp_model
Rc=[0,1,3,6,12,20,36,63,104]
for name,R in (('caps',Rc),('P104heur',[0,1,3,6,12,20,32,55,104])):
    m=cp_model.CpModel()
    a={j:m.NewIntVar(0,104,f'a{j}') for j in range(1,9)}
    m.Add(sum(a.values())==104)
    for s in range(1,8):
        m.Add(sum(a[j]*comb(8-j,s-j) for j in a if j<=s)<=R[s]*comb(8,s))
    m.Minimize(sum(j*a[j] for j in a))
    sv=cp_model.CpSolver(); sv.parameters.num_workers=1
    st=sv.Solve(m); print(name,sv.StatusName(st),sv.ObjectiveValue(),[sv.Value(a[j]) for j in a])
