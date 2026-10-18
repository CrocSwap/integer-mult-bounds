

"""Network-free full replay of PR433 plus twelve source-bound early resets.
Prepared with OpenAI Codex assistance. Apache-2.0; original notices retained.
"""
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path
assert __debug__, 'Assertions must remain enabled'
assert sys.version_info>=(3,14), 'Python 3.14+ is required for the frozen parent gzip byte encoding'
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();out=a.output.resolve()
assert not out.exists() and not out.is_relative_to(ROOT), 'Use a fresh output outside the package'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot():return {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and p.relative_to(ROOT).as_posix()!='MANIFEST.json'}
m=json.loads((ROOT/'MANIFEST.json').read_text());assert snapshot()==m['files'],'Package integrity mismatch'
out.mkdir(parents=True);env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None);steps=[]
def run(name,*args):
 log=out/(name+'.log');start=time.monotonic();print('RUN',name,flush=True)
 with log.open('w') as f:r=subprocess.run([sys.executable,'-B',*map(str,args)],env=env,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,(name,r.returncode,str(log))
 steps.append(dict(name=name,exit_code=r.returncode,seconds=time.monotonic()-start,log_sha256=sha(log)));print('PASS',name,flush=True)
parent=out/'parent';source=parent/'bit426-source-centres/bit-source-centres.json';word=out/'constructed/bit-source-centres.json';candidate=out/'candidate'
run('parent-full-phase',ROOT/'vendor/pr433/verify.py',parent,'--replay-phases')
run('construct-twelve',ROOT/'constructor/construct.py','--source',source,'--out',out/'constructed')
run('independent-reset-controls',ROOT/'constructor/local_audit.py','--source',source,'--out',out/'LOCAL-AUDIT.json')
run('changed-global-admission',ROOT/'admission/verify.py','--word',word,'--expected-sha256','fc5b2fb84dbbdbcf9b1bb36ebf768f31130dd5a93edec3d12f52c8e4be66ce48','--base-source',ROOT/'vendor/pr433','--complex-proof',parent,'--work',candidate)
run('independent-invoices-outer',ROOT/'code/independent_audit.py',candidate,out/'independent')
r=json.loads((candidate/'RESULT.json').read_text());expected=json.loads((ROOT/'EXPECTED.json').read_text())
for key,value in expected.items():assert r[key]==value,(key,r.get(key),value)
assert snapshot()==m['files'],'Package changed during replay'
receipt=dict(status='PASS_SOURCE_BOUND_R746_FULL_REPLAY',kappa=r['kappa'],kappa_decimal=r['kappa_decimal'],candidate_sha256=sha(word),manifest_sha256=sha(ROOT/'MANIFEST.json'),steps=steps,result_sha256=sha(candidate/'RESULT.json'),independent_sha256=sha(out/'independent/RESULT.json'))
(out/'VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],r['kappa_decimal'],flush=True)
