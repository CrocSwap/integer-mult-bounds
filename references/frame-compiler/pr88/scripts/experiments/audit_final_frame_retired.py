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
klass=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='RetiredIndex')
space={};exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef)],type_ignores=[]),str(SOURCE),'exec'),space);Index=space['RetiredIndex']
contains=lambda f,g:not(g[0]&~f[0]) and not(f[1]&~g[1])
def valid_frames(h):
 return [(c,d) for d in range(1,1<<h) for c in range(1,d+1) if not c&~d]
def order(records,target):return sorted((s for s,(f,r) in records.items() if contains(f,target)),key=lambda s:(-records[s][1],s))
queries=mutations=0
# Every nonempty core/cover pair in three coordinates appears once at sparse role IDs.
idx=Index(3);records={}
for s,frame in enumerate(valid_frames(3)):
 role=3*s+2;rank=(s%4);idx.insert(role,frame,rank);records[role]=(frame,rank);mutations+=1
for target in valid_frames(3):
 check(list(idx.eligible(target))==order(records,target),'Exhaustive ternary-frame order differs');queries+=1
# Repeated removal, slot reuse and promotion exercise all dimensions and sparse IDs.
rng=Random(81420261008)
for h in (1,2,3,7,19,23,25,31):
 idx=Index(h);records={};full=(1<<h)-1
 def frame():
  d=rng.randrange(1,1<<h);c=rng.randrange(1,1<<h)&d
  if not c:c=d&-d
  return c,d
 for iteration in range(3000):
  if records and (len(records)>150 or rng.random()<0.48):
   s=rng.choice(list(records));f,r=records.pop(s);idx.remove(s,f,r)
  else:
   s=rng.randrange(1200)
   if s in records:continue
   f=frame();r=rng.randrange(h+1);idx.insert(s,f,r);records[s]=(f,r)
  mutations+=1
  if iteration%4==0:
   for target in (frame(),(1,full)):
    check(list(idx.eligible(target))==order(records,target),'Random exact frame/order query differs');queries+=1
  if iteration%100==0:
   check(idx.all==sum(1<<s for s in records),'Index all bitmap stale')
   for k in range(h+1):check(idx.ranks[k]==sum(1<<s for s,(f,r) in records.items() if r==k),'Rank bitmap stale')
   for k in range(h):
    check(idx.core[k]==sum(1<<s for s,(f,r) in records.items() if f[0]>>k&1),'Core bitmap stale')
    check(idx.cover[k]==sum(1<<s for s,(f,r) in records.items() if f[1]>>k&1),'Cover bitmap stale')
# The actual integrated raise function keeps already-retired controls indexed at their new frame.
compile_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='compile_')
raise_node=next(n for n in compile_node.body if isinstance(n,ast.FunctionDef) and n.name=='raise_')
blocks=[dict(frame=(3,3),rank=1),dict(frame=(1,7),rank=2),dict(frame=(1,15),rank=3)]
idx=Index(4);idx.insert(0,blocks[0]['frame'],1)
env=dict(frames=[0,0],blocks=blocks,contains=contains,retired={0},retired_index=idx,pending={},pending_index=space['PendingIndex'](4),hist=Counter(),events=[])
exec(compile(ast.Module(body=[raise_node],type_ignores=[]),str(NEW),'exec'),env)
env['raise_'](0,1)
check(list(idx.eligible(blocks[0]['frame']))==[] and list(idx.eligible(blocks[1]['frame']))==[0],'Actual retired control frame promotion not reflected')
env['raise_'](1,1)
check(idx.all==1 and env['frames']==[1,1],'Nonretired raise inserted an indexed role')
env['raise_'](0,2);idx.remove(0,blocks[2]['frame'],3)
check(idx.all==0 and not any(idx.ranks) and not any(idx.core) and not any(idx.cover),'Actual promoted role removal leaves stale bits')
receipt=dict(status='PASS actual ordered retired index and frame lifecycle',source_sha256=sha256(SOURCE.read_bytes()).hexdigest(),mutations=mutations,ordered_queries=queries,actual_raise_fixture=True)
(ROOT/'certificates/final-frame-retired-index-validation.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt))
