"""Exact rational-frame integer elimination; prepared with OpenAI Codex assistance, Apache-2.0."""
from math import gcd
def prim(v):
 g=0
 for x in v:g=gcd(g,abs(x))
 if g>1:v=[x//g for x in v]
 f=next((x for x in v if x),0)
 return tuple(-x for x in v) if f<0 else tuple(v)
def reduce_rows(rows,h):
 rows=[list(r) for r in rows];out=[];pivs=[]
 for r in rows:
  for pr,pc in zip(out,pivs):
   if r[pc]:
    a,b=pr[pc],r[pc];r=[x*a-y*b for x,y in zip(r,pr)]
  r=list(prim(r));c=next((j for j in range(h) if r[j]),None)
  if c is None:continue
  for i,(pr,pc) in enumerate(zip(out,pivs)):
   if pr[c]:
    a,b=r[c],pr[c];out[i]=list(prim([x*a-y*b for x,y in zip(pr,r)]))
  out.append(r);pivs.append(c)
 return out,pivs
def kernel(rows,h):
 red,pivs=reduce_rows(rows,h);ps=set(pivs);basis=[]
 for f in range(h):
  if f in ps:continue
  D=1
  for r,c in zip(red,pivs):
   if r[f]:D=D*abs(r[c])//gcd(D,abs(r[c]))
  v=[0]*h;v[f]=D
  for r,c in zip(red,pivs):
   if r[f]:v[c]=-r[f]*D//r[c]
  basis.append(prim(v))
 return basis,len(red)
def dot(x,y):return sum(a*b for a,b in zip(x,y))
class Module:
 dot=staticmethod(dot);reduce_rows=staticmethod(reduce_rows);kernel=staticmethod(kernel)
