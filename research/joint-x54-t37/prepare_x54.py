"""Rebuild the T37 PLAN/SPEC/PROFILE for the X54 joint-entrance word.

Adapted from PR1169's candidate-tools-joint/prepare.py (Rohan Arun/Codex, Apache-2.0).
Sole changes: the provider plan is the rebound X54 plan supplied by --source-plan (instead of
research/k8-joint-entrances/PLAN.json.gz), the expected idle/windows/owners are unchanged, and the
SPEC records PR1169's value as the comparison baseline.
"""
import argparse,collections,copy,gzip,hashlib,importlib.util,json,shutil
from pathlib import Path
def rd(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def identity(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
ap=argparse.ArgumentParser();ap.add_argument('--layout',type=Path,required=True);ap.add_argument('--construction',type=Path,required=True);ap.add_argument('--flow',type=Path,required=True);ap.add_argument('--source-plan',type=Path,required=True);ap.add_argument('--baseline-kappa',required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();assert __debug__ and not a.out.exists();a.out.mkdir();out=a.out
F=a.layout.resolve();R=F/'owner37-round44';S=R/'source/research/r480-owner-optimum';B=F/'demotions1148-round43/baseline-replay'
assert rd(B/'RESULT.json')['status']=='PASS_THREE_DEMOTIONS_COMPLETE_ADMISSION'
L=load('lift',S/'lift.py');W=load('windows',S/'vendor/pr1074/t16/build_parent.py');base=B/'parent/t16/global8/base';parent=L.lift(rd(base/'split-centres/GLOBAL-TEMPLATE.json.gz'));flow=rd(a.flow);order=flow['order'];windows,schedule=W.actual_windows(parent,order)
expected={f'{r},{ch}':[cap,ts] for r,cap,ts,chs in flow['groups'] for ch in chs};assert windows==expected
roles=rd(a.construction/'OWNERS.json.gz');plan=rd(a.source_plan);used=collections.Counter();seen=set()
for z in roles:
 assert order[z['time']]==[z['stage'],z['replica']];k=z['owner_replica'],z['child'],z['port'];cap,ts=windows[f'{k[0]},{k[1]}'];assert z['time'] in ts;key=z['time'],z['family'];assert key not in seen;seen.add(key);used[k]+=z['width'];assert used[k]<=cap
idle=collections.Counter()
for key,(cap,ts) in windows.items():
 r,ch=map(int,key.split(','))
 for port in range(112):
  rem=cap-used[r,ch,port]
  if rem:idle[rem]+=1
assert idle=={1:834,48:11374}
profile=collections.Counter({int(r):len(order)*n for r,n in plan['provider_registry']['gauge44']['actual_paid_profile'].items()});profile.update(idle)
plan.update(T=37,live=896*37,deficit=320*37,order=order,windows=windows,profile={str(r):n for r,n in sorted(profile.items())},status='EXPLICIT_T37_THREE_DEMOTIONS_OWNER_NOMINATION',mode='three-demotions-t37',solver_status='exact integer flow and matching',gap=None)
for field in ('provider_calls','per_call_widths'):
 old={(z['stage'],z['replica']):z for z in plan[field]};plan[field]=[]
 for t,(s,r) in enumerate(order):
  z=copy.deepcopy(old[s,r%16]);z['replica']=r
  if 'time' in z:z['time']=t
  plan[field].append(z)
shutil.copy2(a.construction/'OWNERS.json.gz',out/'OWNERS.json.gz');plan.update(assignment_sha256=sha(out/'OWNERS.json.gz'),assignment_content_sha256=identity(roles));plan['replica_lift']=dict(groups=[8,8,8,8,5],source_replicas=8,replicas=37,parent_template_content_sha256=identity(parent),owners_file_sha256=sha(out/'OWNERS.json.gz'),schedule_content_sha256=identity(schedule),window_semantics='Strict physical source-event intervals, including bridges')
assert sum(r*n for r,n in profile.items())==73*plan['live']-plan['deficit']
(out/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');L.write_gzip(out/'GLOBAL-TEMPLATE.json.gz',parent)
spec=rd(S/'data/SPEC.json');spec.update(name='joint-x54-t37',call_order=order,dispatch=[[s,r,'gauge44'] for s,r in order],providers={},expected={'gain_baseline_kappa':a.baseline_kappa},data={'plan_sha256':sha(out/'PLAN.json'),'owners_sha256':sha(out/'OWNERS.json.gz')});(out/'SPEC.json').write_text(json.dumps(spec,indent=2)+'\n');(out/'PROFILE.json').write_text(json.dumps(dict(profile),indent=2)+'\n');print('PREPARED',len(roles),dict(idle))
