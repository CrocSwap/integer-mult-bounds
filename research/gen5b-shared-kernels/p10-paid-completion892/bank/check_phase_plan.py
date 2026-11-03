from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import support
support.require_assertions()
"""Independent exact phase-plan specification, not a raw compiler admission.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import json,hashlib,copy
if not __debug__:raise RuntimeError('Assertions required')
HERE=support.BANK

def plan(split):
 phases=[]
 for s in range(5):
  phases.extend({'kind':'helper','stage':s,'replica':t,'cover':'all_GL_classes'}for t in range(60))
  off=40
  for r in split:
   phases.append({'kind':'paid_bank_completion','stage':s,'family':230400+(s+1)*85575-1,'rank':r,'coordinate_interval':[off,off+r],'cover':'all_GL_classes','projector':'g*diag(interval)*g^-1','weighted_by':'existing_common_ancestor_chart','high_fibers':'batched','row_restoration':'inherited_completed_child_contract'});off+=r
  if s in [1,2,4]:
   b={1:0,2:1,4:2}[s]
   for t in range(60):
    phases.extend([{'kind':'idle','stage':s,'which':b,'replica':t,'cover':'all_GL_classes'},{'kind':'bridge','stage':s,'which':b,'replica':t,'cover':'all_GL_classes'}])
 phases.extend({'kind':'terminal_exchange','replica':t,'cover':'all_GL_classes'}for t in range(60))
 return phases

def validate(phases,split):
 assert phases==plan(split),'Exact stage-major order and literals required'
 assert len(phases)==730
 for s in range(5):
  helpers=[i for i,p in enumerate(phases)if p['kind']=='helper'and p['stage']==s]
  cs=[i for i,p in enumerate(phases)if p['kind']=='paid_bank_completion'and p['stage']==s]
  assert len(helpers)==60 and len(cs)==2 and max(helpers)<min(cs)
  assert [phases[i]['rank']for i in cs]==list(split)
  assert all(type(phases[i]['family'])is int and 230400<=phases[i]['family']<658275 for i in cs)
  bs=[i for i,p in enumerate(phases)if p.get('stage')==s and p['kind']in('idle','bridge')]
  if bs:assert max(cs)<min(bs)
 return True
for split in [(49,11)]:
 phases=plan(split);assert validate(phases,split)
 controls=[];first=next(i for i,p in enumerate(phases)if p['kind']=='paid_bank_completion')
 mutations={}
 z=copy.deepcopy(phases);del z[first];mutations['omitted_completion']=z
 z=copy.deepcopy(phases);z.insert(first,z[first]);mutations['repeated_completion']=z
 z=copy.deepcopy(phases);z[first],z[first-1]=z[first-1],z[first];mutations['completion_before_last_helper']=z
 z=copy.deepcopy(phases);z[first]['coordinate_interval'][0]-=1;mutations['overlapping_support']=z
 z=copy.deepcopy(phases);z[first]['family']='43885/4';mutations['fractional_stock_index']=z
 for name,z in mutations.items():
  try:validate(z,split)
  except AssertionError:controls.append(name)
  else:raise AssertionError('Mutation accepted: '+name)
 out={'status':'PASS_EXACT_PROPOSED_PHASE_PLAN_NOT_RAW_WORD_BINDING','split':list(split),'phases':phases,'phase_count':len(phases),'existing_phase_count':720,'added_completion_sweeps':10,'inverse_phase_indices':list(reversed(range(len(phases)))),'rejected_mutations':controls,'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'remaining_gate':'Bind these descriptors and the admitted892 source operand/event stream in the actual global lowering; this file is an explicit validated plan, not proof that upstream lowering was executed.'}
 d=HERE/f'split_{split[0]}_{split[1]}';(d/'LOWERING-PLAN.json').write_text(json.dumps(out,indent=2)+'\n')
 print(split,'phases',len(phases),'controls',controls)
