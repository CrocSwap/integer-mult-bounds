"""Bounded registered replay; the complete cold release remains separate."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile
from fractions import Fraction as Q
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
def need(v,m):
 if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 for rel,digest in json.loads((P/'ARTIFACTS.json').read_bytes()).items():
  q=P/rel;need(q.is_file() and not q.is_symlink() and sha(q)==digest,'immutable package input '+rel)
 before={str(p.relative_to(P)):sha(p) for p in P.rglob('*') if p.is_file()}
 with tempfile.TemporaryDirectory(prefix='staged-owner-moment-') as t:
  out=Path(t)/'replay';env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPYCACHEPREFIX=str(Path(t)/'pycache'))
  for k in ('PYTHONOPTIMIZE','PYTHONPATH'):env.pop(k,None)
  r=subprocess.run([sys.executable,'-B',str(P/'check_owners_and_moment.py'),'--repo',str(ROOT),'--word-package',str(ROOT/'research/staged-644-660-width-reduction'),'--out',str(out)],env=env)
  need(r.returncode==0,'fresh owner and moment replay failed')
  result=json.loads((out/'RESULT.json').read_bytes())
  need(result['status']=='PASS_FRESH_FINITE_OWNER_MOMENT_AND_OUTER' and result['roles']==2717280,'fresh full owner check result')
  claim=json.loads((P/'CLAIM.json').read_bytes())
  need(result['profile']==claim['profile'] and result['root_interval']==claim['root_interval'],'fresh complete histogram and root bind claim')
  need(Q(result['kappa'])==Q(claim['kappa'])==Q(claim['kappa_decimal'])>Q('0.00173'),'fresh exact conditional arithmetic binds claim')
 need(all((P/rel).is_file() and sha(P/rel)==digest for rel,digest in before.items()),'package input drift')
 print('PASS_STAGED_PAIR_REGISTERED_OWNER_MOMENT_OUTER')
if __name__=='__main__':main()
