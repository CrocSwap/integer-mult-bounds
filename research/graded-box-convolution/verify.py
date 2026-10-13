"""Offline exact reconstruction of the graded box-convolution experiment."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
if not __debug__:raise RuntimeError('Assertions must remain enabled')
assert sys.version_info>=(3,11)
assert len(sys.argv)==2,'Usage: python -B verify.py /absolute/new/output'
ROOT=Path(__file__).resolve().parent;OUT=Path(sys.argv[1]).resolve();assert not OUT.exists() and not OUT.is_relative_to(ROOT)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def integrity():
 inv={str(f.relative_to(ROOT)):sha(f)for f in ROOT.rglob('*')if f.is_file()and f!=ROOT/'MANIFEST.json'and '__pycache__'not in f.parts}
 assert inv==read(ROOT/'MANIFEST.json'),'Complete package manifest'
 for name,z in read(ROOT/'SOURCE.json')['files'].items():assert sha(ROOT/name)==z['sha256'],name
integrity();OUT.mkdir();t=time.monotonic();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
with(OUT/'check.log').open('w')as log:r=subprocess.run([sys.executable,'-B',str(ROOT/'code/check.py'),str(OUT/'CHECKS.json')],env=env,stdout=log,stderr=subprocess.STDOUT)
if r.returncode:
 (OUT/'FAILURE.json').write_text(json.dumps(dict(exit_code=r.returncode,log_sha256=sha(OUT/'check.log')),indent=2)+'\n');raise SystemExit(r.returncode)
x=read(OUT/'CHECKS.json');assert x==read(ROOT/'EXPECTED.json'),'Complete deterministic checks differ'
assert x['status']=='PASS_EXACT_GRADED_BOX_CONVOLUTION_AND_WEIGHTED_FIXTURES'
assert len(x['controls'])==5 and len(x['weighted'])==8 and len(x['large_separable_cases'])==2
integrity()
result=dict(status='PASS_GRADED_BOX_CONVOLUTION_PACKAGE',checks_sha256=sha(OUT/'CHECKS.json'),manifest_sha256=sha(ROOT/'MANIFEST.json'),carry_identity_pairs=x['carry_identity_pairs'],invalid_aliases_rejected=x['invalid_flat_aliases_rejected'],actual_integer_products=sum(z['integer_products']for field in ['integer_cases','large_separable_cases','weighted']for z in x[field]),scope=x['scope'])
(OUT/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
(OUT/'RECEIPT.json').write_text(json.dumps(dict(status=result['status'],python=sys.version.split()[0],seconds=time.monotonic()-t,exit_code=r.returncode,artifacts={f:sha(OUT/f)for f in ['CHECKS.json','RESULT.json','check.log']}),indent=2)+'\n');print(result['status'],result['actual_integer_products'],'actual integer products')
