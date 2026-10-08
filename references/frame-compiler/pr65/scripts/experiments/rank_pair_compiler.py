"""Exact-envelope block synthesis on the pinned PR48 scalar graph.
Experimental finite compiler; no fixed-I+J profile or multiplication claim.
"""
# Derived from eumemic's PR57 compiler; original notices remain applicable.
# Descending-rank reclamation priority: Chafik Boukhalfa, with OpenAI Codex assistance.
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'references/frame-compiler/pr48'
from hashlib import sha256
import json
manifest=json.loads((ROOT/'SOURCE.json').read_text())
for name,digest in manifest['files'].items():
 assert sha256((ROOT/name).read_bytes()).hexdigest()==digest, 'Changed producer source: '+name
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'research/copied-fixed')]
from changed_graph import graph
from collections import defaultdict,Counter,deque
import argparse,json,time,struct

def independent(rows,vec):
 for row in rows:
  vec=min(vec,vec^row)
 return bool(vec)
def basis(rows):
 out=[]
 for vec in rows:
  for row in out:vec=min(vec,vec^row)
  if vec:out.append(vec)
 return out

def build(h):
 c=graph(h);groups={};owner={};signal={};blocks=[]
 for x in sorted(c.active):
  key=(c.core[x],c.union[x])
  if key not in groups:
   groups[key]=len(blocks);blocks.append(dict(nodes=[],frame=key,inputs=set(),uses=[]))
  g=groups[key];owner[x]=g;blocks[g]['nodes'].append(x)
  signal[x]=(signal[c.args[x][0]]^signal[c.args[x][1]])if c.args[x]else 1<<(x-1)
 for x in sorted(c.active):
  for y in c.args[x]or():
   if owner[y]!=owner[x]:blocks[owner[x]]['inputs'].add(y)
 uses=[];value_uses=defaultdict(list)
 for g,b in enumerate(blocks):
  b['inputs']=sorted(b['inputs']);b['source']=not c.args[b['nodes'][0]]
  for y in b['inputs']:
   k=len(uses);uses.append((y,g,None));value_uses[y].append(k);blocks[owner[y]]['uses'].append(k)
 for target,x in c.outputs.items():
  k=len(uses);uses.append((x,owner[x],target));value_uses[x].append(k);blocks[owner[x]]['uses'].append(k)
 for g,b in enumerate(blocks):
  b['rank']=1 if b['source']else b['frame'][1].bit_count()-b['frame'][0].bit_count()
 order=sorted(range(len(blocks)),key=lambda g:(blocks[g]['rank'],min(blocks[g]['nodes'])))
 place={g:i for i,g in enumerate(order)}
 def contained(a,b):return not(b[0]&~a[0])and not(a[1]&~b[1])
 for g,b in enumerate(blocks):
  coeff={y:1<<i for i,y in enumerate(b['inputs'])}
  if b['source']:coeff[b['nodes'][0]]=1
  for x in b['nodes']:
   if c.args[x]:coeff[x]=coeff[c.args[x][0]]^coeff[c.args[x][1]]
  b['coeff']=coeff;b['outvalues']=sorted({uses[u][0]for u in b['uses']})
  b['outbasis']=basis(coeff[x]for x in b['outvalues']);b['candidates']=[];b['selected']=set()
  if not b['source']:
   for i,y in enumerate(b['inputs']):
    if not independent(b['outbasis'],1<<i):continue
    for u in value_uses[y]:
     _,target,terminal=uses[u]
     if place[g]<place[target]and contained(b['frame'],blocks[target]['frame']):
      b['candidates'].append((u,i))
 return c,blocks,uses,value_uses,owner,signal,order,contained

def match(blocks,uses,enabled):
 edges=[];byblock=[]
 for g,b in enumerate(blocks):
  row=[]
  for u,i in b['candidates']:row.append(len(edges));edges.append((g,u,i))
  byblock.append(row)
 chosen=set();right={};stats=Counter()
 def can(e,drop=None):
  g,u,i=edges[e];selected=blocks[g]['selected']
  rows=blocks[g]['outbasis']+[1<<edges[f][2]for f in selected if f!=drop]
  return independent(basis(rows),1<<i)
 if not enabled:return edges,chosen,right,stats
 # Greedy first, then exact augmenting paths in linear/partition matroid intersection.
 for e,(g,u,i)in enumerate(edges):
  if u not in right and can(e):chosen.add(e);right[u]=e;blocks[g]['selected'].add(e)
 while True:
  prev={};queue=deque()
  for e,(g,u,i)in enumerate(edges):
   if e not in chosen and can(e):prev[e]=None;queue.append(e)
  end=None
  while queue:
   e=queue.popleft();g,u,i=edges[e]
   if u not in right:end=e;break
   f=right[u];fg=edges[f][0]
   if f in prev:continue
   prev[f]=e
   for z in byblock[fg]:
    if z not in chosen and z not in prev and can(z,f):prev[z]=f;queue.append(z)
  if end is None:break
  path=[]
  while end is not None:path.append(end);end=prev[end]
  for e in path:
   g,u,i=edges[e]
   if e in chosen:chosen.remove(e);blocks[g]['selected'].remove(e);del right[u]
  for e in path:
   if e not in chosen and e not in path[1::2]:
    g,u,i=edges[e];chosen.add(e);blocks[g]['selected'].add(e);assert u not in right;right[u]=e
  stats['augmentations']+=1
  if stats['augmentations']%100==0:print('augment',stats['augmentations'],len(chosen),flush=True,file=sys.stderr)
 for g,b in enumerate(blocks):assert len(basis(b['outbasis']+[1<<edges[e][2]for e in b['selected']]))==len(b['outbasis'])+len(b['selected'])
 return edges,chosen,right,stats

def compile_(h,matching=True,reclaim=False,dirty=True):
 t0=time.time();c,blocks,uses,value_uses,owner,signal,order,contains=build(h);v=len(c.inputs)
 print('built',h,len(blocks),'regions',flush=True,file=sys.stderr)
 edges,chosen,right,stats=match(blocks,uses,matching)
 print('matched',len(chosen),'seconds',time.time()-t0,flush=True,file=sys.stderr)
 slots=[];frames=[];ops=[];events=[];hist=Counter();assign={};sources={};retired=set();stats['regions']=len(blocks);stats['matched']=len(chosen);stats['multi_node_regions']=sum(len(b['nodes'])>1 for b in blocks)
 def new(g):
  s=len(slots);slots.append(0);frames.append(g);hist[blocks[g]['rank']]+=1;events.append((s,-1,g));return s
 def raise_(s,g):
  old=frames[s];assert contains(blocks[old]['frame'],blocks[g]['frame']);hist[blocks[g]['rank']-blocks[old]['rank']]+=1;frames[s]=g;events.append((s,old,g))
 def xor(a,b,g):
  assert a!=b;raise_(a,g);raise_(b,g);slots[a]^=slots[b];ops.append((a,b,g))
 def acquire(g,anchors):
  if reclaim:
   bb={}
   def ins(s):
    row=slots[s];expr=1<<s
    while row:
     p=row.bit_length()-1
     if p not in bb:bb[p]=(row,expr);return None
     old,e=bb[p];row^=old;expr^=e
    return expr
   for s in anchors:ins(s)
   for s in sorted(retired,key=lambda s:(-blocks[frames[s]]['rank'],s)):
    if not contains(blocks[frames[s]]['frame'],blocks[g]['frame']):continue
    e=ins(s)
    if e is None:continue
    assert e>>s&1;e^=1<<s;aa=[]
    while e:
     bit=e&-e;aa.append(bit.bit_length()-1);e^=bit
    for a in aa:xor(s,a,g)
    assert not slots[s];retired.remove(s);stats['reclaimed']+=1;stats['clearing_xors']+=len(aa);return s
  return new(g)
 for step,g in enumerate(order):
  b=blocks[g];outuses=[u for u in b['uses']if u not in right];outvalues=sorted({uses[u][0]for u in outuses});assert outvalues==b['outvalues']
  if b['source']:
   x=b['nodes'][0];s=new(g);sources[x-1]=s;slots[s]=signal[x];value_slots={x:s};spare=[]
  else:
   ins=[assign[next(u for u in value_uses[y]if uses[u][1]==g and uses[u][2]is None)]for y in b['inputs']]
   assert len(set(ins))==len(ins)
   for s,y in zip(ins,b['inputs']):assert slots[s]==signal[y];raise_(s,g)
   # Independent desired output rows first, then preserved input signals,
   # then standard-unit completion. Every row is a literal linear form
   # on incoming physical roles, hence invertible on all dirty inputs.
   rows=[];labels=[];echelon=[]
   for x in outvalues:
    r=b['coeff'][x]
    if independent(echelon,r):rows.append(r);labels.append(('value',x));echelon=basis(rows)
   output_rank=len(rows)
   for e in sorted(b['selected']):
    _,u,i=edges[e];r=1<<i;assert independent(echelon,r);rows.append(r);labels.append(('carry',u));echelon=basis(rows)
   for i in range(len(ins)):
    if independent(echelon,1<<i):rows.append(1<<i);labels.append(('retire',i));echelon=basis(rows)
   assert len(rows)==len(ins)
   rr=rows.copy();elim=[]
   for i in range(len(ins)):
    j=next(j for j in range(i,len(ins))if rr[j]>>i&1)
    if j!=i:
     # Synthesize swap as three XORs at the single common frame.
     for a,z in ((i,j),(j,i),(i,j)):rr[a]^=rr[z];elim.append((a,z))
    for j in range(len(ins)):
     if j!=i and rr[j]>>i&1:rr[j]^=rr[i];elim.append((j,i))
   assert rr==[1<<i for i in range(len(ins))]
   for a,z in reversed(elim):xor(ins[a],ins[z],g)
   value_slots={};spare=[]
   for s,(kind,key)in zip(ins,labels):
    if kind=='value':value_slots[key]=s;assert slots[s]==signal[key]
    elif kind=='carry':assign[key]=s;assert slots[s]==signal[uses[key][0]]
    else:retired.add(s);spare.append(s)
   # Express every dependent desired output in the new independent basis.
   ob=list(value_slots);bb={}
   for i,x in enumerate(ob):
    r=b['coeff'][x];e=1<<i
    while r:
     p=r.bit_length()-1
     if p not in bb:bb[p]=(r,e);break
     old,ee=bb[p];r^=old;e^=ee
   for x in outvalues:
    if x in value_slots:continue
    r=b['coeff'][x];e=0
    while r:p=r.bit_length()-1;old,ee=bb[p];r^=old;e^=ee
    s=acquire(g,list(value_slots.values()))
    for i,y in enumerate(ob):
     if e>>i&1:xor(s,value_slots[y],g)
    assert slots[s]==signal[x];value_slots[x]=s
  used=set()
  for u in outuses:
   x=uses[u][0];s=value_slots[x]
   if x in used:
    ss=acquire(g,list(value_slots.values()));xor(ss,s,g);s=ss
   used.add(x);assert u not in assign;assign[u]=s
  if step%5000==0:print('compile',h,step,len(slots),'reclaimed',stats['reclaimed'],'seconds',time.time()-t0,flush=True,file=sys.stderr)
 output_slots=[];output_records=[];scatter=[0]*v;J=[]
 for u,(x,g,target)in enumerate(uses):
  if target is None:continue
  s=assign[u];assert slots[s]==signal[x];raise_(s,g);output_slots.append(s)
  common,triple=target;output_records.append((s,g,common,triple))
  targets=[i for i,t in enumerate(c.inputs)if common in t]if len(triple)==1 else[c.inputs.index(triple)]
  for i in targets:scatter[i]^=slots[s];J.append((v+i,2*v+s))
  rank=blocks[g]['rank']
  if len(triple)==1:hist[rank]+=1;hist[h-rank]+=1
  else:hist[h-1-rank]+=1;hist[1]+=1
 assert len(set(output_slots))==len(output_slots)
 for s in retired:hist[h-blocks[frames[s]]['rank']]+=1
 assert len(retired)+len(output_slots)==len(slots)
 assert scatter==[1<<i for i in range(v)]
 R=len(slots);mass=sum(k*v for k,v in hist.items());assert mass==h*R+h*(h-1),(mass,R)
 if dirty:
  initial=[1<<i for i in range(2*v+R)];M=[(2*v+a,2*v+b)for a,b,g in ops];V=[(2*v+s,i)for i,s in sources.items()];word=M+J+M[::-1]+V+M+J+M[::-1]+V
  for dual in (False,True):
   values=initial.copy()
   for a,b in reversed(word)if dual else word:
    if dual:a,b=b,a
    values[a]^=values[b]
   assert values[2*v:]==initial[2*v:]
   if dual:assert values[:v]==[initial[i]^initial[v+i]for i in range(v)]and values[v:2*v]==initial[v:2*v]
   else:assert values[v:2*v]==[initial[i]^initial[v+i]for i in range(v)]and values[:v]==initial[:v]
 return dict(h=h,mode=dict(matching=matching,reclaim=reclaim),roles=R,baseline_pr48_roles={23:36432,25:48329}[h],histogram=dict(hist),rank_mass=mass,elementary_xors=len(ops),stats=dict(stats),dirty_basis_vectors=2*v+R,complete_dirty_basis_both_orientations=dirty,all_physical_frame_inclusions=True,seconds=time.time()-t0),dict(h=h,v=v,R=R,ops=ops,sources=sources,scatter=J,outputs=output_records,frames=[b['frame']for b in blocks],events=events)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--h',type=int,default=23);p.add_argument('--no-match',action='store_true');p.add_argument('--reclaim',action='store_true');p.add_argument('--output',type=Path,required=True);p.add_argument('--word',type=Path);a=p.parse_args();result,word=compile_(a.h,not a.no_match,a.reclaim);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
 if a.word:
  import gzip
  raw=(json.dumps(word,separators=(',',':'))+'\n').encode()
  if a.word.suffix=='.gz':
   with a.word.open('wb') as stream:
    with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0) as archive:archive.write(raw)
  else:a.word.write_bytes(raw)
