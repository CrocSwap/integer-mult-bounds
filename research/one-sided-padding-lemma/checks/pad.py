# EXCESS: one-sided padding P112 -> P120 (E8). For a one-sided P112 decoder (P, Y; P Y^T = C) with corrected set I,
# build the one-sided E8 decoder: rows f_i (i in I) get p_k(f_i)=2/y_k[i] on the corrected term; for j not in I add term (delta_{f_j}, y=2e_j).
# Check exactness P_E Y^T = C_E (C_E rows: c_t, and 2e_j for f_j) and cost_E = cost_P112 + 8, cost by two implementations:
#  (A) rank_F2 of B[R_k, A_k], B_ts = 1 + <r_t,r_s> mod 2 from the root vectors (no labels);
#  (B) label formula dim U_k - eps_k (Lemma 3.1 form; eps only for y ∝ f_i with z_i in U and f_i not in A_k).
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

# --- adapter names used by the checks below (E8 data from the construction above)
L=P112; F0=Fc; dot=ip; FC=G[:n]; LAB=lab[:n]; Z=lab[n:]; LABE=lab
def toint(v): return int(''.join(map(str,v)),2)
def rk(vs):
    b=[]
    for x in vs:
        for y in b: x=min(x,x^y)
        if x: b.append(x)
    return len(b)
def f2rank(vs): return rk([toint(v) for v in vs])
import sympy as sp
C=[[int(x) for x in row] for row in FC]
ROOTS=[list(r) for r in L]+[list(f) for f in F0]   # 120 lines: P112 then frame
CE=C+[[2 if i==j else 0 for i in range(8)] for j in range(8)]
assert all(sum(int(dot(ROOTS[n+j],F0[i])) for _ in [0])==CE[n+j][i] for j in range(8) for i in range(8))
def gf2rank(rows):
    rows=[int(''.join(map(str,r)),2) if r else 0 for r in rows]; r=0
    basis=[]
    for x in rows:
        for b in basis: x=min(x,x^b)
        if x: basis.append(x)
    return len(basis)
def costA(R,A,lines):
    return gf2rank([[ (1+int(dot(lines[t],lines[s])))%2 for s in A] for t in R]) if R and A else 0
def costB(R,y,lab,A):
    U=[lab[t] for t in R]; w=f2rank(U); nz=[i for i in range(8) if y[i]!=0]
    # label span of A is full unless y ∝ f_i and no line of A has label outside W_i (Lemma 3.1 + frame lines)
    if len(nz)==1:
        i=nz[0]
        Alab=[lab[s] for s in A]
        if f2rank(Alab)==8 and f2rank(U+[Z[i]])==w and f2rank(Alab+[Z[i]])==9: return w-1
    return w
def cost(Pcols,Y,lines,lab,N):
    ca=cb=0
    for k,col in enumerate(Pcols):
        y=list(Y[k]); R=[t for t in range(N) if col[t]!=0]
        if not R or all(v==0 for v in y): continue
        A=[s for s in range(N) if sum(sp.Rational(CE[s][i])*y[i] for i in range(8))!=0]
        ca+=costA(R,A,lines); cb+=costB(R,y,lab,A)
    return ca,cb
def solve(cols):
    P=sp.Matrix(n,len(cols),lambda t,k: cols[k][t]); sol,par=P.gauss_jordan_solve(sp.Matrix(C))
    Y=sol.subs({s:0 for s in sol.free_symbols}); assert P*Y==sp.Matrix(C); return Y
def pad_and_check(cols,tag):
    Y=solve(cols); Yl=[list(Y.row(k)) for k in range(len(cols))]
    c112=cost(cols,Yl,ROOTS,LABE,n)
    # corrected set
    Ecols=[c+[0]*8 for c in cols]; EY=[y[:] for y in Yl]; I=[]
    for k,y in enumerate(Yl):
        nz=[i for i in range(8) if y[i]!=0]; R=[t for t in range(n) if cols[k][t]!=0]
        if len(nz)==1 and f2rank([LAB[t] for t in R]+[Z[nz[0]]])==f2rank([LAB[t] for t in R]) and nz[0] not in I:
            i=nz[0]; I.append(i); Ecols[k][n+i]=sp.Rational(2)/y[i]
    for j in range(8):
        if j not in I:
            c=[0]*(n+8); c[n+j]=1; Ecols.append(c); EY.append([2 if i==j else 0 for i in range(8)])
    PE=sp.Matrix(n+8,len(Ecols),lambda t,k: Ecols[k][t]); YE=sp.Matrix(EY)
    assert PE*YE==sp.Matrix(CE), 'exactness'
    cE=cost(Ecols,EY,ROOTS,LABE,n+8)
    print(tag,'I=',sorted(I),'P112 cost (A,B)=',c112,' E8 one-sided cost (A,B)=',cE, 'diff', cE[0]-c112[0])
    assert c112[0]==c112[1] and cE[0]==cE[1] and cE[0]==c112[0]+8
# coordinate decoder
pad_and_check([[C[t][l] for t in range(n)] for l in range(8)],'coord')
def swap(J,roots):
    cols=[[C[t][l] for t in range(n)] for l in range(8) if l not in J]
    for r in roots:
        pr=[sum(C[t][i]*C[r][i] for i in range(8)) for t in range(n)]; pr[r]=0; cols.append(pr)
        d=[0]*n; d[r]=1; cols.append(d)
    return cols
for k in (1,2,3,4):
    for J in itertools.combinations(range(8),k):
        rs=[]
        for m in J:
            cand=[t for t in range(n) if C[t][m]!=0 and all(C[t][j]==0 for j in J if j!=m) and t not in rs]
            if not cand: break
            rs.append(cand[0])
        else: pad_and_check(swap(list(J),rs),'swap k=%d J=%s'%(k,J)); break
print('PAD OK')
