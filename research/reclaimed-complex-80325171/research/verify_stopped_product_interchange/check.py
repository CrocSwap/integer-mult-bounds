from fractions import Fraction as Q
from random import Random
from pathlib import Path
import json, math, hashlib, time
START=time.monotonic()
BASE=Path(__file__).resolve().parents[1]/'pr_watch_2316/PR104'

def eye(n): return [[Q(i==j) for j in range(n)] for i in range(n)]
def zero(m,n): return [[Q(0) for j in range(n)] for i in range(m)]
def trans(A): return [list(x) for x in zip(*A)]
def add(A,B): return [[x+y for x,y in zip(a,b)] for a,b in zip(A,B)]
def neg(A): return [[-x for x in a] for a in A]
def sub(A,B): return add(A,neg(B))
def mul(A,B): return [[sum((x*y for x,y in zip(a,b)),Q(0)) for b in trans(B)] for a in A]
def inv(A):
 n=len(A); T=[list(a)+e for a,e in zip(A,eye(n))]
 for j in range(n):
  p=next((i for i in range(j,n) if T[i][j]),None)
  if p is None: raise ValueError('Singular')
  T[j],T[p]=T[p],T[j]; c=T[j][j]; T[j]=[x/c for x in T[j]]
  for i in range(n):
   if i!=j:
    c=T[i][j]; T[i]=[x-c*y for x,y in zip(T[i],T[j])]
 return [t[n:] for t in T]
def nonsingular(A):
 try: inv(A); return True
 except ValueError: return False
def lower(A): return all(not A[i][j] for i in range(len(A)) for j in range(i+1,len(A)))
def block(A,B,C,D): return [a+b for a,b in zip(A,B)]+[c+d for c,d in zip(C,D)]
def diag(A,B): return block(A,zero(len(A),len(B)),zero(len(B),len(A)),B)
def kron(A,B): return [[x*y for x in a for y in b] for a in A for b in B]
def reverse(n): return [list(reversed(a)) for a in eye(n)]
def trace(A): return sum(A[i][i] for i in range(len(A)))
def specialize(A,mod): return [[int(x.numerator*pow(x.denominator,-1,mod)%mod) for x in a] for a in A]
def modmul(A,B,mod): return [[sum(x*y for x,y in zip(a,b))%mod for b in trans(B)] for a in A]

m=4; I=eye(m); C=reverse(m)
H=[[Q(i==j)-Q(1,9) for j in range(m)] for i in range(m)]
raw=[]
for support in ((0,1,2),(0,1,3)):
 t=[[Q(i in support)] for i in range(m)]
 q=mul(t,mul(trans(t),H)); q=[[x/2 for x in a] for a in q]
 raw.append((3,sub(I,q)))
for r in (1,2,3): raw.append((r,[[Q(i==j and i<r) for j in range(m)] for i in range(m)]))
comm=sub(mul(raw[0][1],raw[1][1]),mul(raw[1][1],raw[0][1]))
assert trace(mul(comm,comm))==Q(-3,8)
rng=Random(104)
for attempt in range(1,201):
 G=[[Q(rng.randint(-3,3)) for j in range(m)] for i in range(m)]
 if not nonsingular(G): continue
 Gi=inv(G); fam=[(r,mul(mul(G,P),Gi)) for r,P in raw]
 if all(nonsingular([row[:k] for row in P[:k]]) for r,P in fam for k in range(1,r+1)): break
else: raise AssertionError('No common basis in bounded controls')

checks=[]; all_matrices=[]; full_identities=[]
for pi,(r,P) in enumerate(fam):
 assert mul(P,P)==P
 M=mul(P,C); X=[a[:] for a in M]; L=eye(m); R=eye(m)
 for i in range(r):
  j=m-1-i; assert X[i][j]
  A=eye(m); A[i][i]=1/X[i][j]; X=mul(A,X); L=mul(A,L)
  A=eye(m)
  for ii in range(i+1,m): A[ii][i]=-X[ii][j]
  X=mul(A,X); L=mul(A,L)
  A=eye(m)
  for jj in range(j): A[j][jj]=-X[i][jj]
  X=mul(X,A); R=mul(R,A)
 E=[[Q(i==j) for j in range(r)] for i in range(m)]
 F=[[Q(i==m-1-j) for j in range(r)] for i in range(m)]
 Et,Ft=trans(E),trans(F); Pi=mul(E,Ft)
 assert X==Pi and lower(L) and lower(R) and lower(inv(L)) and lower(inv(R))
 D=block(sub(I,P),mul(P,C),mul(C,P),mul(mul(C,sub(I,P)),C))
 Qmat=diag(L,inv(R)); g=mul(mul(Qmat,D),inv(Qmat)); gm=sub(g,eye(2*m))
 # Upper-left rows give A, and last reverse-index columns give B.
 A=[row[:m] for row in gm[:r]]
 B=[[gm[m+i][2*m-1-j] for j in range(r)] for i in range(m)]
 assert gm==mul(E+B,[a+f for a,f in zip(A,Ft)])
 assert add(mul(A,E),mul(Ft,B))==[[-2*x for x in a] for a in eye(r)]
 K=add(neg(mul(add(B,F),Et)),mul(mul(F,A),sub(I,mul(E,Et))))
 S=block(I,zero(m,m),K,I)
 target=block(sub(I,mul(E,Et)),Pi,mul(F,Et),sub(I,mul(F,Ft)))
 assert mul(mul(S,g),inv(S))==target
 assert lower(Qmat) and lower(S) and lower(inv(Qmat)) and lower(inv(S))
 all_matrices += [P,L,R,K]
 for f in (1,2):
  If,Cf=eye(f),reverse(f); bigI=eye(m*f)
  Df=block(kron(sub(I,P),If),kron(mul(P,C),Cf),kron(mul(C,P),Cf),kron(mul(mul(C,sub(I,P)),C),If))
  Qf=diag(kron(L,If),kron(inv(R),If)); Sf=block(bigI,zero(m*f,m*f),kron(K,Cf),bigI)
  out=mul(mul(mul(mul(Sf,Qf),Df),inv(Qf)),inv(Sf))
  expected=eye(2*m*f)
  for a in range(r*f):
   h=a; d=2*m*f-1-a
   expected[h]=[Q(i==d) for i in range(2*m*f)]
   expected[d]=[Q(i==h) for i in range(2*m*f)]
  assert out==expected
  full_identities.append((Sf,Qf,Df,inv(Qf),inv(Sf),expected))
 checks.append({'projector':pi,'rank':r,'rational_atom_counts':[1,2],'full_involution':True,'lower_triangular_adapters':True})

# Fixed prime chosen after the complete rational tables.
for prime in (101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,179,181,191,193,197,199):
 if all(x.denominator%prime and (not x or x.numerator%prime) for A in all_matrices for a in A for x in a): break
else: raise AssertionError('No tested prime avoids coefficients')
# Every proved rational full identity specializes to the non-field prime-power ring.
ring_checks=[]
for w in (1,2,4):
 mod=prime**w
 for r,P in fam:
  Pm=specialize(P,mod)
  assert modmul(Pm,Pm,mod)==Pm
 for Sf,Qf,Df,Qfi,Sfi,expected in full_identities:
  z=specialize(Sf,mod)
  for factor in (Qf,Df,Qfi,Sfi): z=modmul(z,specialize(factor,mod),mod)
  assert z==specialize(expected,mod)
 ring_checks.append({'atom_width':w,'modulus':mod,'projector_identities':True,'full_involution_identities':len(full_identities)})
# Original finite wrapper action, in three independent cyclic atoms.
for w in (1,2,4):
 mod=prime**w
 h=[7,11,13]; d=[17,19,23]; H=h[:]; D=d[:]
 D=[(y-x)%mod for x,y in zip(H,D)]
 H,D=list(reversed(D)),list(reversed(H))
 D=[(y+x)%mod for x,y in zip(H,D)]
 H,D=list(reversed(D)),list(reversed(H))
 D=[(x-y)%mod for x,y in zip(H,D)]
 assert (H,D)==(d,h)

row=json.loads((BASE/'certificates/stopped-product-bit-axis.json').read_text())
h=row['h']; v=row['v']; Rcount=row['R']; ell=row['loss']; hist=row['histogram'][:]
hist[h]-=h; hist[1]+=h
assert sum(r*z for r,z in enumerate(hist))==h*Rcount+ell
m=h*h; N=v*v; B=v*Rcount; W=2*N+2*B; Lloss=2*v*ell
counts={m-h:2*B,(h-1)**2:2*N,h-1:4*N,1:N}
for r,z in enumerate(hist):
 if r and z: counts[r]=counts.get(r,0)+2*v*z
s=sum(r*z for r,z in counts.items()); assert s==W*m-N+Lloss
assert max(counts)==506 and all(0<r<m for r in counts)
a=Q(4019,50000000); old=Q(384599,10**10); theta=Q(1,1000); ab=(1-theta)*a+theta*old
assert ab==Q(803380799,10**13) and theta>ab

def ceil_grid(x):
 den=1<<100; return Q((x.numerator*den+x.denominator-1)//x.denominator,den)
def smalllog(y):
 z=(y-1)/(y+1)
 return 2*sum((z**(2*j+1)/Q(2*j+1) for j in range(24)),Q(0))+2*z**49/(49*(1-z*z))
def logupper(x):
 k=0
 while x>=2: x/=2; k+=1
 return ceil_grid(k*smalllog(Q(2))+smalllog(x))
mu=Q(0)
for r,z in counts.items():
 u=a*logupper(Q(m,r)); assert 0<u<3
 mu+=z*r*ceil_grid(1+u+u*u/(2*(1-u/3)))
mu/=W*m
assert mu<1 and Q(s,W*m)<1
cert=json.loads((BASE/'certificates/stopped-product-network.json').read_text())
assert 1-mu==Q(cert['bit']['strict_gap'])
assert sum((16*28,9*28,17*28))==1176
assert Q(4000)-Q(51,25)*1176==Q(40024,25)
for mm,rr,t in ((529,506,16),(575,529,9),(576,552,17)):
 assert mm**t>2*rr**t
 assert mm**(t-1)<=2*rr**(t-1)
result={'status':'PASS independent bounded controls','scope':'Algebra, counts, enclosure and exponent only; no full producer or upstream verification','common_basis_attempt':attempt,'common_basis':[[str(x) for x in a] for a in G],'exterior_commutator_square_trace':'-3/8','full_involution_checks':checks,'prime':prime,'ring_checks':ring_checks,'widths':sorted(counts),'weighted_rank':s,'coarse_moment_gap':str(1-mu),'rank_gap':str(1-Q(s,W*m)),'bit_saving':str(ab),'row_coefficient':1176,'elapsed_seconds':time.monotonic()-START}
Path(__file__).with_name('CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
