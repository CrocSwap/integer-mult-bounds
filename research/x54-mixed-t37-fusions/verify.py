"""Finite mixed-provider replay; exact inherited theorem obligations remain conditional.
Default: sequential fresh native replays. Explicit native reuse validates word and stage bindings.
"""
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,tarfile,time
from pathlib import Path
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--base-native-from',type=Path);ap.add_argument('--extra-native-from',type=Path);a=ap.parse_args();work=a.work.resolve();assert __debug__ and not work.exists() and not work.is_relative_to(P)
def rd(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pins=rd(P/'MANIFEST.json');actual={x.relative_to(P).as_posix() for x in P.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x!=P/'MANIFEST.json'};assert actual==set(pins)
for rel,h in pins.items():assert sha(P/rel)==h,rel
work.mkdir();layout=work/'layout';layout.mkdir();tmp=work/'tmp';tmp.mkdir();env=dict(os.environ,TMPDIR=str(tmp),PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0')
for k in ('PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_DISCOVER','WITNESS_RECORD'):env.pop(k,None)
with tarfile.open(P/'upstream-layout.tar.gz') as t:
 for m in t.getmembers():assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
 t.extractall(layout,filter='data')
M=layout/'x54fusion50';M.mkdir();data=M/'candidate';data.mkdir();SRC=layout/'joint1148-round45/source'
for name in ('replay.py','freeze_spec.py','audit_mixed.py','independent_core.py'):shutil.copy2(P/name,M/name)
for name in ('PLAN.json','SPEC.json','PROFILE.json','OWNERS.json.gz','DISPATCH.json','CONSTRUCTION.json','GLOBAL-TEMPLATE.json.gz'):shutil.copy2(P/name,data/name)
stages=[]
def run(name,script,*args):
 start=time.monotonic();log=work/(name+'.log')
 with log.open('w') as f:r=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],cwd=layout,env=env,stdout=f,stderr=subprocess.STDOUT)
 stages.append(dict(name=name,exit_code=r.returncode,seconds=time.monotonic()-start,log_sha256=sha(log)));(work/'STAGES.json').write_text(json.dumps(stages,indent=2));assert r.returncode==0,(name,log.read_text()[-5000:]);print('PASS',name,flush=True)
run('literal-construct',P/'construct.py','--base',P/'baseline','--search',P/'SEARCH.json','--out',work/'constructed')
for name in ('OWNERS.json.gz','DISPATCH.json'):
 decode=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
 assert decode(work/'constructed'/name)==decode(P/name),name
for key,name in [('base','gauge44-word.json.gz'),('extra','extra-word.json.gz')]:
 run('literal-word-'+key,P/'build_word.py','--base',P/'inputs'/(key+'.json.gz'),'--recipe',P/('RECIPE-'+key+'.json.gz'),'--out',work/('rebuilt-'+key+'.json.gz'))
 assert gzip.decompress((work/('rebuilt-'+key+'.json.gz')).read_bytes())==gzip.decompress((P/name).read_bytes())
natives={}
for key,word,reuse in [('base',P/'gauge44-word.json.gz',a.base_native_from),('extra',P/'extra-word.json.gz',a.extra_native_from)]:
 run('independent-local-'+key,SRC/'research/gauge44-slots/independent/audit_local.py','--word',word,'--main',SRC,'--output',work/('INDEPENDENT-LOCAL-'+key+'.json'))
 run('fusion-controls-'+key,P/'controls.py','--main',SRC,'--sites',P/('CONTROL-SITES-'+key+'.json'),'--word',word,'--out',work/('FUSION-CONTROLS-'+key+'.json'))
 assert len(rd(work/('FUSION-CONTROLS-'+key+'.json'))['rejected'])==10
 run('x54-controls-'+key,P/'x54_controls.py','--main',SRC,'--recipe',P/'MAPPED-RECIPE.json','--word',word,'--out',work/('X54-CONTROLS-'+key+'.json'))
 assert len(rd(work/('X54-CONTROLS-'+key+'.json'))['rejected'])==4
 run('leaver-premise-'+key,P/'premise/premise_check.py',word)
 native=reuse.resolve() if reuse else work/('native-'+key)
 if not reuse:run('fresh-native-'+key,SRC/'research/k8-eight-ends/replay_native.py',word,native)
 assert gzip.decompress((native/'local/FULL-WORD.json.gz').read_bytes())==gzip.decompress(word.read_bytes())
 steps=rd(native/'STEPS.json');assert [x['step'] for x in steps]==['native','ledgers','local-replay','wrappers','phases'] and all(x['exit_code']==0 for x in steps)
 natives[key]=native
shutil.copytree(natives['extra'],M/'native-extra')
run('strict-global',M/'replay.py','--data',data,'--work',work/'strict','--local',natives['base']/'local')
r=rd(work/'strict/RESULT.json');assert r['status']=='PASS_STRICT_MIXED_T37_ENTRANCES' and r['kappa']==rd(P/'CLAIM.json')['kappa']
result=dict(status='PASS_X54_MIXED_T37_FUSIONS_NATIVE_AND_STRICT_ADMISSION',kappa=r['kappa'],kappa_decimal=r['kappa_decimal'],parent_geometry_reuse=True,base_native_reuse=bool(a.base_native_from),extra_native_reuse=bool(a.extra_native_from),fusion_controls=20,x54_controls=8,leaver_premise_words=2,admission_controls=114,bit_controls=12,controller_controls=15,independent_owner_controls=8,outer_inequalities=47,stages=stages,scope=rd(P/'CLAIM.json')['scope']);(work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['kappa_decimal'])
