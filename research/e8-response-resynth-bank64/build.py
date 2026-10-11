"""Changed target phases, literal scalar invoice, and 64-replica global replay."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,json,subprocess,sys,time
assert __debug__
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent/'e8-response-subspaces';BANK=ROOT.parent/'e8-response-bank64'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 baseline=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();assert not out.exists();out.mkdir(parents=True);checks=[]
 def run(name,file,*args):
  print('RUN',name,flush=True);t=time.monotonic();log=out/(name+'.log')
  with log.open('w') as f:subprocess.run([sys.executable,'-B',str(file),*map(str,args)],stdout=f,stderr=subprocess.STDOUT,check=True)
  checks.append(dict(name=name,seconds=time.monotonic()-t,log_sha256=sha(log)));print('PASS',name,flush=True)
 try:
  run('construct',ROOT/'construct.py',baseline/'reconstructed/candidate.json',out/'reconstructed')
  cp=out/'reconstructed/candidate.json'
  run('changed-local',ROOT/'local_admit.py',cp,out/'local','--helper-baseline',SOURCE/'inputs/helper781.json','--signed-baseline',SOURCE/'inputs/candidate781.json','--deps',SOURCE/'local/deps','--prior-phase',SOURCE/'local/prior-phase')
  run('phase',SOURCE/'architecture/phase.py',cp,SOURCE/'local/deps',baseline/'phase-replay',out/'phase',SOURCE/'architecture/phase-replay.cpp')
  run('expand',BANK/'expand.py',out/'expanded')
  prior=out/'expanded/PRIOR.json.gz';cfg=BANK/'CONFIG.json';phase=out/'phase/RESIDUALS.json';local=out/'local/LOCAL-PROGRAMS.json.gz';banks=out/'banks'
  run('banks',BANK/'banks.py',cp,BANK/'PATTERNS.json',phase,local,out/'local/RESULT.json',prior,SOURCE/'local/deps',banks,SOURCE/'architecture/inputs/DATA-PHASES.json',cfg)
  run('independent-audit',BANK/'audit.py',banks,cp,phase,local,prior,cfg)
  run('bridge',BANK/'bridge.py',banks,cfg)
  run('outer',SOURCE/'code/outer.py',banks/'OUTER-INPUT.json',out/'OUTER.json')
  a=read(banks/'ADMISSION.json');audit=read(banks/'INDEPENDENT-ADMISSION.json');outer=read(out/'OUTER.json')
  assert Q(outer['kappa'])==Q(read(ROOT/'SOURCE.json')['expected_kappa'])>Q(read(BANK/'CONFIG.json')['expected_kappa'])
  assert len(outer['strict_constraints'])==47 and len(audit['structural_controls_rejected'])==8
  result=dict(status='PASS_RESYNTH_BANK64_LOCAL_PHASES_TEMPLATE_INVOICE_AND_PRICE',kappa=outer['kappa'],complex_coarse=outer['complex_coarse'],bit_coarse=outer['bit_coarse'],checks=checks,invoice=a['invoice'],profile=a['profile'],template_sha256=a['template_sha256'],candidate_sha256=sha(cp),scope=outer['scope'])
  (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
 except BaseException as e:
  (out/'FAILURE.json').write_text(json.dumps(dict(error=str(e),completed=checks),indent=2)+'\n');raise
if __name__=='__main__':main()
