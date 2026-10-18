"""Rebuild the frozen endpoint recipe and run unchanged strict admission."""
import argparse,gzip,hashlib,importlib.util,json,os,shutil,subprocess,sys,time
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1];UP=ROOT/'research/gauge44-slots'
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def payload(p):return hashlib.sha256(gzip.decompress(Path(p).read_bytes())).hexdigest()
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 assert __debug__,'Assertions required'
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--base',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--native-from',type=Path);a=ap.parse_args();work=a.work.resolve();assert not work.exists() and not work.is_relative_to(ROOT)
 for name,h in read(P/'MANIFEST.json').items():assert sha(P/name)==h,('package drift',name)
 for name,h in read(P/'SOURCE-PINS.json').items():assert sha(ROOT/name)==h,('source drift',name)
 work.mkdir(parents=True);env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None);steps=[]
 def run(name,script,*args):
  t=time.monotonic();log=work/(name+'.log')
  with log.open('w') as f:p=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
  steps.append(dict(step=name,exit_code=p.returncode,seconds=time.monotonic()-t,log_sha256=sha(log)));dump(work/'STEPS.json',steps);assert p.returncode==0,(name,log.read_text()[-5000:]);print('PASS',name,flush=True)
 raw=work/'FULL-WORD.json.gz';run('build',P/'build_word.py','--base',a.base.resolve(),'--out',raw)
 assert payload(raw)==read(P/'RECIPE.json')['output_content_sha256']==payload(P/'FULL-WORD.json.gz')
 run('independent-local',UP/'independent/audit_local.py','--word',raw,'--main',ROOT,'--output',work/'AUDIT-LOCAL.json')
 run('end-controls',P/'end_controls.py',work/'END-CONTROLS.json');assert len(read(work/'END-CONTROLS.json')['rejected'])==32
 if a.native_from:native=a.native_from.resolve()
 else:
  native=work/'native';run('native',P/'replay_native.py',raw,native)
 ns=read(native/'STEPS.json');assert [s['step'] for s in ns]==['native','ledgers','local-replay','wrappers','phases'] and all(s['exit_code']==0 for s in ns)
 local=native/'local';assert payload(local/'FULL-WORD.json.gz')==payload(raw)
 ident=module('native_identity',UP/'code/generated_identity.py');plan=read(P/'PLAN.json.gz');assert ident.artifact_identities(local)==plan['provider_registry']['gauge44']['artifact_semantic_sha256']
 runtime=work/'runtime';runtime.mkdir();shutil.copytree(UP/'code',runtime/'code',ignore=shutil.ignore_patterns('__pycache__'));shutil.copytree(UP/'inputs',runtime/'inputs');shutil.copy2(UP/'verify_global.py',runtime/'verify_global.py');(runtime/'data').mkdir()
 for name in ['OWNERS.json.gz','SPEC.json']:shutil.copy2(P/name,runtime/'data'/name)
 (runtime/'data/PLAN.json').write_bytes(gzip.decompress((P/'PLAN.json.gz').read_bytes()))
 shutil.copy2(UP/'data/UPSTREAM-PINS.json',runtime/'data/UPSTREAM-PINS.json');recipe=Path(read(P/'SPEC.json')['pivot_swap']['recipe']);assert not recipe.is_absolute() and '..' not in recipe.parts;(runtime/recipe).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(UP/recipe,runtime/recipe)
 run('strict-global',runtime/'verify_global.py','--main',ROOT,'--local',local,'--work',work/'global')
 result=read(work/'global/ASSEMBLY.json');claim=read(P/'CLAIM.json');assert result['kappa_decimal']==claim['kappa_decimal'];assert result['complex_profile']==plan['profile'];assert len(result['outer'])==47
 from fractions import Fraction as F
 assert F(result['kappa'])>F(claim['previous_kappa']);assert all(F(v)>0 for v in result['outer'].values());controls=read(work/'global/ADMISSION-CONTROLS.json');bit=read(work/'global/BIT-SUPPLIER-CONTROLS.json');assert len(controls['rejected_controls'])==69 and len(bit['rejected_controls'])==12
 receipt=dict(status='PASS_K8_EIGHT_RANK7_ENDS_COMPLETE_ADMISSION',kappa_decimal=result['kappa_decimal'],complex_lower=result['complex_lower'],bit_lower=result['bit_lower'],previous_kappa=claim['previous_kappa'],end_controls=32,admission_controls=69,bit_supplier_controls=12,outer_strict_inequalities=47,native_steps=ns,native_reuse=bool(a.native_from),native_semantic_artifacts=ident.artifact_identities(local),assembly_sha256=sha(work/'global/ASSEMBLY.json'),scope=result['scope'],steps=steps);dump(work/'RESULT.json',receipt);print(receipt['status'],receipt['kappa_decimal'])
if __name__=='__main__':main()
