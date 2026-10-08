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
tree=ast.parse(SOURCE.read_text());body=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='compile_').body
start=next(i for i,n in enumerate(body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='lookup' for t in n.targets))
end=start+3
check(isinstance(body[start+1],ast.Assert) and isinstance(body[start+2],ast.For),'Unexpected cycle block structure')
helpers={};helpernodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('basis','independent')]
exec(compile(ast.Module(body=helpernodes,type_ignores=[]),str(SOURCE),'exec'),helpers)
carry_can=next(n for n in body if isinstance(n,ast.FunctionDef) and n.name=='carry_can')
basis=helpers['basis'];independent=helpers['independent']
class Instrument(ast.NodeTransformer):
 def visit_AugAssign(self,node):
  if isinstance(node.target,ast.Name) and node.target.id=='changes':
   return [node,ast.Expr(value=ast.Call(func=ast.Name(id='audit_cycle',ctx=ast.Load()),args=[ast.Name(id=x,ctx=ast.Load()) for x in ('e','other','f','z')],keywords=[]))]
  return node
mod=Instrument().visit(ast.Module(body=[deepcopy(carry_can)]+deepcopy(body[start:end]),type_ignores=[]));ast.fix_missing_locations(mod)
code=compile(mod,str(SOURCE)+':instrumented','exec')
cycles=0;cases=0

def run(blocks,edges,chosen,prices,expected=None):
 global cycles,cases
 blocks=deepcopy(blocks);chosen=set(chosen);right={edges[e][1]:e for e in chosen};initial=len(chosen)
 for b in blocks:b['selected']=set()
 for e in chosen:blocks[edges[e][0]]['selected'].add(e)
 previous=sum(prices[e] for e in chosen);observed=[]
 def invariant():
  check(len(chosen)==len(right)==initial,'Cardinality changed')
  check(len({edges[e][1] for e in chosen})==initial and right=={edges[e][1]:e for e in chosen},'Future-use partition failed')
  check(chosen==set().union(*(b['selected'] for b in blocks)),'Selection tables inconsistent')
  for g,b in enumerate(blocks):
   check(all(edges[e][0]==g for e in b['selected']),'Wrong group assignment')
   rows=b['outbasis']+[1<<edges[e][2] for e in b['selected']]
   check(len(basis(rows))==len(rows),'Group linear independence broken')
 def audit_cycle(e,other,f,z):
  nonlocal previous
  invariant();check(len({e,other,f,z})==4,'Repeated edge in atomic cycle')
  check(edges[e][0]!=edges[other][0] and {edges[e][1],edges[other][1]}=={edges[f][1],edges[z][1]},'Not a two-group/two-use swap')
  check(e in chosen and other in chosen and f not in chosen and z not in chosen,'Atomic replacement incomplete')
  gain=prices[f]+prices[z]-prices[e]-prices[other]
  current=sum(prices[x] for x in chosen)
  check(gain>0 and current==previous-gain,'Fixed integer price does not strictly improve')
  previous=current;observed.append([e,other,f,z])
 invariant()
 env=dict(blocks=blocks,edges=edges,chosen=chosen,right=right,prices=prices,priority=sorted(range(len(edges)),key=lambda e:(prices[e],edges[e])),basis=basis,independent=independent,stats=Counter(),sys=types.SimpleNamespace(stderr=io.StringIO()),audit_cycle=audit_cycle)
 exec(code,env);invariant();check(env['stats']['carry_two_cycles']==len(observed),'Cycle count differs')
 if expected is not None:check(len(observed)==expected,'Targeted cycle outcome differs')
 cycles+=len(observed);cases+=1
 return observed

# Each group is full (one outbasis row + one carrier). Neither cross-group
# single addition is independent, but simultaneous replacement is legal.
blocks=[{'outbasis':[3]},{'outbasis':[3]}]
edges=[(1,0,0),(0,1,0),(0,0,1),(1,1,1)]
run(blocks,edges,{0,1},[10,10,9,9],1)
run(blocks,edges,{0,1},[10,10,10,10],0)
# With the receiving group's unit vector already in its output span, reject.
run([{'outbasis':[2]},{'outbasis':[3]}],edges,{0,1},[10,10,9,9],0)
# Missing the complementary future-use edge also rejects.
run(blocks,edges[:3],{0,1},[10,10,9],0)
# Duplicate group/use lookup keys are explicitly rejected before iteration.
try:run(blocks,edges+[(0,0,0)],{0,1},[10,10,9,9,1])
except AssertionError:duplicate_rejected=True
else:raise ValueError('Ambiguous group/use candidate key accepted')
rng=Random(231025)
for trial in range(1200):
 ng=rng.randrange(2,6);nuses=rng.randrange(2,14);blocks=[];edges=[]
 for g in range(ng):
  width=rng.randrange(2,6);rows=[]
  for _ in range(rng.randrange(width)*2):
   v=rng.randrange(1,1<<width)
   if independent(basis(rows),v):rows.append(v)
  blocks.append({'outbasis':rows})
  for u in rng.sample(range(nuses),rng.randrange(1,nuses+1)):edges.append((g,u,rng.randrange(width)))
 chosen=set();used=set();selected=[[] for _ in blocks]
 order=list(range(len(edges)));rng.shuffle(order)
 for e in order:
  g,u,i=edges[e]
  if u not in used and independent(basis(blocks[g]['outbasis']+[1<<j for j in selected[g]]),1<<i):chosen.add(e);used.add(u);selected[g].append(i)
 run(blocks,edges,chosen,[rng.randrange(-500,501) for _ in edges])
receipt=dict(status='PASS actual atomic two-cycle legality and adverse fixtures',source_sha256=sha256(SOURCE.read_bytes()).hexdigest(),cases=cases,accepted_cycles_checked=cycles,duplicate_group_use_key_rejected=duplicate_rejected)
(ROOT/'certificates/final-frame-two-cycle-validation.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt))
