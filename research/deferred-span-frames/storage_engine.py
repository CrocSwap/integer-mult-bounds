# Bounded carry exchanges adapted from Alejandro Zarzuelo Urdiales PR70.
# Exact integer entropy discovery scores replace floating moment prices.
# Composition of PR67 profile-cost reclamation and PR68 pending live controls.
# Next-use transition scoring added by Chafik Boukhalfa with OpenAI Codex assistance.
# All-rank profile-cost selection: Rohan Arun, with OpenAI Codex assistance.
# Derived from Dominik Scholz PR63, Chafik Boukhalfa PR60, Avi Eisenberg PR62
# and eumemic PR57. Apache-2.0; all inherited notices remain applicable.
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

class RetiredIndex:
 """Exact bitset index for active retired roles and their current envelopes."""
 def __init__(self,h):
  self.h=h;self.all=0;self.core=[0]*h;self.cover=[0]*h;self.ranks=[0]*(h+1)
 def insert(self,s,frame,rank):
  bit=1<<s;assert not self.all&bit;self.all|=bit;self.ranks[rank]|=bit
  for arr,mask in ((self.core,frame[0]),(self.cover,frame[1])):
   while mask:
    low=mask&-mask;arr[low.bit_length()-1]|=bit;mask^=low
 def remove(self,s,frame,rank):
  bit=1<<s;assert self.all&bit;self.all^=bit;self.ranks[rank]^=bit
  for arr,mask in ((self.core,frame[0]),(self.cover,frame[1])):
   while mask:
    low=mask&-mask;arr[low.bit_length()-1]^=bit;mask^=low
 def eligible_mask(self,frame):
  eligible=self.all;core=frame[0];outside=((1<<self.h)-1)^frame[1]
  while core and eligible:
   low=core&-core;eligible&=self.core[low.bit_length()-1];core^=low
  while outside and eligible:
   low=outside&-outside;eligible&=~self.cover[low.bit_length()-1];outside^=low
  return eligible
 def eligible(self,frame):
  eligible=self.eligible_mask(frame)
  for rank in range(self.h,-1,-1):
   members=eligible&self.ranks[rank]
   while members:
    low=members&-members;yield low.bit_length()-1;members^=low

class PendingIndex:
 """Two-envelope bitset queries preserving dictionary insertion order."""
 def __init__(self,h):
  self.h=h;self.lower=RetiredIndex(h);self.core=[0]*h;self.cover=[0]*h;self.order={};self.serial=0
 def insert(self,s,source,target):
  self.lower.insert(s,source,0);assert s not in self.order;self.order[s]=self.serial;self.serial+=1;bit=1<<s
  for arr,mask in ((self.core,target[0]),(self.cover,target[1])):
   while mask:
    low=mask&-mask;arr[low.bit_length()-1]|=bit;mask^=low
 def remove(self,s,source,target):
  self.lower.remove(s,source,0);del self.order[s];bit=1<<s
  for arr,mask in ((self.core,target[0]),(self.cover,target[1])):
   while mask:
    low=mask&-mask;arr[low.bit_length()-1]^=bit;mask^=low
 def move(self,s,old,new):
  self.lower.remove(s,old,0);self.lower.insert(s,new,0)
 def eligible(self,frame):
  eligible=self.lower.eligible_mask(frame);outside=((1<<self.h)-1)^frame[0];cover=frame[1]
  while outside and eligible:
   low=outside&-outside;eligible&=~self.core[low.bit_length()-1];outside^=low
  while cover and eligible:
   low=cover&-cover;eligible&=self.cover[low.bit_length()-1];cover^=low
  result=[]
  while eligible:
   low=eligible&-eligible;result.append(low.bit_length()-1);eligible^=low
  return sorted(result,key=self.order.__getitem__)

def compile_(h,matching=True,reclaim=False,dirty=True):
 t0=time.time();c,blocks,uses,value_uses,owner,signal,order,contains=build(h);v=len(c.inputs);position={g:i for i,g in enumerate(order)}
 print('built',h,len(blocks),'regions',flush=True,file=sys.stderr)
 mode=globals().get('OUTPUT_MODE','baseline')
 edges,chosen,right,stats=match(blocks,uses,matching)
 print('matched',len(chosen),'seconds',time.time()-t0,flush=True,file=sys.stderr)
 slots=[];frames=[];ops=[];events=[];hist=Counter();assign={};sources={};retired=set();retired_index=RetiredIndex(h);pending={};pending_index=PendingIndex(h);pending_use={};retired_values=defaultdict(set);deferred={};stats['regions']=len(blocks);stats['matched']=len(chosen);stats['multi_node_regions']=sum(len(b['nodes'])>1 for b in blocks)
 def new(g):
  s=len(slots);slots.append(0);frames.append(g);hist[blocks[g]['rank']]+=1;events.append((s,-1,g));return s
 def raise_(s,g):
  old=frames[s];assert contains(blocks[old]['frame'],blocks[g]['frame'])
  if s in retired:
   retired_index.remove(s,blocks[old]['frame'],blocks[old]['rank']);retired_index.insert(s,blocks[g]['frame'],blocks[g]['rank'])
  if s in pending:pending_index.move(s,blocks[old]['frame'],blocks[g]['frame'])
  hist[blocks[g]['rank']-blocks[old]['rank']]+=1;frames[s]=g;events.append((s,old,g))
 def xor(a,b,g):
  assert a!=b;raise_(a,g);raise_(b,g);slots[a]^=slots[b];ops.append((a,b,g))
 import subprocess,struct
 from binary_frame_math import logs
 # Integer midpoint enclosures give a reproducible discovery score.
 # Every candidate is independently checked by the complete exact screen.
 weights=[0]+[int(t*sum(logs(t))*10**30//2) for t in range(1,h+1)]
 oracle_input=Path(ORACLE_INPUT)
 with oracle_input.open('wb') as stream:
  stream.write(struct.pack('<6I2Q',h,v,0,len(blocks)+2,0,0,h*(h-1),h*(h-1)))
  stream.write(struct.pack('<2QI',0,0,0));stream.write(struct.pack('<2QI',0,0,h))
  for b in blocks:stream.write(struct.pack('<2QI',*b['frame'],b['rank']))
 oracle=subprocess.Popen([ORACLE_EXE,str(oracle_input)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1)
 oracles.append(oracle)
 cache={}
 def profile_entropy(a,b):
  if (a,b) not in cache:
   oracle.stdin.write(f'{a} {b}\n');oracle.stdin.flush()
   answer=oracle.stdout.readline()
   assert answer, 'profile oracle failed'
   parts=list(map(int,answer.split()));assert len(parts)==h+1
   cache[a,b]=sum(n*w for n,w in zip(parts,weights))
  return cache[a,b]
 def profile_cost(a,g):
  old=frames[a]+2;target=g+2
  endpoint=pending[a]+2 if PENDING_COST and a in pending else 1
  return profile_entropy(old,endpoint)-profile_entropy(old,target)-profile_entropy(target,endpoint)
 def materialize(s,g):
  if s not in deferred:return
  controls=deferred.pop(s)
  for q in controls:
   assert pending[q]==g and pending_use[q] is None
   xor(s,q,g)
   pending_index.remove(q,blocks[frames[q]]['frame'],blocks[g]['frame'])
   del pending[q];del pending_use[q]
   retired.add(q);retired_values[slots[q]].add(q)
   retired_index.insert(q,blocks[frames[q]]['frame'],blocks[frames[q]]['rank'])
  stats['deferred_materializations']+=1
  stats['deferred_materialization_xors']+=len(controls)
 # Three deterministic improving exchanges, preserving both matroid constraints.
 def carry_price(edge):
  g,u,i=edge;producer=owner[blocks[g]['inputs'][i]];target=uses[u][1]
  return (-profile_entropy(g+2,target+2)+profile_entropy(g+2,1)
          +profile_entropy(0,producer+2)+profile_entropy(producer+2,target+2))
 prices=[carry_price(edge) for edge in edges]
 priority=sorted(range(len(edges)),key=lambda e:(prices[e],edges[e]))
 initial_count=len(chosen);initial_price=sum(prices[e] for e in chosen)
 def carry_can(e,drop=None):
  g,u,i=edges[e]
  rows=blocks[g]['outbasis']+[1<<edges[f][2] for f in blocks[g]['selected'] if f!=drop]
  return independent(basis(rows),1<<i)
 for phase in range(3):
  changes=0
  for e in priority:
   if e in chosen:continue
   g,u,i=edges[e];f=right.get(u)
   if f is not None:
    if prices[e]>=prices[f]:continue
    if not carry_can(e,f if edges[f][0]==g else None):continue
   else:
    f=next((z for z in sorted(blocks[g]['selected'],key=lambda z:(-prices[z],z)) if prices[e]<prices[z] and carry_can(e,z)),None)
    if f is None:continue
   fg,fu,fi=edges[f];chosen.remove(f);blocks[fg]['selected'].remove(f);del right[fu]
   chosen.add(e);blocks[g]['selected'].add(e);assert u not in right;right[u]=e;changes+=1
  stats['carry_exchanges']+=changes
  print('carry exchanges',phase,changes,flush=True,file=sys.stderr)
  if not changes:break
 # Bounded two-donor exchanges after single-edge local optimization.
 lookup={(g,u):e for e,(g,u,i) in enumerate(edges)}
 assert len(lookup)==len(edges)
 for phase in range(3):
  changes=0
  for e in priority:
   if e in chosen:continue
   g,u,i=edges[e];f=right.get(u)
   if f is None:continue
   fg,fu,fi=edges[f]
   if fg==g:continue
   options=[]
   for z in sorted(blocks[g]['selected']):
    zg,zu,zi=edges[z];other=lookup.get((fg,zu))
    if other is None or other in chosen:continue
    gain=prices[f]+prices[z]-prices[e]-prices[other]
    if gain>0 and carry_can(e,z) and carry_can(other,f):options.append((-gain,z,other))
   if not options:continue
   _,z,other=min(options)
   for old in (f,z):
    og,ou,oi=edges[old];chosen.remove(old);blocks[og]['selected'].remove(old);del right[ou]
   for new_edge in (e,other):
    ng,nu,ni=edges[new_edge];assert nu not in right;chosen.add(new_edge);blocks[ng]['selected'].add(new_edge);right[nu]=new_edge
   changes+=1
  stats['carry_two_cycles']+=changes
  print('carry two-cycles',phase,changes,flush=True,file=sys.stderr)
  if not changes:break
 assert len(chosen)==len(right)==initial_count
 assert sum(prices[e] for e in chosen)<=initial_price
 for b in blocks:assert len(basis(b['outbasis']+[1<<edges[e][2] for e in b['selected']]))==len(b['outbasis'])+len(b['selected'])
 # Allocation requests are determined by output rank and multiplicity;
 # source port creation is compulsory and cannot reclaim these carriers.
 acquisition_bits=0;acquisition_counts={};frame_core=[0]*h;frame_cover=[0]*h
 for future_step,future_g in enumerate(order):
  block=blocks[future_g]
  remaining=[u for u in block['uses'] if u not in right]
  distinct={uses[u][0] for u in remaining}
  count=len(remaining)-len(distinct)
  if not block['source']:count+=len(distinct)-len(block['outbasis'])
  assert count>=0
  if not count:continue
  bit=1<<future_step;acquisition_bits|=bit;acquisition_counts[future_step]=count
  for arrays,mask in ((frame_core,block['frame'][0]),(frame_cover,block['frame'][1])):
   while mask:
    low=mask&-mask;arrays[low.bit_length()-1]|=bit;mask^=low
 acquisition_superspaces={}
 def reservation_opportunities(q,target):
  frame=blocks[frames[q]]['frame']
  if frame not in acquisition_superspaces:
   eligible=acquisition_bits;outside=((1<<h)-1)^frame[0];cover=frame[1]
   while outside and eligible:
    low=outside&-outside;eligible&=~frame_core[low.bit_length()-1];outside^=low
   while cover and eligible:
    low=cover&-cover;eligible&=frame_cover[low.bit_length()-1];cover^=low
   acquisition_superspaces[frame]=eligible
  deadline=position[target]
  assert deadline>=step
  if deadline==step:return 0
  interval=(1<<deadline)-(1<<(step+1))
  possible=acquisition_superspaces[frame]&interval
  count=0
  while possible:
   low=possible&-possible;count+=acquisition_counts[low.bit_length()-1];possible^=low
  return count
 def acquire(g,anchors):
  if reclaim:
   bb={};pending_relations=[];anchor_set=set(anchors)
   def ins(s):
    row=slots[s];expr=1<<s
    while row:
     p=row.bit_length()-1
     if p not in bb:bb[p]=(row,expr);return None
     old,e=bb[p];row^=old;expr^=e
    return expr
   for s in anchors:ins(s)
   for s in pending_index.eligible(blocks[g]['frame']):
    assert contains(blocks[frames[s]]['frame'],blocks[g]['frame']) and contains(blocks[g]['frame'],blocks[pending[s]]['frame'])
    relation=ins(s);stats['live_anchor_candidates']+=1
    if relation is not None and s not in anchor_set and s not in deferred and pending_use[s] is not None:
     assert relation>>s&1;relation^=1<<s;aa=[]
     while relation:
      low=relation&-relation;aa.append(low.bit_length()-1);relation^=low
     assert aa
     pending_relations.append((s,tuple(aa)))
     stats['pending_linear_relations']+=1
     stats['pending_relations_with_multiple_controls']+=int(len(aa)>1)
   best=None
   # Inspect every eligible dependent candidate across all retired ranks.
   # Rank the actual fixed-basis growth/cleanup profiles by an integer entropy score.
   for s in retired_index.eligible(blocks[g]['frame']):
    assert contains(blocks[frames[s]]['frame'],blocks[g]['frame'])
    e=ins(s)
    if e is None:continue
    assert e>>s&1;e^=1<<s;aa=[]
    while e:
     bit=e&-e;aa.append(bit.bit_length()-1);e^=bit
    cost=sum(profile_cost(a,g) for a in [s]+aa)
    key=(cost,len(aa),s)
    if best is None or key<best[0]:best=(key,s,aa)
   if best is not None:
    _,s,aa=best
    retired_values[slots[s]].remove(s)
    for a in aa:
     if a in pending:stats['live_anchor_xors']+=1
     xor(s,a,g)
    assert not slots[s];retired_index.remove(s,blocks[frames[s]]['frame'],blocks[frames[s]]['rank']);retired.remove(s);stats['reclaimed']+=1;stats['clearing_xors']+=len(aa);return s
  if reclaim:
   best=None;witness_cache={};retired_span_cache={}
   for p,aa in pending_relations:
    target=pending[p];stats['deferred_redundant_pending']+=1
    assert slots[p]==signal[uses[pending_use[p]][0]]
    cache_key=(slots[p],target)
    if cache_key not in witness_cache:
     eligible=retired_index.eligible_mask(blocks[target]['frame'])
     witnesses=[]
     for q in sorted(retired_values.get(slots[p],())):
      if eligible>>q&1:witnesses.append((q,))
     members=eligible
     while members:
      low=members&-members;q=low.bit_length()-1;members^=low
      for r in sorted(retired_values.get(slots[p]^slots[q],())):
       if q<r and eligible>>r&1:witnesses.append((q,r))
     if target not in retired_span_cache:
      members=eligible;candidates=[]
      while members:
       low=members&-members;q=low.bit_length()-1;members^=low
       if reservation_opportunities(q,target)==0:candidates.append(q)
      candidates.sort(key=lambda q:(-blocks[frames[q]]['rank'],slots[q].bit_count(),q))
      rb={}
      for q in candidates:
       row=slots[q];expression=1<<q
       while row:
        pivot=row.bit_length()-1
        if pivot not in rb:rb[pivot]=(row,expression);break
        old,e=rb[pivot];row^=old;expression^=e
      retired_span_cache[target]=rb
      stats['retired_span_bases']+=1
      stats['retired_span_basis_carriers']+=len(candidates)
     row=slots[p];expression=0;rb=retired_span_cache[target]
     while row:
      pivot=row.bit_length()-1
      if pivot not in rb:break
      old,e=rb[pivot];row^=old;expression^=e
     if not row and expression.bit_count()>=3:
      witness=[]
      while expression:
       low=expression&-expression;witness.append(low.bit_length()-1);expression^=low
      witnesses.append(tuple(witness))
      stats['retired_span_extra_witnesses']+=1
      stats['retired_span_extra_witness_carriers']+=len(witness)
     witness_cache[cache_key]=witnesses
    for witness in witness_cache[cache_key]:
     stats['deferred_migration_candidates']+=1
     stats['witnesses_with_multiple_clearing_controls']+=int(len(aa)>1)
     opportunity=sum(reservation_opportunities(q,target) for q in witness)
     stats['reservation_opportunity_requests']+=opportunity
     if opportunity:
      stats['reservation_rejections']+=1
      continue
     stats['reservation_zero_opportunity_candidates']+=1
     assert witness and len(witness)==len(set(witness))
     row=0
     for q in witness:row^=slots[q]
     assert row==slots[p]
     score=(profile_entropy(frames[p]+2,target+2)+profile_entropy(0,g+2)
            -profile_entropy(frames[p]+2,g+2)+sum(profile_cost(a,g) for a in aa)
            +sum(profile_entropy(frames[q]+2,1)-profile_entropy(frames[q]+2,target+2) for q in witness)
            -(len(witness)-1)*profile_entropy(target+2,1))
     key=(score,len(witness),len(aa),p,witness,aa)
     if best is None or key<best[0]:best=(key,p,witness,aa,target)
   if best is not None:
    _,p,witness,aa,target=best;u=pending_use[p];q=witness[0]
    assert assign[u]==p and uses[u][1]==target and p not in aa
    row=0
    for a in aa:row^=slots[a]
    assert slots[p]==row
    assert contains(blocks[frames[p]]['frame'],blocks[g]['frame'])
    assert contains(blocks[g]['frame'],blocks[target]['frame'])
    pending_index.remove(p,blocks[frames[p]]['frame'],blocks[target]['frame'])
    del pending[p];del pending_use[p]
    for r in witness:
     assert r in retired and contains(blocks[frames[r]]['frame'],blocks[target]['frame'])
     retired_values[slots[r]].remove(r)
     retired_index.remove(r,blocks[frames[r]]['frame'],blocks[frames[r]]['rank'])
     retired.remove(r);pending[r]=target;pending_use[r]=u if r==q else None
     pending_index.insert(r,blocks[frames[r]]['frame'],blocks[target]['frame'])
    assign[u]=q
    if len(witness)>1:deferred[q]=witness[1:]
    for a in aa:
     assert contains(blocks[frames[a]]['frame'],blocks[g]['frame'])
     if a in pending:assert contains(blocks[g]['frame'],blocks[pending[a]]['frame'])
     xor(p,a,g)
     if a in pending:stats['live_anchor_xors']+=1
    assert not slots[p]
    stats['deferred_migrations']+=1;stats['clearing_xors']+=len(aa)
    stats['span_migrations_with_three_or_more_carriers']+=int(len(witness)>=3)
    stats['span_migration_reserved_carriers']+=len(witness)
    stats['linear_migration_controls']+=len(aa)
    stats['linear_migrations_with_multiple_controls']+=int(len(aa)>1)
    return p
  return new(g)
 for step,g in enumerate(order):
  b=blocks[g];outuses=[u for u in b['uses']if u not in right];outvalues=sorted({uses[u][0]for u in outuses});assert outvalues==b['outvalues']
  if mode.startswith('route-'):
   def deadline(u):return len(order)+1 if uses[u][2] is not None else position[uses[u][1]]
   outuses.sort(key=lambda u:((1 if mode=='route-early' else -1)*deadline(u),u))
  if b['source']:
   x=b['nodes'][0];s=new(g);sources[x-1]=s;slots[s]=signal[x];value_slots={x:s};spare=[]
  else:
   ins=[assign[next(u for u in value_uses[y]if uses[u][1]==g and uses[u][2]is None)]for y in b['inputs']]
   assert len(set(ins))==len(ins)
   for s in ins:materialize(s,g)
   for s in ins:
    assert pending[s]==g;pending_index.remove(s,blocks[frames[s]]['frame'],blocks[g]['frame']);del pending[s];del pending_use[s]
   for s,y in zip(ins,b['inputs']):assert slots[s]==signal[y];raise_(s,g)
   # Independent desired output rows first, then preserved input signals,
   # then standard-unit completion. Every row is a literal linear form
   # on incoming physical roles, hence invertible on all dirty inputs.
   rows=[];labels=[];echelon=[]
   basis_values=outvalues
   if mode=='basis-reverse':basis_values=outvalues[::-1]
   elif mode=='basis-fanout':basis_values=sorted(outvalues,key=lambda x:(-len(value_uses[x]),b['coeff'][x].bit_count(),x))
   elif mode=='basis-support':basis_values=sorted(outvalues,key=lambda x:(signal[x].bit_count(),-len(value_uses[x]),x))
   elif mode=='basis-sparse':basis_values=sorted(outvalues,key=lambda x:(b['coeff'][x].bit_count(),signal[x].bit_count(),x))
   for x in basis_values:
    r=b['coeff'][x]
    if independent(echelon,r):rows.append(r);labels.append(('value',x));echelon=basis(rows)
   output_rank=len(rows)
   for e in sorted(b['selected']):
    _,u,i=edges[e];r=1<<i;assert independent(echelon,r);rows.append(r);labels.append(('carry',u));echelon=basis(rows)
   def future_priority(i):
    compatible=sum(position[uses[u][1]]>step and contains(b['frame'],blocks[uses[u][1]]['frame']) for u in value_uses[b['inputs'][i]])
    return (-compatible,slots[ins[i]].bit_count(),i)
   for i in sorted(range(len(ins)),key=future_priority):
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
    elif kind=='carry':assign[key]=s;pending[s]=uses[key][1];pending_use[s]=key;pending_index.insert(s,blocks[frames[s]]['frame'],blocks[pending[s]]['frame']);assert slots[s]==signal[uses[key][0]]
    else:retired.add(s);retired_values[slots[s]].add(s);retired_index.insert(s,blocks[frames[s]]['frame'],blocks[frames[s]]['rank']);spare.append(s)
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
   used.add(x);assert u not in assign;assign[u]=s;assert s not in pending;pending[s]=uses[u][1];pending_use[s]=u;pending_index.insert(s,blocks[frames[s]]['frame'],blocks[pending[s]]['frame'])
  if step%5000==0:print('compile',h,step,len(slots),'reclaimed',stats['reclaimed'],'seconds',time.time()-t0,flush=True,file=sys.stderr)
 output_slots=[];output_records=[];scatter=[0]*v;J=[]
 for u,(x,g,target)in enumerate(uses):
  if target is None:continue
  s=assign[u];materialize(s,g);assert slots[s]==signal[x];raise_(s,g);output_slots.append(s)
  common,triple=target;output_records.append((s,g,common,triple))
  targets=[i for i,t in enumerate(c.inputs)if common in t]if len(triple)==1 else[c.inputs.index(triple)]
  for i in targets:scatter[i]^=slots[s];J.append((v+i,2*v+s))
  rank=blocks[g]['rank']
  if len(triple)==1:hist[rank]+=1;hist[h-rank]+=1
  else:hist[h-1-rank]+=1;hist[1]+=1
 assert not deferred
 assert all(u is not None for u in pending_use.values())
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
