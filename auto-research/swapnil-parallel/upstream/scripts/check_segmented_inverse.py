"""Numerical check of the segmented inverse (Idea B') against a direct solve.

Builds the s x s Gaussian correction N with cyclic indices at 260 decimal digits, checks
that each segment block equals D T D^{-1}, then applies N^{-1} by block Gohberg-Semencul
style segment solves plus a Woodbury correction on the cross-wrap columns, and compares
with Gaussian elimination on N. Arguments: s t alpha^2 Q_bits P1_digits P2_digits.
"""
from decimal import Decimal as Dm, getcontext
from fractions import Fraction as F
import math, sys, random
args=[int(a) for a in sys.argv[1:]] or [60, 67, 9, 200, 120, 100]
s,t,a2,Qbits,P1,P2=args
getcontext().prec=260
PI=Dm('3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196')
sig=F(t,s); th=sig-1
q=lambda j: math.floor(F(t*j,s)+F(1,2)); beta=lambda j:F(t*j,s)-q(j)
dec=lambda f: Dm(f.numerator)/Dm(f.denominator)
E=lambda x:(-PI*a2*dec(x)).exp()
N=[[Dm(0)]*s for _ in range(s)]
for l in range(s):
  for j in range(l-3*s,l+3*s):
    X=(sig*j-q(l))**2-beta(j)**2
    N[l][j%s]+=E(X)
# segments on Z/sZ: start at index after a wrap
wraps=[j for j in range(s) if q(j+1)-q(j)==2]
segs=[]
for i,w0 in enumerate(wraps):
  st=w0+1; en=wraps[(i+1)%len(wraps)]+ (s if i+1==len(wraps) else 0)
  segs.append(list(range(st,en+1)))
print('theta',float(th),'nwraps',len(wraps),'seglens',sorted(set(len(g) for g in segs)))
# check M_k = D T D^{-1} vs principal block of N (cyclic indices)
maxerr=Dm(0)
for g in segs:
  l0=g[0]; ls=l0-(beta(l0)+F(1,2))/th
  for a in g:
    for b in g:
      h=b-a; u=a-ls; v=b-ls
      val=E(sig*h*h-h)* (PI*a2*dec(th*u*u)).exp()*(-PI*a2*dec(th*v*v)).exp()
      maxerr=max(maxerr,abs(val-N[a%s][b%s]))
print('max |M_k - N block| =',float(maxerr))
def solve(A,bv):
  n=len(A); M=[row[:]+[bv[i]] for i,row in enumerate(A)]
  for c in range(n):
    p=max(range(c,n),key=lambda r:abs(M[r][c])); M[c],M[p]=M[p],M[c]
    for r in range(n):
      if r!=c and M[r][c]!=0:
        f=M[r][c]/M[c][c]
        for k in range(c,n+1): M[r][k]-=f*M[c][k]
  return [M[i][n]/M[i][i] for i in range(n)]
random.seed(1)
u=[Dm(random.uniform(-1,1)) for _ in range(s)]
x=solve(N,u)
# segmented: M^{-1} via Toeplitz solve with D scaling at reduced precision P digits
lam=Dm(2)**(-Qbits-int(math.log2(s))-4)
w=1+math.sqrt(Qbits/(4.53*a2))
print('w formula',w)
def Minv(vec,Pdig):
  out=[Dm(0)]*s
  for g in segs:
    l0=g[0]; ls=l0-(beta(l0)+F(1,2))/th; L=len(g)
    getcontext().prec=Pdig
    T=[[+E(sig*(b-a)**2-(b-a)) for b in range(L)] for a in range(L)]
    rhs=[+(vec[g[i]%s]*(-PI*a2*dec(th*(i+l0-ls)**2)).exp()) for i in range(L)]
    y=solve(T,rhs)
    getcontext().prec=260
    for i in range(L): out[g[i]%s]=y[i]*(PI*a2*dec(th*(i+l0-ls)**2)).exp()
  return out
segid={}
for k,g in enumerate(segs):
  for j in g: segid[j%s]=k
Delta=[[N[a][b] if segid[a]!=segid[b] and N[a][b]>lam else Dm(0) for b in range(s)] for a in range(s)]
cols=sorted({b for a in range(s) for b in range(s) if Delta[a][b]!=0})
# max column offset from nearest wrap
print('Delta cols',len(cols),'per wrap',len(cols)/len(wraps))
fails=0
for Pdig in [P1,P2]:
  y=Minv(u,Pdig)
  # Woodbury capacitance solve
  MU=[Minv([Delta[r][c] for r in range(s)],Pdig) for c in cols]
  C=[[ (Dm(1) if i==j else Dm(0)) + MU[j][cols[i]] for j in range(len(cols))] for i in range(len(cols))]
  z=solve(C,[y[c] for c in cols])
  xs=[y[r]-sum(MU[j][r]*z[j] for j in range(len(cols))) for r in range(s)]
  err=max(abs(xs[i]-x[i]) for i in range(s))
  ok=err<Dm(2)**-Qbits
  fails+=not ok
  print('P digits',Pdig,'err vs direct %.3e'%float(err),'target %.3e'%float(Dm(2)**-Qbits),'PASS' if ok else 'FAIL')
  print("C nonzero block offsets", sorted({(segid[cols[i]]-segid[cols[j]])%len(segs) for i in range(len(cols)) for j in range(len(cols)) if i!=j and abs(C[i][j])>0}))

if fails: raise SystemExit('segmented inverse check failed')
