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
compile_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='compile_');body=compile_node.body
start=next(i for i,n in enumerate(body) if isinstance(n,ast.FunctionDef) and n.name=='carry_price')
end=next(i for i,n in enumerate(body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='lookup' for t in n.targets))
helpernodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('basis','independent','match')]
helpers={'Counter':Counter}
from collections import deque
helpers['deque']=deque;helpers['sys']=types.SimpleNamespace(stderr=io.StringIO())
exec(compile(ast.Module(body=helpernodes,type_ignores=[]),str(SOURCE),'exec'),helpers)
basis=helpers['basis'];independent=helpers['independent']
price_node=body[start]
price_calls=[]
def entropy(a,b):price_calls.append((a,b));return 100*a+b
price_env=dict(blocks=[{'inputs':[7]}],owner={7:1},uses=[(7,2,None)],profile_entropy=entropy)
exec(compile(ast.Module(body=[price_node],type_ignores=[]),str(SOURCE),'exec'),price_env)
price=price_env['carry_price']((0,0,0))
check(price_calls==[(2,4),(2,1),(0,3),(3,4)],'Carry price endpoint calls differ')
check(price==-(204)+201+3+304,'Carry price exact integer expression differs')
class Instrument(ast.NodeTransformer):
 def visit_AugAssign(self,node):
  if isinstance(node.target,ast.Name) and node.target.id=='changes':
   return [node,ast.Expr(value=ast.Call(func=ast.Name(id='audit_exchange',ctx=ast.Load()),args=[ast.Name(id='e',ctx=ast.Load()),ast.Name(id='f',ctx=ast.Load())],keywords=[]))]
  return node
# The price array is supplied by fixtures. The exact price function was checked separately.
exchange_nodes=deepcopy(body[start+2:end])
exchange_tree=Instrument().visit(ast.Module(body=exchange_nodes,type_ignores=[]));ast.fix_missing_locations(exchange_tree)
exchange_code=compile(exchange_tree,str(SOURCE)+':instrumented','exec')

counts=Counter();total_exchanges=0

def run_case(blocks,edges,chosen,prices,expected=None):
 global total_exchanges
 blocks=deepcopy(blocks);chosen=set(chosen);right={edges[e][1]:e for e in chosen}
 for b in blocks:b['selected']=set()
 for e in chosen:blocks[edges[e][0]]['selected'].add(e)
 initial=len(chosen);previous=sum(prices[e] for e in chosen);observed=[]
 def invariant():
  check(len(chosen)==len(right)==initial,'Exchange changed cardinality')
  check(right=={edges[e][1]:e for e in chosen} and len({edges[e][1] for e in chosen})==initial,'Exchange broke unique future-use partition')
  check(chosen==set().union(*(b['selected'] for b in blocks)),'Chosen/block selections inconsistent')
  for g,b in enumerate(blocks):
   check(all(edges[e][0]==g for e in b['selected']),'Selected edge stored in wrong region')
   rows=b['outbasis']+[1<<edges[e][2] for e in b['selected']]
   check(len(basis(rows))==len(rows),'Exchange broke output/carrier linear independence')
 def audit_exchange(e,f):
  nonlocal previous
  check(prices[e]<prices[f],'Exchange does not strictly improve fixed integer price')
  invariant();current=sum(prices[x] for x in chosen)
  check(current==previous+prices[e]-prices[f] and current<previous,'Exchange price accounting differs')
  previous=current;observed.append((e,f))
 invariant()
 env=dict(blocks=blocks,edges=edges,chosen=chosen,right=right,prices=prices,stats=Counter(),basis=basis,independent=independent,audit_exchange=audit_exchange,sys=types.SimpleNamespace(stderr=io.StringIO()))
 exec(exchange_code,env)
 invariant();check(env['stats']['carry_exchanges']==len(observed),'Exchange count differs')
 if expected is not None:check(len(observed)==expected,'Targeted exchange path did not behave as expected')
 for e,f in observed:counts['same_region' if edges[e][0]==edges[f][0] else 'different_region']+=1;counts['same_future_use' if edges[e][1]==edges[f][1] else 'new_future_use']+=1
 total_exchanges+=len(observed)
 return observed

B=lambda n,rows=[]:dict(outbasis=list(rows),selected=set(),candidates=[],width=n)
run_case([B(2)],[(0,0,0),(0,0,1)],{0},[10,0],1)
run_case([B(2),B(2)],[(0,0,0),(1,0,1)],{0},[10,0],1)
run_case([B(2)],[(0,0,0),(0,1,1)],{0},[10,0],1)
run_case([B(2,[1])],[(0,0,1),(0,0,0)],{0},[10,0],0)
run_case([B(2)],[(0,0,0),(0,1,1)],{0},[10,10],0)
rng=Random(71082026);cases=0
for trial in range(800):
 blocks=[];nuses=rng.randrange(2,12)
 for g in range(rng.randrange(1,5)):
  n=rng.randrange(1,6);rows=[]
  for _ in range(rng.randrange(n+1)*2):
   vec=rng.randrange(1,1<<n)
   if independent(basis(rows),vec):rows.append(vec)
  candidates=sorted({(rng.randrange(nuses),rng.randrange(n)) for _ in range(rng.randrange(1,20))})
  blocks.append(dict(outbasis=rows,candidates=candidates,selected=set(),width=n))
 edges,chosen,right,stats=helpers['match'](blocks,None,True)
 prices=[rng.randrange(-500,501) for _ in edges]
 run_case(blocks,edges,chosen,prices);cases+=1
receipt=dict(status='PASS actual bounded single-exchange legality',source_sha256=sha256(SOURCE.read_bytes()).hexdigest(),random_matroid_cases=cases,targeted_cases=5,total_exchanges_checked=total_exchanges,exercised_exchange_types=dict(counts))
(ROOT/'certificates/final-frame-exchange-validation.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt))
