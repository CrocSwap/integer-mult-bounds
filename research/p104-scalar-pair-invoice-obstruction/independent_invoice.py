"""Independent scalar-pair invoice audit and all-rank sector census.
Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Portable adaptation changes only paths and explicit receipt-authoring mode.
"""
from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path
import json,hashlib,sys
HERE=Path(__file__).resolve().parent
VOCAB=(2,3,4,6,7,12,14,15)
R5=(2,2,3,4,4,4,12,15)
def need(ok,message):
 if not ok:raise ValueError(message)
def count_vectors(total,width,prefix=()):
 if width==1:yield prefix+(total,);return
 for n in range(total+1):yield from count_vectors(total-n,width-1,prefix+(n,))
def census():
 out={}
 for c in count_vectors(8,8):
  r=tuple(sum(n*((m>>i)&1)for m,n in zip(VOCAB,c))for i in range(4))
  if r[0]!=2 or r[1]!=4 or r[2]<5 or r[3]!=2:continue
  if c[0]<1 or c[2]<1 or c[7]<1:continue
  masks=tuple(m for m,n in zip(VOCAB,c)for _ in range(n));out[masks]=r
 need(Counter(r[2]for r in out.values())=={5:1,6:4,7:3},'Complete all-rank census')
 need(next(m for m,r in out.items()if r[2]==5)==R5,'Unique rank-five necessary profile')
 reductions={}
 for m,r in out.items():
  if r[2]!=7:continue
  choices=[]
  for j,x in enumerate(m):
   if not(x&4):continue
   lower=tuple(sorted(m[:j]+(x^4,)+m[j+1:]))
   if lower in out and out[lower][2]==6:choices.append(lower)
  need(choices,'Every rank-seven inventory improves by deleting one C incidence')
  reductions[str(m)]=choices[0]
 return out,reductions
def invoice(masks,sizes=(4,4,1,1,4,4),orientation=(0,1)):
 helpers={1:14,2:8,3:4,4:108,5:16,6:3,7:9,8:40,9:361};paid={1:2231,2:454,3:490,4:109,5:152,6:8,7:9,8:1}
 f=sum(sizes);a,b,c,d,e,z=sizes;groups=(a,b+c,d+e,z)
 r=tuple(sum(m>>i&1 for m in masks)for i in range(4))
 t=Counter({k:f*v for k,v in helpers.items()});p=Counter({k:f*v for k,v in paid.items()})
 def node(n):
  if n==1:return
  node(n//2);node(n-n//2);t[8*n+1]+=208;p[8*n]+=208;p[1]+=104
 for n in sizes:node(n)
 for m in masks:t[1+8*sum(groups[i]for i in range(4)if m>>i&1)]+=104
 for g,rr in zip(groups,r):p[8*g]+=104*(rr-2)
 p[1]+=3*104
 for group,(left,right),o in zip((b+c,d+e),((b,c),(d,e)),orientation):
  headless,headed=(left,right)if o==0 else(right,left)
  t[8*group+1]-=104;t[8*headless]+=104;t[8*headed+1]+=104
  p[8*group]-=104;p[8*left]+=104;p[8*right]+=104
 need(all(n>=0 for n in t.values())and all(n>=0 for n in p.values()),'No missing pure target or idle during granted split')
 return +t,+p
def signed(t,p):
 out=Counter(t);out.subtract(p);return {r:n for r,n in out.items()if n}
def main():
 inv,red=census();reference=(0,2,2,3,4,4,12,15)
 source=json.loads((HERE/'inputs/pr6726-INVOICE-EXTRACT.json').read_text())
 st,sp=invoice(reference)
 need(st==Counter({int(k):v for k,v in source['targets'].items()})and sp==Counter({int(k):v for k,v in source['paid'].items()}),'Independent literal source histogram equals exact #6726 receipt')
 at,ap=invoice(R5)
 reported=json.loads((HERE/'RESULT.json').read_text())['candidate_granted_invoice']
 need(at==Counter({int(k):v for k,v in reported['targets'].items()})and ap==Counter({int(k):v for k,v in reported['paid'].items()}),'Every independently counted candidate coefficient matches A')
 need((sum(at.values()),sum(ap.values()))==(13670,66956),'Complete candidate census')
 cases=[(1,1,1,1,1,1),(4,4,1,1,4,4),(2,3,5,7,11,13),(9,1,2,3,1,8)]
 checks=0
 for sizes in cases:
  for orient in product((0,1),repeat=2):
   t,p=invoice(R5,sizes,orient);rt,rp=invoice(reference,sizes,orient)
   delta=Counter(signed(t,p));delta.subtract(signed(rt,rp));delta={r:n for r,n in delta.items()if n}
   cg=sizes[3]+sizes[4];expected=Counter({8*cg+1:104,8*cg:-104,1:-104})
   need(delta==expected,'Exact rank-five signed invoice difference for every tested split orientation');checks+=1
 rank6=[]
 for masks,r in inv.items():
  if r[2]!=6:continue
  dt=Counter(masks);dt.subtract(R5)
  rank6.append(dict(masks=masks,target_delta={str(m):n for m,n in dt.items()if n},paid_C_extra=1))
 result=dict(status='PASS_INDEPENDENT_A_INVOICE_AND_ALL_RANK_SECTOR_AUDIT',census=[dict(masks=m,ranks=r)for m,r in sorted(inv.items())],rank6_formal_differences=rank6,rank7_deletion_controls=red,complete_literal_invoice_cases=checks,source_targets=dict(st),source_paid=dict(sp),candidate_targets=dict(at),candidate_paid=dict(ap),candidate_productive=sum(at.values()),candidate_paid_requests=sum(ap.values()),scope='Independent invoice audit only; all-rank extension assumes A universal geometry gives P union Q=I, endpoint nesting, and at least one pureB and pureC target for the two granted fragments; does not prove physical fragments or new geometry')
 rendered=json.dumps(result,indent=2)+'\n'
 if '--write' in sys.argv:(HERE/'INDEPENDENT-INVOICE.json').write_text(rendered)
 else:need((HERE/'INDEPENDENT-INVOICE.json').read_text()==rendered,'Retained independent receipt matches replay')
 print(rendered,end='')
if __name__=='__main__':main()
