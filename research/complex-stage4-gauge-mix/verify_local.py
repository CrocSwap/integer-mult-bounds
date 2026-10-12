"""Fresh local finite admission for the two mixed-stage words using pinned upstream checks."""
from pathlib import Path
import json,gzip,shutil,subprocess,os,sys,time,hashlib
ROOT=Path(__file__).resolve().parent;R=Path(sys.argv[1]).resolve();O=R/'local';O.mkdir(exist_ok=False);S=ROOT/'vendor/complex/e8-complex-gauge-kernel';C=S/'code';BASE=R/'provider/gauge80-kernel42';P=ROOT;env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',LG_BASE=str(O));steps=[];start=time.monotonic()
def run(name,script,*args,cwd):
 t=time.monotonic();log=O/(name+'.log');print('RUN',name,flush=True)
 with log.open('w') as f:q=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,returncode=q.returncode,seconds=time.monotonic()-t,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()));(O/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n');assert q.returncode==0,(name,log.read_text()[-4000:]);print('PASS',name,flush=True)
try:
 for name,filename in [('baseline','BASE-WORD.json.gz'),('middle','STAGE4-WORD.json.gz')]:
  d=O/name;d.mkdir();shutil.copytree(BASE/'work',d/'work');shutil.copytree(BASE/'sc_base',d/'sc_base');shutil.copy2(BASE/'BIT-PRICE.json',d/'BIT-PRICE.json');sc=d/'split-centres';sc.mkdir();shutil.copy2(P/'data'/filename,sc/'FULL-WORD.json.gz')
  for tag,script in [('scalar',C/'audit_gk.py'),('emit',C/'emit_gk.py'),('gaussian',S.parent/'split-centres-global/code/complex_phases_full.py')]:run(name+'-'+tag,script,cwd=d)
  run(name+'-adapters',C/'adapters_gk.py',sc/'CANONICAL-WORD.json.gz',sc/'RESIDUAL-ADAPTERS.json',d/'LEMMA-A.json',cwd=d)
  for tag,script in [('integrate',C/'integrate_gk.py'),('readback',C/'replay_gk.py')]:run(name+'-'+tag,script,cwd=d)
  run(name+'-word-mutants',C/'controls_gk.py',sc/'FULL-WORD.json.gz',d/'CONTROLS-WORD.json',cwd=d)
  guards=d/'lemmaG';guards.mkdir();run(name+'-labels',C/'lemmaG/run_labels.py',name,cwd=guards)
  for script in ['lg_instances.py','lg_e2e.py']:run(name+'-guarded-'+script[:-3],ROOT/'code/guarded_lemma.py',S,script,name,cwd=guards)
  (d/'RECEIPT.json').write_text(json.dumps(dict(status='PASS_LOCAL_WORD_SCALAR_PHASE_LABEL_GUARDED_PHYSICS',word=filename,steps=[s for s in steps if s['name'].startswith(name+'-')]),indent=2)+'\n')
 (O/'RECEIPT.json').write_text(json.dumps(dict(status='PASS_BOTH_LOCAL_WORDS_NO_MIXED_GLOBAL_ADMISSION',steps=steps,seconds=time.monotonic()-start),indent=2)+'\n')
except BaseException as e:
 (O/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),steps=steps),indent=2)+'\n');raise
