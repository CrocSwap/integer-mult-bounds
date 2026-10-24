"""Exact literature adaptations: transposition, transparent echoes and MV decoding.
Prepared for Dugongue with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
import itertools,json

Z=(F(0),F(0));ONE=(F(1),F(0))
def q(a=0,b=0):return F(a),F(b)
def add(a,b):return a[0]+b[0],a[1]+b[1]
def neg(a):return -a[0],-a[1]
def mul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def cj(a):return a[0],-a[1]
def sm(a,c):return [mul(q(c),x)for x in a]
def plus(a,b,c=1):return [add(x,mul(q(c),y))for x,y in zip(a,b)]
def inner(a,b):
 s=Z
 for x,y in zip(a,b):s=add(s,mul(cj(x),y))
 return s

def gaussian(a,f,inverse=False):
 a=a[:];alpha=q(F(1,2),F(-1 if inverse else 1,2));beta=cj(alpha)
 for j in range(f):
  bit=1<<(3*j);out=[Z]*len(a)
  for x in range(len(a)):out[x]=add(mul(alpha,a[x]),mul(beta,a[x^bit]))
  a=out
 return a

def monomial(a,f,which,adjoint=False):
 p=([0,5,2,7,4,1,6,3] if which=='P' else [0,2,1,3,4,6,5,7]);out=[Z]*len(a);unit=[q(1),q(0,1),q(-1),q(0,-1)]
 for x in range(len(a)):
  dest=0;phase=0
  for j in range(f):
   d=(x>>(3*j))&7;dest|=p[d]<<(3*j);phase+=d.bit_count()+p[d].bit_count()
  if adjoint:out[x]=mul(unit[(-phase)&3],a[dest])
  else:out[dest]=mul(unit[phase&3],a[x])
 return out

def L(a,f,adjoint=False):return plus(monomial(a,f,'P',adjoint),monomial(a,f,'Q',adjoint),2)
def forward(x,y,f):
 t=gaussian(x,f);return t,gaussian(plus(y,L(t,f)),f)
def inverse(t,s,f):return gaussian(t,f,True),plus(gaussian(s,f,True),L(t,f),-1)
def adjoint(u,v,f):
 y=gaussian(v,f,True);return gaussian(plus(u,L(y,f,True)),f,True),y
def inverse_adjoint(u,v,f):return plus(gaussian(u,f),L(v,f,True),-1),gaussian(v,f)
def pairinner(a,b):return add(inner(a[0],b[0]),inner(a[1],b[1]))
def need(ok,label):
 if not ok:raise ValueError(label)

def run():
 ids=0;controls=0;echo=0
 for f in (1,2,3):
  N=8**f
  for seed in range(3):
   x=[q((3*j+seed)%7-3,(j+2*seed)%5-2)for j in range(N)];y=[q((5*j+seed)%11-5,(7*j+seed)%3-1)for j in range(N)]
   u=[q((11*j+seed)%13-6,(2*j+seed)%7-3)for j in range(N)];v=[q((7*j+seed)%5-2,(3*j+seed)%11-5)for j in range(N)]
   out=forward(x,y,f);need(inverse(*out,f)==(x,y),'forward reverse');ids+=1
   need(pairinner(out,(u,v))==pairinner((x,y),adjoint(u,v,f)),'weighted transpose');ids+=1
   need(adjoint(*inverse_adjoint(x,y,f),f)==(x,y),'inverse adjoint');ids+=1
   # A conjugated translation is transparent on every arbitrary baseline.
   delta=[q((j+seed)%3-1,0)for j in range(N)]
   shifted=inverse(plus(out[0],delta),out[1],f)
   need(shifted==(plus(x,gaussian(delta,f,True)),plus(y,L(delta,f),-1)),'transparent echo');echo+=1
   # Ordinary forward calls are not automatically Hermitian transposes.
   need(pairinner(out,(u,v))!=pairinner((x,y),forward(u,v,f)),'wrong adjoint control');controls+=1
 # Exact cyclic-character selector from a simple matching-vector family.
 p=13;m=3;omega=3;r=4;N=8
 need(pow(omega,m,p)==1 and omega!=1,'nontrivial character')
 data=[[(i*7+j*3+1)%p for j in range(N)]for i in range(r)]
 def G(a):return [(a[j]+2*a[(j+1)%N]+5*a[(j+3)%N])%p for j in range(N)]
 queries={tuple(t*(int(i!=j))%m for i in range(r))for j in range(r)for t in range(m)}
 encoded={z:[sum(pow(omega,z[i],p)*data[i][k]for i in range(r))%p for k in range(N)]for z in queries}
 transformed={z:G(a)for z,a in encoded.items()};inv_m=pow(m,-1,p)
 for j in range(r):
  zs=[tuple(t*int(i!=j)%m for i in range(r))for t in range(m)]
  got=[inv_m*sum(transformed[z][k]for z in zs)%p for k in range(N)]
  need(got==G(data[j]),'MV exact decoding')
 bad=[sum(data[i][k]for i in range(r))%p for k in range(N)]
 need(any(bad!=data[j]for j in range(r)),'trivial character rejects')
 need(len(queries)==1+(m-1)*r==9,'query union bill')
 # A rank-three transform at each encoded query would use 27 calls, not 12.
 need(3*len(queries)>3*r,'no false independent-job gain')
 # Outside prefactors and a multiplier at every recursive node differ.
 # Four calls at every rank-eight level give 4**d leaves; doubling the
 # complete runtime once gives 2*4**d, whereas doubling each invoice
 # gives 8**d. This distinction already appears at depth two.
 for depth in (2,3,4):
  baseline=sum(1 for _ in itertools.product(range(4),repeat=depth))
  local_multiplier=sum(1 for _ in itertools.product(range(8),repeat=depth))
  need(baseline==4**depth and local_multiplier==8**depth,'recursive leaf invoice')
  need(local_multiplier>2*baseline,'local multiplier is not outside prefactor')
 return {'status':'PASS_CATALYTIC_TRANSPOSE_LITERATURE','widths':[1,2,3],'exact_port_identities':ids,'transparent_echo_cases':echo,'wrong_adjoint_controls':controls,'matching_vector_recovered_arrays':r,'matching_vector_encoded_queries':len(queries),'hypothetical_rank_three_query_calls':27,'direct_rank_three_calls':12,'transpose_forward_calls':2,'transpose_reverse_calls':2,'echo_paid_calls':4,'new_kappa':False}

if __name__=='__main__':print(json.dumps(run(),sort_keys=True))
