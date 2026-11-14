"""Proof-role identities and lower-corner oracle, not a global constructor.
No C/root implementation imported. Apache-2.0; substantial OpenAI assistance.
"""
from itertools import product
from math import isqrt
from pathlib import Path
import json,argparse
H=((1,1,1,1),(1,-1,1,-1),(1,1,-1,-1),(1,-1,-1,1));s=(1,-1,-1,1)
R2=tuple(tuple(2*(i==j)-s[i]*s[j] for j in range(4)) for i in range(4))
E2=tuple(tuple((1 if i<3 else -1)*H[i][j] for j in range(4)) for i in range(4))
def need(ok,m):
 if not ok:raise ValueError(m)
def mm(A,B):return tuple(tuple(sum(A[i][k]*B[k][j] for k in range(4)) for j in range(4)) for i in range(4))
def mv(A,v):return tuple(sum(a*b for a,b in zip(row,v)) for row in A)
def n2(v):return sum(t*t for t in v)
def interval(m,n,bits):
 a=isqrt(max(m,n)<<(2*bits));b=isqrt(min(m,n)<<(2*bits));return(max(0,a-b-1),a-b+1)
def check():
 I4=tuple(tuple(4*(i==j) for j in range(4)) for i in range(4))
 need(mm(H,H)==I4 and mm(R2,R2)==I4,'orthogonal involutions')
 need(mm(E2,R2)==tuple(tuple(2*t for t in row) for row in H),'ER=U')
 need(mm(tuple(zip(*E2)),E2)==I4,'E orthogonality')
 for x in product((0,1),repeat=4):
  if sum(x)%2:
   t=mv(R2,x);q=mv(tuple(zip(*E2)),x)
   need(all(z%2 for z in t) and sum(t)%4==2,'R odd-to-A congruence')
   need(all(z%2 for z in q) and sum(q)%4==0,'E transpose odd-to-B congruence')
 for t in product((1,3),repeat=4):
  A=R2 if sum(t)%4==2 else E2
  need(all(z%4==0 for z in mv(A,t)),'half-coset integrality')
 records=[]
 for k in (0,1,2,7,100,10**20):
  a2=4*k+1;to=(a2,-a2,a2+2,a2+2);qo=(a2+2,-a2,a2+2,a2+2)
  tb=(a2,a2,a2+2,a2+2);qa=(a2+2,a2,a2+2,a2+2)
  outs=[mv(A,t) for A,t in ((R2,to),(E2,qo),(R2,qa),(E2,tb))]
  need(all(z%4==0 for v in outs for z in v),'integer attaining families')
  xo,yo,xi,yi=[tuple(z//4 for z in v) for v in outs]
  need(xo==(0,0,4*k+2,1) and yo==(2*k+2,2*k+1,-2*k-1,-2*k-1),'outward family')
  need(xi==(2*k+1,2*k+1,2*k+2,2*k+1) and yi==(4*k+2,0,-1,0),'inverse family')
  need(n2(xo)==n2(yi)==16*k*k+16*k+5 and n2(yo)==n2(xi)==16*k*k+20*k+7,'norm polynomials')
  records.append({'k':k,'lower_norm2':n2(xo),'upper_norm2':n2(yo)})
 lower=[]
 for m in (2,3,4,8,64,10**6,10**30,10**100):
  z=(m+1,m,m,m);h=mv(H,z);cs=list(product(*[(t//2,t//2+1) for t in h]));n=n2(z);best=4*m*m+3
  need(len(cs)==16 and all(sum((2*y[i]-h[i])**2 for i in range(4))==4 for y in cs),'complete error-one corners')
  norms=set(map(n2,cs));ok=False
  for bits in (32,64,128,256,512,1024):
   spans={v:interval(v,n,bits) for v in norms}
   if all(spans[best][1]<spans[v][0] for v in norms if v!=best):ok=True;break
  need(ok and best<n,'exact unrestricted inward minimum')
  lower.append({'m':m,'minimum_norm2':best,'input_norm2':n,'comparison_bits':bits})
 # Both failures are mathematical premise controls, not an alternative map.
 need((4*(3-1)-1)**2>16,'unstaggered a=.5 radius1-to-sqrt3 exceeds half')
 t=(1,1,3,3);i=min(range(4),key=lambda j:(abs(t[j]),j));u=list(t);u[i]+=2
 need(i==0 and min(range(4),key=lambda j:(abs(u[j]),j))==1,'current magnitude is not invariant pairing score')
 S=((1,0,0,0),(0,-1,0,0),(0,0,1,0),(0,0,0,1));L=((1,0,0,0),(0,0,1,0),(0,0,0,-1),(0,1,0,0))
 Cp=((1,-1,1,1),(1,1,-1,1),(1,1,1,-1),(-1,1,1,1))
 need(mm(mm(L,Cp),S)==H,'Gaussian signed transfer')
 return {'marker':'PASS_STAGGERED_BIJECTION_PROOF_IDENTITIES','scope':'Matrices, attaining families and complete unrestricted lower corners; global implementation separately checked by C/root, not imported here.',
  'attaining_family_cases':records,'lower_corner_cases':lower,
  'controls':['unstaggered pairing violates radial half bound','current magnitude is not partner-invariant','exact local lower minimum is inward'],
  'limits':['No universal forward-only lower1/2','No stronger #6509 invariant inheritance','No physical/tensor/caller admission']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();r=check();dest=Path(__file__).with_name('RESULT.json')
 if a.write:dest.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
 else:need(json.loads(dest.read_text())==r,'receipt drift')
 print('PASS_STAGGERED_BIJECTION_PROOF_IDENTITIES: matrices, families and complete lower corners agree.')
