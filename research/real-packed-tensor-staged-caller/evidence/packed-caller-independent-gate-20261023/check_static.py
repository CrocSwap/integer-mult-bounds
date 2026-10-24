#!/usr/bin/env python3
"""Source/AST-only independent gate. Never imports cohort or numerical code."""
import ast
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
AUTHOR=HERE.parent/'real-packed-outer-consumer-20261023'
ROOT=AUTHOR/'staged-source'
PKG=ROOT/'research/physical-tensor-crt-sandwich-recovery'

def digest(path):return sha256(path.read_bytes()).hexdigest()
def dump(node):return ast.dump(node,include_attributes=False)
def cls(tree):return next(x for x in tree.body if isinstance(x,ast.ClassDef))
def methods(tree):return {x.name:x for x in cls(tree).body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef))}

source=AUTHOR/'SOURCE-sandwich.py';draft=AUTHOR/'packed_sandwich_DRAFT.py'
assert digest(source)=='1d45e8deed1b138fcd9800cc563b8cd894cbd2d072033ba23215566d299a4325'
assert digest(draft)=='5dfcdfe63d9d03a89a00dd92e681ab0a0efc5bbc86aa7edae58f007baf752483'
assert source.read_bytes()==(PKG/'sandwich.py').read_bytes()
st,dt=ast.parse(source.read_text()),ast.parse(draft.read_text())
sm,dm=methods(st),methods(dt)
unchanged=[name for name in sm if dump(sm[name])==dump(dm[name])]
assert set(unchanged)=={'__init__','consume','child','ingress','recover','carries','admit'}
sg=next(x for x in st.body if isinstance(x,ast.FunctionDef) and x.name=='private_tapes')
dg=next(x for x in dt.body if isinstance(x,ast.FunctionDef) and x.name=='private_tapes')
assert dump(sg)==dump(dg)
def imports(tree):
 return {(getattr(x,'module',None),n.name,n.asname) for x in tree.body if isinstance(x,(ast.Import,ast.ImportFrom)) for n in x.names}
assert imports(st)<=imports(dt)
assert imports(dt)-imports(st)=={('compact_counts','copy_bits',None),('ring_words','add',None),('ring_words','difference',None)}
sr,dr=sm['run'],dm['run']
assert dump(sr.args)==dump(dr.args)
sto=next(x for x in sr.body if isinstance(x,ast.Try));dto=next(x for x in dr.body if isinstance(x,ast.Try))
assert [dump(x) for x in sto.finalbody]==[dump(x) for x in dto.finalbody]
sti=sto.body[0].body[0];dti=dto.body[0].body[0]
assert isinstance(sti,ast.Try) and isinstance(dti,ast.Try)
assert [dump(x) for x in sti.finalbody]==[dump(x) for x in dti.finalbody]
assert [dump(x) for x in sr.body[-2:]]==[dump(x) for x in dr.body[-2:]]
for name in ('pack_real','move_bits','negate_frequencies','pointwise','run'):
 assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='Tape' for n in ast.walk(dm[name]))
calls=[]
for n in ast.walk(dr):
 if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='child':
  calls.append({'operation':ast.unparse(n.args[0]),'line':n.lineno,'options':{k.arg:ast.unparse(k.value) for k in n.keywords}})
assert sum(x['operation']=='self.tensor.run' for x in calls)==2
assert [x for x in calls if x['operation']=='self.tensor.run' and x['options'].get('opposite')=='True']
assert sum(x['operation']=='self.converter.run_plan' for x in calls)==2
assert [x for x in calls if x['operation']=='self.converter.run_plan' and x['options'].get('inverse')=='True']
checks=[]
for row in json.loads((PKG/'SOURCES.json').read_text())['files']:
 if row['usage']=='input':
  path=ROOT/row['path'];assert not path.is_symlink() and digest(path)==row['sha256']
  checks.append({'path':row['path'],'sha256':row['sha256'],'binding':'PR5095 declared input'})
for row in json.loads((AUTHOR/'PUBLIC-TEXT-MANIFEST.json').read_text()):
 path=ROOT/row['path'];assert not path.is_symlink() and digest(path)==row['sha256']
 checks.append({'path':row['path'],'sha256':row['sha256'],'binding':'public PR5095 file'})
fixture=PKG/'inputs/p48-5x7.bin'
assert digest(fixture)=='7dd7adbe9e8f6d5ffbecd425a72827b31d7222ee51bcd67a4148ebfd03420381'
leaf=json.loads((AUTHOR/'METHOD-LEAF-RESULT.json').read_text())
assert leaf['status']=='PASS_BOUNDED_PHYSICAL_METHOD_LEAF'
assert leaf['numerical_Tensor_calls']==leaf['numerical_Converter_calls']==0
assert leaf['all_consumed_source_and_draft_hashes_unchanged']
freeze=json.loads((AUTHOR/'FULL-PLAN-FREEZE.json').read_text())
for filename, expected in freeze['files'].items():assert digest(AUTHOR/filename)==expected
assert freeze['execution_authorized'] is False and freeze['executed'] is False
harness=AUTHOR/'run_full_packed_DRAFT.py'
ht=ast.parse(harness.read_text())
# This parses the proposed program as data; it does not execute its imports.
assert any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='run'
           and isinstance(n.func.value,ast.Name) and n.func.value.id=='machine'
           and any(k.arg=='require_recovery' and isinstance(k.value,ast.Constant) and k.value.value is False for k in n.keywords)
           for n in ast.walk(ht))
for name in ('observe_tensor','observe_converter'):
 fn=next(n for n in ast.walk(ht) if isinstance(n,ast.FunctionDef) and n.name==name)
 cleanup=next(n for n in ast.walk(fn) if isinstance(n,ast.ExceptHandler) and isinstance(n.type,ast.Name) and n.type.id=='BaseException')
 assert any(isinstance(n,ast.Call) and ast.unparse(n.func)=='returned.clear' for n in ast.walk(cleanup))
 assert any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='erase_marker' for n in ast.walk(cleanup))
assert 'FAIL_SOURCE_OR_HARNESS_DRIFT' in harness.read_text()
result={'status':'PASS_STATIC_DRAFT_AND_SOURCE_BINDING','no_numeric_execution':True,
        'source_head':'e65f47db55b9a3779fbf7fe23e93a8a4c5eb3ce1',
        'source_sha256':digest(source),'draft_sha256':digest(draft),
        'unchanged_methods':unchanged,'private_owner_graph_unchanged':True,
        'original_imports_retained':True,'new_imports':['compact_counts.copy_bits','ring_words.add','ring_words.difference'],'outer_and_inner_run_finally_unchanged':True,
        'literal_recovery_default_and_pending_return_tail_unchanged':True,
        'new_methods_and_run_allocate_no_Tape':True,'static_child_callsites':calls,
        'note':'Converter forward callsite lies in two-input loop: three total conversions. Two Tensor callsites total, latter opposite.',
        'authenticated_inputs':checks,'fixture_sha256':digest(fixture),
        'prior_method_leaf_sha256':digest(AUTHOR/'METHOD-LEAF-RESULT.json'),
        'whole_caller_harness_review_pending':False,
        'harness_sha256':digest(harness),'full_plan_sha256':digest(AUTHOR/'FULL-CALLER-PLAN.md'),
        'plan_freeze_sha256':digest(AUTHOR/'FULL-PLAN-FREEZE.json'),
        'review_scope':'Static PASS for root consideration of one separately authorized reduced whole-call fixture; no numerical execution permission.',
        'numeric_Tensor_calls_authorized_by_reviewer':0}
(HERE/'STATIC-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'],len(checks),'manifest file checks; no cohort imports')
