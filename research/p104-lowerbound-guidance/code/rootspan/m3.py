# ROOTSPAN m2: m1 + generalized Hall (Low_l U T_m) family, CP-SAT exact integers.
import sys
from math import comb
from ortools.sat.python import cp_model
N={0:0,1:1,2:2,3:4,4:8,5:12,6:20,7:36,8:60,9:104}
Rcap=[0,1,3,6,12,20,36,63,104]
def solve(D,Rc=Rcap,gen=True,hall=True,tl=300):
    m=cp_model.CpModel()
    c={l:m.NewIntVar(0,D,f'c{l}') for l in range(1,10)}
    m.Add(sum(c.values())==D)
    w={0:104}; w.update({b:N[9-b] for b in range(1,9)})
    n={b:c[b+1] for b in range(0,9)}
    cnt=0
    def Rof(expr,name,ub=8):
        v=m.NewIntVar(0,8,name+'m'); m.AddMinEquality(v,[expr,8])
        r=m.NewIntVar(0,104,name+'r'); m.AddElement(v,list(Rc[:9]),r); return r
    # forced crossing: any non-free depositor with b<l (l<=8) forces a crossing node at level l
    for l in range(2,9):
        ex=m.NewBoolVar(f'ex{l}')
        low=sum(n[b] for b in range(0,l))
        m.Add(low>=1).OnlyEnforceIf(ex); m.Add(low==0).OnlyEnforceIf(ex.Not())
        m.Add(c[l]>=1).OnlyEnforceIf(ex)
    # OS clique constraint
    for l in range(1,9):
        hits=sum(min(13,N[9-b])*n[b] for b in range(max(l,1),9))
        fl=m.NewIntVar(0,10**4,f'fl{l}'); m.AddDivisionEquality(fl,hits,13)
        mn=m.NewIntVar(0,8,f'mn{l}'); m.AddMinEquality(mn,[fl,8])
        m.Add(c[l]>=8-mn)
    # generalized: for level l=1..9, m'=0..D: sum of smallest (h-m') weights among High_l >= 104 - R(c_l+m')
    for l in range(1,10):
        hb=list(range(l,9))      # high levels beta in [l,8]
        h=sum(n[b] for b in hb) if hb else 0
        # smallest-first order: beta=8,7,...,l
        for mm in range(0,D+1):
            rr=m.NewIntVar(0,D,f'r{l}_{mm}')   # r=max(0,h-mm)
            m.AddMaxEquality(rr,[h-mm,0])
            # sum of smallest rr
            tot=[]; used_before=0
            above=[]  # list of n of levels above
            for b in sorted(hb,reverse=True):
                pre=sum(n[x] for x in above)
                take=m.NewIntVar(0,D,f't{l}_{mm}_{b}')
                rem=m.NewIntVar(-D,D,f'rem{l}_{mm}_{b}'); m.Add(rem==rr-pre)
                rem0=m.NewIntVar(0,D,f'rem0{l}_{mm}_{b}'); m.AddMaxEquality(rem0,[rem,0])
                m.AddMinEquality(take,[n[b],rem0])
                tot.append(w[b]*take); above.append(b)
            sm=sum(tot) if tot else 0
            Rv=Rof(c[l]+mm if True else mm,f'G{l}_{mm}')
            m.Add(sm>=104-Rv)
            if not gen: break
    if hall:
        from math import comb
        J=min(D,24)
        x={j:m.NewIntVar(0,104,f'x{j}') for j in range(1,J+1)}
        m.Add(sum(x.values())==104)
        cap=sum(w[b]*n[b] for b in range(0,9))
        m.Add(sum(j*x[j] for j in x)<=cap)
        for s in range(1,8):
            m.Add(sum(x[j]*comb(D-j,s-j) for j in x if j<=s)<=Rc[s]*comb(D,s))
    sol=cp_model.CpSolver(); sol.parameters.num_workers=1; sol.parameters.max_time_in_seconds=tl
    st=sol.Solve(m)
    if st in (cp_model.OPTIMAL,cp_model.FEASIBLE): return [sol.Value(c[l]) for l in range(1,10)]
    return None if st==cp_model.INFEASIBLE else 'UNK'
if __name__=='__main__':
    for D in range(24,70):
        r=solve(D); print(D,r,flush=True)
        if r is not None: break
