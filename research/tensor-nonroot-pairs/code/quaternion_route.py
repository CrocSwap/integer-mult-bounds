"""Exact four-copy rational orthogonal residual routing; no symbolic square roots."""
from fractions import Fraction as Q
from pathlib import Path
from math import isqrt,gcd,lcm
import json,sys,hashlib

def dot(a,b):return sum((x*y for x,y in zip(a,b)),Q(0))
def eye(n):return [[Q(i==j)for j in range(n)]for i in range(n)]
def transpose(A):return list(map(list,zip(*A)))
def mm(A,B):return [[dot(a,b)for b in transpose(B)]for a in A]
def orthogonalize(vs):
 out=[]
 for v in vs:
  v=list(map(Q,v))
  for u in out:
   a=dot(v,u)/dot(u,u);v=[x-a*y for x,y in zip(v,u)]
  if any(v):out.append(v)
 return out

def four_squares(n):
 assert n>0
 pairs={}
 for a in range(isqrt(n)+1):
  for b in range(isqrt(n-a*a)+1):pairs.setdefault(a*a+b*b,(a,b))
 for v,ab in pairs.items():
  if n-v in pairs:return ab+pairs[n-v]
 raise AssertionError('Lagrange four-square representation not found')
def quaternion(a,b,c,d):return [[a,-b,-c,-d],[b,a,-d,c],[c,d,a,-b],[d,-c,b,a]]
def tensor_unit_rows(v,n,copies=4):
 a=dot(v,v);N=a.numerator*a.denominator
 if copies==2:
  z=next(((t,isqrt(N-t*t))for t in range(isqrt(N)+1)if isqrt(N-t*t)**2==N-t*t),None)
  if z is None:raise ValueError('This Gram-Schmidt pivot requires the four-copy fallback')
  x,y=[Q(t,a.denominator)for t in z];H=[[x,-y],[y,x]]
 else:
  z=[Q(t,a.denominator)for t in four_squares(N)];H=quaternion(*z)
 assert mm(H,transpose(H))==[[a*Q(i==j)for j in range(copies)]for i in range(copies)]
 return [[H[i][j//n]*v[j%n]/a for j in range(copies*n)]for i in range(copies)]
def primes(n):
 p=2;out=[]
 while p*p<=n:
  if n%p==0:
   out.append(p)
   while n%p==0:n//=p
  p+=1
 if n>1:out.append(n)
 return out

def construct(roots,frame,copies=4,basis=None):
 n=len(roots[0]);E=orthogonalize(basis if basis is not None else [roots[i]for i in frame]);e=len(E);R=[]
 for row in eye(n):
  for v in E:
   a=dot(row,v)/dot(v,v);row=[x-a*y for x,y in zip(row,v)]
  R.append(row)
 R=orthogonalize(R);w=len(R);assert e+w==n
 G=[u for v in R for u in tensor_unit_rows(v,n,copies)]+[u for v in E for u in tensor_unit_rows(v,n,copies)]
 N=copies*n;assert mm(G,transpose(G))==eye(N)
 P=[[sum((v[i]*v[j]/dot(v,v)for v in R),Q(0))for j in range(n)]for i in range(n)]
 image=[]
 for k in range(copies):
  B=[[Q(0)]*N for _ in range(N)]
  for i in range(n):
   for j in range(n):B[k*n+i][k*n+j]=P[i][j]
  U=mm(mm(G,B),transpose(G));assert mm(U,U)==U and transpose(U)==U
  assert all(U[i][j]==0 for i in range(N)for j in range(N)if i>=copies*w or j>=copies*w)
  assert sum(U[i][i]for i in range(N))==w;image.append(U)
 assert [[sum(U[i][j]for U in image)for j in range(N)]for i in range(N)]==[[Q(i==j and i<copies*w)for j in range(N)]for i in range(N)]
 for i in range(copies):
  for j in range(i):assert not any(any(row)for row in mm(image[i],image[j]))
 # Explicit orthogonal reflection reduction of the full route.
 cur=[r[:]for r in G];factors=[]
 for j in range(N):
  x=[cur[i][j]for i in range(N)];v=[a-Q(i==j)for i,a in enumerate(x)]
  if not any(v):continue
  den=dot(v,v);assert den>0
  H=[[Q(i==k)-2*v[i]*v[k]/den for k in range(N)]for i in range(N)]
  cur=mm(H,cur);factors.append(dict(vector=v,denominator=den))
 assert cur==eye(N) and len(factors)<=N
 denoms=[q.denominator for row in G for q in row]
 # Every denominator in the literal reflection matrices, not just the final map.
 for f in factors:
  denoms += [(2*x*y/f['denominator']).denominator for x in f['vector']for y in f['vector']]
 # Literal elementary row operations, including inverse-admission denominators.
 elim=[r[:]for r in G];elementary=[]
 for j in range(N):
  k=next(i for i in range(j,N)if elim[i][j])
  if k!=j:elim[k],elim[j]=elim[j],elim[k];elementary.append(['swap',j,k])
  a=elim[j][j]
  if a!=1:
   elementary.append(['scale',j,1/a]);denoms.extend([a.denominator,abs(a.numerator)]);elim[j]=[x/a for x in elim[j]]
  for i in range(N):
   if i!=j and elim[i][j]:
    a=elim[i][j];elementary.append(['add',i,j,-a]);denoms.append(a.denominator);elim[i]=[x-a*y for x,y in zip(elim[i],elim[j])]
 assert elim==eye(N) and len(elementary)<=N*N+N
 D=lcm(*denoms);bad=primes(D)
 def encode(x):
  if isinstance(x,Q):return str(x)
  if isinstance(x,list):return [encode(v)for v in x]
  if isinstance(x,dict):return {k:encode(v)for k,v in x.items()}
  return x
 return encode(dict(status='PASS_EXACT_RATIONAL_MULTICOPY_ROUTE',copies=copies,entrance_basis=basis,ambient=N,local=n,frame=frame,entrance_rank=e,residual_rank=w,pending_width=copies*w,spectator_dimensions=copies*e,route=G,inverse=transpose(G),individual_residual_projectors=image,reflection_reduction=factors,elementary_reduction=elementary,elementary_count=len(elementary),excluded_primes=bad,all_denominator_lcm=str(D),route_factor_count=len(factors),conservative_elementary_factor_bound=2*N*N+2*N,scope='Exact rational whole-residual multicopy route and reduction. Requires one common idle family/window with copies*w pending dimensions and copies*e same-family restored spectator dimensions. No global candidate or kappa claimed.'))
if __name__=='__main__':
 src=Path(sys.argv[1]);out=Path(sys.argv[2]);w=json.loads(src.read_text());frame=list(map(int,sys.argv[3:])) or [0,32];r=construct(w['lines'],frame);r['source_word_sha256']=hashlib.sha256(src.read_bytes()).hexdigest();out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k not in ['route','inverse','individual_residual_projectors','reflection_reduction','elementary_reduction']}))
