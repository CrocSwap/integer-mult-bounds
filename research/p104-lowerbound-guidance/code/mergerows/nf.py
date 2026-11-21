"""MERGEROWS nf: constructive normal form for a freely refactorable row class G (saturated rows, or equal supports).
2-adic elementary divisors: H = B1 P, where B1 = Z_2-basis of L1={h: W h in Z_2^n}, B2 = basis of L2={h: U h in Z_2^n},
B1^-1 B2^-T = P diag(2^d) R (Smith over Z_(2)).  New rows w'_k = W H e_k, u'_k = U H^-T e_k.  Then both families of
normalised digit-0 reductions are F2-independent (Goldman-Iwahori), and M_G = W U^T is unchanged."""
import numpy as np
from fractions import Fraction as Fr
import sys; sys.path.insert(0,'../iso3')
from gmax import v2, BIG
def mat(r,c,f): return [[f(i,j) for j in range(c)] for i in range(r)]
def mul(A,B): return [[sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
def T(A): return [list(r) for r in zip(*A)]
def inv(A):
    n=len(A); M=[list(map(Fr,A[i]))+[Fr(int(i==j)) for j in range(n)] for i in range(n)]
    for c in range(n):
        p=next(i for i in range(c,n) if M[i][c]!=0); M[c],M[p]=M[p],M[c]
        pv=M[c][c]; M[c]=[x/pv for x in M[c]]
        for i in range(n):
            if i!=c and M[i][c]!=0: f=M[i][c]; M[i]=[a-f*b for a,b in zip(M[i],M[c])]
    return [r[n:] for r in M]
def colval(W,j): return min(v2(W[i][j]) for i in range(len(W)) if W[i][j]!=0)
def lattice_basis(W):
    """columns of B (g x g) form a Z_2-basis of L={h: W h 2-integral}; W n x g rank g."""
    n=len(W); g=len(W[0]); B=[[Fr(int(i==j)) for j in range(g)] for i in range(g)]
    while True:
        WB=mul(W,B)
        for j in range(g):   # normalise each column to min valuation 0
            m=colval(WB,j)
            for i in range(g): B[i][j]*=Fr(2)**(-m)
        WB=mul(W,B)
        red=[[int(((x.numerator*pow(x.denominator,-1,2))%2) if v2(x)==0 else 0) if x!=0 else 0 for x in row] for row in WB]
        # find F2 dependency among columns
        cols=[int(''.join(str(red[i][j]) for i in range(n)),2) for j in range(g)]
        piv={}; dep=None
        for j,x in enumerate(cols):
            comb=1<<j
            while x:
                h=x.bit_length()-1
                if h in piv: px,pc=piv[h]; x^=px; comb^=pc
                else: piv[h]=(x,comb); break
            if x==0: dep=comb; break
        if dep is None: return B
        idx=[j for j in range(g) if dep>>j&1]; j0=idx[-1]
        for j in idx[:-1]:
            for i in range(g): B[i][j0]+=B[i][j]
def smith2(X):
    """X = P D R over Z_(2) (odd denominators are units); returns P (g x g, unimodular over Z_(2)) and d list."""
    g=len(X); A=[list(map(Fr,r)) for r in X]; P=[[Fr(int(i==j)) for j in range(g)] for i in range(g)]; d=[]
    for t in range(g):
        best=None
        for i in range(t,g):
            for j in range(t,g):
                if A[i][j]!=0 and (best is None or v2(A[i][j])<best[0]): best=(v2(A[i][j]),i,j)
        _,i,j=best
        A[t],A[i]=A[i],A[t]
        for r in A: r[t],r[j]=r[j],r[t]
        for r in P: r[t],r[i]=r[i],r[t]   # P <- P * swap  (we track A = P^-1 X R^-1)
        pv=A[t][t]
        for i2 in range(t+1,g):
            if A[i2][t]!=0:
                f=A[i2][t]/pv; A[i2]=[a-f*b for a,b in zip(A[i2],A[t])]
                for r in P: r[t]+=f*r[i2]      # row op E on A  => P <- P E^-1
        for j2 in range(t+1,g):
            if A[t][j2]!=0:
                f=A[t][j2]/pv
                for r in A: r[j2]-=f*r[t]
        d.append(v2(pv))
    return P,d
def normal_form(rows,cls):
    """refactor the rows in cls; returns new row list (same order, cls rows replaced) and depths d."""
    n=len(rows[0][0]); W=[[rows[k][0][t] for k in cls] for t in range(n)]; U=[[rows[k][1][t] for k in cls] for t in range(n)]
    B1=lattice_basis(W); B2=lattice_basis(U)
    X=mul(inv(B1),T(inv(B2))); P,d=smith2(X)
    H=mul(B1,P); Hit=T(inv(H))
    W2=mul(W,H); U2=mul(U,Hit)
    new=list(rows)
    for a,k in enumerate(cls): new[k]=([W2[t][a] for t in range(n)],[U2[t][a] for t in range(n)])
    return new,d
def drop_kernel(rows,cls):
    """if the class's W (or U) columns are dependent over Q, refactor so that a row gets w'=0 (or u'=0) and vanishes:
    H with first column h in ker W; w'_1 = 0.  Cost strictly drops.  Repeats until full rank.  Returns (rows, cls)."""
    import sympy
    n=len(rows[0][0])
    while len(cls)>=2:
        for side in (0,1):
            M=sympy.Matrix([[rows[k][side][t] for k in cls] for t in range(n)])
            ker=M.nullspace()
            if ker: break
        else: return rows,cls
        h=ker[0]; j=max(range(len(cls)),key=lambda i: h[i]!=0)
        g=len(cls); H=sympy.eye(g); H[:,j]=h
        Hm=[[Fr(int(sympy.fraction(H[i,l])[0]),int(sympy.fraction(H[i,l])[1])) for l in range(g)] for i in range(g)]
        if side==1: Hm=T(inv(Hm))      # want U H^-T to have a zero column => H^-T = [.. h ..]
        W=[[rows[k][0][t] for k in cls] for t in range(n)]; U=[[rows[k][1][t] for k in cls] for t in range(n)]
        W2=mul(W,Hm); U2=mul(U,T(inv(Hm)))
        new=list(rows)
        for a,k in enumerate(cls): new[k]=([W2[t][a] for t in range(n)],[U2[t][a] for t in range(n)])
        k0=cls[j]; new[k0]=([Fr(0)]*n,[Fr(0)]*n)
        rows=new; cls=[k for k in cls if k!=k0]
    return rows,cls
