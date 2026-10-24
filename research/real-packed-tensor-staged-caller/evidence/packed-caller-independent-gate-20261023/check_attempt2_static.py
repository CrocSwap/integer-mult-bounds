#!/usr/bin/env python3
"""Minimal read/hash/AST gate only; never imports the proposed harness."""
import ast
import difflib
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
AUTHOR=HERE.parent/'real-packed-outer-consumer-20261023'
def need(x,m):
    if not x:raise ValueError(m)
def digest(p):return sha256(p.read_bytes()).hexdigest()
def dump(n):return ast.dump(n,include_attributes=False)
old=AUTHOR/'run_full_packed_DRAFT.py'
new=AUTHOR/'run_full_packed_attempt2_DRAFT.py'
need(digest(old)=='5797e4a8bc6bb69403db119f7740abc41c590484225103120087fe46e9acd671','preserved prior harness')
need(digest(new)=='c7bb6a705f42469709995f7d8a4c29ab0c12764d744546508a443151ec0345dc','exact new static harness')
freeze=json.loads((AUTHOR/'FULL-ATTEMPT2-STATIC-FREEZE.json').read_text())
need(not freeze['executed'] and not freeze['execution_authorized'],'no attempt2 execution authorization in proposal')
for name,h in freeze['files'].items():need(digest(AUTHOR/name)==h,'new proposal binding '+name)
backup=json.loads((AUTHOR/'full-attempt1-frozen/SHA256SUMS.json').read_text())
for name,h in backup.items():
    need(digest(AUTHOR/name)==h,'original attempt1 artifact preserved '+name)
    need(digest(AUTHOR/'full-attempt1-frozen'/name)==h,'attempt1 backup identical '+name)
patch=''.join(difflib.unified_diff(old.read_text().splitlines(True),new.read_text().splitlines(True),fromfile='frozen-attempt1/run_full_packed_DRAFT.py',tofile='proposed-attempt2/run_full_packed_attempt2_DRAFT.py'))
need(patch==(AUTHOR/'FULL-ATTEMPT2-HARNESS-DIFF.patch').read_text(),'exact diff matches frozen harness pair')
ot,nt=ast.parse(old.read_text()),ast.parse(new.read_text())
of={n.name:n for n in ast.walk(ot) if isinstance(n,ast.FunctionDef)}
nf={n.name:n for n in ast.walk(nt) if isinstance(n,ast.FunctionDef)}
for name in ('need','hashes','heartbeat','capture'):
    need(dump(of[name])==dump(nf[name]),'unchanged helper '+name)
class RemoveCheckpoint(ast.NodeTransformer):
    def visit_Expr(self,n):
        if isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='checkpoint_completed_children':return None
        return self.generic_visit(n)
for name in ('observe_tensor','observe_converter','observe_pointwise'):
    transformed=RemoveCheckpoint().visit(ast.parse(ast.unparse(nf[name]))).body[0]
    need(dump(transformed)==dump(of[name]),'observer differs only by post-match checkpoint '+name)
selected={'machine.run','machine.consume','original_tensor','original_converter','original_pointwise','Tensor','Converter','full','p48_setup','no_decode'}
def scientific_calls(tree):
    return [dump(n) for n in ast.walk(tree) if isinstance(n,ast.Call) and ast.unparse(n.func) in selected]
need(scientific_calls(ot)==scientific_calls(nt),'all scientific/ownership calls unchanged')
for name in ('FIRST','SECOND','P','ROOT','PKG','DRAFT'):
    def assignments(t):
        return [dump(n) for n in ast.walk(t) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id==name for x in n.targets)]
    need(assignments(ot)==assignments(nt),'same fixture/path '+name)
checkpoint=nf['checkpoint_completed_children']
checkpoint_calls=[ast.unparse(n.func) for n in ast.walk(checkpoint) if isinstance(n,ast.Call)]
need(all(x in checkpoint_calls for x in ('json.dump','target.flush','os.fsync','temporary.replace')),'flush/fsync then atomic replace implementation')
need(set(nf)-set(of)=={'checkpoint_completed_children'},'only new function is evidence checkpoint')
need("R['deadline_triggered']=True" in new.read_text(),'deadline flag retained before raising')
receipt=json.loads((AUTHOR/'FULL-PACKED-RESULT.json').read_text())
need(receipt['status']=='FAIL' and receipt['Tensor_calls']==2 and receipt['Converter_calls']==2,'preserved incomplete first outcome')
need(receipt['source_and_candidate_unchanged'] and receipt['harness_unchanged'],'prior exact-byte integrity')
need('TimeoutError' in receipt['traceback'] and 'empty body before owned marker erasure' in receipt['traceback'],'deadline and inherited cleanup failure visible')
need('actual_Tensor_observations' not in receipt,'first-attempt durability gap preserved rather than repaired retrospectively')
for path,h in receipt['before_hashes'].items():need(digest(AUTHOR/path)==h,'same original scientific inputs '+path)
log=(AUTHOR/'FULL-PACKED.log').read_text()
need(log.count('NUMERICAL_TENSOR_FINISH 0')==1 and 'NUMERICAL_TENSOR_FINISH 1' not in log,'one logged successful full Tensor return, no opposite completion')
need('NUMERICAL_TENSOR_START 1 True' in log,'second/opposite started before deadline')
for filename in ('FULL-PACKED-ATTEMPT2-RESULT.json','FULL-PACKED-ATTEMPT2-CHILD-CHECKPOINT.json','FULL-PACKED-ATTEMPT2-CHILD-CHECKPOINT.json.tmp','FULL-PACKED-ATTEMPT2.log'):
    need(not(AUTHOR/filename).exists(),'fresh attempt2 evidence path '+filename)
result={'status':'PASS_MINIMAL_ATTEMPT2_STATIC_DURABILITY_GATE','no_numeric_execution':True,
 'new_harness_sha256':digest(new),'prior_harness_sha256':digest(old),
 'addendum_sha256':digest(AUTHOR/'FULL-ATTEMPT2-PLAN-ADDENDUM.md'),
 'exact_diff_sha256':digest(AUTHOR/'FULL-ATTEMPT2-HARNESS-DIFF.patch'),
 'prior_receipt_sha256':digest(AUTHOR/'FULL-PACKED-RESULT.json'),
 'prior_backup_files_verified':len(backup),'all_original_source_input_hashes_preserved':True,
 'scientific_and_ownership_call_ASTs_unchanged':True,'observer_changes_only_post_match_checkpoint':True,
 'fresh_attempt2_evidence_paths':True,'proposed_external_cap':900,'proposed_internal_alarm':880,
 'durability_scope':'Matched completed-stage records, atomic whole-file replacement and process-failure retention; no whole-caller-success or power-loss persistence claim.',
 'remaining_limits':['No observed opposite/recovery/postconditions from attempt1','Inherited deadline/numerical-child cleanup not repaired','Four full-stage mutants remain unrun','require_recovery=False remains diagnostic','No execution authorized by this reviewer']}
(HERE/'ATTEMPT2-STATIC-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'],'no numerical import/execution')
