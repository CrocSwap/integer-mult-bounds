# usage: python3 twisted_site_singular.py S Sprime [k timeout]   e.g. 01 23 2 600
# exact Q: does a single twisted site (k=2, n=4, N=5, unit inside mask) with |S|=2 exist?  Singular groebner over Q, 1 in ideal => none (even over C).
import sys, subprocess, itertools
from fractions import Fraction as Fr
def inv(M):
    m=len(M); A=[r[:]+[Fr(int(i==j)) for j in range(m)] for i,r in enumerate(M)]
    for c in range(m):
        p=next(r for r in range(c,m) if A[r][c]!=0); A[c],A[p]=A[p],A[c]
        pv=A[c][c]; A[c]=[v/pv for v in A[c]]
        for r in range(m):
            if r!=c and A[r][c]!=0:
                f=A[r][c]; A[r]=[a-f*b for a,b in zip(A[r],A[c])]
    return [r[m:] for r in A]
def signroot(n):
    s=lambda i,j:1 if i>j else -1
    xs=[[Fr(int(j==i)) for j in range(n)] for i in range(n)]
    ys=[[Fr(0 if i==j else s(i,j)) for j in range(n)] for i in range(n)]+[[Fr(1)]*n]
    S=[[Fr(0 if i==j else s(i,j)) for j in range(n)] for i in range(n)]
    xs.append([sum(a*b for a,b in zip(r,[Fr(-1)]*n)) for r in inv(S)]); return xs,ys
n=4;N=5
xs,ys=signroot(n)
def mat(x,y): return [[Fr(int(i==j))-2*x[i]*y[j] for j in range(n)] for i in range(n)]
def mm(A,B): return [[sum(A[i][k]*B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
T=[mat(x,y) for x,y in zip(xs,ys)]
k=int(sys.argv[3]) if len(sys.argv)>3 else 2
A=[[Fr(int(i==j)) for j in range(n)] for i in range(n)]
for j in range(N-1,k,-1): A=mm(A,T[j])  # A_k = T_{N-1}...T_{k+1}  (rightmost applied first)
# careful: A_k = T_{N-1} ... T_{k+1}: product with T_{N-1} leftmost
A=[[Fr(int(i==j)) for j in range(n)] for i in range(n)]
for j in range(N-1,k,-1): A=mm(A,T[j])
S=set(map(int,sys.argv[1])); Sp=set(map(int,sys.argv[2]))
def sm(M): return "matrix M[%d][%d]="%(n,n)+",".join("%s"%(("(%d)/(%d)"%(v.numerator,v.denominator))) for r in M for v in r)+";"
eqs=[]
cv=lambda name,i,j: "%s(%d)"%(name,i*n+j+1)
# CiA C : (Ci*Mat*C)[i][j] = sum_{a,b} Ci[i][a]*Mat[a][b]*C[b][j]
def prod_entry(M,i,j):
    terms=[]
    for a in range(n):
        for b in range(n):
            if M[a][b]!=0:
                terms.append("(%d/%d)*c(%d)*d(%d)"%(M[a][b].numerator,M[a][b].denominator,i*n+a+1,b*n+j+1))
    return "+".join(terms) if terms else "0"
# c = Ci, d = C
for i in range(n):
    for j in range(n):
        eqs.append("+".join("c(%d)*d(%d)"%(i*n+a+1,a*n+j+1) for a in range(n))+("-1" if i==j else ""))
for i in range(n):
    for j in range(n):
        if (j in S and i not in Sp) or (j not in S and i in Sp): eqs.append(prod_entry(A,i,j))
tau=T[k]
for i in range(n):
    for j in range(n):
        if not (i in S and j in S):
            e=prod_entry(tau,i,j)+("-1" if i==j else "")
            eqs.append(e)
# idempotent mask commutes: ok since x,y inside S
scr="ring r=0,(c(1..16),d(1..16)),dp;\noption(redSB);\nideal I=%s;\nideal G=groebner(I);\nprint(G[1]);\nprint(size(G));\nquit;\n"%",\n".join(eqs)
out=subprocess.run(['Singular','-q'],input=scr,capture_output=True,text=True,timeout=int(sys.argv[4]) if len(sys.argv)>4 else 600)
print(sys.argv[1:3],'k=%d'%k,'G[1]=',out.stdout.strip()[:200],out.stderr[:200])
