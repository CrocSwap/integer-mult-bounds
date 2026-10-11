"""Full immutable PR401 replay, changed global banks, and fresh bit composition."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,json,os,subprocess,sys,time
assert __debug__
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent/'e8-response-subspaces'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def integrity():
 for directory in (ROOT,SOURCE):
  expected=read(directory/'MANIFEST.json')['files']
  assert {p.relative_to(directory).as_posix():sha(p) for p in directory.rglob('*') if p.is_file() and p!=directory/'MANIFEST.json'}==expected
def main():
 integrity();out=Path(sys.argv[1]).resolve();assert not out.exists() and not out.is_relative_to(ROOT.parent);out.mkdir(parents=True);(out/'tmp').mkdir();checks=[]
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',TMPDIR=str(out/'tmp'));env.pop('PYTHONOPTIMIZE',None)
 for key in list(env):
  if key.startswith(('COMPLEX_','CX_')) or key in ('PR315','HETEROBANKS','BANK_PHASE','BANK_REVIEW'):env.pop(key,None)
 def run(name,file,*args):
  print('RUN',name,flush=True);t=time.monotonic();log=out/(name+'.log')
  with log.open('w') as f:subprocess.run([sys.executable,'-B',str(file),*map(str,args)],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
  checks.append(dict(name=name,seconds=time.monotonic()-t,log_sha256=sha(log)));print('PASS',name,flush=True)
 try:
  run('full-source401',SOURCE/'verify.py',out/'baseline')
  baseline=read(out/'baseline/RESULT.json');assert baseline['status']=='PASS_RESPONSE_SUBSPACES_CONDITIONAL_COMPOSITION'
  run('changed-banks',ROOT/'build.py',out/'baseline',out/'changed')
  result=read(out/'changed/RESULT.json')
  run('fresh-bit',SOURCE/'code/bit-compose-replay.py',out/'bit','--pr381',SOURCE/'vendor/bit','--reuse',SOURCE/'vendor/reuse','--complex',result['complex_coarse'])
  bit=read(out/'bit/BIT-COMPOSITION-RECEIPT.json');assert Q(bit['pricing']['bit_coarse'])==Q(result['bit_coarse'])==Q(baseline['bit_coarse'])
  integrity();result.update(status='PASS_FULL_RESPONSE_BANK64_AND_FRESH_BIT_COMPOSITION',full_checks=checks,manifest_sha256=sha(ROOT/'MANIFEST.json'))
  (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
 except BaseException as e:
  (out/'FAILURE.json').write_text(json.dumps(dict(error=str(e),completed=checks),indent=2)+'\n');raise
if __name__=='__main__':main()
