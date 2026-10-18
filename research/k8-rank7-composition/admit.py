# SPDX-License-Identifier: Apache-2.0
# Prepared for 1337isnot1337 with substantial OpenAI Codex assistance.
import argparse,copy,gzip,hashlib,json,os,shutil,subprocess,sys,time,importlib.util
from pathlib import Path
from collections import Counter,defaultdict
ap=argparse.ArgumentParser();ap.add_argument('--owners',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
for k in ('root','predecessor','local','baseline'):ap.add_argument('--'+k,type=Path,required=True)
a=ap.parse_args()
assert __debug__, 'Assertions required'
root=a.root.resolve();old=a.predecessor.resolve();local=a.local.resolve();baseline=a.baseline.resolve();work=a.out.resolve();assert not work.exists();work.mkdir()
pkg=work/'package';pkg.mkdir();shutil.copytree(old/'code',pkg/'code');shutil.copytree(old/'construction',pkg/'construction');shutil.copytree(old/'inputs',pkg/'inputs');data=pkg/'data';data.mkdir();shutil.copyfile(a.owners,data/'OWNERS.json.gz')
rd=lambda path:json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes());sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
plan=rd(old/'data/PLAN.json');word=rd(local/'CANONICAL-WORD.json.gz');checks=rd(local/'LOCAL-CHECKS.json');widths=[len(word['frames'][word['final'][224+h]])-len(word['frames'][word['start'][224+h]]) for h in range(480)]
assert Counter(widths)=={4:56,5:32,7:32,8:120,9:240};used=defaultdict(set);calls=defaultdict(set);families=defaultdict(set)
for z in rd(data/'OWNERS.json.gz'):
 t=z['time'];assert plan['order'][t]==[z['stage'],z['replica']];assert z['helper'] not in calls[t] and z['family'] not in families[t];calls[t].add(z['helper']);families[t].add(z['family'])
 cap,ts=plan['windows'][f"{z['owner_replica']},{z['child']}"];assert t in ts and z['width']==widths[z['helper']]
 assert z['family']==z['owner_replica']*896+(2*plan['pairs'][str(z['child'])]+plan['sides'][str(z['child'])])*112+z['port']
 assert z['copy']==z['owner_replica']*112+z['port'];k=z['owner_replica'],z['child'],z['port'];new=set(range(z['offset'],z['offset']+z['width']));assert 0<=z['offset']<cap and z['offset']+z['width']<=cap and not used[k]&new;used[k]|=new
assert len(calls)==144 and all(v==set(range(480)) for v in calls.values());idle=Counter()
for key,(cap,ts) in plan['windows'].items():
 r,ch=map(int,key.split(','))
 for port in range(112):
  cells=used[r,ch,port];assert cells==set(range(len(cells)));left=cap-len(cells)
  if left:idle[left]+=1
H=Counter({int(k):144*v for k,v in word['local_profile'].items()});H.update(idle);assert sum(k*v for k,v in H.items())==1041408
sys.path.insert(0,str(pkg/'code'));from generated_identity import artifact_identities,FILES
for c in plan['provider_calls']:c['local_program_sha256']=checks[c['orientation']]['sha256']
for c in plan['per_call_widths']:c['widths']=widths
plan['provider_registry']={'gauge44':dict(directory='providers/gauge44',artifact_sha256={name:sha(local/name) for name in FILES},ports=word['ports'],centers=word['centers'],widths=widths,actual_paid_profile=word['local_profile'],orientation_program_sha256={k:v['sha256'] for k,v in checks.items()},artifact_semantic_sha256=artifact_identities(local))}
plan['profile']={str(k):v for k,v in sorted(H.items())};plan['assignment_sha256']=sha(data/'OWNERS.json.gz');plan['solver_status']='frozen feasible changed-width whole-helper nomination; not optimality';(data/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
spec=rd(old/'data/SPEC.json');spec['name']='k8-rank7-composition';spec['data']={'plan_sha256':sha(data/'PLAN.json'),'owners_sha256':sha(data/'OWNERS.json.gz')};spec['providers']={'gauge44':{}};spec['expected']={'gain_baseline_kappa':rd(old/'data/SPEC.json')['expected']['gain_baseline_kappa'],'assembly_controls_rejected':69,'mutations_rejected':15};(data/'SPEC.json').write_text(json.dumps(spec,indent=2)+'\n')
src=root/'research/complex-k492-owner-repair/vendor/multicold';vendor=src/'vendor/pr558/vendor/pr552/complex-global/vendor531';env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',GAIN_PR564_SOURCE=str(src),MULTICOLD_SOURCE=str(src),WITNESS_SPEC=str(data/'SPEC.json'));env.pop('PYTHONOPTIMIZE',None);steps=[]
def run(label,script,args,extra={}):
 log=work/(label+'.log');begin=time.monotonic()
 with log.open('w') as f:rc=subprocess.run([sys.executable,'-B',str(src/'code/run_portable.py'),str(script),*map(str,args)],env=dict(env,**extra),stdout=f,stderr=subprocess.STDOUT).returncode
 steps.append(dict(name=label,exit_code=rc,seconds=time.monotonic()-begin,log_sha256=sha(log)));(work/'STAGES.json').write_text(json.dumps(steps,indent=2)+'\n')
 if rc:raise RuntimeError(label+'\n'+log.read_text()[-5000:])
 print('PASS',label,flush=True)
for mode in ('discovery','strict'):
 g=work/mode;extra={'WITNESS_DISCOVER':'1','WITNESS_RECORD':str(work/'WITNESS-RECORD.jsonl')} if mode=='discovery' else {'WITNESS_DISCOVER':'0'}
 run(mode+'-bind',pkg/'code/bind_providers_portable.py',['--baseline',baseline/'parent16','--provider','gauge44='+str(local),'--plan',data/'PLAN.json','--out',g],extra)
 run(mode+'-emit',pkg/'code/emit_allcold.py',['--base',g/'base','--owners',data/'OWNERS.json.gz','--plan',g/'PLAN.json','--out',g/'hosted'],extra)
 run(mode+'-audit',pkg/'code/audit_allcold.py',[g/'base',g/'hosted',g/'audit/ASYNC-AUDIT.json','--mutation-controls'],extra)
 run(mode+'-invoice',pkg/'code/invoice_allcold.py',['--base',g/'base','--hosted',g/'hosted','--audit',g/'audit','--out',g/'audit','--retained-invoice',vendor/'evidence/audit/PREFIX-AND-INVOICE.json'],extra)
 run(mode+'-assembly',pkg/'code/assemble.py',[src,g,work/(mode+'-ASSEMBLY.json')],extra)
 if mode=='discovery':
  # Freeze values that were independently derived with every substantive guard enabled.
  for line in (work/'WITNESS-RECORD.jsonl').read_text().splitlines():
   k,v=json.loads(line);parts=k.split('.')
   if len(parts)>3 and parts[0]=='providers' and parts[2]=='artifacts':parts=parts[:3]+['.'.join(parts[3:])]
   d=spec
   for key in parts[:-1]:d=d.setdefault(key,{})
   if parts[-1] in d:assert d[parts[-1]]==v,(k,d[parts[-1]],v)
   d[parts[-1]]=v
  asm=rd(work/'discovery-ASSEMBLY.json')
  for k in ('complex_lower','conservative_complex_lower','kappa','kappa_decimal','conservative_kappa_decimal'):spec['expected'][k]=asm[k]
  (data/'SPEC.json').write_text(json.dumps(spec,indent=2)+'\n')
g=work/'strict'
for nm,sc in [('admission','assembly_controls.py'),('bit','bit_supplier_controls.py')]:run(nm,pkg/'code'/sc,['--source-package',src,'--owner',g/'audit/OWNERS-AND-PROFILE.json','--invoice',g/'audit/PREFIX-AND-INVOICE.json','--out',work/(nm+'-CONTROLS.json')],{'WITNESS_DISCOVER':'0'})
run('independent',old/'t16/indep16.py',['--baseline-parent',baseline/'global8/base/split-centres/GLOBAL-TEMPLATE.json.gz','--owners',data/'OWNERS.json.gz','--word',local/'CANONICAL-WORD.json.gz','--out',work/'INDEPENDENT.json'],{'T16_EXPECTED_IDLE':json.dumps(dict(idle)),'T16_EXPECTED_WIDTHS':json.dumps(dict(Counter(widths)))})
asm=rd(work/'strict-ASSEMBLY.json');ind=rd(work/'INDEPENDENT.json')
assert ind['profile']==asm['complex_profile'] and ind['rank_mass']==1041408 and ind['deficit']==5120
assert len(ind['controls_rejected'])==6
from fractions import Fraction as Q
assert len(asm['outer'])==47 and all(Q(x)>0 for x in asm['outer'].values())
assert Q(asm['kappa'])>Q(rd(old/'data/SPEC.json')['expected']['kappa'])
print('PASS_COMPLETE_K8_RANK7_ASSEMBLY',asm['kappa_decimal'],flush=True)
