from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import json,math
HERE=Path(__file__).resolve().parent
if not __debug__: raise RuntimeError('Exact replay requires assertions enabled')
ZERO=(F(0),F(0));ONE=(F(1),F(0))
def ga(a,b):return(a[0]+b[0],a[1]+b[1])
def gm(a,b):return(a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def gp(q,n):
 out=ONE
 for _ in range(n%4):out=gm(out,q)
 return out

def padd(a,b,c):
 out=a.copy()
 for m,x in b.items():
  z=ga(out.get(m,ZERO),gm(c,x))
  if z!=ZERO:out[m]=z
  elif m in out:del out[m]
 return out

def radd(a,b,c):return[padd(x,y,c) for x,y in zip(a,b)]
def rscale(a,c):return[{m:gm(c,x) for m,x in p.items() if gm(c,x)!=ZERO} for p in a]
def rd(a,k):
 out=[]
 for p in a:
  q={}
  for m,x in p.items():
   assert(m//4**k)%4<3
   q[m+4**k]=x
  out.append(q)
 return out

def replay(C,q,check=True):
 n=C['roles'];R=[[{0:ONE} if i==j else {} for j in range(n)] for i in range(n)];peak=0;den=1;mag=F(0)
 for e in C['events']:
  op=e[0]
  if op=='ADD':R[e[1]]=radd(R[e[1]],R[e[2]],(F(e[3]),F(0)))
  elif op=='SCALE':R[e[1]]=rscale(R[e[1]],(F(e[2]),F(0)))
  elif op=='SWAP':R[e[1]],R[e[2]]=R[e[2]],R[e[1]]
  elif op=='QUERY':R[e[1]]=radd(R[e[1]],R[e[2]],gp(q,e[3]))
  elif op=='LAMBDA':R[e[1]]=rscale(R[e[1]],ONE if q[1]==0 else(F(0),F(e[2])))
  elif op=='IDLE_ONE':
   for k in e[2]:R[e[1]]=rd(R[e[1]],k)
  elif op=='HOST':
   x,y,k=e[1:4];old=R[x];R[x]=rd(radd(old,R[y],gp(q,1)),k);R[y]=rd(rscale(old,gm((F(-1),F(0)),gp(q,-1))),k)
  else:raise ValueError(op)
  peak=max(peak,sum(len(p) for row in R for p in row))
  for row in R:
   mass=F(0)
   for p in row:
    for z in p.values():
     mass+=abs(z[0])+abs(z[1]);den=math.lcm(den,z[0].denominator,z[1].denominator)
   mag=max(mag,mass)
 target=[[{sum(4**k for k in range(C['stages']) if C['masks'][i]>>k&1):q} if i==j else{} for j in range(n)] for i in range(n)]
 if check:assert R==target
 return dict(ok=R==target,peak_monomials=peak,common_denominator=str(den),denominator_bits=den.bit_length(),max_coefficient_row_l1=str(mag))


if __name__=='__main__':
 result={}
 for g in [3,9,18]:
  C=json.loads((HERE/f'caller_L{g}.json').read_text())
  chars=[ONE,(-F(1),F(0)),(F(0),F(1)),(F(0),-F(1))]
  result[str(g)]=dict(characters=[replay(C,q)for q in chars])
  controls={}
  for op in ['HOST','QUERY','IDLE_ONE','LAMBDA','ADD']:
   bad=json.loads(json.dumps(C));idx=next(i for i,e in enumerate(bad['events'])if e[0]==op);del bad['events'][idx]
   controls['drop_'+op]=any(not replay(bad,q,False)['ok']for q in chars)
  assert all(controls.values());result[str(g)]['controls']=controls
 expected=HERE/'REPLAY.json'
 if expected.exists():assert result==json.loads(expected.read_text())
 print(json.dumps(result,indent=2));print('PASS_FOUR_CHARACTER_CALLER')
