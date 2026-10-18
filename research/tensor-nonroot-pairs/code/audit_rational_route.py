"""Independent literal-matrix audit of a saved rational multicopy route."""
from fractions import Fraction as F
from pathlib import Path
import json,sys,copy

def tr(A):return [list(x) for x in zip(*A)]
def mul(A,B):return [[sum((x*y for x,y in zip(a,b)),F(0)) for b in tr(B)] for a in A]
def matrix(A):return [[F(x) for x in a] for a in A]
def ident(n):return [[F(i==j) for j in range(n)] for i in range(n)]
def check(d):
 G=matrix(d['route']);Gi=matrix(d['inverse']);N=d['ambient'];n=d['local'];c=d['copies'];w=d['residual_rank'];e=d['entrance_rank']
 assert N==n*c and n==w+e and d['pending_width']==c*w and d['spectator_dimensions']==c*e
 assert len(G)==N and all(len(r)==N for r in G)
 assert Gi==tr(G) and mul(G,Gi)==ident(N)
 Ps=list(map(matrix,d['individual_residual_projectors']));assert len(Ps)==c
 total=[[F(0)]*N for _ in range(N)]
 for j,P in enumerate(Ps):
  assert P==tr(P) and mul(P,P)==P and sum(P[i][i] for i in range(N))==w
  assert all(P[i][k]==0 for i in range(N) for k in range(N) if i>=c*w or k>=c*w)
  B=mul(mul(Gi,P),G)
  assert all(B[i][k]==0 for i in range(N) for k in range(N) if not(j*n<=i<(j+1)*n and j*n<=k<(j+1)*n))
  if d.get('entrance_basis') is not None:
   for v0 in d['entrance_basis']:
    v=[F(0)]*N;v[j*n:(j+1)*n]=map(F,v0)
    assert all(sum((x*y for x,y in zip(row,v)),F(0))==0 for row in B)
  for Q in Ps[:j]:assert all(x==0 for row in mul(P,Q) for x in row)
  total=[[a+b for a,b in zip(x,y)] for x,y in zip(total,P)]
 assert total==[[F(i==j and i<c*w)for j in range(N)]for i in range(N)]
 A=[r[:]for r in G];values=[x for row in G+Gi for x in row]
 for op in d['elementary_reduction']:
  typ=op[0]
  if typ=='swap':i,j=op[1:];A[i],A[j]=A[j],A[i]
  elif typ=='scale':i,x=op[1:];x=F(x);assert x;values.extend([x,1/x]);A[i]=[x*a for a in A[i]]
  else:
   assert typ=='add';i,j,x=op[1:];assert i!=j;x=F(x);values.append(x);A[i]=[a+x*b for a,b in zip(A[i],A[j])]
 assert A==ident(N) and len(d['elementary_reduction'])==d['elementary_count']
 bad=d['excluded_primes']
 for x in values:
  q=x.denominator
  for p in bad:
   while q%p==0:q//=p
  assert q==1
 return dict(status='PASS_INDEPENDENT_EXACT_MATRIX_AUDIT',ambient=N,pending=c*w,spectators=c*e,whole_residuals=c,route_operations_one_direction=len(d['elementary_reduction']))
if __name__=='__main__':
 d=json.loads(Path(sys.argv[1]).read_text());result=check(d);mutations=[]
 for name in ['route','projector','inverse','factor']:
  z=copy.deepcopy(d)
  if name=='route':z['route'][0][0]=str(F(z['route'][0][0])+1)
  elif name=='inverse':z['inverse'][0][0]=str(F(z['inverse'][0][0])+1)
  elif name=='projector':z['individual_residual_projectors'][0][0][0]=str(F(z['individual_residual_projectors'][0][0][0])+1)
  else:z['elementary_reduction']=z['elementary_reduction'][:-1]
  try:check(z)
  except (AssertionError,ValueError):mutations.append(name)
  else:raise AssertionError('mutation accepted: '+name)
 result['rejected_mutations']=mutations;print(json.dumps(result,indent=2))
