"""Bounded exact ring checker; no root/C implementation or solver imported.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from itertools import product
from functools import lru_cache
from math import isqrt
from pathlib import Path
import argparse,json
def need(ok,m):
 if not ok:raise ValueError(m)
def J(v):return(-v[1],v[0])
def B(v):return(v[0]+v[1],v[0]-v[1])
def n2(v):return sum(x*x for x in v)
def edge(a,b):return tuple(sorted((a,b)))
@lru_cache(None)
def ring(m):
 need(0<=m<=16,'bounded-checker radius; not a production tariff')
 a=4*m+1;b=a+2;edges=set()
 def orbit(u,v):
  for _ in range(4):edges.add(edge(u,v));u,v=J(u),J(v)
 orbit((a,a),(b,a))
 for points in [[(x,a) for x in range(-a+2,a,2)],[(x,b) for x in range(b,-a,-2)]]:
  need(len(points)%2==0,'even arc')
  for j in range(0,len(points),2):orbit(points[j],points[j+1])
 partner={}
 for u,v in edges:
  need(n2((u[0]-v[0],u[1]-v[1]))==4,'unit domino')
  need(u not in partner and v not in partner,'disjoint matching');partner[u]=v;partner[v]=u
 expected={v for v in product(range(-b,b+1,2),repeat=2) if max(map(abs,v)) in (a,b)}
 need(set(partner)==expected and len(partner)==32*m+16,'complete ring pair')
 for v,w in partner.items():need(partner[J(v)]==J(w),'quarter equivariance')
 return partner
def M(v):return ring((max(map(abs,v))-1)//4)[v]
def F(x):
 s=(x[0]+x[2],x[1]+x[3]);d=(x[0]-x[2],x[1]-x[3])
 if s[0]%2==s[1]%2:z=J(d)
 else:
  q=B(M(B(J(d))));need(all(a%2==0 for a in q),'d integrality');z=tuple(a//2 for a in q)
 out=tuple(s[j]+sgn*z[j] for sgn in (1,-1) for j in range(2))
 need(all(a%2==0 for a in out),'Gaussian output');return tuple(a//2 for a in out)
def swap(x):return x[2:]+x[:2]
def I(x):return(-x[1],x[0],-x[3],x[2])
def K(x):return(x[0],-x[1],x[2],-x[3])
def gap_interval(m,n,bits):
 if m==n:return(0,0)
 a=isqrt(max(m,n)<<(2*bits));b=isqrt(min(m,n)<<(2*bits));return(max(0,a-b-1),a-b+1)
def cap(m,n):
 if {m,n}=={13,19}:return True
 for bits in (32,64,128,256,512):
  lo,hi=gap_interval(m,n,bits);bl,bh=gap_interval(19,13,bits)
  if hi<bl:return True
  if lo>bh:return False
 raise ValueError('undecided exact radical comparison')
def verify():
 counts=[]
 for m in range(7):
  p=ring(m);seen=set()
  for u,v in p.items():
   if edge(u,v) in seen:continue
   seen.add(edge(u,v));a=(n2(u)+2)//4;b=(n2(v)+2)//4
   need(cap(a,b),'constructed edge radial cap at smallest sum')
  counts.append({'m':m,'vertices':len(p),'edges':len(seen)})
 D=set(product((-5,-3,-1,1,3,5),repeat=2));boundary=set();internal=set()
 for v in D:
  for step in ((2,0),(-2,0),(0,2),(0,-2)):
   w=(v[0]+step[0],v[1]+step[1])
   (internal if w in D else boundary).add(edge(v,w))
 need(len(D)==36 and len(boundary)==24 and len(D)%8==4,'exact finite boundary counts')
 crossing_types={};central_overlap=False
 for e in internal:
  u,v=e;orbit=set()
  for _ in range(4):orbit.add(edge(u,v));u,v=J(u),J(v)
  need(len(orbit)==4,'no half-turn-fixed edge')
  if len({v for e in orbit for v in e})!=8:central_overlap=True
 need(central_overlap,'geometric orbit overlap premise control')
 for e in boundary:
  a,b=sorted(((n2(v)+2)//4 for v in e));crossing_types[a,b]=crossing_types.get((a,b),0)+1
  need(({a,b}=={13,19}) or not cap(a,b),'crossing jump lower bound')
 need(crossing_types=={(7,13):8,(9,15):8,(13,19):8},'corner minimum beta')
 rect={}
 for y in (-5,-3,-1,1,3,5):
  for a,b in ((-5,-3),(-1,1),(3,5)):rect[a,y]=(b,y);rect[b,y]=(a,y)
 need(any(rect[J(v)]!=J(rect[v]) for v in D),'quarter equivariance is a material premise')
 C=((1,-1,1,1),(1,1,-1,1),(1,1,1,-1),(-1,1,1,1));count=0
 for x in product(range(-2,3),repeat=4):
  y=F(x);count+=1;s=(x[0]+x[2],x[1]+x[3])
  need((y[0]+y[2],y[1]+y[3])==s and F(y)==swap(x),'sum and exact square')
  need(swap(F(y))==x and F(swap(F(x)))==x,'both inverse directions')
  need(F(I(x))==I(y),'Gaussian-unit covariance')
  e=sum((2*y[i]-sum(C[i][j]*x[j] for j in range(4)))**2 for i in range(4))
  need(e==(0 if s[0]%2==s[1]%2 else 4),'nearest exact error')
  need(cap(n2(x),n2(y)),'Gaussian radial cap')
 cycle=[(3,0,-2,0)];cur=cycle[0]
 for _ in range(4):cur=F(cur);cycle.append(cur)
 need(cycle==[(3,0,-2,0),(0,3,1,-3),(-2,0,3,0),(1,-3,0,3),(3,0,-2,0)],'finite beta-attaining cycle')
 need([n2(v) for v in cycle]==[13,19,13,19,13],'attained squared norms')
 x=(1,0,0,0);need(K(F(K(x)))!=swap(F(x)),'inverse-by-conjugation obstruction')
 def layer(z,columns):
  out=list(z)
  for a,b in (((0,2),(1,3)) if columns else ((0,1),(2,3))):
   p=F(z[a]+z[b]);out[a],out[b]=p[:2],p[2:]
  return tuple(out)
 w=((0,-1),(0,0),(1,0),(0,0));a=layer(layer(w,True),False);b=layer(layer(w,False),True)
 need(a!=b and sum(n2((u[0]-v[0],u[1]-v[1])) for u,v in zip(a,b))==2,'known6778 tensor witness')
 return {'marker':'PASS_ANNULAR_GAUSSIAN_ORDER_OPTIMUM','bounded_ring_groups':counts,
  'lower_box_vertices':36,'geometric_boundary_edges':24,'boundary_types':[[a,b,n] for (a,b),n in sorted(crossing_types.items())],
  'Gaussian_box':[-2,2],'Gaussian_cases':count,'attaining_cycle':cycle,
  'unit_inverse_control':{'inverse':swap(F(x)),'conjugated':K(F(K(x)))},
  'known6778_orders':[a,b],'known6778_squared_defect':2,
  'controls':['edge orbits that overlap cannot lie in an equivariant matching','internal rectangle matching without quarter equivariance evades count',
    'inverse-by-conjugation fails','same-map tensor commutation blocked by known6778'],
  'scope':'Finite exact corroboration of all-input proof; checker generates bounded rings, not a physical or accelerated implementation.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();r=json.loads(json.dumps(verify()));dest=Path(__file__).with_name('RESULT.json')
 if a.write:dest.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
 else:need(json.loads(dest.read_text())==r,'receipt drift')
 print('PASS_ANNULAR_GAUSSIAN_ORDER_OPTIMUM: sharp constrained beta and exact order corroborated.')
