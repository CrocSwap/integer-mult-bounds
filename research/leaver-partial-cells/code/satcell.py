"""Layered CP-SAT for helper-free leaver circuits (exact set + taint semantics).
regs 0..na-1 atoms (mutable), na..na+ny-1 targets. A gate t += s: set(t) |= set(s) (disjoint, s nonempty),
taint(t)=taint(s)=taint(t)|taint(s); forbidden: taint bit i on target i. Target sources only into targets."""
from ortools.sat.python import cp_model
def solve(na,ny,goalY,Mgoal,Mhosts,T0,L,yy=True,maxyy=None,time_limit=120,workers=8,forbid_solutions=(),fixed_prefix=(),ne=0,hostallow=None,Yallow=None,nh=0,hint=None,maxh=None,S0Y=None,hreads=None):
    NA=na;na_regs=na+nh
    nr=na_regs+ny;m=cp_model.CpModel();NY=ny;ny=ny+ne
    goalY=list(goalY)
    S=[[[m.NewBoolVar('') for j in range(na)] for r in range(nr)] for k in range(L+1)]
    T=[[[m.NewBoolVar('') for i in range(ny)] for r in range(nr)] for k in range(L+1)]
    for r in range(nr):
        for j in range(na):m.Add(S[0][r][j]==(1 if (r<na and j==r) else (((S0Y[r-na_regs]>>j)&1) if (S0Y is not None and r>=na_regs) else 0)))
        for i in range(ny):m.Add(T[0][r][i]==((T0[r]>>i)&1))
    act=[m.NewBoolVar('') for k in range(L)]
    selt=[[m.NewBoolVar('') for r in range(nr)] for k in range(L)]
    sels=[[m.NewBoolVar('') for r in range(nr)] for k in range(L)]
    nyy=[]
    for k in range(L):
        m.Add(sum(selt[k])==act[k]);m.Add(sum(sels[k])==act[k])
        if k:m.AddImplication(act[k],act[k-1])
        for r in range(nr):m.AddBoolOr([selt[k][r].Not(),sels[k][r].Not()])
        ysrc=m.NewBoolVar('');m.Add(sum(sels[k][na_regs:])==ysrc)
        m.Add(sum(selt[k][na_regs:])>=ysrc);nyy.append(ysrc)
        if not yy:m.Add(ysrc==0)
        A=[m.NewBoolVar('') for j in range(na)];Bt=[m.NewBoolVar('') for j in range(na)]
        Ts=[m.NewBoolVar('') for i in range(ny)];Tt=[m.NewBoolVar('') for i in range(ny)]
        for r in range(nr):
            for j in range(na):
                m.Add(A[j]==S[k][r][j]).OnlyEnforceIf(sels[k][r])
                m.Add(Bt[j]==S[k][r][j]).OnlyEnforceIf(selt[k][r])
            for i in range(ny):
                m.Add(Ts[i]==T[k][r][i]).OnlyEnforceIf(sels[k][r])
                m.Add(Tt[i]==T[k][r][i]).OnlyEnforceIf(selt[k][r])
        for j in range(na):
            m.Add(A[j]==0).OnlyEnforceIf(act[k].Not());m.Add(Bt[j]==0).OnlyEnforceIf(act[k].Not());m.Add(A[j]+Bt[j]<=1)
        for i in range(ny):
            m.Add(Ts[i]==0).OnlyEnforceIf(act[k].Not());m.Add(Tt[i]==0).OnlyEnforceIf(act[k].Not())
        m.Add(sum(A)>=1).OnlyEnforceIf(act[k])
        J=[m.NewBoolVar('') for i in range(ny)]
        for i in range(ny):
            m.AddMaxEquality(J[i],[Ts[i],Tt[i]])
            if i<NY:m.AddImplication(selt[k][na_regs+i],J[i].Not());m.AddImplication(sels[k][na_regs+i],J[i].Not())
        for r in range(nr):
            for j in range(na):
                m.Add(S[k+1][r][j]>=S[k][r][j])
                m.Add(S[k+1][r][j]<=S[k][r][j]+A[j])
                m.Add(S[k+1][r][j]<=S[k][r][j]).OnlyEnforceIf(selt[k][r].Not())
                m.Add(S[k+1][r][j]>=A[j]).OnlyEnforceIf(selt[k][r])
            inv=m.NewBoolVar('');m.AddMaxEquality(inv,[selt[k][r],sels[k][r]])
            for i in range(ny):
                m.Add(T[k+1][r][i]==J[i]).OnlyEnforceIf(inv)
                m.Add(T[k+1][r][i]==T[k][r][i]).OnlyEnforceIf(inv.Not())
    for i in range(NY):
        for j in range(na):m.Add(S[L][na_regs+i][j]==((goalY[i]>>j)&1))
        if Yallow is not None:
            for b in range(ny):
                if not (Yallow[i]>>b)&1:m.Add(T[L][na_regs+i][b]==0)
    hv=[m.NewBoolVar('') for h in Mhosts]
    for b,h in zip(hv,Mhosts):
        for j in range(na):m.Add(S[L][h][j]==((Mgoal>>j)&1)).OnlyEnforceIf(b)
        if hostallow is not None:
            for i in range(ny):
                if not (hostallow>>i)&1:m.Add(T[L][h][i]==0).OnlyEnforceIf(b)
    m.AddBoolOr(hv)
    if maxyy is not None:m.Add(sum(nyy)<=maxyy)
    for sol in forbid_solutions:
        lits=[]
        for k,(t,s) in enumerate(sol):lits+=[selt[k][t].Not(),sels[k][s].Not()]
        m.AddBoolOr(lits)
    for k,(t,s) in enumerate(fixed_prefix):m.Add(selt[k][t]==1);m.Add(sels[k][s]==1)
    hu=[]
    for h in range(na,na_regs):
        u=m.NewBoolVar('');m.AddMaxEquality(u,[selt[k][h] for k in range(L)]+[sels[k][h] for k in range(L)]);hu.append(u)
    if maxh is not None:m.Add(sum(hu)<=maxh)
    if hreads is not None:
        # hreads: {helper_index_offset: [allowed target indices]} -> helper read exactly once by each allowed target, nothing else
        for ho,allowed in hreads.items():
            h=na+ho
            for i in allowed:
                bs=[]
                for k in range(L):
                    b=m.NewBoolVar('');m.AddBoolAnd([sels[k][h],selt[k][na_regs+i]]).OnlyEnforceIf(b)
                    m.AddBoolOr([sels[k][h].Not(),selt[k][na_regs+i].Not()]).OnlyEnforceIf(b.Not());bs.append(b)
                m.Add(sum(bs)==1)
            for k in range(L):
                for r in range(nr):
                    if r>=na_regs and (r-na_regs) in allowed:continue
                    m.AddBoolOr([sels[k][h].Not(),selt[k][r].Not()])
    if hint:
        for k in range(L):
            on=k<len(hint);m.AddHint(act[k],on)
            for r in range(nr):
                m.AddHint(selt[k][r],on and hint[k][0]==r);m.AddHint(sels[k][r],on and hint[k][1]==r)
    m.Minimize(sum(act)*100+sum(nyy)+sum(hu)*10000)
    sv=cp_model.CpSolver();sv.parameters.max_time_in_seconds=time_limit;sv.parameters.num_workers=workers
    st=sv.Solve(m)
    if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE):return sv.StatusName(st),None
    sol=[]
    for k in range(L):
        if not sv.Value(act[k]):break
        t=[r for r in range(nr) if sv.Value(selt[k][r])][0];s=[r for r in range(nr) if sv.Value(sels[k][r])][0]
        sol.append((t,s))
    return sv.StatusName(st),sol
