#!/usr/bin/env python3
from pathlib import Path
import json

def parts(L,w):
 if L<=2*w:return [('B',0,L)]
 out=[('B',0,w)];pos=w;R=L-2*w
 while R>4*w:
  B=1<<((R-w).bit_length()-1)
  out.append(('I',pos,pos+B));pos+=B
  out.append(('B',pos,pos+w));pos+=w;R-=B+w
 if R:out.append(('B',pos,pos+R));pos+=R
 out.append(('B',pos,L))
 return out
cases=edges=0
for w in range(1,41):
 for L in range(1,2001):
  ps=parts(L,w)
  assert ps[0][1]==0 and ps[-1][2]==L
  assert all(a[2]==b[1] for a,b in zip(ps,ps[1:]))
  ins=[x for x in ps if x[0]=='I']
  assert all((b-a)&(b-a-1)==0 for _,a,b in ins)
  assert all(y[1]-x[2]>=w for x,y in zip(ins,ins[1:]))
  assert len(ins)<=2+max(0,(max(1,L//w)).bit_length())
  assert sum(b-a for t,a,b in ps if t=='B')<=w*(8+max(1,L//w).bit_length())
  # For each new interior, all boundary neighbors reachable by an original band edge
  # lie in its two adjacent retained blocks. Eliminating it can fill only their union.
  labels=[-1]*L;bid=0
  for typ,a,b in ps:
   if typ=='B':
    for i in range(a,b):labels[i]=bid;bid+=1
  for _,a,b in ins:
   ns=[labels[i] for i in list(range(max(0,a-w),a))+list(range(b,min(L,b+w))) if labels[i]>=0]
   if ns:assert max(ns)-min(ns)<=10*w
   edges+=len(ns)
  cases+=1
out={'status':'all exact assertions passed','cell_partitions':cases,'reachable_boundary_records':edges,'scope':'Dyadic lengths, exact coverage, w-wide separation, logarithmic block count, and O(w) Schur boundary span.'}
Path(__file__).with_name('DYADIC-INTERIOR-CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
