"""Deterministic unimodular resynthesis of contiguous constant caller blocks."""
from fractions import Fraction as Q
OPS={'ADD','SCALE','SWAP'}
def need(ok,message):
 if not ok:raise ValueError(message)

def matrix(es,n):
 a=[[int(i==j) for j in range(n)] for i in range(n)]
 for e in es:
  if e[0]=='ADD':
   q=Q(e[3]);need(q.denominator==1,'integer coefficient');q=q.numerator;a[e[1]]=[v+q*w for v,w in zip(a[e[1]],a[e[2]])]
  elif e[0]=='SCALE':
   q=Q(e[2]);need(q in (-1,1),'unit scaling');a[e[1]]=[q.numerator*v for v in a[e[1]]]
  elif e[0]=='SWAP':a[e[1]],a[e[2]]=a[e[2]],a[e[1]]
  else:raise ValueError(e)
 return a

def factor(m):
 a=[r[:] for r in m];n=len(a);ops=[]
 for j in range(n):
  while True:
   k=min((k for k in range(j,n) if a[k][j]),key=lambda k:(abs(a[k][j]),sum(bool(x) for x in a[k]),k))
   if k!=j:a[j],a[k]=a[k],a[j];ops.append(['SWAP',j,k])
   k=next((k for k in range(j+1,n) if a[k][j]),None)
   if k is None:break
   q=a[k][j]//a[j][j]
   if q:a[k]=[x-q*y for x,y in zip(a[k],a[j])];ops.append(['ADD',k,j,str(-q)])
   if a[k][j]:a[j],a[k]=a[k],a[j];ops.append(['SWAP',j,k])
  need(abs(a[j][j])==1,'unimodular pivot')
  if a[j][j]<0:a[j]=[-x for x in a[j]];ops.append(['SCALE',j,'-1'])
  for k in range(j):
   q=a[k][j]
   if q:a[k]=[x-q*y for x,y in zip(a[k],a[j])];ops.append(['ADD',k,j,str(-q)])
 need(a==[[int(i==j) for j in range(n)] for i in range(n)],'elimination endpoint')
 out=[]
 for e in reversed(ops):
  if e[0]=='ADD':
   q=-int(e[3]);sgn=1 if q>0 else -1;q=abs(q)
   while q:
    v=min(q,3);out.append(['ADD',e[1],e[2],str(sgn*v)]);q-=v
  else:out.append(e)
 need(matrix(out,n)==m,'inverse word matrix')
 return out

def run(c):
 es=c['events'];out=[];records=[];start=0
 for i,e in enumerate(es+[None]):
  if e is not None and e[0] in OPS:continue
  if i>start:
   old=es[start:i];new=factor(matrix(old,c['roles']))
   if len(new)<len(old):out.extend(new);records.append([start,i,len(new)])
   else:out.extend(old)
  if e is not None:out.append(e)
  start=i+1
 r=dict(c);r['events']=out
 return r,records
