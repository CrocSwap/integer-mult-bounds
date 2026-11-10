"""Independent exact small matrix and literal invoice checks; Apache-2.0.
Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from itertools import combinations
from collections import Counter
from decimal import Decimal,localcontext
import json
def need(ok,message):
 if not ok:raise ValueError(message)
def mm(a,b):return [[sum(x*y for x,y in zip(row,col))for col in zip(*b)]for row in a]
def add(a,b,s=1):return [[x+s*y for x,y in zip(ar,br)]for ar,br in zip(a,b)]
def out(a,b):return [[x*y for y in b]for x in a]
def rank(a):
 a=[list(map(Q,row))for row in a];r=0
 for c in range(len(a[0])):
  p=next((i for i in range(r,len(a))if a[i][c]),None)
  if p is None:continue
  a[r],a[p]=a[p],a[r];v=a[r][c];a[r]=[x/v for x in a[r]]
  for i in range(len(a)):
   if i!=r:
    v=a[i][c];a[i]=[x-v*y for x,y in zip(a[i],a[r])]
  r+=1
  if r==len(a):break
 return r
def matrix_checks():
 eye=[[int(i==j)for j in range(4)]for i in range(4)];zero=[[0]*4 for _ in range(4)]
 u=eye+[[-1,1,-1,1]];v=[[int(i>j)-int(i<j)for j in range(4)]for i in range(5)]
 rr=[out(a,b)for a,b in zip(u,v)];prefix=eye;prefixes=[]
 for r in rr:
  need(mm(r,r)==zero and rank(r)==1,'Each canonical query is rank-one square-zero')
  prefix=mm(add(eye,r,-2),prefix);prefixes.append(prefix)
 need(prefix==[[-x for x in row]for row in eye],'Actual complete five-query endpoint')
 for i,adj in((1,0),(3,4)):
  h=[int(j<=i)for j in range(4)];a=[(-1)**j if j<=i else 0 for j in range(4)]
  e=add(out(u[i],h),out(a,v[i]))
  need(mm(e,e)==e and rank(e)==2,'Forced odd minimal projector')
  need(mm(e,prefixes[i])==mm(prefixes[i],e),'Actual full prefix commutation')
  for j in(i,adj):need(mm(e,rr[j])==rr[j]and mm(rr[j],e)==rr[j],'Odd closure supports adjacent endpoint query')
 for sites in combinations((0,1,3,4),3):
  us=[[u[j][i]for j in sites]for i in range(4)];vs=[v[j]for j in sites]
  need((rank(us),rank(vs),rank(mm(vs,us)))==(3,3,2),'Three-stage image/row union forces all four scalar coordinates')
 bad=add(out(u[1],u[1]),out(u[0],v[1]))
 need(mm(bad,bad)==bad and mm(bad,rr[1])==rr[1]and mm(rr[1],bad)==rr[1],'Compatibility-only negative-control premise')
 need(mm(bad,prefixes[1])!=mm(prefixes[1],bad),'Wrong query-only prefix surrogate is rejected')
 return dict(canonical_queries=5,odd_closures=2,three_stage_unions=4,failed_prefix_control=True)
def literal_invoice():
 helpers={1:14,2:8,3:4,4:108,5:16,6:3,7:9,8:40,9:361};paid={1:2231,2:454,3:490,4:109,5:152,6:8,7:9,8:1}
 a=(8,1,1,8);masks=(3,3,6,6,12,12,15,15);r=(4,6,6,4);f=sum(a)
 t=Counter({i:f*n for i,n in helpers.items()});p=Counter({i:f*n for i,n in paid.items()});nodes=[]
 def binary(n):
  if n==1:return
  binary(n//2);binary(n-n//2);nodes.append(n);t[8*n+1]+=208;p[8*n]+=208;p[1]+=104
 for n in a:binary(n)
 for m in masks:t[1+8*sum(a[i]for i in range(4)if m>>i&1)]+=52
 for i in range(4):p[8*a[i]]+=52*(r[i]-4)
 p[1]+=104
 need(len(nodes)==14 and(sum(t.values()),sum(p.values()))==(13462,66852),'Literal complete winning relaxed census')
 need(sum(i*n for i,n in t.items())-sum(i*n for i,n in p.items())==760,'Complete rank mass surplus')
 with localcontext()as ctx:
  ctx.prec=60;k=Decimal('0.00330720');h=lambda x:(Decimal(x).ln()*(1-k)).exp()
  gap=sum(n*h(i)for i,n in t.items())-sum(n*h(i)for i,n in p.items())
  need(Decimal('-6.765')<gap<Decimal('-6.764'),'Independent high precision literal histogram sign')
  need(gap+104>0,'Omitting thin query is detected on the actual histogram')
  value=str(gap/104)
 return dict(native_invocations=f,binary_nodes=len(nodes),thin_queries=15,productive_fields=sum(t.values()),paid_requests=sum(p.values()),rank_mass_surplus=760,targets=dict(t),paid=dict(p),decimal_gap_per_port=value,decimal_precision=60)
def run():return dict(status='PASS_EXACT_CONVENTIONS_AND_INDEPENDENT_LITERAL_INVOICE',matrix=matrix_checks(),invoice=literal_invoice())
if __name__=='__main__':print(json.dumps(run(),indent=2))
