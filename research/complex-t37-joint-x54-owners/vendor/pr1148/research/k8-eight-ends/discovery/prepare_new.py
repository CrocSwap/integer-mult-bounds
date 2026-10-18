"""Nominate new checked endpoints and whole owners; unchanged admission guards."""
import argparse,json,gzip,hashlib,importlib.util,shutil
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[3];UP=ROOT/'research/gauge44-slots'
def read(p):
 p=Path(p);raw=p.read_bytes();return json.loads(gzip.decompress(raw) if str(p).endswith('.gz') else raw)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def prepare(local,candidate,out):
 assert not out.exists() and not out.resolve().is_relative_to(ROOT)
 word=read(local/'CANONICAL-WORD.json.gz');checks=read(local/'LOCAL-CHECKS.json');plan=read(candidate/'PLAN.json');owners=read(candidate/'OWNERS.json.gz');widths=[len(word['frames'][word['final'][224+h]])-len(word['frames'][word['start'][224+h]]) for h in range(480)];desc=plan['provider_registry']['gauge44']
 assert (word['v'],word['h'],word['R'])==(112,9,480);assert word['ports']==desc['ports'] and word['centers']==desc['centers'];assert widths==desc['widths'] and word['local_profile']==desc['actual_paid_profile'];assert all(c['paid_profile']==word['local_profile'] for c in checks.values())
 ident=module('identity',UP/'code/generated_identity.py');desc.update(artifact_sha256={name:sha(local/name) for name in ident.FILES},artifact_semantic_sha256=ident.artifact_identities(local),orientation_program_sha256={o:c['sha256'] for o,c in checks.items()})
 for c in plan['provider_calls']:
  assert c['provider']=='gauge44';c['local_program_sha256']=checks[c['orientation']]['sha256']
 for c in plan.get('per_call_widths',[]):c['widths']=widths
 audit=module('roles',UP/'hosting/reuse_owners.py');used,_=audit.audit_roles(owners,plan,{tuple(c):widths for c in plan['order']},112,480);idle=Counter()
 for key,(cap,_) in plan['windows'].items():
  rep,ch=map(int,key.split(','))
  for port in range(112):
   rem=cap-len(used[rep,ch,port]);assert rem>=0
   if rem:idle[rem]+=1
 H=Counter({int(r):72*c for r,c in word['local_profile'].items()});H.update(idle);assert {str(r):c for r,c in H.items()}==plan['profile'];assert 73*7168-sum(r*c for r,c in H.items())==2560
 plan.update(status='NOMINATED_EIGHT_SMALLER_ENDPOINTS_REQUIRES_STRICT_ADMISSION',assignment_sha256=hashlib.sha256(gzip.decompress((candidate/'OWNERS.json.gz').read_bytes())).hexdigest(),solver_status='Frozen feasible whole owners; exact admission required',gap=None)
 out.mkdir(parents=True);shutil.copytree(UP/'code',out/'code',ignore=shutil.ignore_patterns('__pycache__'));shutil.copytree(UP/'inputs',out/'inputs');shutil.copy2(UP/'verify_global.py',out/'verify_global.py');(out/'data').mkdir();shutil.copy2(UP/'data/UPSTREAM-PINS.json',out/'data/UPSTREAM-PINS.json');shutil.copy2(candidate/'OWNERS.json.gz',out/'data/OWNERS.json.gz');dump(out/'data/PLAN.json',plan)
 spec=read(UP/'data/SPEC.json');recipe=Path(spec['pivot_swap']['recipe']);assert not recipe.is_absolute() and '..' not in recipe.parts;(out/recipe).parent.mkdir(parents=True);shutil.copy2(UP/recipe,out/recipe);spec.update(name='k8-eight-rank7-ends',providers={},expected={'gain_baseline_kappa':spec['expected']['gain_baseline_kappa']},data={'plan_sha256':sha(out/'data/PLAN.json'),'owners_sha256':sha(out/'data/OWNERS.json.gz')});dump(out/'data/SPEC.json',spec)
 dump(out/'PREPARATION.json',dict(status='PASS_CHECKED_LOCAL_AND_LITERAL_OWNER_NOMINATION',width_inventory=dict(Counter(widths)),local_profile=word['local_profile'],idle=dict(idle),global_profile=dict(H),local_artifacts=desc['artifact_semantic_sha256']))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--local',type=Path,required=True);ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();prepare(a.local.resolve(),a.candidate.resolve(),a.out.resolve());print('PASS_NOMINATION')
