"""Audit the actual coordinate-pricing writer and whole-engine delta. Apache-2.0."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from itertools import combinations
from random import Random
import ast,io,json,struct,sys
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
ROOT=Path(__file__).resolve().parents[2]
def check(ok,why):
 if not ok:raise ValueError(why)
# At source level, restore only the oracle writer and remove the audited helper/call.
engine=ast.parse((ROOT/'scripts/experiments/aligned_composition_engine.py').read_text());base=ast.parse((ROOT/'references/frame-compiler/indexed-r5/scripts/experiments/compiler.py').read_text());new_compile=next(n for n in engine.body if isinstance(n,ast.FunctionDef) and n.name=='compile_');base_compile=next(n for n in base.body if isinstance(n,ast.FunctionDef) and n.name=='compile_')
writer=next(n for n in new_compile.body if isinstance(n,ast.With) and 'oracle_input.open' in ast.unparse(n.items[0].context_expr));base_writer=next(n for n in base_compile.body if isinstance(n,ast.With) and 'oracle_input.open' in ast.unparse(n.items[0].context_expr))
trim=deepcopy(engine);trim.body=[n for n in trim.body if not(isinstance(n,ast.FunctionDef) and n.name=='improve_three_cycles')];fn=next(n for n in trim.body if isinstance(n,ast.FunctionDef) and n.name=='compile_');fn.body=[deepcopy(base_writer) if isinstance(n,ast.With) and 'oracle_input.open' in ast.unparse(n.items[0].context_expr) else n for n in fn.body];fn.body=[n for n in fn.body if not(isinstance(n,ast.For) and 'THREE_CYCLE_PASSES' in ast.unparse(n.iter))];check(ast.dump(trim,include_attributes=False)==ast.dump(base,include_attributes=False),'Whole engine changes exceed pricing writer plus cleared three-cycle helper/call')
# Exercise the ACTUAL binary oracle writer in memory. The block objects must stay
# untouched; only serialized core/cover masks are conjugated, while IDs/ranks stay.
class Capture:
 def __init__(self):self.stream=None;self.bytes=None
 def open(self,mode):check(mode=='wb','Unexpected oracle file mode');self.stream=io.BytesIO();return self
 def __enter__(self):return self.stream
 def __exit__(self,*args):self.bytes=self.stream.getvalue();return False
writer_code=compile(ast.Module(body=[deepcopy(writer)],type_ignores=[]),'actual_coordinate_oracle_writer','exec');base_code=compile(ast.Module(body=[deepcopy(base_writer)],type_ignores=[]),'original_oracle_writer','exec')
rng=Random(202610092046);writer_cases=0
for h in (3,5,23,25):
 for trial in range(100):
  blocks=[]
  for _ in range(rng.randrange(1,30)):
   cover=rng.randrange(1,1<<h);core=(rng.randrange(1,1<<h)&cover) or (cover&-cover);blocks.append(dict(frame=(core,cover),rank=cover.bit_count()-core.bit_count()))
  unchanged=deepcopy(blocks);perm=list(range(h));rng.shuffle(perm);v=len(list(combinations(range(h),3)))
  capture=Capture();env=dict(h=h,v=v,blocks=blocks,oracle_input=capture,struct=struct,ORACLE_COORDINATES=perm);exec(writer_code,env)
  expected_bytes=struct.pack('<6I2Q',h,v,0,len(blocks)+2,0,0,h*(h-1),h*(h-1))+struct.pack('<2QI',0,0,0)+struct.pack('<2QI',0,0,h)
  for b in blocks:
   mapped=tuple(sum((1<<perm[i]) for i in range(h) if mask&(1<<i)) for mask in b['frame']);check(mapped[0]&~mapped[1]==0 and mapped[1].bit_count()-mapped[0].bit_count()==b['rank'],'Conjugation changes containment/rank');expected_bytes+=struct.pack('<2QI',*mapped,b['rank'])
  check(capture.bytes==expected_bytes and blocks==unchanged,'Oracle writer changed block legality state or serialized wrong masks')
  identity=Capture();env['oracle_input']=identity;env['ORACLE_COORDINATES']=list(range(h));exec(writer_code,env);original=Capture();env['oracle_input']=original;exec(base_code,env);check(identity.bytes==original.bytes,'Pricing-off identity differs from original writer');writer_cases+=1
capture=Capture();env=dict(h=3,v=1,blocks=[dict(frame=(1,7),rank=2)],oracle_input=capture,struct=struct,ORACLE_COORDINATES=[0,1,1])
try:exec(writer_code,env)
except AssertionError:pass
else:raise ValueError('Invalid oracle coordinate map accepted')

receipt={'status':'PASS actual coordinate-aware oracle writer and whole engine delta','source_sha256':sha256((ROOT/'scripts/experiments/aligned_composition_engine.py').read_bytes()).hexdigest(),'writer_cases':writer_cases,'identity_writer_byte_exact':True,'invalid_permutation_rejected':True,'in_memory_legality_unchanged':True}
(ROOT/'certificates/aligned-composition-pricing-validation.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt))
