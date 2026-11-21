# DECOMP dc1 (own code): exact construction + check of a k=3, n=2 Q=0 legal caller word whose frame is
# indecomposable and NON-tight (n+2 = 4 < 6 = |Iota|).  Pure Fractions; Gaussian rationals as pairs.
from fractions import Fraction as F
import itertools, sys
# ---------- 2x2 rational helpers ----------
def mm(X,Y): return [[sum(X[i][k]*Y[k][j] for k in range(len(Y))) for j in range(len(Y[0]))] for i in range(len(X))]
def inv2(X):
    d=X[0][0]*X[1][1]-X[0][1]*X[1][0]; assert d!=0
    return [[X[1][1]/d,-X[0][1]/d],[-X[1][0]/d,X[0][0]/d]]
def neg(X): return [[-a for a in r] for r in X]
I2=[[F(1),F(0)],[F(0),F(1)]]
def H(a,b,u): return [[F(1),a*u],[b/u,1+a*b]]
def tr(X): return X[0][0]+X[1][1]
def kry(X): v=[F(1),F(0)]; Xv=[X[0][0],X[1][0]]; return [[v[0],Xv[0]],[v[1],Xv[1]]]
a1,b1,a3,b3,a2=F(1),F(1),F(1),F(2),F(1)
N=lambda a,b: mm(inv2(H(a,b,1)),H(a,b,-1))
Y1,Y3=H(a1,b1,1),H(a3,b3,1)
P2=inv2(Y3)
V3=mm(mm(inv2(P2),N(a3,b3)),P2); V1=N(a1,b1)
V2=neg(mm(inv2(V3),inv2(V1)))
b2=(tr(V2)-2)/(4*a2)
N2=N(a2,b2); Y2=H(a2,b2,1)
assert tr(N2)==tr(V2)
P1=mm(kry(N2),inv2(kry(V2)))          # N2 P1 = P1 V2
assert mm(N2,P1)==mm(P1,V2)
C0=I2; C1=mm(P1,inv2(Y1)); C2=mm(P2,inv2(mm(Y2,P1)))
print("a,b:",(a1,b1),(a2,b2),(a3,b3)," ab+1:",a1*b1+1,a2*b2+1,a3*b3+1)
print("C1",C1,"C2",C2)
# ---------- decompose a GL2(Q) matrix into ADD/SCALE events (rows r=0,1), first event applied first ----------
def decomp(X):
    # find events e_1..e_m with E_m...E_1 = X ; build by reducing X to I with left row ops, then invert
    X=[r[:] for r in X]; ops=[]   # ops reduce: L_m..L_1 X = I  => X = L_1^-1 ... L_m^-1, apply L_m^-1 first
    if X[0][0]==0:
        ops.append(('add',0,1,F(1))); X[0]=[X[0][j]+X[1][j] for j in range(2)]
    c=-X[1][0]/X[0][0]; ops.append(('add',1,0,c)); X[1]=[X[1][j]+c*X[0][j] for j in range(2)]
    c=-X[0][1]/X[1][1]; ops.append(('add',0,1,c)); X[0]=[X[0][j]+c*X[1][j] for j in range(2)]
    for r in range(2):
        s=1/X[r][r]; ops.append(('scale',r,s)); X[r]=[x*s for x in X[r]]
    assert X==I2
    evs=[]
    for op in reversed(ops):
        if op[0]=='add': evs.append(('add',op[1],op[2],-op[3]))
        else: evs.append(('scale',op[1],1/op[2]))
    return evs
# ---------- Gaussian rationals and polynomials in D0..D2 ----------
class G:
    __slots__=('r','i')
    def __init__(s,r,i=F(0)): s.r=F(r); s.i=F(i)
    def __add__(s,o): o=o if isinstance(o,G) else G(o); return G(s.r+o.r,s.i+o.i)
    __radd__=__add__
    def __neg__(s): return G(-s.r,-s.i)
    def __sub__(s,o): return s+(-(o if isinstance(o,G) else G(o)))
    def __mul__(s,o): o=o if isinstance(o,G) else G(o); return G(s.r*o.r-s.i*o.i,s.r*o.i+s.i*o.r)
    __rmul__=__mul__
    def inv(s): d=s.r*s.r+s.i*s.i; return G(s.r/d,-s.i/d)
    def __eq__(s,o): o=o if isinstance(o,G) else G(o); return s.r==o.r and s.i==o.i
    def iszero(s): return s.r==0 and s.i==0
class P:  # polynomial: dict exponent-tuple -> G
    def __init__(s,d=None): s.d={k:v for k,v in (d or {}).items() if not v.iszero()}
    @staticmethod
    def c(x): return P({(0,0,0):x if isinstance(x,G) else G(x)})
    def __add__(s,o):
        d=dict(s.d)
        for k,v in o.d.items(): d[k]=d.get(k,G(0))+v
        return P(d)
    def __mul__(s,o):
        d={}
        for k1,v1 in s.d.items():
            for k2,v2 in o.d.items():
                k=tuple(a+b for a,b in zip(k1,k2)); d[k]=d.get(k,G(0))+v1*v2
        return P(d)
    def __eq__(s,o): return (s+P({k:-v for k,v in o.d.items()})).d=={}
def Dmono(t): e=[0,0,0]; e[t]=1; return P({tuple(e):G(1)})
# ---------- word ----------
def lam_evs(r,sig): return [('lam',r,sig)]
def J(t,a,b):  # stage t: LIFT-wrapped HOST(0,1,a,b) (LAMBDA on t-register = register 1), then IDLE contacts
    return [('lam',1,-1),('host',0,1,a,b),('lam',1,1),('idle',0,t),('idle',1,t)]
word=decomp(C0) if C0!=I2 else []
word+=J(0,a1,b1)+decomp(C1)+J(1,a2,b2)+decomp(C2)+J(2,a3,b3)+[('lam',0,1),('lam',1,1)]
print("events:",len(word)); [print(" ",e) for e in word]
def evmat(e,q,i):  # 2x2 matrix over P acting on row-stack (R <- M R)
    one,zero=P.c(1),P.c(0)
    M=[[one,zero],[zero,one]]
    if e[0]=='add': _,r,s,c=e; M[r][s]=M[r][s]+P.c(c)
    elif e[0]=='scale': _,r,c=e; M[r][r]=P.c(c)
    elif e[0]=='lam':
        _,r,sg=e; M[r][r]=P.c(G(F(1,2),F(sg,2)) + G(F(1,2),F(-sg,2))*q*q)
    elif e[0]=='idle': _,r,t=e; M[r][r]=Dmono(t)
    elif e[0]=='host':
        _,s,t,a,b=e
        M[s][s]=one; M[s][t]=P.c(G(a)*q); M[t][s]=P.c(G(b)*q.inv()); M[t][t]=P.c(1+a*b)
    return M
def pm(X,Y): return [[X[i][0]*Y[0][j]+X[i][1]*Y[1][j] for j in range(2)] for i in range(2)]
ok=True
for q in [G(1),G(-1),G(0,1),G(0,-1)]:
    R=[[P.c(1),P.c(0)],[P.c(0),P.c(1)]]
    for e in word: R=pm(evmat(e,q,G(0,1)),R)
    Dall=Dmono(0)*Dmono(1)*Dmono(2)
    tgt=[[P.c(q)*Dall,P.c(0)],[P.c(0),P.c(q)*Dall]]   # q^1 * D0 D1 D2 on both rows, masks {0,1,2}, ex=1
    good=all(R[a][b]==tgt[a][b] for a in range(2) for b in range(2))
    print("q=",(q.r,q.i),"replay==target:",good); ok&=good
# ---------- frame (CallerWord Aw/Bw at q=1, D=1; columns = nonzero q-odd terms; block = event index) ----------
def ratmat(e,q):
    if e[0]=='add': _,r,s,c=e; M=[r_[:] for r_ in I2]; M[r][s]+=c; return M
    if e[0]=='scale': _,r,c=e; M=[r_[:] for r_ in I2]; M[r][r]=c; return M
    if e[0] in ('lam','idle'): return [r_[:] for r_ in I2]      # q=+-1 (q^2=1), D=1
    _,s,t,a,b=e; M=[[F(0)]*2 for _ in range(2)]; M[s][s]=F(1); M[s][t]=a*q; M[t][s]=b/q; M[t][t]=1+a*b; return M
pre=[I2]
for e in word: pre.append(mm(ratmat(e,1),pre[-1]))
cols=[]  # (event j, x, y, coef): evMat(-1)-evMat(1) = sum E_{x,y} coef
for j,e in enumerate(word):
    if e[0]=='host':
        _,s,t,a,b=e
        for (x,y,c) in [(s,t,-2*a),(t,s,-2*b)]:
            if c!=0: cols.append((j,x,y,c))
Pinv=lambda j: inv2(pre[j])
A=[[Pinv(j+1)[r][x]*c for (j,x,y,c) in cols] for r in range(2)]
B=[[pre[j][y][r] for (j,x,y,c) in cols] for r in range(2)]
m=len(cols); beta=[c[0] for c in cols]
Gm=[[sum(B[r][p]*A[r][q] for r in range(2)) for q in range(m)] for p in range(m)]
K=[[ (2 if p==q else 0) + (Gm[p][q] if beta[p]<=beta[q] else -Gm[p][q]) for q in range(m)] for p in range(m)]
def rank(M):
    M=[r[:] for r in M]; rk=0; rows=len(M); cs=len(M[0])
    for c in range(cs):
        piv=next((r for r in range(rk,rows) if M[r][c]!=0),None)
        if piv is None: continue
        M[rk],M[piv]=M[piv],M[rk]
        for r in range(rows):
            if r!=rk and M[r][c]!=0:
                f=M[r][c]/M[rk][c]; M[r]=[M[r][k]-f*M[rk][k] for k in range(cs)]
        rk+=1
    return rk
# product of stages V_j = I + A Pi_j B^T over all events in order
Pk=I2
for j in range(len(word)):
    idx=[p for p in range(m) if beta[p]==j]
    V=[[ (1 if a==b else 0)+sum(A[a][p]*B[b][p] for p in idx) for b in range(2)] for a in range(2)]
    Pk=mm(V,Pk)
print("|Iota| =",m," n+2 =",4," prod V =",Pk)
print("rank G =",rank(Gm)," rank K =",rank(K))
for j in sorted(set(beta)):
    idx=[p for p in range(m) if beta[p]==j]
    blk=[[K[p][q] for q in idx] for p in idx]; d=blk[0][0]*blk[1][1]-blk[0][1]*blk[1][0]
    print(" stage(event",j,") K-block det =",d)
hs=sorted(set(beta))
for s,t in itertools.combinations(hs,2):
    i1=[p for p in range(m) if beta[p]==s]; i2=[p for p in range(m) if beta[p]==t]
    blk=[[K[p][q] for q in i2] for p in i1]; print(" off-block",(s,t),"det =",blk[0][0]*blk[1][1]-blk[0][1]*blk[1][0])
meets=[[any(A[r][p]!=0 or B[r][p]!=0 for p in range(m) if beta[p]==j) for j in hs] for r in range(2)]
print("role meets stage:",meets)
print("ALL OK" if ok and Pk==neg(I2) else "FAIL")
