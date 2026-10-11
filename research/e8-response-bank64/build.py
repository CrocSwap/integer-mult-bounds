"""Fresh global packing and exact invoice from source-bound local replay files."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,json,os,subprocess,sys,time
assert __debug__
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent/'e8-response-subspaces'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 baseline=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();assert not out.exists();out.mkdir(parents=True);checks=[]
 def run(name,file,*args):
  print('RUN',name,flush=True);t=time.monotonic();log=out/(name+'.log')
  with log.open('w') as f:subprocess.run([sys.executable,'-B',str(file),*map(str,args)],stdout=f,stderr=subprocess.STDOUT,check=True)
  checks.append(dict(name=name,seconds=time.monotonic()-t,log_sha256=sha(log)));print('PASS',name,flush=True)
 try:
  run('expand',ROOT/'expand.py',out/'expanded')
  cp=baseline/'reconstructed/candidate.json';phase=baseline/'phase/RESIDUALS.json';local=baseline/'local/LOCAL-PROGRAMS.json.gz';prior=out/'expanded/PRIOR.json.gz';cfg=ROOT/'CONFIG.json'
  run('banks',ROOT/'banks.py',cp,ROOT/'PATTERNS.json',phase,local,baseline/'local/RESULT.json',prior,SOURCE/'local/deps',out/'banks',SOURCE/'architecture/inputs/DATA-PHASES.json',cfg)
  run('independent-audit',ROOT/'audit.py',out/'banks',cp,phase,local,prior,cfg)
  run('bridge',ROOT/'bridge.py',out/'banks',cfg)
  run('outer',SOURCE/'code/outer.py',out/'banks/OUTER-INPUT.json',out/'OUTER.json')
  a=read(out/'banks/ADMISSION.json');audit=read(out/'banks/INDEPENDENT-ADMISSION.json');outer=read(out/'OUTER.json');config=read(cfg)
  assert Q(outer['kappa'])==Q(config['expected_kappa'])>Q(config['benchmark_kappa']) and len(outer['strict_constraints'])==47 and len(audit['structural_controls_rejected'])==8
  result=dict(status='PASS_FRESH_BANK64_TEMPLATE_INDEPENDENT_AUDIT_INVOICE_AND_PRICE',kappa=outer['kappa'],complex_coarse=outer['complex_coarse'],bit_coarse=outer['bit_coarse'],checks=checks,invoice=a['invoice'],profile=a['profile'],template_sha256=a['template_sha256'],scope=outer['scope'])
  (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
 except BaseException as e:
  (out/'FAILURE.json').write_text(json.dumps(dict(error=str(e),completed=checks),indent=2)+'\n');raise
if __name__=='__main__':main()
