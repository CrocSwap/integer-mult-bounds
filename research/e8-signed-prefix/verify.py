"""Offline replay of this fixed changed composition, not upstream PR pipelines."""
from pathlib import Path
from fractions import Fraction as Q
import argparse,concurrent.futures,hashlib,json,os,subprocess,sys,time
assert __debug__, 'Assertions must be enabled'
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);args=ap.parse_args();OUT=args.output.resolve()
assert not OUT.exists() and not OUT.is_relative_to(ROOT);OUT.mkdir(parents=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
manifest=read(ROOT/'MANIFEST.json')
actual={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'MANIFEST.json'}
assert actual==manifest['files'],'Package incomplete or changed; restore manifest-listed files'
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
for key in list(env):
 if key.startswith('COMPLEX_') or key.startswith('CX_') or key=='PR315':env.pop(key,None)
checks=[]
def py(name,file,*args):
 t=time.monotonic();log=OUT/(name+'.log');print('RUN',name,flush=True)
 with log.open('w',encoding='utf-8') as f:p=subprocess.run([sys.executable,'-B',str(ROOT/'code'/file),*map(str,args)],env=env,stdout=f,stderr=subprocess.STDOUT)
 assert p.returncode==0,(name,p.returncode,str(log))
 checks.append(dict(name=name,seconds=time.monotonic()-t,log_sha256=sha(log)));print('PASS',name,flush=True)
try:
 py('reconstruct','reconstruct.py',OUT/'reconstructed')
 def complex_run():py('complex','run-admission.py','--source',ROOT/'vendor/cx','--base',OUT/'reconstructed/base.json','--candidate',OUT/'reconstructed/candidate.json.gz','--output',OUT/'complex')
 def bit_run():py('bit','bit-compose-replay.py',OUT/'bit','--pr381',ROOT/'vendor/bit','--reuse',ROOT/'vendor/reuse','--complex','979981116881/976562500000000')
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  futures=[pool.submit(complex_run),pool.submit(bit_run)]
  for f in futures:f.result()
 cx=read(OUT/'complex/FINAL-ADMISSION.json');bit=read(OUT/'bit/BIT-COMPOSITION-RECEIPT.json')
 assert Q(cx['complex_coarse'])==Q(979981116881,976562500000000)
 x={k:cx[k] for k in ('profile','m','stock','bridge')};x['bit_coarse']=bit['pricing']['bit_coarse'];x['supplier_receipt_sha256']=sha(OUT/'complex/FINAL-ADMISSION.json')
 (OUT/'outer-input.json').write_text(json.dumps(x,indent=2)+'\n')
 py('outer','outer.py',OUT/'outer-input.json',OUT/'OUTER.json');outer=read(OUT/'OUTER.json')
 assert outer['kappa']=='125311832453733/125000000000000000' and len(outer['strict_constraints'])==47
 assert actual=={p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.rglob('*')if p.is_file()and p!=ROOT/'MANIFEST.json'}
 result=dict(status='PASS_SIGNED_PREFIX_CONDITIONAL_COMPOSITION',kappa=outer['kappa'],kappa_decimal='0.001002494659629864',complex_coarse=outer['complex_coarse'],bit_coarse=outer['bit_coarse'],checks=checks,manifest_sha256=sha(ROOT/'MANIFEST.json'),global_template_sha256=cx['global_template_sha256'],scope='Finite conditional construction with explicit inherited all-size assumptions. No Lean certification or unconditional multiplication theorem.')
 (OUT/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['kappa'],flush=True)
except BaseException as e:
 (OUT/'FAILURE.json').write_text(json.dumps({'error':str(e),'completed':checks},indent=2)+'\n');raise
