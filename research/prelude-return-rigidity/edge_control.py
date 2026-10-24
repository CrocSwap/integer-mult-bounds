#!/usr/bin/env python3
"""Positive scope control; not an emitted native supplier. Apache-2.0."""
from pathlib import Path
from collections import defaultdict
import importlib.util,gzip,json
sp=importlib.util.spec_from_file_location('V',Path(__file__).with_name('verify.py'));V=importlib.util.module_from_spec(sp);sp.loader.exec_module(V)

def basis(s):
 b=[];z={0}
 for v in sorted(s):
  if v not in z:b.append(v);z|={x^v for x in tuple(z)}
 return b

def check(d):
 c=d['canonical'];result={}
 for direction in ('forward','backward'):
  p,links=V.skeleton(d,direction);deleted=(('scalar',9067),('scalar',9068));V.need(links[deleted]=={33},'source scalar edge control')
  outs=defaultdict(set)
  for u,v in links:
   if (u,v)!=deleted:outs[u].add(v)
  full=set(range(512));U={('exit',r):V.span(c['frames'][c['final'][r]]) for r in range(112,224)}
  for i in reversed(range(len(p))):
   if p[i][0]=='scalar':
    n=('scalar',i);s=set(full)
    for v in outs[n]:s&=U[v]
    U[n]=s
  for n in outs:
   if n not in U:
    s=set(full)
    for v in outs[n]:s&=U[v]
    U[n]=s
  # Keep only the same fixed main X/Y boundaries used in the forcing proof.
  for r in range(112):U['entry',r]=V.span(c['frames'][c['start'][r]])
  checked=0
  for u,v in links:
   if (u,v)==deleted:continue
   V.need(U[u]<=U[v],'all remaining containment edges hold');checked+=1
  V.need(U['scalar',9067]=={0,75,138,193,288,363,426,481},'rank-three relaxed cap')
  V.need(U['scalar',6327]=={0,5,40,45,73,76,97,100},'compatible rank-three last prelude cap')
  # Explicit partial inverse map: a->45 and a three-space onto the fourth contact.
  A=[138,75,288];B=[45,5,73]
  for X in (A,B):
   for j in range(9):
    if (1<<j) not in V.span(X):X.append(1<<j)
  G={0:0}
  for a,b in zip(A,B):G.update({x^a:y^b for x,y in tuple(G.items())})
  V.need(len(G)==len(set(G.values()))==512 and G[138]==45,'explicit invertible compatible prelude map')
  V.need({G[x] for x in U['scalar',9067]}==U['scalar',6327],'inverse can return a rank-three space after graph cut')
  contacts=[U['scalar',i] for i in range(6324,6328)]
  V.need({0,45}<=contacts[0] and all(a<=b for a,b in zip(contacts,contacts[1:])), 'complete positive-to-inverse prelude chain in graph control')
  V.need(contacts[-1]=={G[x] for x in U['scalar',9067]},'same G/inverse pair at its actual inverse input')
  result[direction]={'deleted_edge':deleted,'owner':33,'all_remaining_edges_checked':checked,'post_inverse_next_contact_basis':basis(U['scalar',9067]),'last_prelude_basis':basis(U['scalar',6327]),'G_columns':[G[1<<j] for j in range(9)],'prelude_contact_dimensions':[len(basis(s)) for s in contacts],'scope':'Optimistic cut-warp containment model only; not a complete physical native construction.'}
 return result

if __name__=='__main__':
 import sys
 result=json.loads(json.dumps(check(V.load_source())))
 if '--write' in sys.argv:
  Path(__file__).with_name('EDGE-DELETION-CONTROL.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 else:
  V.need(result==json.loads(Path(__file__).with_name('EDGE-DELETION-CONTROL.json').read_text()),'deterministic graph-change control')
 print('PASS_SOURCE_EDGE_DELETION_PERMITS_RANK_THREE_RETURN_NOT_A_NATIVE_CIRCUIT')
