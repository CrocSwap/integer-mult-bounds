"""Screen two-hop bypasses under instantaneous original-receipt preservation.

Retain an arbitrary history of all local forms and allow any source form to be
sent on each surviving contact.  The original form at each surviving receipt
(including at the replaced egress) must be reconstructible at its original
clock.  If the required form is already in receiver stock, we grant the
receiver the sender's ENTIRE stock. This dominates every one-scalar choice.
Do not interpret a failure as excluding changed receipt requirements or clocks.
"""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from bisect import bisect_left
from pathlib import Path
import json
from native_model import SOURCE_SHA256,load,primitive,paths,record,insert,contains

def initial(G):
 S=defaultdict(dict)
 for i,c in enumerate(G['start']):insert(S[c],1<<i)
 return S

def advance(S,R,F):
 if contains(R,F):
  B=R.copy()
  for v in S.values():insert(B,v)
  return B,True
 if not contains(S,F):
  union=R.copy()
  for v in S.values():insert(union,v)
  if not contains(union,F):return None,False
 B=R.copy();insert(B,F);return B,False

def same(A,B):return len(A)==len(B) and all(contains(B,x) for x in A.values())

def fail_terminal(stock,final):
 return [r for c,outputs in final.items() for r,F in outputs if not contains(stock[c],F)]

def prepare(G,edges):
 stock=initial(G);history=defaultdict(list);overgrants=0
 for c in range(len(G['frames'])):history[c].append((-1,stock[c].copy()))
 for j,e in enumerate(edges):
  S=stock[e['a']];R=stock[e['b']];e['S']=S.copy();e['R']=R.copy()
  B,grant=advance(S,R,e['F']);assert B is not None
  overgrants+=grant;stock[e['b']]=B;e['Rafter']=B.copy();history[e['b']].append((j,B.copy()))
 assert overgrants==0
 return history,overgrants

def at(history,c,j):
 a=history[c];return a[bisect_left(a,(j,))-1][1]

def optimized(G,edges,final,history,path):
 h,first,last=path;ie=edges[first];a=ie['a'];alt={h:ie['R'].copy()};grants=0
 for j in range(first+1,len(edges)):
  e=edges[j];special=j==last;sa=a if special else e['a'];tb=e['b']
  if not special and sa not in alt and tb not in alt:continue
  S=alt[sa] if sa in alt else (at(history,sa,j) if special else e['S'])
  R=alt[tb] if tb in alt else e['R'];B,grant=advance(S,R,e['F']);grants+=grant
  if B is None:
   phase='bridge' if special else ('before_bridge' if j<last else 'after_bridge')
   return {'outcome':'receipt_failure','phase':phase,'failure_clock':e['clock'],'failure_register':e['reg'],'overgrants':grants}
  if same(B,e['Rafter']):alt.pop(tb,None)
  else:alt[tb]=B
 missing=[r for c,B in alt.items() for r,F in final[c] if not contains(B,F)]
 if missing:return {'outcome':'terminal_failure','missing_outputs':sorted(missing),'overgrants':grants}
 return {'outcome':'optimistic_survivor','overgrants':grants}

def naive(G,edges,final,path):
 """Control: recompute all stocks chronologically from scratch, no snapshots."""
 _,first,last=path;stock=initial(G);a=edges[first]['a']
 for j,e in enumerate(edges):
  if j==first:continue
  sa=a if j==last else e['a'];B,_=advance(stock[sa],stock[e['b']],e['F'])
  if B is None:
   phase='bridge' if j==last else ('before_bridge' if j<last else 'after_bridge')
   return {'outcome':'receipt_failure','phase':phase,'failure_clock':e['clock'],'failure_register':e['reg']}
  stock[e['b']]=B
 missing=fail_terminal(stock,final)
 return {'outcome':'terminal_failure','missing_outputs':sorted(missing)} if missing else {'outcome':'optimistic_survivor'}

def main():
 p=ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('--control-all',action='store_true');p.add_argument('--output',default=str(Path(__file__).with_name('RECEIPT-RESULTS.json')));args=p.parse_args()
 G=load(args.source);edges,inn,out,final=primitive(G);cases=paths(G,edges,inn,out);history,base_grants=prepare(G,edges)
 results=[];stats=Counter();hinges=defaultdict(Counter);total_grants=0
 for ci,path in enumerate(cases):
  row=optimized(G,edges,final,history,path);total_grants+=row['overgrants'];stats[row['outcome']]+=1
  if row['outcome']=='receipt_failure':stats['phase_'+row['phase']]+=1
  h=path[0];hinges[h][row['outcome']]+=1
  if args.control_all:
   check=naive(G,edges,final,path);assert {k:v for k,v in row.items() if k!='overgrants'}==check,(record(edges,path),row,check)
  results.append({**record(edges,path),**row})
 assert stats=={'receipt_failure':1253,'phase_before_bridge':616,'phase_bridge':619,'phase_after_bridge':18,'terminal_failure':304}
 result={'source_sha256':SOURCE_SHA256,'cases':len(cases),'baseline_overgrant_events':base_grants,'candidate_overgrant_events':total_grants,'counts':dict(stats),
 'nine_hinges':{str(h):dict(hinges[h]) for h in range(510,519)},'controls':{'native_primitive_outputs':630,'all_candidate_full_chronological_replay':args.control_all},'results':results}
 Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2,sort_keys=True))
if __name__=='__main__':main()
