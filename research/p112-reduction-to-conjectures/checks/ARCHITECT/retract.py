# Retraction test (ARCHITECT §3): for an exact decoder (P,Q) of N0 on P112, for every outside direction on each side,
# replace it by C'h (h = 0, h = pivot shear for each term carrying it, and 2 random h) and record the new cost.
# Retraction keeps PQ^T = N0 (WALL §2: outside factors are free). Exact Fractions.
import sys, json, random, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../TWINSWAP'))
from lib import *
import sympy as sp
Cp=sp.Matrix([[sp.Rational(C[t][i],2) for i in range(8)] for t in range(n)])   # n x 8
def decomp(P):
    """P: list of m vectors. Return (X: 8 x m, E: list of s vectors, X2: s x m) with p_k = C'x_k + sum_a X2[a,k] E[a]."""
    M=sp.Matrix([[sp.Rational(str(x)) for x in p] for p in P]).T     # n x m
    E=[]; cur=Cp
    for k in range(M.shape[1]):
        cand=cur.row_join(M[:,k])
        if cand.rank()>cur.rank(): E.append(M[:,k]); cur=cand
    B=Cp
    for e_ in E: B=B.row_join(e_)
    sol=(B.T*B).LUsolve(B.T*M)       # exact least squares = exact solve (B full column rank, M in col B)
    assert B*sol==M
    return sol[:8,:], E, sol[8:,:]
def rebuild(X,E,X2):
    B=Cp
    for e_ in E: B=B.row_join(e_)
    M=B*X.col_join(X2)
    return [[Fr(str(M[t,k])) for t in range(n)] for k in range(M.shape[1])]
def cost_of(P,Q): return sum(costs(P,Q))
def retractions(P,Q,side,rng):
    if side=='Q': P,Q=Q,P          # Bd and N0 symmetric: treat columns as rows
    X,E,X2=decomp(P); out=[]
    for a in range(len(E)):
        hs=[('zero',sp.zeros(8,1))]
        for k in range(X.shape[1]):
            if X2[a,k]!=0: hs.append((f'pivot{k}',-X[:,k]/X2[a,k]))
        for r in range(2): hs.append((f'rand{r}',sp.Matrix([rng.randint(-3,3) for _ in range(8)])))
        res=[]
        for name,h in hs:
            E2=list(E); E2[a]=Cp*h
            P2=rebuild(X,E2,X2)
            res.append((cost_of(P2,Q),name))
        out.append((a,sorted(res)[:3]))
    return out
def report(tag,P,Q):
    rng=random.Random(1)
    assert check(P,Q,masked=True)==0
    c=cost_of(P,Q)
    for side in 'PQ':
        r=retractions(P,Q,side,rng)
        for a,best in r:
            print(f'{tag}: cost {c}; side {side} dir {a}: best retractions {best}  {"NONINCREASING" if best[0][0]<=c else "ALL INCREASE"}',flush=True)
if __name__=='__main__':
    which=sys.argv[1]
    if which=='json':
        d=json.load(open(os.path.join(os.path.dirname(__file__),'../TWINSWAP/decoder.json')))
        P=[[Fr(x) for x in p] for p in d['P']]; Q=[[Fr(x) for x in q] for q in d['Q']]
        report('MS3a(2,1)',P,Q)
    elif which=='wit':
        src=open(os.path.join(os.path.dirname(__file__),'../TWINSWAP/witness16.py')).read()
        src=src.replace("    P,Q=build(Xh,Yh,E,F)\n","    P,Q=build(Xh,Yh,E,F); STASH.append((mode,P,Q))\n")
        STASH=[]; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../TWINSWAP'))
        g={'STASH':STASH,'__name__':'w16'}; exec(src,g)
        for mode,P,Q in STASH: report('witness16-'+mode,P,Q)
    elif which=='swap':
        kr,kc=int(sys.argv[2]),int(sys.argv[3])
        os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../TWINSWAP'))
        from swapfam import feasible_search, build_family
        b,ex=feasible_search(kr,kc)
        Xh,Yh,E,F,names=build_family(*ex,verbose=False)
        P,Q=build(Xh,Yh,E,F)
        report(f'swap({kr},{kc})',P,Q)
if __name__=='__main__' and sys.argv[1]=='dbl':
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../TWINSWAP'))
    src=open('dbl.py').read()
    src=src.replace("for trial in range(200):","for trial in range(40):")
    src=src.replace("        if best is None or sum(cs)<best[0]: best=(sum(cs),cs,bad,slots)","        if best is None or sum(cs)<best[0]: best=(sum(cs),cs,bad,slots); BEST[0]=(P,Q)")
    src=src.split("pairs=[(r,rp)")[0]
    BEST=[None]; g={'BEST':BEST,'__name__':'dbl'}; exec(src,g)
    pairs=[(r,rp) for r in range(n) for rp in range(n) if r!=rp and G[r][rp]!=0][:2]
    for r,rp in pairs:
        BEST[0]=None; b=g['run'](r,rp); P,Q=BEST[0]; report(f'double-swap r={r},r\'={rp}',P,Q)
