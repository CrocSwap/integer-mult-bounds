"""Reconstruct eleven chronological clean resets; regenerate arbitrary-dirt compensation.
Rohan Arun with OpenAI Codex assistance, using icekylinx's PR433 and ai-nanachi's PR426.
"""
import copy,hashlib,json,sys
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parent

def reconstruct(raw,selection):
 assert hashlib.sha256(raw).hexdigest()==selection['source_sha256']
 w=json.loads(raw);v=w['v'];n=2*v+w['R'];entries=selection['entries'];cut=len(w['A'])-w['source_basis_gates'];assert all(d>=2*v for f,d,ss in w['A'][:cut])
 removed={z['new_helper'] for z in entries};retired={z['retired_helper'] for z in entries}
 assert len(removed)==len(retired)==len(entries) and not removed&retired
 assert all(2*v<=x<n for x in removed|retired)
 by=defaultdict(list)
 for z in entries:
  pos,h,dead=z['position'],z['new_helper'],z['retired_helper'];assert 0<pos<cut
  assert all(h!=d and h not in ss for f,d,ss in w['A'][:pos])
  assert all(dead!=d and dead not in ss for f,d,ss in w['A'][pos:]+w['B'])
  assert h not in z['parents'] and dead not in z['parents'] and len(set(z['parents']))==len(z['parents'])
  by[pos].append(z)
 # Each reset must zero the actual clean form at its actual insertion time.
 alias={z['new_helper']:z['retired_helper'] for z in entries}
 role=lambda x:alias.get(x,x)
 clean=[1<<i if i<v else 0 for i in range(n)];a=[]
 for i,e in enumerate(w['A']):
  for z in by[i]:
   dead=z['retired_helper'];before=clean[dead];assert before
   for parent in z['parents']:clean[dead]^=clean[role(parent)]
   assert clean[dead]==0
   a.append([z['frame'],dead,z['parents']])
  f,d,ss=e
  for q in ss:clean[role(d)]^=clean[role(q)]
  a.append(e)
 physical=[x for x in range(n) if x not in removed];mp={x:i for i,x in enumerate(physical)}
 for z in entries:mp[z['new_helper']]=mp[z['retired_helper']]
 def remap(gs):return [[f,mp[d],[mp[s] for s in ss]] for f,d,ss in gs]
 c=copy.deepcopy(w);c['A']=remap(a);c['B']=remap(w['B']);c['C']=[[w['final'][0],d,ss] for f,d,ss in reversed(c['A'][:cut+len(entries)])];c['R']-=len(entries);c['start']=[w['start'][i] for i in physical];c['final']=[w['final'][i] for i in physical];c['ret']=[mp[x] for x in w['ret']]
 nn=2*v+c['R'];vals=[1<<i for i in range(nn)]
 for ph in ['A','B','C']:
  if ph=='B':
   totals=[vals[i] for i in c['ret']]
   for t,ks in enumerate(c['scatter']):
    for k in ks:vals[v+t]^=totals[k]
  for f,d,ss in c[ph]:
   assert d not in ss
   for q in ss:vals[d]^=vals[q]
 for i in list(range(v))+list(range(2*v,nn)):assert vals[i]==1<<i
 D=[]
 for t in range(v):
  z=vals[v+t]^(1<<(v+t))^(1<<t);assert not z&((1<<(2*v))-1)
  ss=[i for i in range(2*v,nn) if z>>i&1]
  if ss:D.append([0,v+t,ss])
 c['D']=D;raw=json.dumps(c,sort_keys=True,separators=(',',':')).encode();assert hashlib.sha256(raw).hexdigest()==selection['word_sha256'];return raw

def controls(raw,sel):
 rejected=[]
 cases=[]
 for label in ('missing reset parent','wrong insertion time','duplicate physical reuse'):
  s=copy.deepcopy(sel)
  if label=='missing reset parent':s['entries'][0]['parents'].pop()
  elif label=='wrong insertion time':s['entries'][0]['position']=0
  else:s['entries'][1]['new_helper']=s['entries'][0]['new_helper']
  cases.append((label,s))
 for label,s in cases:
  try:reconstruct(raw,s)
  except AssertionError:rejected.append(label)
  else:raise AssertionError(label)
 return rejected
if __name__=='__main__':
 raw=Path(sys.argv[1]).read_bytes();s=json.loads((ROOT/'SELECTION.json').read_text());out=Path(sys.argv[2]);data=reconstruct(raw,s);out.write_bytes(data);print(json.dumps(dict(status='PASS_EXACT_CHRONOLOGICAL_RECONSTRUCTION',helpers_removed=len(s['entries']),R=s['R'],sha256=hashlib.sha256(data).hexdigest(),controls=controls(raw,s))))
