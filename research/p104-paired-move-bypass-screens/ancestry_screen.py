"""Unlimited-capacity ancestry control for the screened two-hop bypasses.

Each surviving MOVE grants every independently available public input at its
source to its destination. A target input missing at a final output chart
rules out every causal binary-linear coding for that fixed contact schedule.
Passing is only a necessary condition and supplies no actual one-scalar code.
"""
from argparse import ArgumentParser
from bisect import bisect_left
from collections import Counter,defaultdict
from pathlib import Path
import json
from native_model import SOURCE_SHA256,load,primitive,paths,record

def initial(G):
 S=defaultdict(int)
 for i,c in enumerate(G['start']):S[c]|=1<<i
 return S

def prepare(G,edges):
 stock=initial(G);history=defaultdict(list)
 for c in range(len(G['frames'])):history[c].append((-1,stock[c]))
 for j,e in enumerate(edges):
  a=e['a'];b=e['b'];e['S']=stock[a];e['R']=stock[b];stock[b]|=stock[a];e['Rafter']=stock[b];history[b].append((j,stock[b]))
 return history,stock

def at(history,c,j):
 a=history[c];return a[bisect_left(a,(j,))-1][1]

def missing(stock,final):
 bad=[]
 for c,rows in final.items():
  for output,F in rows:
   bits=F&~stock[c]
   if bits:bad.append({'output':output,'chart':c,'missing_inputs':[i for i in range(630) if bits>>i&1]})
 return sorted(bad,key=lambda r:r['output'])

def optimized(edges,final,history,path):
 h,first,last=path;ie=edges[first];a=ie['a'];alt={h:ie['R']}
 for j in range(first+1,len(edges)):
  e=edges[j];special=j==last;sa=a if special else e['a'];tb=e['b']
  if not special and sa not in alt and tb not in alt:continue
  S=alt[sa] if sa in alt else (at(history,sa,j) if special else e['S']);R=alt[tb] if tb in alt else e['R'];B=R|S
  if B==e['Rafter']:alt.pop(tb,None)
  else:alt[tb]=B
 bad=[]
 for c,bits in alt.items():
  for output,F in final[c]:
   absent=F&~bits
   if absent:bad.append({'output':output,'chart':c,'missing_inputs':[i for i in range(630) if absent>>i&1]})
 return sorted(bad,key=lambda r:r['output'])

def naive(G,edges,final,path):
 """Independent from-scratch chronological propagation, with no snapshots."""
 _,first,last=path;stock=initial(G);a=edges[first]['a']
 for j,e in enumerate(edges):
  if j==first:continue
  sa=a if j==last else e['a'];stock[e['b']]|=stock[sa]
 return missing(stock,final)

def main():
 p=ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('--control-all',action='store_true');p.add_argument('--output',default=str(Path(__file__).with_name('ANCESTRY-RESULTS.json')));args=p.parse_args()
 G=load(args.source);edges,inn,out,final=primitive(G);cases=paths(G,edges,inn,out);history,stock=prepare(G,edges);assert not missing(stock,final)
 rows=[];stats=Counter();hinges=defaultdict(Counter)
 for path in cases:
  bad=optimized(edges,final,history,path)
  if args.control_all:assert bad==naive(G,edges,final,path),record(edges,path)
  outcome='impossible' if bad else 'necessary_test_only'
  stats[outcome]+=1;hinges[path[0]][outcome]+=1
  rows.append({**record(edges,path),'outcome':outcome,**({'missing':bad} if bad else {})})
 assert stats=={'impossible':10,'necessary_test_only':1547}
 result={'source_sha256':SOURCE_SHA256,'cases':len(cases),'counts':dict(stats),'nine_hinges':{str(h):dict(hinges[h]) for h in range(510,519)},'controls':{'native_primitive_outputs':630,'baseline_all_targets_reachable':True,'all_candidate_full_chronological_replay':args.control_all},'results':rows}
 Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2,sort_keys=True))
if __name__=='__main__':main()
