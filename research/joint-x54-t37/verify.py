"""Strict finite replay of the X54 slot on PR1148's joint-entrance k8 word with PR1169's exact T37 owner packing.
Requires Python 3.11+, a C++ compiler and Boost headers. No network or optimization solver is used.

Stages: sibling-pin check, literal owner construction (PR1169, unchanged), plan/geometry reconstruction with the
rebound X54 provider plan, joint-entrance word rebuild (PR1148), X54 word build, independent local audit, PR1148's
27 entrance controls, X54's 10 slot controls, fresh native five-stage replay, provider rebind from that replay,
strict T37 admission (bind, emit, audit, invoice, assembly, 69 admission + 12 bit controls, independent owner
checker) and the fixed-family all-T upper bound.
"""
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,tarfile,time
from pathlib import Path
P=Path(__file__).resolve().parent;Q=P.parent/'three-demotions-t37-composition'
ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--native-from',type=Path);a=ap.parse_args();work=a.work.resolve();assert __debug__ and not work.exists() and not work.is_relative_to(P)
def rd(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def raw(p):return gzip.decompress(p.read_bytes())
pins=rd(P/'MANIFEST.json');actual={str(x.relative_to(P)) for x in P.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.name!='MANIFEST.json'};assert actual==set(pins),sorted(actual^set(pins))
for rel,h in pins.items():assert sha(P/rel)==h,rel
for rel,h in rd(P/'SOURCE-PINS.json').items():assert sha(P.parent/rel)==h,rel
claim=rd(P/'CANDIDATE.json')
work.mkdir();layout=work/'layout';layout.mkdir();tmp=work/'tmp';tmp.mkdir();env=dict(os.environ,TMPDIR=str(tmp),PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0')
for k in ('PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_DISCOVER','WITNESS_RECORD'):env.pop(k,None)
with tarfile.open(Q/'upstream-layout.tar.gz') as t:
 for m in t.getmembers():assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
 t.extractall(layout,filter='data')
R=layout/'owner37-round44';N=layout/'joint1148-round45';SRC=N/'source';tools=R/'candidate-tools-joint';data=work/'data';data.mkdir()
for name in ['PLAN.json','SPEC.json','PROFILE.json']:shutil.copy2(P/name,data/name)
for name in ['OWNERS.json.gz','GLOBAL-TEMPLATE.json.gz']:shutil.copy2(Q/name,data/name)
stages=[]
def run(name,script,*args):
 start=time.monotonic();log=work/(name+'.log')
 with log.open('w') as f:r=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],cwd=layout,env=env,stdout=f,stderr=subprocess.STDOUT)
 stages.append(dict(name=name,exit_code=r.returncode,seconds=time.monotonic()-start,log_sha256=sha(log)));(work/'STAGES.json').write_text(json.dumps(stages,indent=2));assert r.returncode==0,(name,log.read_text()[-5000:]);print('PASS',name,flush=True)
run('literal-construct',Q/'construct.py','--flow',Q/'PATTERN-FLOW.json','--plan',P/'PLAN.json','--out',work/'constructed')
assert raw(work/'constructed/OWNERS.json.gz')==raw(Q/'OWNERS.json.gz')
run('parent-and-plan',P/'prepare_x54.py','--layout',layout,'--construction',work/'constructed','--flow',Q/'PATTERN-FLOW.json','--source-plan',P/'PLAN-SOURCE-X54.json.gz','--baseline-kappa',claim['previous_kappa'],'--out',work/'reconstructed-data')
assert rd(work/'reconstructed-data/PLAN.json')==rd(P/'PLAN.json') and rd(work/'reconstructed-data/PROFILE.json')==rd(P/'PROFILE.json')
assert raw(work/'reconstructed-data/GLOBAL-TEMPLATE.json.gz')==raw(Q/'GLOBAL-TEMPLATE.json.gz')
base=SRC/'research/k8-joint-entrances/FULL-WORD.json.gz'
run('joint-entrance-recipe',SRC/'research/k8-joint-entrances/build_word.py','--out',work/'rebuilt-joint-word.json.gz')
assert raw(base)==raw(work/'rebuilt-joint-word.json.gz')
word=work/'X54-JOINT-WORD.json.gz'
run('x54-recipe',P/'build_word.py','--base',base,'--out',word)
run('independent-local',SRC/'research/gauge44-slots/independent/audit_local.py','--word',word,'--main',SRC,'--output',work/'INDEPENDENT-LOCAL.json')
loc=rd(work/'INDEPENDENT-LOCAL.json');plan=rd(P/'PLAN.json');reg=plan['provider_registry']['gauge44']
assert loc['status']=='PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES' and loc['local_profile']==reg['actual_paid_profile']=={'1':2364,'2':498,'3':414,'4':126,'5':84,'8':8}
assert loc['width_inventory']=={'4':44,'5':44,'7':38,'8':114,'9':240}
run('demotion-controls',SRC/'research/k8-joint-entrances/controls.py','--out',work/'DEMOTION-CONTROLS.json')
assert len(rd(work/'DEMOTION-CONTROLS.json')['rejected'])==27
run('x54-controls',P/'x54_controls.py','--base',base,'--audit',SRC/'research/gauge44-slots/independent/audit_local.py','--out',work/'x54-controls')
native=a.native_from.resolve() if a.native_from else work/'native'
if not a.native_from:run('fresh-native',SRC/'research/k8-eight-ends/replay_native.py',word,native)
assert raw(native/'local/FULL-WORD.json.gz')==raw(word)
steps=rd(native/'STEPS.json');assert [x['step'] for x in steps]==['native','ledgers','local-replay','wrappers','phases'] and all(x['exit_code']==0 for x in steps)
run('provider-rebind',P/'rebind_plan.py','--layout',layout,'--native-local',native/'local','--out',work/'PLAN-SOURCE-X54.json.gz')
assert raw(work/'PLAN-SOURCE-X54.json.gz')==raw(P/'PLAN-SOURCE-X54.json.gz')
run('strict-global',tools/'replay.py','--data',data,'--work',work/'strict','--local',native/'local')
r=rd(work/'strict/RESULT.json');assert r['status']=='PASS_STRICT_T37_THREE_DEMOTIONS' and r['kappa']==claim['kappa'] and r['kappa_decimal']==claim['kappa_decimal']
run('fixed-family-upper',P/'all_t_bound_x54.py','--root',SRC,'--plan',P/'PLAN-SOURCE-X54.json.gz','--out',work/'UPPER.json')
assert rd(work/'UPPER.json')['all_T_grid_upper']==r['kappa']
result=dict(status='PASS_X54_JOINT_ENTRANCES_T37_NATIVE_AND_STRICT_ADMISSION',kappa=r['kappa'],kappa_decimal=r['kappa_decimal'],previous_kappa=claim['previous_kappa'],word_content_sha256=hashlib.sha256(raw(word)).hexdigest(),parent_geometry_reuse=True,native_reuse=bool(a.native_from),local_controls=27,x54_controls=10,admission_controls=69,bit_controls=12,independent_owner_controls=7,outer_inequalities=47,stages=stages,scope=claim['scope']);(work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['kappa_decimal'])
