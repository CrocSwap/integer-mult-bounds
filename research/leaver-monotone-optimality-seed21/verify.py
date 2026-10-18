"""Exact monotone-cell lower bound, independently written for @woklerx.
Substantial OpenAI Codex assistance; Apache-2.0. Standard library only.
"""
import argparse
from collections import deque, Counter
from fractions import Fraction as Q
import gzip
import hashlib
import itertools
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PREFIX='research/gauge44-slots-t16/'
CORES=[f'CORE-{p}{s}.json' for p in ('01','23','45','67') for s in ('+','-')]
REQUIRED={PREFIX+'construction/leaver/cells-k8/'+s for s in CORES}|{
 PREFIX+'construction/leaver/CODED-CELLS-k8.json',
 PREFIX+'construction/leaver/cgx_leaver.py',PREFIX+'README.md',
 'research/community-frontier1042-audit/ASSEMBLY.json'}
NAMES=[f'x{i}' for i in range(6)]+[f'y{i}' for i in range(6)]

def need(ok,msg):
 if not ok: raise ValueError(msg)

def pairs_object(items):
 d={}
 for k,v in items:
  need(k not in d,'duplicate JSON key'); d[k]=v
 return d

def read_json(path):
 raw=path.read_bytes()
 if path.suffix=='.gz': raw=gzip.decompress(raw)
 return json.loads(raw,object_pairs_hook=pairs_object,
  parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON')))

def digest(path):
 b=path.read_bytes()
 if path.suffix!='.gz': b=b.replace(b'\r\n',b'\n')
 return hashlib.sha256(b).hexdigest()

def check_pins(pins):
 need(set(pins)==REQUIRED,'required source set mismatch')
 for name,h in pins.items(): need(digest(ROOT/name)==h,'source hash mismatch: '+name)

def matrix(gates):
 a=[[Q(i==j) for j in range(12)] for i in range(12)]
 for t,s,q in gates:
  need(t in NAMES and s in NAMES and t!=s,'invalid gate')
  i,j=NAMES.index(t),NAMES.index(s); q=Q(q)
  need(q!=0,'zero gate')
  a[i]=[v+q*w for v,w in zip(a[i],a[j])]
 return a

def binary(a):
 need(all(v in (0,1) for row in a for v in row),'nonbinary endpoint')
 return [sum(int(v)<<j for j,v in enumerate(row)) for row in a]

def structure(rows):
 need(len(rows)==12 and all(type(r) is int and r>>i&1 for i,r in enumerate(rows)),'diagonal missing')
 xs=[]
 for i in range(6):
  extra=rows[i]^(1<<i)
  need(extra<64 and extra.bit_count()<=1,'invalid source pair')
  if extra: xs.append((i,extra.bit_length()-1))
 need(len(xs)==3 and sorted(j for p in xs for j in p)==list(range(6)),'source pairs not a matching')
 edges=[(i,j) for i in range(6,12) for j in range(6,12) if i!=j and rows[i]>>j&1]
 need(len(edges)==3 and sorted(j for p in edges for j in p)==list(range(6,12)),'target edges not a matching')
 for a,b in xs:
  cv=lambda r: ((r>>a)&1)+2*((r>>b)&1)
  need(sorted((cv(rows[s]),cv(rows[t])) for t,s in edges)==[(1,3),(3,2),(3,3)],'projection type mismatch')
 return xs,edges

def conjugacy(unit,scaled):
 need(len(unit)==len(scaled),'gate count mismatch')
 adj=[[] for _ in NAMES]
 for (t,s,q),(tt,ss,r) in zip(unit,scaled):
  need((t,s)==(tt,ss) and type(q) is int and q==1,'unit/scaled shape mismatch')
  i,j=NAMES.index(t),NAMES.index(s); r=Q(r); need(r!=0,'zero scale ratio')
  adj[j].append((i,r)); adj[i].append((j,1/r))
 d=[None]*12
 for start in range(12):
  if d[start] is not None: continue
  d[start]=Q(1); todo=[start]
  for j in todo:
   for i,q in adj[j]:
    if d[i] is None: d[i]=q*d[j]; todo.append(i)
    else: need(d[i]==q*d[j],'inconsistent diagonal conjugacy')
 u=matrix(unit); v=matrix(scaled)
 need(v==[[d[i]*u[i][j]/d[j] for j in range(12)] for i in range(12)],'conjugated endpoint mismatch')
 return [str(x) for x in d]

def projected_minimum(target,edges):
 """Full 0/1 BFS of a relaxation: one X sum and three Y copies cost zero.
 Y<-X additions cost one. State=(source-merged bit,Y-edge-used mask,six 2-bit rows).
 """
 start=(0,0,(0,)*6); dist={start:0}; todo=deque([start])
 while todo:
  state=todo.popleft(); merged,used,ys=state; cost=dist[state]; outgoing=[]
  if not merged: outgoing.append(((1,used,ys),0))
  for k,(t,s) in enumerate(edges):
   z=ys[s]
   if not used>>k&1 and not ys[t]&z and (ys[t]|z)&~target[t]==0:
    ny=list(ys); ny[t]|=z; outgoing.append(((merged,used|(1<<k),tuple(ny)),0))
  for t in range(6):
   for z in ((3 if merged else 1),2):
    if not ys[t]&z and (ys[t]|z)&~target[t]==0:
     ny=list(ys); ny[t]|=z; outgoing.append(((merged,used,tuple(ny)),1))
  for ns,w in outgoing:
   nc=cost+w
   if nc<dist.get(ns,10**9):
    dist[ns]=nc
    (todo.append if w else todo.appendleft)(ns)
 goal=(1,7,tuple(target)); need(goal in dist,'projection unreachable')
 return {'minimum_YX':dist[goal],'states':len(dist),
  'distance_histogram':dict(sorted(Counter(dist.values()).items()))}

def endpoint_permutation(rows,reference):
 xs,_=structure(rows); refxs,_=structure(reference)
 for order in itertools.permutations(refxs):
  perm={i:j for p,q in zip(xs,order) for i,j in zip(p,q)}
  def translate(r): return sum(1<<perm[k] for k in range(6) if r>>k&1)
  possible=True
  for i in range(6,12):
   cand=[j for j in range(6,12) if reference[j]&63==translate(rows[i]&63)]
   if len(cand)!=1: possible=False; break
   perm[i]=cand[0]
  if possible and len(set(perm.values()))==12:
   if all(sum(1<<perm[j] for j in range(12) if rows[i]>>j&1)==reference[perm[i]] for i in range(12)):
    return [perm[i] for i in range(12)]
 raise ValueError('no endpoint permutation')

def controls(core,rows,pins):
 import copy
 passed=[]
 def reject(name,fn):
  try: fn()
  except (ValueError,KeyError): passed.append(name); return
  raise ValueError('negative control accepted: '+name)
 bad=rows.copy(); bad[0]|=1<<6
 reject('source_receives_target_dirt',lambda:structure(bad))
 bad2=rows.copy(); bad2[6]|=1<<7
 reject('extra_target_dependency',lambda:structure(bad2))
 bad3=rows.copy(); bad3[7]^=1
 reject('projection_coefficient_deleted',lambda:structure(bad3))
 bad4=copy.deepcopy(core['scaled']); bad4[-1][2]='3'
 reject('inconsistent_scaled_gate',lambda:conjugacy(core['unit'],bad4))
 reject('one_gate_omitted',lambda:need(matrix(core['unit'][:-1])==matrix(core['unit']),'endpoint differs'))
 bad5=copy.deepcopy(core['unit']); bad5[0][2]=True
 reject('boolean_unit_coefficient',lambda:conjugacy(bad5,core['scaled']))
 reject('required_pin_deleted',lambda:check_pins(dict(list(pins.items())[1:])))
 reject('duplicate_json_key',lambda:json.loads('{"a":1,"a":2}',object_pairs_hook=pairs_object))
 reject('nonfinite_json',lambda:json.loads('[NaN]',parse_constant=lambda x:need(False,'nonfinite')))
 reject('floating_seed',lambda:validate_identity({'seed':21.0}))
 # Outside the sharp type condition: relaxing one required donor contribution lowers the bound.
 target=[2,3,3,3,3,1]; edges=[(0,1),(2,3),(4,5)]
 relaxed=target.copy(); relaxed[4]=1
 low=projected_minimum(relaxed,edges)
 need(low['minimum_YX']==4,'relaxed projection control should attain four')
 passed.append('relaxed_projection_attains_four')
 return passed

def validate_identity(d): need(type(d.get('seed')) is int and d['seed']==21,'wrong exact seed')

def build(pins):
 check_pins(pins)
 source=ROOT/(PREFIX+'construction/leaver/cells-k8')
 cores=[read_json(source/name) for name in CORES]
 coded=read_json(ROOT/(PREFIX+'construction/leaver/CODED-CELLS-k8.json'))
 need(len(coded)==8,'coded cell count')
 assembly=read_json(ROOT/'research/community-frontier1042-audit/ASSEMBLY.json')
 need(Q(assembly['kappa'])==Q(1672188119205421,10**18),'selected-at-base assembly mismatch')
 need({c['cell'] for c in coded}=={name[5:-5] for name in CORES},'coded cell identity set')
 reference=binary(matrix(cores[0]['unit'])); results=[]
 for name,core in zip(CORES,cores):
  rows=binary(matrix(core['unit'])); xs,ys=structure(rows)
  need(len(core['unit'])==21,'attaining word length')
  projections=[]
  for a,b in xs:
   target=[((r>>a)&1)+2*((r>>b)&1) for r in rows[6:]]
   p=projected_minimum(target,[(t-6,s-6) for t,s in ys]); need(p['minimum_YX']==5,'five gate floor')
   projections.append(p)
  diag=conjugacy(core['unit'],core['scaled'])
  same=next(c for c in coded if c['cell']==name[5:-5])
  need(same['scaled']==core['scaled'] and same['unit']==core['unit'],'coded core mismatch')
  results.append({'core':name,'unit_endpoint':rows,'diagonal':diag,
   'endpoint_permutation_to_first':endpoint_permutation(rows,reference),
   'X_pairs':xs,'Y_edges':ys,'projections':projections,'minimum_ADD':21,
   'attaining_gate_types':dict(sorted(Counter(t[0]+s[0] for t,s,q in core['unit']).items()))})
 ctl=controls(cores[0],reference,pins)
 return {'seed':21,'base':'ba82555c64e1879e4b7decce28186f208fcb8262',
  'selected_PR':1042,'source_hashes':pins,'cell_count':8,'cell_ADD_total':168,
  'scope':'No extra registers; fixed diagonal conjugates of unit positive ADD; exact complete scalar endpoints. No paid-frame or unrestricted rational lower bound.',
  'cores':results,'negative_controls':ctl}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--write',action='store_true'); args=ap.parse_args()
 pins=read_json(HERE/'SOURCES.json')
 receipt=build(pins)
 if args.write: (HERE/'CERTIFICATE.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 else:
  saved=read_json(HERE/'CERTIFICATE.json'); validate_identity(saved)
  canonical=lambda d:json.dumps(json.loads(json.dumps(d)),sort_keys=True,separators=(',',':'))
  need(canonical(receipt)==canonical(saved),'complete certificate mismatch')
 print(f'PASS_LEAVER_MONOTONE_S21 cells=8 minimum=21 projected_minimum=5 controls={len(receipt["negative_controls"])}')

if __name__=='__main__': main()
