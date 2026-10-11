"""Full immutable R781 supplier replay, changed composition, and fresh bit replay."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,importlib.util,json,os,subprocess,sys,time
assert __debug__
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent/'e8-r781-signed-source';FUSION=ROOT.parent/'e8-signed-padding';BOOT=ROOT.parent/'e8-prefix-bootstrap'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def integrity():
 manifest=read(ROOT/'MANIFEST.json');assert {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and p.name!='MANIFEST.json'}==manifest
 expected=read(SOURCE/'MANIFEST.json')['files'];assert {p.relative_to(SOURCE).as_posix():sha(p) for p in SOURCE.rglob('*') if p.is_file() and p!=SOURCE/'MANIFEST.json'}==expected
 s=importlib.util.spec_from_file_location('inherited_integrity',FUSION/'verify.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.integrity()
 old=ROOT.parent/'e8-prefix-restoration/public/381/source/research/e8-nine-stage-kappa/complex377/work/odd-stages/clifford_exact.py';assert sha(old)==sha(SOURCE/'vendor/cx/work/odd-stages/clifford_exact.py')
def main():
 out=Path(sys.argv[1]).resolve();integrity();assert not out.exists() and not out.is_relative_to(ROOT.parent);out.mkdir(parents=True);(out/'tmp').mkdir();checks=[]
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',TMPDIR=str(out/'tmp'));env.pop('PYTHONOPTIMIZE',None)
 for key in list(env):
  if key.startswith(('COMPLEX_','CX_')) or key in ['PR315','HETEROBANKS','BANK_PHASE','BANK_REVIEW']:env.pop(key,None)
 def run(name,cmd):
  print('RUN',name,flush=True);t=time.monotonic();log=out/(name+'.log')
  with log.open('w') as f:subprocess.run([str(x) for x in cmd],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
  checks.append(dict(name=name,seconds=time.monotonic()-t,log_sha256=sha(log)));print('PASS',name,flush=True)
 try:
  run('full-r781-supplier',[sys.executable,'-B',SOURCE/'verify.py',out/'baseline'])
  prior=read(out/'baseline/RESULT.json');assert prior['status']=='PASS_SIGNED_PREFIX_CONDITIONAL_COMPOSITION'
  run('heterofusion-global',[sys.executable,'-B',ROOT/'build.py',out/'baseline/reconstructed/candidate.json.gz',out/'baseline/complex/DATA-PHASES.json',out/'changed'])
  result=read(out/'changed/RESULT.json');expected=read(ROOT/'EXPECTED.json')
  for key,value in expected.items():assert result[key]==value,key
  assert len(result['controls_rejected'])==13
  run('fresh-bit-composition',[sys.executable,'-B',SOURCE/'code/bit-compose-replay.py',out/'bit','--pr381',SOURCE/'vendor/bit','--reuse',SOURCE/'vendor/reuse','--complex',result['coarse18']])
  bit=read(out/'bit/BIT-COMPOSITION-RECEIPT.json');assert bit['pricing']['bit_coarse']==prior['bit_coarse']
  sys.path.insert(0,str(BOOT));from refine import refine
  witness=refine(Q(result['coarse_lower']),Q(bit['pricing']['bit_coarse']));assert witness==read(out/'changed/WITNESS.json') and len(witness['negative_controls_rejected'])==6
  assert Q(result['kappa'])>Q(read(ROOT/'SOURCE.json')['benchmark_kappa']);integrity()
  answer=dict(status='PASS_FULL_R781_HETEROFUSION_AND_FRESH_BIT_COMPOSITION',kappa=result['kappa'],kappa_float=result['kappa_float'],checks=checks,strict_constraints=47,controls_rejected=result['controls_rejected'],bootstrap_controls=6,invoice=result['invoice'],scope=result['scope'])
  (out/'RESULT.json').write_text(json.dumps(answer,indent=2)+'\n');print(json.dumps(answer,indent=2),flush=True)
 except BaseException as e:
  (out/'FAILURE.json').write_text(json.dumps(dict(error=str(e),completed=checks),indent=2)+'\n');raise
if __name__=='__main__':main()
