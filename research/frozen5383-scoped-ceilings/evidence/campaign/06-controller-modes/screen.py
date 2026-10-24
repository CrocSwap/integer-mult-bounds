#!/usr/bin/env python3
"""Independent exact p16 fixed-boundary Laurent screen; stdlib only.
Source maps/profiles credited in DERIVATION.md. Substantial OpenAI assistance.
"""
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json,time
HERE=Path(__file__).resolve().parent
CAMPAIGN=HERE.parent
CAPSULE=CAMPAIGN/'09-capsule-cold/capsule-v1'
CP=CAPSULE/'snapshot/research/joint-helper-lattice/CONTROLLER.json'
IP=CAMPAIGN/'02-census/INVOICE-v1.json'
c=json.loads(CP.read_text()); inv=json.loads(IP.read_text())
assert sha256(CP.read_bytes()).hexdigest()=='1f5d6aa267e4e66048818714b5d3b5eae17a58abe91d15deeaa34574f7391a5f'
assert sha256(IP.read_bytes()).hexdigest()=='7c6dfe167dd83cc48b32743e6bcfa76e3420ccd5be997c935b02a99e3636f44e'
N=32; ALL=(1<<33)-1; oldS={0,32,*range(1,32,2)}
# Six bits per stage leave room for all possible repeated powers on a path.
# No order-two/Pauli quotient is used, and powers are validated at the end.
def packed(stages):return sum(1<<(6*s) for s in stages)
def add(a,b,f=1):
 out=a.copy()
 for k,v in b.items():
  out[k]=out.get(k,0)+f*v
  if not out[k]:del out[k]
 return out
def scale(poly,q=0,d=0,f=1):return {(k[0]+q,k[1]+d):v*f for k,v in poly.items()}
def skeleton():
 events=[]; idles=[]
 def idle(pair,stages,kind):
  idx=len(idles); r={'index':idx,'pair':pair,'stages':list(stages),'kind':kind,'retained':bool(c['keep_mask']>>idx&1)}; idles.append(r)
  if r['retained']:events.append(['IDLE',pair,r['stages']])
 def local(stage,pair,back):
  events.append(['LOCAL',stage,pair,back])
  if stage%2 and stage<=29:idle((stage+1)//2,range(stage+1),'initial')
  elif stage%2==0 and 2<=stage<=30:idle(stage//2,[stage],'middle')
  elif stage==32:
   for j in range(15):idle(j,range(2*j+3,33),'terminal')
 def bridge(dst,src,f):events.extend([['ADD',2*dst,2*src,f],['ADD',2*src+1,2*dst+1,-f]])
 local(0,0,False)
 for j in range(16):
  local(2*j+1,j,True)
  if j<15:bridge(j,j+1,1)
  local(2*j+2,j,False)
  if j<15:bridge(j,j+1,-1)
 for j in reversed(range(15)):bridge(j+1,j,1)
 for j in range(16):events.append(['SIGNED_SWAP',2*j,2*j+1])
 return events,idles
EVENTS,IDLES=skeleton()
def emit(S):
 out=[]
 for e in EVENTS:
  if e[0]=='LOCAL':out.append([('LOCAL' if e[1] in S else 'QUERY_SHEAR'),*e[1:]])
  elif e[0]=='IDLE':
   st=[s for s in e[2] if s in S]
   if st:out.append(['IDLE',e[1],st])
  else:out.append(e)
 return out
assert emit(oldS)==c['physical_events'], 'Skeleton does not reproduce all frozen events'
L=[[int(Fraction(v)) for v in row] for row in c['boundaries']['left']]
R=[[int(Fraction(v)) for v in row] for row in c['boundaries']['right']]
assert all(Fraction(v).denominator==1 for mat in [c['boundaries']['left'],c['boundaries']['right']] for row in mat for v in row)
def replay(events, right=R):
 A=[[{(0,0):v} if v else {} for v in row] for row in right]
 for e in events:
  op=e[0]
  if op in ['LOCAL','QUERY_SHEAR']:
   _,stage,pair,back=e;x,y=2*pair,2*pair+1
   if back:x,y=y,x
   A[y]=[add(a,scale(b,q=(1 if back else -1),f=(-1 if back else 1))) for a,b in zip(A[y],A[x])]
   if op=='LOCAL':
    for z in (x,y):A[z]=[scale(a,d=packed([stage])) for a in A[z]]
  elif op=='IDLE':
   for z in (2*e[1],2*e[1]+1):A[z]=[scale(a,d=packed(e[2])) for a in A[z]]
  elif op=='ADD':A[e[1]]=[add(a,b,e[3]) for a,b in zip(A[e[1]],A[e[2]])]
  elif op=='SIGNED_SWAP':A[e[1]],A[e[2]]=A[e[2]],[scale(a,f=-1) for a in A[e[1]]]
  else:raise ValueError(op)
 out=[[{} for j in range(N)] for i in range(N)]
 for i,row in enumerate(L):
  for k,f in enumerate(row):
   if f:
    for j in range(N):out[i][j]=add(out[i][j],A[k][j],f)
 return out

def specialise(A,S):
 mask=sum(63<<(6*s) for s in S)
 return [[special_poly(poly,mask) for poly in row] for row in A]
def special_poly(poly,mask):
 out={}
 for (q,d),v in poly.items():
  k=(q,d&mask);out[k]=out.get(k,0)+v
 return {k:v for k,v in out.items() if v}
def endpoint(A):
 for i in range(N):
  for j in range(N):
   if i!=j and A[i][j]:
    k,v=next(iter(sorted(A[i][j].items())))
    return None,{'reason':'OFF_DIAGONAL_LAURENT_RESIDUE','row':i,'column':j,'Q':k[0],'stage_powers':unpack(k[1]),'coefficient':v}
 terms=[]
 for i in range(N):
  if len(A[i][i])!=1:return None,{'reason':'NON_MONOMIAL_DIAGONAL','row':i,'terms':len(A[i][i])}
  (q,d),v=next(iter(A[i][i].items()));powers=unpack(d)
  if v!=1 or q not in (-1,1) or any(x not in (0,1) for x in powers):return None,{'reason':'OUTSIDE_SOURCE_NORMALIZATION','row':i,'coefficient':v,'Q':q,'stage_powers':powers}
  terms.append((q,powers))
 return terms,None
def unpack(d):return [(d>>(6*s))&63 for s in range(33)]
def hist(x):return Counter({int(k):v for k,v in x.items()})
def bill(S,terms):
 T=Counter();P=Counter();main=Counter();idle=Counter();nb=nf=0
 for e in EVENTS:
  if e[0]=='LOCAL':
   if e[1] in S:
    ori='backward' if e[3] else 'forward';nb+=int(e[3]);nf+=int(not e[3]);T.update(hist(inv['locals'][ori]['helpers']));P.update(hist(inv['locals'][ori]['paid']))
   else:P[1]+=112
  elif e[0]=='IDLE':
   r=8*len(S.intersection(e[2]))
   if r:idle[r]+=224
 for q,powers in terms:main[1+8*sum(powers)]+=112
 T.update(main);P.update(idle)
 return T,P,{'backward_full':nb,'forward_full':nf,'queries':33-len(S),'main':dict(sorted(main.items())),'idle':dict(sorted(idle.items())),'paid_jobs':sum(P.values()),'productive_fields':sum(T.values()),'rank_surplus':sum(r*n for r,n in T.items())-sum(r*n for r,n in P.items())}
TARGETS=['.00302235','.00302666','.003026674765']
def margins(T,P):
 with localcontext() as ctx:
  ctx.prec=65
  return {k:str(sum(Decimal(T[r]-P[r])*(Decimal(r)**(1-Decimal(k))) for r in T.keys()|P.keys())) for k in TARGETS}
def main(output=None):
 start=time.monotonic(); U=replay(EVENTS)
 assert max((d>>(6*s))&63 for row in U for poly in row for q,d in poly for s in range(33))<63
 base,err=endpoint(specialise(U,oldS));assert err is None
 assert [[q,*p] for q,p in base]==c['diagonal']
 T,P,bi=bill(oldS,base); assert T==hist(inv['histograms']['productive']) and P==hist(inv['histograms']['paid'])
 # Independent literal replay and universal specialization agree for baseline.
 assert replay(emit(oldS))==specialise(U,oldS)
 rows=[]; valid=[]
 for n in range(3):
  for changes in combinations(range(33),n):
   S=oldS.symmetric_difference(changes);A=specialise(U,S);terms,error=endpoint(A)
   row={'changed_stages':list(changes),'full_stages':sorted(S),'endpoint_status':'REJECTED' if error else 'EXACT_SOURCE_DIAGONAL'}
   if error:row['counterexample']=error
   else:
    T,P,counts=bill(S,terms);row.update(counts);row['T']=dict(sorted(T.items()));row['P']=dict(sorted(P.items()));row['favorable_moment_decimal']=margins(T,P);row['diagonal']=[[q,*p] for q,p in terms];valid.append(row)
   rows.append(row)
 assert len(rows)==562
 # Independent full literal chronological replay of every endpoint-surviving variant.
 for row in valid:
  S=set(row['full_stages']);assert replay(emit(S))==specialise(U,S)
 # Reject a source-invalid order-two map and orientation mutation.
 bad=emit(oldS);next(e for e in bad if e[0]=='QUERY_SHEAR')[3]=True
 assert replay(bad)!=specialise(U,oldS)
 out={'schema':'fixed-p16-modes-screen/1','script_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'source_controller_sha256':sha256(CP.read_bytes()).hexdigest(),'invoice_sha256':sha256(IP.read_bytes()).hexdigest(),'derivation_sha256':sha256((HERE/'DERIVATION.md').read_bytes()).hexdigest(),'domain_size':len(rows),'nonempty_mode_changes':561,'valid_endpoint_count':len(valid),'rejected_endpoint_count':len(rows)-len(valid),'baseline':bi,'targets':TARGETS,'arithmetic':'exact integer Laurent coefficients; decimal moments are discovery screens only','nonrecursive_penalty':'optimistically_relaxed_zero; no funding claim','universal_nonzero_cells':sum(bool(p) for row in U for p in row),'universal_terms':sum(len(p) for row in U for p in row),'runtime_seconds':round(time.monotonic()-start,6),'rows':rows}
 (output or HERE/'FEASIBILITY-v1.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2)); return out
if __name__=='__main__':main()
