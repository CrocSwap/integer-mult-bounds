"""Focused actual-source audit. Chafik Boukhalfa with OpenAI Codex assistance; Apache-2.0."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from random import Random
from collections import Counter
from copy import deepcopy
import ast,gzip,json,io,types,sys
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
SOURCE=HERE/'final_frame_engine.py';NEW=SOURCE
source=SOURCE.read_text();tree=ast.parse(source)
def check(ok,why):
 if not ok:raise ValueError(why)
space={};exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef)],type_ignores=[]),str(SOURCE),'exec'),space);Pending=space['PendingIndex'];Retired=space['RetiredIndex']
contains=lambda f,g:not(g[0]&~f[0]) and not(f[1]&~g[1])
def frames(h):return [(c,d) for d in range(1,1<<h) for c in range(1,d+1) if not c&~d]
def query(records,target):return [s for s,(lower,upper) in records.items() if contains(lower,target) and contains(target,upper)]
queries=mutations=0
idx=Pending(3);records={};i=0
for f in frames(3):
 for g in frames(3):
  if contains(f,g):
   s=2*i+3;i+=1;idx.insert(s,f,g);records[s]=(f,g);mutations+=1
for target in frames(3):check(idx.eligible(target)==query(records,target),'Exhaustive pending interval query differs');queries+=1
# Random reinsertions change insertion order; frame raises must not change it.
rng=Random(202610081917)
for h in (1,2,3,7,19,23,25,31):
 idx=Pending(h);records={};mask=(1<<h)-1
 def envelope():
  d=rng.randrange(1,1<<h);c=rng.randrange(1,1<<h)&d
  return (c or (d&-d)),d
 def extend(f):
  c=rng.randrange(1,1<<h)&f[0];c=c or (f[0]&-f[0]);d=f[1]|rng.randrange(1<<h)
  return c,d
 def between(f,g):
  c=g[0]|(f[0]&rng.randrange(1<<h));d=f[1]|(g[1]&rng.randrange(1<<h));return c,d
 for iteration in range(3500):
  choice=rng.random()
  if records and (len(records)>150 or choice<.34):
   s=rng.choice(list(records));f,g=records.pop(s);idx.remove(s,f,g)
  elif records and choice<.66:
   s=rng.choice(list(records));f,g=records[s];new=between(f,g);check(contains(f,new) and contains(new,g),'Invalid random promotion')
   before_order=dict(idx.order);idx.move(s,f,new);records[s]=(new,g);check(idx.order==before_order,'Frame move changes insertion order')
  else:
   s=rng.randrange(1200)
   if s in records:continue
   f=envelope();g=extend(f);idx.insert(s,f,g);records[s]=(f,g)
  mutations+=1
  if iteration%4==0:
   for target in (envelope(),(1,mask)):
    check(idx.eligible(target)==query(records,target),'Random ordered pending query differs');queries+=1
  if iteration%100==0:
   check(idx.lower.all==sum(1<<s for s in records),'Pending active bitmap stale')
   check(sorted(records,key=idx.order.__getitem__)==list(records),'Pending serial order differs from dictionary')
   for k in range(h):
    check(idx.core[k]==sum(1<<s for s,(f,g) in records.items() if g[0]>>k&1),'Target core bitmap stale')
    check(idx.cover[k]==sum(1<<s for s,(f,g) in records.items() if g[1]>>k&1),'Target cover bitmap stale')
idx=Pending(4);idx.insert(1,(1,3),(1,5))
check(idx.lower.eligible_mask((1,7))==2 and idx.eligible((1,7))==[],'Fixture does not reject missing future containment')
# Audit the actual integrated raise_ function on passive live controls.
compile_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='compile_');raise_node=next(n for n in compile_node.body if isinstance(n,ast.FunctionDef) and n.name=='raise_')
blocks=[dict(frame=(3,3),rank=1),dict(frame=(1,7),rank=2),dict(frame=(1,15),rank=3)]
idx=Pending(4);idx.insert(0,blocks[0]['frame'],blocks[2]['frame']);idx.insert(1,blocks[0]['frame'],blocks[2]['frame'])
env=dict(frames=[0,0],blocks=blocks,contains=contains,retired=set(),retired_index=Retired(4),pending={0:2,1:2},pending_index=idx,hist=Counter(),events=[])
exec(compile(ast.Module(body=[raise_node],type_ignores=[]),str(NEW),'exec'),env);env['raise_'](0,1)
check(idx.eligible(blocks[0]['frame'])==[1] and idx.eligible(blocks[1]['frame'])==[0,1],'Actual raise changes pending selection incorrectly')
check(idx.order=={0:0,1:1},'Actual raise changes pending order')
receipt=dict(status='PASS actual ordered two-envelope pending index and frame lifecycle',source_sha256=sha256(SOURCE.read_bytes()).hexdigest(),mutations=mutations,ordered_queries=queries,actual_raise_fixture=True,future_containment_negative_fixture=True)
(ROOT/'certificates/final-frame-pending-index-validation.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt))
