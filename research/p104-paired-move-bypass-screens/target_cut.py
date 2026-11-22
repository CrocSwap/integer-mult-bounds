"""Terminal cuts granting full native preclock source stocks on each ingress.

For every enumerated path whose hinge is a final public-output chart, delete
its first ingress. Grant that hinge all input forms from the native preclock
sender history of every other incoming MOVE, at unlimited capacity and with
free local history. A dual input difference that all granted forms annihilate
and the target detects excludes any reconstruction under the frozen-exterior
stock contract, independently of intermediate receipt requirements.
"""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import json
from native_model import SOURCE_SHA256,load,primitive,paths,record,insert,contains
from receipt_screen import prepare


def residual(B,v):
 out=0
 while v:
  p=v.bit_length()-1
  if p in B:v^=B[p]
  else:out|=1<<p;v^=1<<p
 return out

def parity(x):return x.bit_count()&1

def separating_probe(B,target):
 """Return q with row·q=0 for all rows in B and target·q=1."""
 rem=residual(B,target)
 if not rem:return None
 q=1<<(rem.bit_length()-1)
 for pivot in sorted(B):
  if parity(B[pivot]&q):q|=1<<pivot
 assert all(parity(row&q)==0 for row in B.values()) and parity(target&q)==1
 return q

def main():
 p=ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('--output',default=str(Path(__file__).with_name('TARGET-CUT-RESULTS.json')));args=p.parse_args()
 G=load(args.source);edges,incoming,outgoing,final=primitive(G);cases=paths(G,edges,incoming,outgoing);prepare(G,edges)
 cache={};rows=[];counts=Counter();hinges=set()
 for path in cases:
  h,first,last=path
  if not final[h]:continue
  counts['paths_with_hinge_output']+=1;hinges.add(h)
  key=(h,first)
  if key not in cache:
   B={}
   starts=[i for i,c in enumerate(G['start']) if c==h]
   for i in starts:insert(B,1<<i)
   sources=[]
   for j in incoming[h]:
    if j==first:continue
    e=edges[j];S=e['S']
    for v in S.values():insert(B,v)
    sources.append({'clock':e['clock'],'source_chart':e['a'],'stock_dimension':len(S)})
   certificates=[]
   for owner,target in final[h]:
    q=separating_probe(B,target)
    if q is None:continue
    assert all(parity(v&q)==0 for v in B.values())
    assert parity(target&q)==1
    assert parity(edges[first]['F']&q)==1
    control=B.copy();insert(control,edges[first]['F'])
    assert contains(control,target),('positive control',h,first,owner)
    certificates.append({'output':owner,'probe_inputs':[i for i in range(630) if q>>i&1],
     'deleted_ingress_detected':True,'native_deleted_row_restores_target':True})
   cache[key]={'native_start_inputs':starts,'remaining_ingress_sources':sources,
    'granted_source_union_rank':len(B),'target_certificates':certificates}
  cert=cache[key]
  if cert['target_certificates']:counts['excluded_paths']+=1
  else:counts['survivor_paths']+=1
  rows.append({**record(edges,path),**cert})
 assert counts=={'paths_with_hinge_output':854,'excluded_paths':854} and len(hinges)==111 and len(cache)==304
 result={'source_sha256':SOURCE_SHA256,'counts':dict(counts),'public_output_hinges':len(hinges),
  'distinct_hinge_ingress_cuts':len(cache),'positive_deleted_row_controls':len(cache),'scope':'each surviving hinge ingress can convey its entire original native preclock source stock; fixed exterior stock envelopes and public endpoints',
  'results':rows}
 Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2,sort_keys=True))
if __name__=='__main__':main()
