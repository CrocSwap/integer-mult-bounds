# AUDIT-PAD: independent re-implementation of the EXCESS padding lemma (own E8, own frame, own labels; no base.py).
# Cost (A): rank_F2 B[R,A], B_ts = 1 + <r_t,r_s> mod 2 (integer inner products).
# Cost (B): dim U - dim(U ∩ span ℓ(A)^⊥β), labels ℓ=(1, simple-root coords mod 2), β = ab + n^T Cartan n' (mod 2): subspace algebra only.
import itertools, random
from fractions import Fraction as Fr
# E8 roots in doubled coords
R2=[]
for i,j in itertools.combinations(range(8),2):
    for si in (2,-2):
        for sj in (2,-2):
            v=[0]*8; v[i]=si; v[j]=sj; R2.append(tuple(v))
for s in itertools.product((1,-1),repeat=8):
    if s.count(-1)%2==0: R2.append(s)
assert len(R2)==240
ip=lambda a,b: sum(x*y for x,y in zip(a,b))//4
lines=[];seen=set()
for v in R2:
    w=tuple(-x for x in v)
    if w in seen: continue
    seen.add(v); lines.append(v)
assert len(lines)==120
F=[(2,2,0,0,0,0,0,0),(2,-2,0,0,0,0,0,0),(0,0,2,2,0,0,0,0),(0,0,2,-2,0,0,0,0),(0,0,0,0,2,2,0,0),(0,0,0,0,2,-2,0,0),(0,0,0,0,0,0,2,2),(0,0,0,0,0,0,2,-2)]
assert all(ip(F[i],F[j])==2*(i==j) for i in range(8) for j in range(8))
def canon(v):
    w=tuple(-x for x in v); return v if v in seen else w
Fc=[canon(f) for f in F]
P112=[l for l in lines if l not in Fc]; assert len(P112)==112
E=P112+Fc; n=112; N=120
G=[[ip(a,f) for f in F] for a in E]           # Gram realisation rows c_t (C_E); frame rows = 2e_j
for j in range(8): assert G[n+j]==[2*(i==j) for i in range(8)]
# simple roots of E8 (doubled coords), coords of each line in that basis (solve over Q)
S=[(1,-1,-1,-1,-1,-1,-1,1),(2,2,0,0,0,0,0,0),(-2,2,0,0,0,0,0,0),(0,-2,2,0,0,0,0,0),(0,0,-2,2,0,0,0,0),(0,0,0,-2,2,0,0,0),(0,0,0,0,-2,2,0,0),(0,0,0,0,0,-2,2,0)]
def solveQ(M,b):  # M square list rows; solve M x = b
    m=len(M); A=[[Fr(x) for x in M[i]]+[Fr(b[i])] for i in range(m)]
    for c in range(m):
        p=next(r for r in range(c,m) if A[r][c]!=0); A[c],A[p]=A[p],A[c]
        for r in range(m):
            if r!=c and A[r][c]!=0:
                f=A[r][c]/A[c][c]; A[r]=[x-f*y for x,y in zip(A[r],A[c])]
    return [A[i][m]/A[i][i] for i in range(m)]
ST=[[S[k][i] for k in range(8)] for i in range(8)]
coef=[solveQ(ST,v) for v in E]
assert all(all(x.denominator==1 for x in c) for c in coef)
Cart=[[ip(a,b)%2 for b in S] for a in S]
lab=[(1,)+tuple(int(x)%2 for x in c) for c in coef]
assert len(set(lab[:n]))==112
def beta(a,b): return (a[0]*b[0]+sum(a[1+i]*Cart[i][j]*b[1+j] for i in range(8) for j in range(8)))%2
for t in random.Random(0).sample(range(N),30):
    for s in random.Random(t).sample(range(N),30): assert beta(lab[t],lab[s])==(1+ip(E[t],E[s]))%2
def toint(v): return int(''.join(map(str,v)),2)
def basis(vs):
    b=[]
    for x in vs:
        for y in b: x=min(x,x^y)
        if x: b.append(x)
    return b
def rk(vs): return len(basis(vs))
def costA(Rr,Aa): return rk([toint([(1+ip(E[t],E[s]))%2 for s in Aa]) for t in Rr]) if Rr and Aa else 0
def costB(Rr,Aa):
    if not Rr or not Aa: return 0
    U=[lab[t] for t in Rr]; Al=[lab[s] for s in Aa]
    # perp of span(Al): solve beta(x,a)=0 for all a, x in F2^9 (brute 512)
    perp=[x for x in itertools.product((0,1),repeat=9) if all(beta(x,a)==0 for a in basis_vecs(Al))]
    Ub=rk([toint(u) for u in U]); Pb=rk([toint(p) for p in perp])
    inter=Ub+Pb-rk([toint(u) for u in U]+[toint(p) for p in perp])
    return Ub-inter
def basis_vecs(vs):
    out=[];b=[]
    for v in vs:
        x=toint(v)
        for y in b: x=min(x,x^y)
        if x: b.append(x); out.append(v)
    return out
def decoder_cost(cols,Y,Nl):
    ca=cb=0
    for col,y in zip(cols,Y):
        Rr=[t for t in range(Nl) if col[t]!=0]
        Aa=[s for s in range(Nl) if sum(G[s][i]*y[i] for i in range(8))!=0]
        a=costA(Rr,Aa); b=costB(Rr,Aa); assert a==b,(a,b); ca+=a
    return ca
def exact(cols,Y,Nl):
    for t in range(Nl):
        row=[sum(Fr(col[t])*Fr(y[i]) for col,y in zip(cols,Y)) for i in range(8)]
        if row!=[Fr(x) for x in G[t]]: return False
    return True
def corrected(col,y):
    nz=[i for i in range(8) if y[i]!=0]
    if len(nz)!=1: return None
    i=nz[0]; Rr=[t for t in range(n) if col[t]!=0]; z=lab[n+i]
    return i if rk([toint(lab[t]) for t in Rr]+[toint(z)])==rk([toint(lab[t]) for t in Rr]) else None
def merge(cols,Y):  # merge corrected terms with proportional y (normalisation)
    out=[];outY=[];seenI={}
    for col,y in zip(cols,Y):
        i=corrected(col,y)
        if i is not None and i in seenI:
            k=seenI[i]; mu=Fr(y[i])/Fr(outY[k][i]); out[k]=[a+mu*b for a,b in zip(out[k],col)]
        else:
            if i is not None: seenI[i]=len(out)
            out.append(list(col)); outY.append(list(y))
    return out,outY
def pad(cols,Y,tag):
    assert exact(cols,Y,n),'P112 exactness'
    c0=decoder_cost(cols,Y,n); cols,Y=merge(cols,Y); assert exact(cols,Y,n)
    c=decoder_cost(cols,Y,n); assert c<=c0
    Ec=[list(col)+[0]*8 for col in cols]; EY=[list(y) for y in Y]; I=[]
    for k,(col,y) in enumerate(zip(cols,Y)):
        i=corrected(col,y)
        if i is not None: I.append(i); Ec[k][n+i]=Fr(2)/Fr(y[i])
    for j in range(8):
        if j not in I:
            u=[0]*N; u[n+j]=1; Ec.append(u); EY.append([2*(i==j) for i in range(8)])
    assert exact(Ec,EY,N),'E8 exactness'
    # one-sidedness: q_k = C_E y_k by construction (Y given); also N = P_E (C_E Y)^T = C_E C_E^T follows from P_E Y^T = C_E
    cE=decoder_cost(Ec,EY,N)
    print(f"{tag:28s} terms={len(cols):2d} I={sorted(I)} P112={c} (raw {c0}) E8={cE} diff={cE-c} ok={cE==c+8}")
    return cE-c
C=[G[t] for t in range(n)]
coordcols=lambda skip=(): [[C[t][j] for t in range(n)] for j in range(8) if j not in skip]
e=lambda j,s=1:[s*(i==j) for i in range(8)]
res=[]
# 1 coordinate decoder
res.append(pad(coordcols(),[e(j) for j in range(8)],'coord'))
# 2 root swaps (own search over all J up to size 4 that admit roots)
for k in (1,2,3,4):
    for J in itertools.combinations(range(8),k):
        rs=[]
        for m in J:
            cand=[t for t in range(n) if C[t][m]!=0 and all(C[t][j]==0 for j in J if j!=m) and t not in rs]
            if not cand: break
            rs.append(cand[0])
        else: break
    else: continue
    cols=coordcols(J); Y=[e(j) for j in range(8) if j not in J]
    for m,r in zip(J,rs):
        p=[sum(C[t][i]*C[r][i] for i in range(8)) for t in range(n)]; a=p[r]; p[r]=0
        # p_{r} with y = C_r-direction; express: term (p_r - a δ_r, y = c_r/|c_r|^2 ...) -> use y = e_m-proportional? build via h=c_r
        cols.append(p); Y.append(None); cols.append([int(t==r) for t in range(n)]); Y.append(None)
    # solve Y exactly: unknown y's for the swap terms; use generic solve P Y^T = C
    import sympy as sp
    Pm=sp.Matrix(n,len(cols),lambda t,kk: cols[kk][t]); sol,par=Pm.gauss_jordan_solve(sp.Matrix(C)); Ys=sol.subs({s:0 for s in sol.free_symbols})
    res.append(pad(cols,[[Fr(int(sp.fraction(x)[0]),int(sp.fraction(x)[1])) for x in Ys.row(kk)] for kk in range(len(cols))],f'rootswap k={k} J={J}'))
# 3 generic basis change: P = C A, Y^T = A^{-1}  (no corrections expected)
import sympy as sp
rng=random.Random(7)
for trial in range(2):
    A=sp.Matrix(8,8,lambda i,j: rng.choice([0,0,1,-1,2]) + (3 if i==j else 0))
    if A.det()==0: continue
    Ai=A.inv(); cols=[[sum(C[t][i]*A[i,k] for i in range(8)) for t in range(n)] for k in range(8)]
    Y=[[Fr(int(sp.fraction(Ai[k,i])[0]),int(sp.fraction(Ai[k,i])[1])) for i in range(8)] for k in range(8)]
    res.append(pad(cols,Y,f'basis-change {trial}'))
# 4 overcomplete m=11 one-sided: P = C A (8x11), Y^T = right inverse of A, A contains e_i columns + sparse sums
A=sp.zeros(8,11)
for i in range(8): A[i,i]=1
A[0,8]=1;A[1,8]=1; A[2,9]=1;A[3,9]=-1;A[4,9]=1; A[5,10]=2;A[6,10]=1;A[7,10]=1
Yt=A.T*(A*A.T).inv()   # right inverse (11x8): A*Yt = I
cols=[[sum(C[t][i]*A[i,k] for i in range(8)) for t in range(n)] for k in range(11)]
Y=[[Fr(int(sp.fraction(Yt[k,i])[0]),int(sp.fraction(Yt[k,i])[1])) for i in range(8)] for k in range(11)]
res.append(pad(cols,Y,'overcomplete m=11'))
# 5 shift decoder with unit term carrying two directions; and a split-correction decoder (exercises merge)
for t0 in (0,57,90):
    cols=coordcols((0,1)); Y=[e(j) for j in range(2,8)]
    c1=[C[t][0]+(t==t0) for t in range(n)]; c2=[C[t][1]+(t==t0) for t in range(n)]
    cols+= [c1,c2,[int(t==t0) for t in range(n)]]; Y+=[e(0),e(1),[-1,-1,0,0,0,0,0,0]]
    res.append(pad(cols,Y,f'shift t0={t0}'))
# 6 root swap split into two proportional corrected terms (tests merge): take first rootswap k=1 and split its swap column
J=(0,); r=[t for t in range(n) if C[t][0]!=0][0]
p=[sum(C[t][i]*C[r][i] for i in range(8)) for t in range(n)]; a=p[r]; p[r]=0
cols=coordcols(J)+[p,[int(t==r) for t in range(n)]]
Pm=sp.Matrix(n,len(cols),lambda t,kk: cols[kk][t]); sol,_=Pm.gauss_jordan_solve(sp.Matrix(C)); Ys=sol.subs({s:0 for s in sol.free_symbols})
Y=[[Fr(int(sp.fraction(x)[0]),int(sp.fraction(x)[1])) for x in Ys.row(kk)] for kk in range(len(cols))]
k=len(cols)-2; half=[Fr(1,2)*x for x in cols[k]]
cols2=cols[:k]+[half,half]+cols[k+1:]; Y2=Y[:k]+[Y[k],Y[k]]+Y[k+1:]
res.append(pad(cols2,Y2,'split swap (merge)'))
print('ALL diff==8:',all(d==8 for d in res), 'n=',len(res))
