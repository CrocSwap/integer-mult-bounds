# Exact min-mass decoder search for a target T (odd cells) on labels; own code.
# rows restricted to readers x gathers (WLOG); rectangles maximal flags; feasibility via Singular GB over QQ.
import subprocess, tempfile, os, itertools
from common import *
from rects import max_rects
def all_covers(R,cells,B,extra=True):
    cells=frozenset(cells)
    cv=[frozenset(c for c in cells if c[0] in r[0] and c[1] in r[1]) for r in R]
    mins=set()
    def rec(chosen,covered,budget):
        if covered==cells: mins.add(tuple(sorted(chosen))); return
        c=min(cells-covered)
        for i,r in enumerate(R):
            if r[2]<=budget and c in cv[i] and i not in chosen:
                rec(chosen+[i],covered|cv[i],budget-r[2])
    rec([],frozenset(),B)
    out=set(mins)
    if extra:
        # add extra rows (multiset) within remaining budget
        frontier=list(mins)
        while frontier:
            nf=[]
            for c in frontier:
                left=B-sum(R[i][2] for i in c)
                for i,r in enumerate(R):
                    if r[2]<=left:
                        c2=tuple(sorted(c+(i,)))
                        if c2 not in out: out.add(c2); nf.append(c2)
            frontier=nf
    return sorted(out,key=lambda c:(len(c),sum(R[i][2] for i in c)))
def singular_feasible(R,cover,T,Q,cells_all,timeout=120):
    # variables w_i_t, v_i_p
    vars_=[];W={};V={}
    for a,i in enumerate(cover):
        D,S,_=R[i]
        for t in sorted(D): W[a,t]=f"w{a}_{t}"; vars_.append(W[a,t])
        for p in sorted(S): V[a,p]=f"v{a}_{p}"; vars_.append(V[a,p])
    eqs=[]
    for (t,p) in cells_all:
        terms=[f"{W[a,t]}*{V[a,p]}" for a,i in enumerate(cover) if t in R[i][0] and p in R[i][1]]
        if not terms: 
            if T[t][p]!=0: return 'uncovered'
            continue
        eqs.append("+".join(terms)+f"-({T[t][p]})")
    if not eqs: return 'trivial'
    src=f"""ring r=0,({','.join(vars_)}),dp;
option(redSB);
ideal I={','.join(eqs)};
ideal G=std(I);
if (size(G)==1 && deg(G[1])==0) {{ print("INFEASIBLE"); }} else {{ print("FEASIBLE dim="+string(dim(G))); }}
quit;
"""
    with tempfile.NamedTemporaryFile('w',suffix='.sing',delete=False) as f: f.write(src); fn=f.name
    try:
        out=subprocess.run(['Singular','-q',fn],capture_output=True,text=True,timeout=timeout).stdout
    except subprocess.TimeoutExpired: out='TIMEOUT'
    os.unlink(fn)
    return out.strip()
def min_mass(h,labs,T,Q,B,timeout=120,verbose=False,extra=True,diagfree=False):
    n=len(labs)
    odd=[(t,p) for t in range(n) for p in range(n) if Q[t][p] and not (diagfree and t==p)]
    nz=[(t,p) for (t,p) in odd if T[t][p]]
    readers=sorted({t for t,p in nz}); gathers=sorted({p for t,p in nz})
    cells_all=[(t,p) for (t,p) in odd if t in readers and p in gathers]
    R=max_rects(h,labs,readers,gathers,B)
    C=all_covers(R,nz,B,extra)
    res=[]
    for c in C:
        r=singular_feasible(R,c,T,Q,cells_all,timeout)
        res.append((c,r))
        if verbose: print([R[i][2] for i in c],r,flush=True)
        if r.startswith('FEASIBLE'): return 'FEASIBLE',c,R,res
    return ('NONE' if all(x[1]=='INFEASIBLE' for x in res) else 'UNDECIDED'),None,R,res
