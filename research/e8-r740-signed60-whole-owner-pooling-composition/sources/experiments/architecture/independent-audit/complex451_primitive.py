from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,gzip,hashlib,sys
P=Path(__file__).resolve().parent;R=P.parents[2];S=R/'experiments/architecture'/sys.argv[1];D=S/'split-centres';t=json.load(gzip.open(D/'GLOBAL-TEMPLATE.json.gz','rt'));c=json.load(gzip.open(D/'CANONICAL-WORD.json.gz','rt'));report=json.load(open(S/'PRIMITIVE-REVIEW.json'));n=240+c['R'];assert n==800
out={}
for orientation,events in t['local_programs'].items():
 A={('L',i):{i:Q(1)} for i in range(n)};norm={k:Q(1) for k in A};count=Counter();peak=1
 for event in events:
  if event[0]!='scalar':continue
  e=event[1];tag=e[0];dst=tuple(e[1])
  if tag=='clear':A[dst]={};norm[dst]=0;count['clear']+=1
  elif tag=='copy':src=tuple(e[2]);A[dst]=dict(A[src]);norm[dst]=norm[src];count['copy']+=1
  elif tag=='scale':
   q=Q(e[2],e[3]);a,b=abs(q.numerator),q.denominator;assert a&(a-1)==0 and b&(b-1)==0
   count['double']+=a.bit_length()-1;count['halve']+=b.bit_length()-1;count['negate']+=int(q<0);peak=max(peak,a*norm[dst]);A[dst]={k:q*v for k,v in A[dst].items()};norm[dst]*=abs(q)
  else:
   assert tag=='add';src=tuple(e[2]);q=Q(e[3],e[4]);a,b=abs(q.numerator),q.denominator;assert b&(b-1)==0
   count['clear']+=2;count['accumulate']+=a.bit_count()+1;count['double']+=a.bit_length()-1;count['halve']+=b.bit_length()-1
   peak=max(peak,a*norm[src]);norm[dst]=norm.get(dst,0)+abs(q)*norm[src];row=A.setdefault(dst,{})
   for k,v in list(A[src].items()):
    row[k]=row.get(k,0)+q*v
    if not row[k]:del row[k]
  peak=max(peak,norm[dst])
 for i in range(n):
  wanted={i:Q(1)}
  if orientation=='forward' and 120<=i<240:wanted[i-120]=1
  if orientation=='backward' and i<120:wanted[i+120]=-1
  assert A['L',i]==wanted
 assert all(not row for k,row in A.items() if k[0]!='L')
 assert dict(count)==report['orientations'][orientation]['primitive_counts'] and 2*sum(count.values())==report['orientations'][orientation]['real_component_primitives'] and peak==Q(report['orientations'][orientation]['cancellation_free_peak'])
 out[orientation]={'counts':dict(count),'real_primitives':2*sum(count.values()),'cancellation_free_prefix':str(peak),'all800columns_and_private_work_exact':True}

result={'status':'PASS_INDEPENDENT_COMPLEX451_EMITTED800_PRIMITIVE_PREFIX','orientations':out};(P/'COMPLEX451-PRIMITIVE.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
