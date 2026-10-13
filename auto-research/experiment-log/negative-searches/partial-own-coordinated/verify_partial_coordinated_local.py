"""Fresh local admission of PR508 coordinated gauges on the verified PR507 factory."""
from pathlib import Path
import json,gzip,shutil,subprocess,os,sys,time,hashlib
R=Path(__file__).resolve().parent;O=R/'partial-coordinated-local';O.mkdir(exist_ok=False);S=R/'source507-review/vendor/complex/e8-complex-gauge-kernel';C=S/'code';B=R/'pr507-local-replay/gauge80-kernel42';name='gauge80-kernel42';D=O/name;D.mkdir();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',LG_BASE=str(O));steps=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.load(open(R/'pr507-async-admission/RECEIPT.json'))['status']=='PASS_PARTIAL_OWN_ASYNC_FINITE_COMPOSITION'
shutil.copytree(B/'work',D/'work');shutil.copytree(B/'sc_base',D/'sc_base');shutil.copy2(B/'BIT-PRICE.json',D/'BIT-PRICE.json');SC=D/'split-centres';SC.mkdir();shutil.copy2(R/'pr507-coordinated-gauge-screen/all-four-WORD.json.gz',SC/'FULL-WORD.json.gz')
def run(tag,script,*args,cwd=D):
 log=O/(tag+'.log');t=time.monotonic();print('RUN',tag,flush=True)
 with log.open('w')as f:q=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT)
 steps.append(dict(name=tag,returncode=q.returncode,seconds=time.monotonic()-t,log_sha256=sha(log)));(O/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n');assert q.returncode==0,(tag,log.read_text()[-5000:]);print('PASS',tag,flush=True)
try:
 run('scalar-frame',C/'audit_gk.py');run('emit',C/'emit_gk.py');run('gaussian',S.parent/'split-centres-global/code/complex_phases_full.py')
 run('adapters',C/'adapters_gk.py',SC/'CANONICAL-WORD.json.gz',SC/'RESIDUAL-ADAPTERS.json',D/'LEMMA-A.json');run('integration',C/'integrate_gk.py');run('readback',C/'replay_gk.py');run('word-mutants',C/'controls_gk.py',SC/'FULL-WORD.json.gz',D/'CONTROLS-WORD.json')
 guards=D/'lemmaG';guards.mkdir();run('labels',C/'lemmaG/run_labels.py',name,cwd=guards)
 for script in ['lg_instances.py','lg_e2e.py']:run('guarded-'+Path(script).stem,R/'source507-review/code/guarded_lemma.py',S,script,name,cwd=guards)
 run('retimed-lemma-mutants',R/'source507-review/code/retimed_lemma_mutants.py',S,O,cwd=guards)
 receipt=dict(status='PASS_FRESH_PARTIAL_COORDINATED_LOCAL',steps=steps,word_sha256=sha(SC/'FULL-WORD.json.gz'),prior_factory_admission_sha256=sha(R/'pr507-async-admission/RECEIPT.json'),scope='Fresh changed-gauge scalar/frame/Gaussian/wrapper and guarded physical local checks. Source factory reused from pinned completed PR507 composition; global asynchronous admission remains separate.')
 (D/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],flush=True)
except BaseException as e:
 (O/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),steps=steps),indent=2)+'\n');raise
