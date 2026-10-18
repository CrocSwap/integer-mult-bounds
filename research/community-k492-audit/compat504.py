from pathlib import Path
import json,os,hashlib,shutil,subprocess,sys,time
R=Path('/tmp/integer-mult-family588');P=Path('/tmp/im-k492-compat504-package');P.mkdir();shutil.copytree(R/'research/complex-571-cold14-k492/code',P/'code');shutil.copytree(R/'research/complex-571-cold14-e1/data',P/'data')
O=Path('/tmp/im-k492-replay/compat504');O.mkdir();S=R/'research/complex-multicold';V=S/'vendor/pr558/vendor/pr552/complex-global/vendor531';baseline=Path('/tmp/im-cold617-replay/pr617/baseline558');locals_={pid:Path('/tmp/im-cold617-replay/pr615')/(pid+'-local')for pid in ['atm3','jp8']};steps=[]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',MULTICOLD_SOURCE=str(S),GAIN_PR564_SOURCE=str(S),WITNESS_SPEC=str(P/'data/SPEC.json'));env.pop('WITNESS_DISCOVER',None);env.pop('PYTHONOPTIMIZE',None)
def run(name,script,*args):
 log=O/(name+'.log');t=time.monotonic()
 with log.open('w')as f:p=subprocess.run([sys.executable,'-B',str(S/'code/run_portable.py'),str(script),*map(str,args)],stdout=f,stderr=subprocess.STDOUT,env=env)
 steps.append(dict(name=name,exit_code=p.returncode,seconds=time.monotonic()-t,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()));(O/'STAGES.json').write_text(json.dumps(steps,indent=2)+'\n');assert p.returncode==0,(name,log.read_text()[-2000:])
 print('PASS',name,flush=True)
s=(R/'research/complex-571-cold14-k492/verify.py').read_text();a=s.index("G=O/'mixed-global'");b=s.index("X=SPEC['expected']",a);exec(compile(s[a:b],'reviewed-622-global-stages','exec'))
a=json.load(open(O/'ASSEMBLY.json'));b=json.load(open('/tmp/im-cold617-replay/pr615/ASSEMBLY.json'))
for key in ['kappa','complex_lower','complex_profile','provider_counts','bit_lower','conservative_kappa']:assert a[key]==b[key],key
(O/'COMPATIBILITY.json').write_text(json.dumps(dict(status='PASS_492_GLOBAL_CODE_ON_504_PROVIDER_FIXTURE',scope='Global stages only; retained freshly verified 615 locals and 617 baseline; no claim to reproduce contributor scratch revert suite.',compared_fields=['kappa','complex_lower','complex_profile','provider_counts','bit_lower','conservative_kappa'],kappa=a['kappa']),indent=2)+'\n')
