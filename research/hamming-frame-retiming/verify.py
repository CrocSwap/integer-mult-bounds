"""Fresh source replay, exact retiming, phase and emitted-program admission."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time
from fractions import Fraction as Q
assert __debug__
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent/'hamming-mutable-basis-complex';out=Path(sys.argv[1]).resolve();assert not out.exists();out.mkdir(parents=True)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def integrity():
 assert {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and p.name!='MANIFEST.json'}==read(ROOT/'MANIFEST.json')['files']
 assert sha(SOURCE/'MANIFEST.json')==read(ROOT/'SOURCE.json')['manifest_sha256']
 for name,digest in read(SOURCE/'MANIFEST.json').items():assert sha(SOURCE/name)==digest
integrity();checks=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
import runpy
compat=ROOT/'compat';runpy.run_path(str(compat/'sitecustomize.py'));env['PYTHONPATH']=str(compat)+os.pathsep+env.get('PYTHONPATH','')
def run(name,file,args=(),cwd=None):
 print('RUN',name,flush=True);t=time.monotonic();log=out/(name+'.log')
 with log.open('w') as f:subprocess.run([sys.executable,'-B',str(file),*map(str,args)],cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 checks.append(dict(name=name,seconds=time.monotonic()-t,log_sha256=sha(log)));print('PASS',name,flush=True)
try:
 run('source425',SOURCE/'verify.py',['--work',out/'baseline'])
 assert read(out/'baseline/REPLAY.json')['status']=='PASS_FRESH_OFFLINE_STRUCTURAL_HAMMING_REPLAY'
 work=out/'changed';shutil.copytree(out/'baseline',work);net=work/'work/complex-network';w=net/'hamming'
 # Remove parent PASS receipts and generated artifacts before changed replay.
 for p in w.iterdir():
  if p.is_file() and p.name not in ('PROOF.txt',):p.unlink()
 for name in ('REPLAY.json','EXPECTED.json'):(work/name).unlink()
 run('construct',ROOT/'construct.py',[out/'baseline/work/complex-network/hamming/FULL-WORD.json.gz',w/'FULL-WORD.json.gz'])
 run('scalar-frames',net/'audit_full.py',cwd=work)
 run('exact-phases',net/'phase_full.py',cwd=work)
 run('physical-invoice-assembly',ROOT/'integrate.py',cwd=work)
 run('independent-emitted-replay',net/'replay_ir.py',cwd=work)
 a=read(w/'INTEGRATION.json');i=read(w/'INDEPENDENT-REPLAY.json');price=read(ROOT/'PRICE.json')
 assert i['status']=='PASS_INDEPENDENT_NEW_STRUCTURAL_IR_REPLAY'
 assert Q(a['prospective_kappa'])==Q(price['kappa'])>Q(read(out/'baseline/REPLAY.json')['conditional_kappa'])
 assert Q(a['complex_b'])==Q(price['complex_b']) and Q(a['bit_c'])==Q(price['bit_c']);integrity()
 (out/'RESULT.json').write_text(json.dumps(dict(status='PASS_FULL_HAMMING_FRAME_RETIMING_AND_SOURCE425_REPLAY',kappa=a['prospective_kappa'],complex_b=a['complex_b'],bit_c=a['bit_c'],checks=checks,manifest_sha256=sha(ROOT/'MANIFEST.json'),scope='Conditional PR425 scalar interface and inherited all-size compiler and analytic assumptions. Bit supplier remains inherited from PR425; no new standalone bit proof.'),indent=2)+'\n')
except BaseException as e:
 (out/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),checks=checks),indent=2)+'\n');raise
