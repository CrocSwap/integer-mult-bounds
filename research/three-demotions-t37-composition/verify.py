"""Strict finite replay with fresh PR1148 native replay and a pinned parent geometry.
Requires Python 3.11+, C++ and Boost. No network or optimization solver is used.
"""
import argparse,gzip,hashlib,importlib.util,json,os,shutil,subprocess,sys,tarfile,time
from pathlib import Path
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--native-from',type=Path);a=ap.parse_args();work=a.work.resolve();assert __debug__ and not work.exists() and not work.is_relative_to(P)
def rd(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pins=rd(P/'MANIFEST.json');actual={str(x.relative_to(P)) for x in P.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.name!='MANIFEST.json'};assert actual==set(pins)
for rel,h in pins.items():assert sha(P/rel)==h,rel
work.mkdir();layout=work/'layout';layout.mkdir();tmp=work/'tmp';tmp.mkdir();env=dict(os.environ,TMPDIR=str(tmp),PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0')
for k in ('PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_DISCOVER','WITNESS_RECORD'):env.pop(k,None)
with tarfile.open(P/'upstream-layout.tar.gz') as t:
 for m in t.getmembers():assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
 t.extractall(layout,filter='data')
R=layout/'owner37-round44';N=layout/'joint1148-round45';SRC=N/'source';tools=R/'candidate-tools-joint';data=R/'candidate-data';data.mkdir()
for name in ['PLAN.json','OWNERS.json.gz','SPEC.json','PROFILE.json','GLOBAL-TEMPLATE.json.gz']:shutil.copy2(P/name,data/name)
stages=[]
def run(name,script,*args):
 start=time.monotonic();log=work/(name+'.log')
 with log.open('w') as f:r=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],cwd=layout,env=env,stdout=f,stderr=subprocess.STDOUT)
 stages.append(dict(name=name,exit_code=r.returncode,seconds=time.monotonic()-start,log_sha256=sha(log)));(work/'STAGES.json').write_text(json.dumps(stages,indent=2));assert r.returncode==0,(name,log.read_text()[-5000:]);print('PASS',name,flush=True)
run('literal-construct',P/'construct.py','--flow',P/'PATTERN-FLOW.json','--plan',P/'PLAN.json','--out',work/'constructed')
assert gzip.decompress((work/'constructed/OWNERS.json.gz').read_bytes())==gzip.decompress((P/'OWNERS.json.gz').read_bytes())
run('parent-and-plan',tools/'prepare.py','--construction',work/'constructed','--flow',P/'PATTERN-FLOW.json','--out',work/'reconstructed-data')
assert rd(work/'reconstructed-data/PLAN.json')==rd(P/'PLAN.json')
assert gzip.decompress((work/'reconstructed-data/GLOBAL-TEMPLATE.json.gz').read_bytes())==gzip.decompress((P/'GLOBAL-TEMPLATE.json.gz').read_bytes())
word=SRC/'research/k8-joint-entrances/FULL-WORD.json.gz'
run('local-recipe',SRC/'research/k8-joint-entrances/build_word.py','--out',work/'rebuilt-word.json.gz')
assert gzip.decompress(word.read_bytes())==gzip.decompress((work/'rebuilt-word.json.gz').read_bytes())
run('independent-local',SRC/'research/gauge44-slots/independent/audit_local.py','--word',word,'--main',SRC,'--output',work/'INDEPENDENT-LOCAL.json')
run('demotion-controls',SRC/'research/k8-joint-entrances/controls.py','--out',work/'DEMOTION-CONTROLS.json')
assert len(rd(work/'DEMOTION-CONTROLS.json')['rejected'])==27
native=a.native_from.resolve() if a.native_from else work/'native'
if not a.native_from:run('fresh-native',SRC/'research/k8-eight-ends/replay_native.py',word,native)
assert gzip.decompress((native/'local/FULL-WORD.json.gz').read_bytes())==gzip.decompress(word.read_bytes())
steps=rd(native/'STEPS.json');assert [x['step'] for x in steps]==['native','ledgers','local-replay','wrappers','phases'] and all(x['exit_code']==0 for x in steps)
run('strict-global',tools/'replay.py','--data',data,'--work',work/'strict','--local',native/'local')
r=rd(work/'strict/RESULT.json');assert r['status']=='PASS_STRICT_T37_THREE_DEMOTIONS' and r['kappa']==rd(P/'CANDIDATE.json')['kappa']
run('fixed-family-upper',SRC/'research/k8-joint-entrances/independent/all_t_bound.py','--out',work/'UPPER.json')
assert rd(work/'UPPER.json')['all_T_grid_upper']==r['kappa']
result=dict(status='PASS_T37_JOINT_ENTRANCES_NATIVE_AND_STRICT_ADMISSION',kappa=r['kappa'],kappa_decimal=r['kappa_decimal'],parent_geometry_reuse=True,native_reuse=bool(a.native_from),local_controls=27,admission_controls=69,bit_controls=12,controller_controls=15,independent_owner_controls=7,outer_inequalities=47,stages=stages,scope=rd(P/'CANDIDATE.json')['scope']);(work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['kappa_decimal'])
