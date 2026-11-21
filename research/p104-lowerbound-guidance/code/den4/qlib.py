"""DEN4 qlib (own code): label sets, decoders (exact, Fractions), 2-adic digit data, F2 ranks."""
import json, itertools, numpy as np
from fractions import Fraction as Fr
D56='<research-tree>/cards/WILD/LUNCH/exchange/d56dir/mod4/'
E=json.load(open(D56+'e8base.json')); GB=np.array(E['Gb'],dtype=object)
CALL=np.array(E['C'],dtype=object)          # 120 E8 lines, root-basis coords; first 104 = P104
def gram(C): return C.dot(GB).dot(C.T)      # diag 2
def Qof(C):
    G=gram(C); return np.array([[1 if G[i,j]%2==0 else 0 for j in range(len(C))] for i in range(len(C))],dtype=np.int64)
def lineset(name):
    C=CALL
    if name=='P104': return C[:104]
    if name=='P120': return C
    G=gram(C)
    if name=='E7': return C[[i for i in range(120) if G[0,i]==0]]          # lines orthogonal to line 0: 63
    if name=='HS64':   # 64 lines not in a D8 sublattice: complement of a maximal set of 56 = D8 roots? use: lines orth-graph
        raise NotImplementedError
    raise KeyError(name)
def rk2(M):
    M=np.asarray(M)%2; piv={}; r=0
    for row in M:
        x=int(''.join(str(int(v)) for v in row),2) if len(row) else 0
        while x:
            h=x.bit_length()-1
            if h in piv: x^=piv[h]
            else: piv[h]=x; r+=1; break
    return r
def v2(x):
    x=Fr(x); 
    if x==0: return 10**9
    k=0; p,q=x.numerator,x.denominator
    while p%2==0: p//=2; k+=1
    while q%2==0: q//=2; k-=1
    return k
def mod2k(x,m):  # 2-adic residue of a 2-integral Fraction mod 2^m
    x=Fr(x); M=2**m; return (x.numerator*pow(x.denominator,-1,M))%M
def normalise(rows,Q):
    """rows: list of (w,u) Fraction vectors with sum_k (w u^T) o Q = I on Q-cells.
    Rescale each row by a power of 2 so w is 2-integral with a unit entry; e = max 2-denominator exponent of u.
    Returns e, W, V (integer residues mod 2^(e+1)) with sum D(w)QD(v) = 2^e I mod 2^(e+1) on Q-cells, plus prices."""
    out=[]
    for w,u in rows:
        s=min(v2(x) for x in w if x!=0); w=[Fr(x)/Fr(2)**s for x in w]; u=[Fr(x)*Fr(2)**s for x in u]
        out.append((w,u))
    e=max(max(-v2(x) for x in u if x!=0) for w,u in out); e=max(e,0)
    m=e+1; n=len(Q)
    W=np.array([[mod2k(x,m) for x in w] for w,u in out],dtype=np.int64).T
    V=np.array([[mod2k(x*2**e,m) for x in u] for w,u in out],dtype=np.int64).T
    D=[[i for i in range(n) if w[i]!=0] for w,u in out]; S=[[i for i in range(n) if u[i]!=0] for w,u in out]
    pr=[rk2(Q[np.ix_(d,s)]) if d and s else 0 for d,s in zip(D,S)]
    return e,W,V,pr,D,S
def check_decoder(rows,Q):
    n=len(Q); bad=0
    for i in range(n):
        for j in range(n):
            if Q[i,j]:
                val=sum(w[i]*u[j] for w,u in rows)
                if val!=(1 if i==j else 0): bad+=1
    return bad
# ---- standard-coordinate E8 lines (scaled x2, norm 8) ----
def std_lines():
    R=[]
    for i,j in itertools.combinations(range(8),2):
        for a in (2,-2):
            for b in (2,-2):
                v=[0]*8; v[i]=a; v[j]=b; R.append(tuple(v))
    for s in itertools.product((1,-1),repeat=8):
        if s.count(-1)%2==0: R.append(tuple(s))
    L=[];seen=set()
    for r in R:
        if tuple(-x for x in r) in seen: continue
        seen.add(r); L.append(r)
    return np.array(L,dtype=object)
def std_set(name):
    L=std_lines()
    if name=='HS64': return L[[i for i in range(len(L)) if all(abs(x)==1 for x in L[i])]]
    if name=='P120s': return L
    if name=='E7s':
        a0=L[0]; return L[[i for i in range(len(L)) if L[i].dot(a0)==0]]
    raise KeyError
def Q_std(L):
    G=L.dot(L.T); return np.array([[1 if G[i,j]%8==0 else 0 for j in range(len(L))] for i in range(len(L))],dtype=np.int64)
def gram_rows_std(L,U):
    """Gram-class decoder: U 8x8 rational (rows u_k), W rows w_k with sum u_k w_k^T = I. row k: w=(l.u_k), u=(l.w_k)/8."""
    import sympy
    Um=sympy.Matrix(U); Wm=(Um.inv()).T   # rows w_k: U^T W = I  => sum_k u_k w_k^T = U^T W
    rows=[]
    for k in range(8):
        uk=[Fr(int(sympy.fraction(x)[0]),int(sympy.fraction(x)[1])) for x in Um.row(k)]
        wk=[Fr(int(sympy.fraction(x)[0]),int(sympy.fraction(x)[1])) for x in Wm.row(k)]
        wv=[sum(Fr(int(l[i]))*uk[i] for i in range(8)) for l in L]
        uv=[sum(Fr(int(l[i]))*wk[i] for i in range(8))/8 for l in L]
        if any(wv) and any(uv): rows.append((wv,uv))
    return rows
def gram_rows_B(L,B,U,norm):
    """General Gram-class decoder: label coords L (n x d), bilinear form B (d x d), U (d x d rational, rows u_k).
    w_k = L B u_k, u-side = L B w'_k / norm with U^T W' = B^-1 (so sum_k u_k w'_k^T = B^-1, M = L B B^-1 B L^T / norm = Gram/norm)."""
    import sympy
    Bm=sympy.Matrix(B); Um=sympy.Matrix(U); Wm=(Um.T).inv()*Bm.inv()
    d=Bm.shape[0]; rows=[]
    LB=[[sum(sympy.Integer(int(L[i][a]))*Bm[a,b] for a in range(d)) for b in range(d)] for i in range(len(L))]
    tofr=lambda x: Fr(int(sympy.fraction(x)[0]),int(sympy.fraction(x)[1]))
    for k in range(d):
        uk=[Um[k,b] for b in range(d)]; wk=[Wm[k,b] for b in range(d)]
        wv=[tofr(sum(r[b]*uk[b] for b in range(d))) for r in LB]
        uv=[tofr(sum(r[b]*wk[b] for b in range(d))/norm) for r in LB]
        if any(wv) and any(uv): rows.append((wv,uv))
    return rows
def rand_unimod(d,rng,steps=12):
    import sympy
    M=sympy.eye(d)
    for _ in range(steps):
        i,j=rng.choice(d,2,replace=False); c=int(rng.choice([-1,1]))
        E=sympy.eye(d); E[i,j]=c; M=M*E
    return M
