# Double swap on one inside rank-one term: x=c_r (row swap at r), y ∝ c_r' (column swap at r'), r,r' non-orthogonal.
# Other 7 dual-basis terms take frame sides where possible. Exact build + cost.
from lib import *
import sympy as sp, itertools
def run(r,rp):
    ip=sum(C[r][i]*C[rp][i] for i in range(8)); assert ip!=0
    x0=croot(r); y0=[Fr(v,ip) for v in C[rp]]
    Sr,Srp=supp8(r),supp8(rp)
    # remaining 7 terms: choose x-frame e_i (needs i notin supp r'), y-frame e_i (needs i notin supp r); best assignment by brute force
    best=None
    for assign in itertools.product(['x','y','b'],repeat=8):
        pass
    # simple: indices i; x-frame allowed if i not in Srp ; y-frame allowed if i not in Sr; need 7 terms; complete basis numerically
    import random
    for trial in range(200):
        rnd=random.Random(trial)
        X=[x0]; PYk={0:y0}; slots=[]
        idx=list(range(8)); rnd.shuffle(idx)
        for i in idx:
            if len(slots)==7: break
            opts=[o for o in ('x','y') if (o=='x' and i not in Srp) or (o=='y' and i not in Sr)]
            slots.append((i,rnd.choice(opts) if opts else 'b'))
        terms=[(x0,y0)]
        for i,o in slots:
            terms.append((e(i),None) if o=='x' else ((None,e(i)) if o=='y' else (None,None)))
        PY=[k for k,t in enumerate(terms) if t[1] is not None]
        Xs=[]
        ok=True
        for l,t in enumerate(terms):
            if t[0] is not None: Xs.append(t[0]); continue
            xs=sp.symbols('x0:8'); eqs=[sum(xs[i]*terms[k][1][i] for i in range(8))-(1 if k==l else 0) for k in PY]
            sol=sp.solve(eqs,xs,dict=True)
            if not sol: ok=False;break
            sol=sol[0]; free=[s for s in xs if s not in sol]; vals={s:rnd.randint(1,9) for s in free}
            Xs.append([Fr(str(sp.sympify(sol.get(s,s)).subs(vals))) for s in xs])
        if not ok: continue
        Xm=sp.Matrix([[sp.Rational(str(v)) for v in r_] for r_ in Xs])
        if Xm.det()==0: continue
        Ym=Xm.inv().T; Y=[[Fr(str(Ym[k,i])) for i in range(8)] for k in range(8)]
        if any(Y[k]!=terms[k][1] for k in PY): continue
        # outside: E=[delta r], F=[delta r']
        vr=sum(Fr(C[r][i],2)*x0[i] for i in range(8)); vc=sum(Fr(C[rp][i],2)*Y[0][i] for i in range(8))
        Xh=[(Xs[0],[-vr]),([Fr(0)]*8,[vr]),(Xs[0],[Fr(0)])]
        Yh=[(Y[0],[-vc]),(Y[0],[-vc]),([Fr(0)]*8,[vc])]
        for k in range(1,8): Xh.append((Xs[k],[Fr(0)])); Yh.append((Y[k],[Fr(0)]))
        P,Q=build(Xh,Yh,[delta(r)],[delta(rp)])
        bad=check(P,Q,masked=False); cs=costs(P,Q)
        if best is None or sum(cs)<best[0]: best=(sum(cs),cs,bad,slots)
    return best
pairs=[(r,rp) for r in range(n) for rp in range(n) if r!=rp and G[r][rp]!=0][:6]
for r,rp in pairs:
    print('r,r\'',r,rp,'best (cost, per-term, mismatches, slots):',run(r,rp))
