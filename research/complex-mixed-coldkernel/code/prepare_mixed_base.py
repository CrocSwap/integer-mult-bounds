"""Bind fresh verified provider bytes to frozen mixed dispatch and ownership.

Prepared with OpenAI Codex assistance. Apache-2.0. Retains all PR558 geometry,
source pins and contracts. Runtime phase receipts may include elapsed time;
only their byte hashes are rebound after checking exact mathematical content.
"""
import argparse,copy,gzip,hashlib,json,shutil
from pathlib import Path
assert __debug__
ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--cold',type=Path,required=True);ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not a.out.exists();a.out.mkdir(parents=True)
base=a.out/'base';shutil.copytree(a.baseline/'complex-global/base',base)
for pid,src in [('rank5_eight',a.baseline/'complex-local'),('coldkernel000',a.cold)]:shutil.copytree(src,base/'providers'/pid)
plan=read(a.plan);original=copy.deepcopy(plan);sources={}
# Byte-stable replay files are pinned against the frozen nomination. Gzip's
# platform header may differ; semantic SHA below additionally pins the word.
for pid,desc in plan['provider_registry'].items():
 d=base/'providers'/pid;can=read(d/'CANONICAL-WORD.json.gz');program=read(d/'LOCAL-PROGRAMS.json.gz');checks=read(d/'LOCAL-CHECKS.json');phase=read(d/'CLIFFORD-REVIEW.json');native=read(d/'INDEPENDENT-LOCAL-REPLAY.json')
 assert (can['v'],can['h'],can['R'])==(112,9,504) and can['ports']==desc['ports']
 assert [9-len(can['frames'][f])for f in can['start'][224:]]==desc['widths']
 assert set(program)=={'forward','backward'}
 for name in ('CANONICAL-WORD.json.gz','LOCAL-CHECKS.json','LOCAL-PROGRAMS.json.gz','INDEPENDENT-LOCAL-REPLAY.json','RESIDUAL-ADAPTERS.json','CLIFFORD-RECIPES.json'):
  assert sha(d/name)==desc['artifact_sha256'][name],(pid,name,'changed non-timing artifact')
 assert native['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY'
 assert phase['all_child_equalities_include_global_phase'] and phase['endpoint_adapters']==224 and phase['directed_edges']==2929
 assert native['paid_profiles']['forward']==native['paid_profiles']['backward'] and len(native['negative_controls_rejected'])==11
 for c in plan['provider_calls']:
  if c['provider']==pid:assert c['local_program_sha256']==checks[c['orientation']]['sha256']
 desc['directory']='providers/'+pid
 desc['artifact_sha256']={name:sha(d/name)for name in desc['artifact_sha256']}
 sources[pid]=dict(artifact_sha256=desc['artifact_sha256'],canonical_content_sha256=hashlib.sha256(json.dumps(can,sort_keys=True,separators=(',',':')).encode()).hexdigest(),all_phase_edges=2929)
plan['runtime_source_plan_sha256']=sha(a.plan)
(a.out/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
(a.out/'BINDING.json').write_text(json.dumps(dict(status='PASS_FROZEN_DISPATCH_FRESH_PROVIDER_BINDING',source_plan_sha256=sha(a.plan),runtime_plan_sha256=sha(a.out/'PLAN.json'),providers=sources,only_rebound_fields=['provider_registry.directory','provider_registry.artifact_sha256.CLIFFORD-REVIEW.json','runtime_source_plan_sha256']),indent=2)+'\n')
print('PASS_FROZEN_DISPATCH_FRESH_PROVIDER_BINDING')
