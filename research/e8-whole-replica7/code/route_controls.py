"""Physical family-routing controls: whole-family similarity versus forbidden split.
Exact small address spaces; complements the full finite slot/phase audit.
"""
from itertools import product
import json

def bit(q,m,r):
 states=list(product(range(2),product(range(q),repeat=2*m)));ix={s:i for i,s in enumerate(states)}
 def action(fam,axes):
  p=[]
  for f,word in states:
   w=list(word)
   if f==fam:
    for j in axes:w[j],w[m+j]=w[m+j],w[j]
   p.append(ix[f,tuple(w)])
  return p
 whole=action(0,range(r));host=action(1,range(r));swap=[ix[1-f,w] for f,w in states]
 routed=[swap[whole[swap[i]]] for i in range(len(states))]
 assert routed==host and all(swap[swap[i]]==i for i in range(len(states)))
 a=action(0,range(1));b=action(1,range(1,r));split=[a[b[i]] for i in range(len(states))]
 trace=lambda p:sum(i==j for i,j in enumerate(p))
 assert trace(whole)==trace(host)!=trace(split)
 return dict(q=q,m=m,rank=r,columns=len(states),whole_family_route=True,whole_trace=trace(whole),split_trace=trace(split))

def complex_case(m,r):
 states=list(product(range(2),range(1<<m)));ix={s:i for i,s in enumerate(states)}
 whole=[(y&((1<<r)-1)).bit_count()%4 if f==0 else 0 for f,y in states]
 host=[(y&((1<<r)-1)).bit_count()%4 if f==1 else 0 for f,y in states]
 assert [whole[ix[1-f,y]] for f,y in states]==host
 split=[((y&1).bit_count() if f==0 else ((y>>1)&((1<<(r-1))-1)).bit_count())%4 for f,y in states]
 tr=lambda x:[x.count(0)-x.count(2),x.count(1)-x.count(3)]
 assert tr(whole)==tr(host)!=tr(split)
 return dict(m=m,rank=r,columns=len(states),whole_family_route=True,whole_trace=tr(whole),split_trace=tr(split))
result=dict(status='PASS_WHOLE_FAMILY_ROUTING_SPLIT_REJECTED',bit=[bit(3,2,2),bit(3,3,3)],complex=[complex_case(3,2),complex_case(9,9)],scope='Exact physical whole-family permutation controls; does not prove the inherited all-size dirty-helper compiler.')
print(json.dumps(result,indent=2))
