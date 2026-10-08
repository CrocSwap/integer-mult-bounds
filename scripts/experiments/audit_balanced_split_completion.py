"""Focused strategy audit by Chafik Boukhalfa with OpenAI Codex assistance. Apache-2.0."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from random import Random
import ast,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
import sys
if sys.flags.optimize: raise ValueError('Assertions must remain enabled')
SOURCE=HERE/'balanced_split_engine.py';OLD=HERE/'split_pair_engine.py'
def check(ok,why):
 if not ok:raise ValueError(why)
s=SOURCE.read_text();old=OLD.read_text()
changed_start='t0=time.time();c,blocks,uses,value_uses,owner,signal,order,contains=build(h);v=len(c.inputs);position={g:i for i,g in enumerate(order)}'
old_start=changed_start.split(';position=')[0]
completion='''   def future_priority(i):
    compatible=sum(position[uses[u][1]]>step and contains(b['frame'],blocks[uses[u][1]]['frame']) for u in value_uses[b['inputs'][i]])
    return (-compatible,slots[ins[i]].bit_count(),i)
   for i in sorted(range(len(ins)),key=future_priority):'''
check(s.count(completion)==1 and s.count(changed_start)==1,'Changed source not uniquely recognized')
check(s.replace(changed_start,old_start).replace(completion,'   for i in range(len(ins)):')==old,'Compiler changed beyond the claimed unit-completion priority')
tree=ast.parse(s)
helpers=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('basis','independent')]
namespace={};exec(compile(ast.Module(body=helpers,type_ignores=[]),str(SOURCE),'exec'),namespace)
basis=namespace['basis'];independent=namespace['independent']
future=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='future_priority')
contains=lambda a,b:not(b[0]&~a[0]) and not(a[1]&~b[1])
# Actual-use fixtures distinguish future compatible uses from backward or nonnested uses.
ns=dict(position={0:0,1:1,2:2,3:3},step=1,b={'frame':(1,3),'inputs':[10,11,12,13]},blocks=[{'frame':(1,3)},{'frame':(1,3)},{'frame':(1,7)},{'frame':(1,5)}],uses=[(10,2,None),(10,2,('terminal',)),(11,2,None),(11,0,None),(12,3,None),(13,3,None)],value_uses={10:[0,1],11:[2,3],12:[4],13:[5]},contains=contains,slots=[7,1,3,3],ins=[0,1,2,3])
exec(compile(ast.Module(body=[future],type_ignores=[]),str(SOURCE),'exec'),ns)
check([ns['future_priority'](i) for i in range(4)]==[(-2,3,0),(-1,1,1),(0,2,2),(0,2,3)],'Priority does not use compatible actual future uses, symbolic support, index')
check(sorted(range(4),key=ns['future_priority'])==[0,1,2,3],'Priority is not deterministic')
# General span argument is below; these adversarial numerical fixtures check the actual helpers and literal synthesis.
rng=Random(20261008);cases=0;operations=0
for n in range(1,10):
 for trial in range(250):
  rows=[]
  for _ in range(rng.randrange(n+1)*3):
   candidate=rng.randrange(1,1<<n)
   if independent(basis(rows),candidate):rows.append(candidate)
  prefix=rows[:];order=list(range(n));rng.shuffle(order)
  for i in order:
   if independent(basis(rows),1<<i):rows.append(1<<i)
  check(len(rows)==n and len(basis(rows))==n and rows[:len(prefix)]==prefix,'Unit completion destroyed independence or retained rows')
  rr=rows[:];ops=[]
  for i in range(n):
   j=next(j for j in range(i,n) if rr[j]>>i&1)
   if j!=i:
    for a,z in ((i,j),(j,i),(i,j)):rr[a]^=rr[z];ops.append((a,z))
   for j in range(n):
    if j!=i and rr[j]>>i&1:rr[j]^=rr[i];ops.append((j,i))
  check(rr==[1<<i for i in range(n)],'Completion elimination not invertible')
  actual=[1<<i for i in range(n)]
  for a,z in reversed(ops):
   check(a!=z,'self XOR in synthesis');actual[a]^=actual[z]
  check(actual==rows,'Literal reversed elimination does not synthesize chosen basis')
  cases+=1;operations+=len(ops)
receipt=dict(status='PASS future-completion source delta, actual-use priority and invertible unit-basis extension',source_sha256=sha256(SOURCE.read_bytes()).hexdigest(),baseline_source_sha256=sha256(OLD.read_bytes()).hexdigest(),tested_independent_completions=cases,tested_literal_xors=operations,priority_fixture='Compatible future use count first, fixed symbolic support popcount second, input index last. Backward and nonnested uses excluded.',proof=['The desired output rows followed by selected carry rows are independent by the unchanged checks. Scanning every standard unit vector in any order and retaining it only when independent must extend that fixed prefix to a basis of the whole input-role space: otherwise all standard units would belong to a proper final span, a contradiction.','The new priority produces a permutation of precisely those same input indices; it never alters the already selected output/carrier rows and changes only the independent completion rows labelled retired. Rank and full-basis checks remain mandatory.','Gaussian elimination and its reversed literal XOR synthesis are unchanged. A square full-rank binary basis is invertible on arbitrary inputs, including dirty roles. Physical frame and clearing charges are still determined by the regenerated actual word.','Future-use counts are computed from fixed graph incidence and order. Popcounts use fixed symbolic linear signals already checked against graph values, not runtime input values. The word remains input-independent.','Matching, pending lifecycles, the two pending-frame containment checks, and next-use profile costs are byte-identical to the frozen compiler. Their prior legality argument applies unchanged.'],scope='Checks only our new completion strategy and composed finite witnesses. No mathematical optimality or all-size transfer claim.')
(ROOT/'certificates/balanced-split-completion-validation.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt,indent=2))
