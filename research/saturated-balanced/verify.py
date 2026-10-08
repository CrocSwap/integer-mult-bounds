"""Complete integration of PR99 readout saturation with PR97/100 interfaces.
Rohan Arun / OpenAI Codex; original constructions retain their own authors.
"""
import sys
if sys.flags.optimize: raise ValueError('Verification requires assertions')
sys.dont_write_bytecode=True
from pathlib import Path
from fractions import Fraction as Q
import json,hashlib,importlib.util,subprocess,tempfile,shutil,gzip
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PARENT=ROOT/'research/deferred-balanced';VENDOR=HERE/'vendor/pr99'
sys.path.insert(0,str(PARENT))
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
parent=load('saturated_parent100',PARENT/'verify.py');js=parent.js

def required():
 return parent.required()|{'research/deferred-balanced/SOURCE.json','.github/workflows/saturated-balanced.yml'}|{str(p.relative_to(ROOT))for p in HERE.rglob('*')if p.is_file()and '__pycache__'not in p.parts and p.suffix not in('.pyc','.pyo')and p not in(HERE/'SOURCE.json',HERE/'validation.json')}

def sources():
 parent.sources();m=json.loads((HERE/'SOURCE.json').read_text());assert required()<=set(m['files'])
 for name,digest in m['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
 upstream=json.loads((VENDOR/'MANIFEST.json').read_text())
 for name,digest in upstream['sha256'].items():assert hashlib.sha256((VENDOR/name).read_bytes()).hexdigest()==digest,name
 return len(m['files'])

def profile(ledger=None):
 c=json.loads((HERE/'bit-ledger.json').read_text())if ledger is None else ledger
 assert all(c[k]for k in('complete_forward_F2','complete_reflected_F2','reflected_frame_continuity','all_scalar_gates_equal_frame_keys','histogram_matches_external'))
 H={int(w):n for w,n in c['histogram'].items()};old,_=parent.physical_profiles()
 assert all(type(w)is int and type(n)is int and 0<w<529 and n>0 for w,n in H.items())
 delta={w:H.get(w,0)-old.get(w,0)for w in set(H)|set(old)if H.get(w,0)!=old.get(w,0)}
 assert delta=={1:-177100,507:-31878,509:-24794,511:56672},delta
 assert c['roles']==28866 and c['formal_basis']==32408
 assert sum(w*n for w,n in H.items())==c['recursive_rank']==57403754177
 expected=json.loads((VENDOR/'experiments/round7-review/saturation-results.json').read_text())['Z']['histogram']
 assert H==dict(expected['hist'])and expected['m']==529 and expected['W']==108516254
 return H

def arithmetic(raw=None):
 raw=json.loads((HERE/'certificate.json').read_text())if raw is None else raw;c=parent.rational(raw);H=profile();a=c['saving'];k=c['kappa'];grid=Q(1,10**18)
 accepted=parent.moments.exact_moment(529,108516254,H,a);rejected=parent.moments.exact_moment(529,108516254,H,a+grid)
 assert accepted['upper']<1<rejected['lower'];assert js(accepted)==raw['moment']and rejected['lower']==c['next_saving_lower']
 p=dict(m=529,W=108516254,child_multiplicities=H)
 assert parent.moments.independent_moment(p,a,js(accepted['terms']))[1]<1
 assert parent.moments.independent_moment(p,a+grid,js(rejected['terms']))[0]>1
 f,_=parent.bridge();r=parent.balanced.assembly(f,a,k,beta=Q(1,10),h=Q(1,10**12),a_complex=Q(36926111,500000000000));assert js(r)==raw['assembly'];assert len(r['constraints'])==47 and len(r['margins'])==7
 assert all(x>0 for x in r['constraints'].values())and all(x>k for x in r['margins'].values())
 assert js(parent.balanced.cutoffs(f,r))==raw['eventual_bounds']
 try:parent.balanced.assembly(f,a,k+grid,beta=Q(1,10),h=Q(1,10**12),a_complex=Q(36926111,500000000000))
 except parent.balanced.InvalidAssembly:pass
 else:raise AssertionError('next kappa accepted')
 old=Q(63978919675787,10**18);assert k>old and c['gain_vs100_percent']==100*(k/old-1)
 print('PASS complete paid delta; independent exact moments; next grids; 47 constraints; seven margins; kappa',k,flush=True)
 return r

def replay(full=False):
 # Rebuild the original signed complex word and baseline physical interface.
 subprocess.run([sys.executable,str(PARENT/'verify.py'),'--replay'if full else'--replay-own'],check=True)
 with tempfile.TemporaryDirectory(prefix='saturated-balanced-')as t:
  out=Path(t);vendor=out/'pr99';shutil.copytree(VENDOR,vendor)
  command=[sys.executable,str(vendor/'verify.py')]
  if full:command.append('--full')
  subprocess.run(command,check=True)
  # Execute Chen's original ledger with changed data only. Every gate, frame
  # movement, reflected event, incidence and paid rank is still reconstructed.
  ledger=load('saturated_literal97',ROOT/'research/deferred-signed/round7_literal_frame_ledger.py')
  W,_=ledger.dr.load(23)
  with gzip.open(vendor/'experiments/round7-review/saturated-Z.json.gz','rt')as f:candidate=json.load(f)
  old_load=ledger.dr.load;old_here=ledger.HERE
  try:
   ledger.dr.load=lambda h=23:(W,candidate);ledger.HERE=out;ledger.main()
  finally:ledger.dr.load=old_load;ledger.HERE=old_here
  actual=json.loads((out/'round7-literal-ledger/result.json').read_text());expected=json.loads((HERE/'bit-ledger.json').read_text())
  assert parent.upstream.stable(actual)==parent.upstream.stable(expected),'complete ledger drift'
  profile(actual)
 print('PASS fresh PR99 rational review and PR97 full forward/reflected candidate ledger',flush=True)

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');p.add_argument('--arithmetic-only',action='store_true');args=p.parse_args();print('PASS',sources(),'source pins',flush=True)
 if not args.arithmetic_only:replay(args.full)
 arithmetic()
