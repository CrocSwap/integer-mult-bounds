"""Original compact exact rational block/transition witness writer."""
from fractions import Fraction as Q
from pathlib import Path
from collections import Counter
import gzip,json,hashlib,struct

def enc(q):
 q=Q(q);return [q.numerator,q.denominator]

def sparse(row):return [[i,*enc(x)] for i,x in sorted(row.items()) if x]

class Writer:
 def __init__(self,path,header):
  self.path=Path(path);self.f=gzip.open(path,'wt',compresslevel=1,newline='\n');self.events=Counter();self.local_gates=0;self.max_den=1;self.max_num=1;self.max_rowsum=Q(1);self.write('header',header)
 def write(self,kind,*data):
  self.events[kind]+=1;self.f.write(json.dumps([kind,*data],separators=(',',':'))+'\n')
 def coeff(self,q):
  q=Q(q);self.max_den=max(self.max_den,q.denominator);self.max_num=max(self.max_num,abs(q.numerator));return enc(q)
 def scalar(self,dst,terms,frame):
  terms=[(s,Q(q)) for s,q in terms if q];assert all(s!=dst for s,q in terms)
  self.write('add',dst,[[s,*self.coeff(q)]for s,q in terms],frame);self.local_gates+=len(terms)
  self.max_rowsum=max(self.max_rowsum,1+sum(abs(q)for s,q in terms))
 def block(self,slots,rows,frame,labels):
  n=len(slots);assert len(rows)==n;M=[[Q(row.get(i,0))for i in range(n)]for row in rows];A=[r[:]for r in M];ops=[]
  for i in range(n):
   j=next(j for j in range(i,n)if A[j][i])
   if i!=j:A[i],A[j]=A[j],A[i];ops.append(['swap',i,j])
   pivot=A[i][i]
   if pivot!=1:A[i]=[x/pivot for x in A[i]];ops.append(['scale',i,*enc(1/pivot)])
   for j in range(n):
    if j==i or not A[j][i]:continue
    q=-A[j][i];A[j]=[x+q*y for x,y in zip(A[j],A[i])];ops.append(['add',j,i,*enc(q)])
  assert A==[[Q(i==j)for j in range(n)]for i in range(n)]
  # Elimination operations left-multiply M to I. Reverse their inverses to synthesize M.
  synthesis=[]
  for op in reversed(ops):
   if op[0]=='swap':synthesis.append(op);self.local_gates+=3
   elif op[0]=='scale':q=1/Q(op[2],op[3]);synthesis.append(['scale',op[1],*self.coeff(q)]);self.coeff(1/q);self.local_gates+=1;self.max_rowsum=max(self.max_rowsum,abs(q),abs(1/q))
   else:q=-Q(op[3],op[4]);synthesis.append(['add',op[1],op[2],*self.coeff(q)]);self.local_gates+=1;self.max_rowsum=max(self.max_rowsum,1+abs(q))
  for row in M:self.max_rowsum=max(self.max_rowsum,sum(abs(x)for x in row))
  for row in M:
   for x in row:self.coeff(x)
  self.write('block',slots,[sparse(row)for row in rows],frame,labels,synthesis)
 def finish(self,profile):
  stats=dict(events=dict(self.events),literal_mixer_scalar_gate_upper=self.local_gates,max_scalar_numerator=self.max_num,max_scalar_denominator=self.max_den,max_local_row_sum=str(self.max_rowsum),profile=profile)
  self.write('footer',stats);self.f.close();stats['sha256']=hashlib.sha256(self.path.read_bytes()).hexdigest();stats['bytes']=self.path.stat().st_size;return stats

def expression(rows,target):
 """Return exact coefficients expressing target in the provided independent rows."""
 basis=[]
 for j,row0 in enumerate(rows):
  row={i:Q(v)for i,v in row0.items()if v};e={j:Q(1)}
  for p,b,be in basis:
   q=row.get(p,0)
   if not q:continue
   for i,v in b.items():
    row[i]=row.get(i,0)-q*v
    if not row[i]:del row[i]
   for i,v in be.items():
    e[i]=e.get(i,0)-q*v
    if not e[i]:del e[i]
  assert row;p=min(row);q=row[p];basis.append((p,{i:v/q for i,v in row.items()},{i:v/q for i,v in e.items()}))
 row={i:Q(v)for i,v in target.items()if v};answer={}
 for p,b,be in basis:
  q=row.get(p,0)
  if not q:continue
  for i,v in b.items():
   row[i]=row.get(i,0)-q*v
   if not row[i]:del row[i]
  for i,v in be.items():answer[i]=answer.get(i,0)+q*v
 assert not row
 return {i:v for i,v in answer.items()if v}
