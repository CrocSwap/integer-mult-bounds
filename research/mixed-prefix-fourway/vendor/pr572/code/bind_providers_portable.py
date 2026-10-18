# PR569 adapter extended to the composed PR568 eight-cold / PR569 width-seven providers.
"""Bind freshly verified plain and width-seven eight-cold providers to the frozen literal owner plan.
Prepared with OpenAI Codex assistance; Apache-2.0. All proof-relevant generated content
is pinned to the plan. Validated gzip container references, phase timing,
serialization and directory fields are rebound; no dispatch, width or owner choice changes.
"""
import argparse,copy,gzip,hashlib,json,shutil
from collections import Counter
from generated_identity import artifact_identities
from pathlib import Path
assert __debug__, 'Assertions required'
ap=argparse.ArgumentParser(description=__doc__)
for name in ('baseline','plain','width7','plan','out'):ap.add_argument('--'+name,type=Path,required=True)
a=ap.parse_args();assert not a.out.exists();a.out.mkdir(parents=True)
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=a.out/'base';shutil.copytree(a.baseline/'complex-global/base',base)
dirs={'multicold_eight':a.plain,'multicold_width7_eight':a.width7}
promotions={'multicold_eight':0,'multicold_width7_eight':32}
for pid,src in dirs.items():shutil.copytree(src,base/'providers'/pid)
plan=read(a.plan);original=copy.deepcopy(plan);sources={}
assert set(plan['provider_registry'])==set(dirs)
assert Counter(c['provider']for c in plan['provider_calls'])=={'multicold_width7_eight': 57, 'multicold_eight': 15}
for pid,desc in plan['provider_registry'].items():
 d=base/'providers'/pid;p=promotions[pid]
 word,program,checks,native,phase=[read(d/name)for name in('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-REVIEW.json')]
 assert (word['v'],word['h'],word['R'],len(word['centers']))==(112,9,504,8)
 assert word['ports']==desc['ports'] and word['centers']==desc['centers']
 widths=[9-len(word['frames'][f])for f in word['start'][224:]]
 assert all(widths[h]==8 for h in (270,271,282,283,294,295,306,307))
 assert widths==desc['widths'] and Counter(widths)==Counter({4:8,5:48,7:p,8:164-p,9:284})
 assert native['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY'
 assert len(native['negative_controls_rejected'])==11
 assert native['canonical_word_sha256']==sha(d/'CANONICAL-WORD.json.gz') and native['local_programs_sha256']==sha(d/'LOCAL-PROGRAMS.json.gz')
 assert phase['status']=='PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES'
 assert phase['canonical_word_sha256']==sha(d/'CANONICAL-WORD.json.gz') and phase['recipe_sha256']==sha(d/'CLIFFORD-RECIPES.json')
 assert phase['all_child_equalities_include_global_phase'] is True and phase['endpoint_adapters']==224 and phase['directed_edges']==(3005 if p else 2929)
 assert set(program)==set(checks)=={'forward','backward'}
 expected={1:2332+p,2:436+5*p,3:448-4*p,4:192,5:56,6:56,8:8}
 for orientation,events in program.items():
  profile=Counter()
  for e in events:
   if e[0]=='climb':profile[e[5]]+=1
   elif e[0]=='center':profile[e[4]]+=1
  assert dict(profile)==expected=={int(r):n for r,n in checks[orientation]['paid_profile'].items()}=={int(r):n for r,n in native['paid_profiles'][orientation].items()}
  assert hashlib.sha256(json.dumps(events,separators=(',',':')).encode()).hexdigest()==checks[orientation]['sha256']
 assert artifact_identities(d)==desc['artifact_semantic_sha256'],(pid,'changed proof-relevant artifact')
 for c in plan['provider_calls']:
  if c['provider']==pid:
   assert c['orientation']==('forward'if c['stage']%2==0 else'backward')
   assert c['local_program_sha256']==checks[c['orientation']]['sha256']
 desc['directory']='providers/'+pid
 desc['artifact_sha256']={name:sha(d/name)for name in desc['artifact_sha256']}
 sources[pid]=dict(artifact_sha256=desc['artifact_sha256'],canonical_content_sha256=hashlib.sha256(json.dumps(word,sort_keys=True,separators=(',',':')).encode()).hexdigest(),all_phase_edges=(3005 if p else 2929))
plan['runtime_source_plan_sha256']=sha(a.plan)
(a.out/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
receipt=dict(status='PASS_FROZEN_048_ALLCOLD_DISPATCH_FRESH_PROVIDER_BINDING',source_plan_sha256=sha(a.plan),runtime_plan_sha256=sha(a.out/'PLAN.json'),providers=sources,only_rebound_fields=['provider_registry.directory','provider_registry.artifact_sha256','runtime_source_plan_sha256'])
(a.out/'BINDING.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'])
