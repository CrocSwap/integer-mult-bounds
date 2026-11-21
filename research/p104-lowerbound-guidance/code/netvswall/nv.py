# NETVSWALL own code: exact decoder min mass m(P) for target M o Q = diag(c), all c_p != 0 (Singular GB over QQ).
import itertools, subprocess, tempfile, os, sys, time
def dot(x,y): return bin(x&y).count('1')&1
def span(g):
    s={0}
    for v in g: s|={x^v for x in s}
    return frozenset(s)
def dimof(S): return len(S).bit_length()-1
def rk2(vecs):
    basis=[]
    for x in vecs:
        for b in basis: x=min(x,x^b)
        if x: basis.append(x)
    return len(basis)
_subs={}
def subspaces(h):
    if h in _subs: return _subs[h]
    seen={frozenset({0})}; fr=[frozenset({0})]
    while fr:
        nf=[]
        for S in fr:
            for v in range(1,1<<h):
                if v not in S:
                    T=frozenset(S|{x^v for x in S})
                    if T not in seen: seen.add(T); nf.append(T)
        fr=nf
    _subs[h]=sorted(seen,key=lambda s:(len(s),sorted(s)))
    return _subs[h]
def perp(S,h): return frozenset(x for x in range(1<<h) if all(dot(x,y)==0 for y in S))
def price(Dl,Sl):
    return rk2([sum(dot(t,p)<<j for j,p in enumerate(Sl)) for t in Dl])
def max_rects(h,labs,Rmax):
    """maximal (D,S,price) rectangles on index sets of labs, price<=Rmax"""
    subs=subspaces(h); best={}
    for V in subs:
        Sset=frozenset(i for i,q in enumerate(labs) if q in V)
        if not Sset: continue
        for K in subs:
            if not K<=V: continue
            r=dimof(V)-dimof(K)
            if r<1 or r>Rmax: continue
            Kp=perp(K,h)
            Dset=frozenset(i for i,q in enumerate(labs) if q in Kp)
            if not Dset: continue
            pr=price([labs[t] for t in Dset],[labs[p] for p in Sset])
            if pr<1: continue
            key=(Dset,Sset)
            if key not in best or best[key]>pr: best[key]=pr
    items=list(best.items()); keep=[]
    for (D,S),pr in items:
        if not any(pr2<=pr and D<=D2 and S<=S2 and (D,S)!=(D2,S2) for (D2,S2),pr2 in items): keep.append((D,S,pr))
    return keep
def sing_feasible(labs,Q,rects,cover,timeout=120):
    n=len(labs); vars_=[]; W={}; V={}
    for a,i in enumerate(cover):
        D,S,_=rects[i]
        for t in sorted(D): W[a,t]=f"w{a}_{t}"; vars_.append(W[a,t])
        for p in sorted(S): V[a,p]=f"v{a}_{p}"; vars_.append(V[a,p])
    eqs=[]
    for t in range(n):
        for p in range(n):
            if not Q[t][p]: continue
            terms=[f"{W[a,t]}*{V[a,p]}" for a,i in enumerate(cover) if t in rects[i][0] and p in rects[i][1]]
            if t==p:
                if not terms: return 'INFEASIBLE'
                vars_.append(f"z{t}"); eqs.append("("+"+".join(terms)+f")*z{t}-1")
            elif terms: eqs.append("+".join(terms))
    src=f"ring r=0,({','.join(vars_)}),dp;\noption(redSB);\nideal I={','.join(eqs)};\nideal G=std(I);\nif (size(G)==1 && deg(G[1])==0) {{ print(\"INFEASIBLE\"); }} else {{ print(\"FEASIBLE\"); }}\nquit;\n"
    with tempfile.NamedTemporaryFile('w',suffix='.sing',delete=False) as f: f.write(src); fn=f.name
    try: out=subprocess.run(['Singular','-q',fn],capture_output=True,text=True,timeout=timeout).stdout.strip()
    except subprocess.TimeoutExpired: out='TIMEOUT'
    os.unlink(fn); return out
def covers(rects,n,B,extra=True):
    cv=[frozenset(t for t in D if t in S) for D,S,_ in rects]  # diag cells covered
    full=frozenset(range(n)); mins=set()
    def rec(chosen,covered,budget):
        if covered==full: mins.add(tuple(sorted(chosen))); return
        c=min(full-covered)
        for i,r in enumerate(rects):
            if r[2]<=budget and c in cv[i] and i not in chosen: rec(chosen+[i],covered|cv[i],budget-r[2])
    rec([],frozenset(),B); out=set(mins)
    if extra:
        fr=list(mins)
        while fr:
            nf=[]
            for c in fr:
                left=B-sum(rects[i][2] for i in c)
                for i,r in enumerate(rects):
                    if r[2]<=left:
                        c2=tuple(sorted(c+(i,)))
                        if c2 not in out: out.add(c2); nf.append(c2)
            fr=nf
    return sorted(out,key=lambda c:(sum(rects[i][2] for i in c),len(c)))
def min_mass(h,labs,B=None,timeout=60,verbose=False):
    n=len(labs); B=n-1 if B is None else B
    Q=[[dot(s,t) for t in labs] for s in labs]
    R=max_rects(h,labs,B); C=covers(R,n,B)
    und=0
    for c in C:
        r=sing_feasible(labs,Q,R,c,timeout)
        if verbose: print([R[i][2] for i in c],r,flush=True)
        if r=='FEASIBLE': return ('FEASIBLE',sum(R[i][2] for i in c),c)
        if r!='INFEASIBLE': und+=1
    return ('NONE' if und==0 else 'UNDECIDED',len(C),und)
if __name__=='__main__':
    h=int(sys.argv[1]); labs=[int(x) for x in sys.argv[2].split(',')]
    t=time.time(); print(min_mass(h,labs,verbose=True),time.time()-t)
