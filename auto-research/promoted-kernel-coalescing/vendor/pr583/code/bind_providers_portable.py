"""Bind freshly verified plain and width-seven four-cold providers to the frozen literal owner plan.
Prepared with OpenAI Codex assistance; Apache-2.0. All byte-stable native
files are pinned to the plan. Only validated phase-receipt timing/serialization
and directory fields are rebound; no dispatch, width or owner choice changes.
"""
import argparse,copy,gzip,hashlib,json,shutil
from collections import Counter
from pathlib import Path
import sys as _s,pathlib as _p;_s.path.insert(0,str(_p.Path(__file__).resolve().parent))
from witness import *
from generated_identity import artifact_identities
assert __debug__, 'Assertions required'
ap=argparse.ArgumentParser(description=__doc__)
for name in ('baseline','plan','out'):ap.add_argument('--'+name,type=Path,required=True)
ap.add_argument('--provider',action='append',required=True,help='PID=DIR');a=ap.parse_args();assert not a.out.exists();a.out.mkdir(parents=True)
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=a.out/'base';shutil.copytree(a.baseline/'complex-global/base',base)
ap2=dict(x.split('=',1)for x in a.provider);dirs={k:Path(v)for k,v in ap2.items()};assert set(dirs)==set(PIDS)
for pid,src in dirs.items():shutil.copytree(src,base/'providers'/pid)
pin('data.plan_sha256',sha(a.plan))
plan=read(a.plan);original=copy.deepcopy(plan);sources={}
assert set(plan['provider_registry'])==set(dirs)
assert {(c['stage'],c['replica']):c['provider']for c in plan['provider_calls']}==DISPATCH,'PLAN dispatch differs from spec dispatch'
stable=('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-RECIPES.json','RESIDUAL-ADAPTERS.json')
for pid,desc in plan['provider_registry'].items():
 d=base/'providers'/pid
 word,program,checks,native,phase=[read(d/name)for name in('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-REVIEW.json')]
 assert (word['v'],word['h'],word['R'],len(word['centers']))==(112,9,504,8)
 assert word['ports']==desc['ports'] and word['centers']==desc['centers']
 widths=[9-len(word['frames'][f])for f in word['start'][224:]]
 assert all(widths[h]==8 for h in (270,282,294,306))
 assert widths==desc['widths'];pin('providers.%s.inventory'%pid,{str(k):v for k,v in sorted(Counter(widths).items())})
 assert native['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY'
 pin('providers.%s.native_negative_controls'%pid,len(native['negative_controls_rejected']))
 assert native['canonical_word_sha256']==sha(d/'CANONICAL-WORD.json.gz') and native['local_programs_sha256']==sha(d/'LOCAL-PROGRAMS.json.gz')
 assert phase['status']=='PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES'
 assert phase['canonical_word_sha256']==sha(d/'CANONICAL-WORD.json.gz') and phase['recipe_sha256']==sha(d/'CLIFFORD-RECIPES.json')
 assert phase['all_child_equalities_include_global_phase'] is True and phase['endpoint_adapters']==224 
 pin('providers.%s.phase_edges'%pid,phase['directed_edges'])
 assert set(program)==set(checks)=={'forward','backward'}
 expected={int(r):n for r,n in checks['forward']['paid_profile'].items()};pin('providers.%s.expected_profile'%pid,checks['forward']['paid_profile'])
 for orientation,events in program.items():
  profile=Counter()
  for e in events:
   if e[0]=='climb':profile[e[5]]+=1
   elif e[0]=='center':profile[e[4]]+=1
  assert dict(profile)==expected=={int(r):n for r,n in checks[orientation]['paid_profile'].items()}=={int(r):n for r,n in native['paid_profiles'][orientation].items()}
  assert hashlib.sha256(json.dumps(events,separators=(',',':')).encode()).hexdigest()==checks[orientation]['sha256']
 identities=artifact_identities(d)
 pin('providers.%s.artifact_semantic_sha256'%pid,identities)
 assert identities==desc['artifact_semantic_sha256']
 for name in ('LOCAL-CHECKS.json','CLIFFORD-RECIPES.json','RESIDUAL-ADAPTERS.json'):
  assert sha(d/name)==desc['artifact_sha256'][name],(pid,name,'changed non-reference artifact')
 for c in plan['provider_calls']:
  if c['provider']==pid:
   assert c['orientation']==('forward'if c['stage']%2==0 else'backward')
   assert c['local_program_sha256']==checks[c['orientation']]['sha256']
 desc['directory']='providers/'+pid
 desc['artifact_sha256']={name:sha(d/name)for name in desc['artifact_sha256']}
 sources[pid]=dict(artifact_sha256=desc['artifact_sha256'],canonical_content_sha256=hashlib.sha256(json.dumps(word,sort_keys=True,separators=(',',':')).encode()).hexdigest(),all_phase_edges=phase['directed_edges'])
plan['runtime_source_plan_sha256']=sha(a.plan)
(a.out/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
receipt=dict(status='PASS_FROZEN_048_ALLCOLD_DISPATCH_FRESH_PROVIDER_BINDING',source_plan_sha256=sha(a.plan),runtime_plan_sha256=sha(a.out/'PLAN.json'),providers=sources,only_rebound_fields=['provider_registry.directory','provider_registry.artifact_sha256','runtime_source_plan_sha256'])
(a.out/'BINDING.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'])
