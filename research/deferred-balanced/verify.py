"""Exact refinement of PR97 and transfer to the inherited balanced layout.
Zhihao Chen and Swapnil Jain supply all physical networks and signed interfaces.
This composition: Rohan Arun with OpenAI Codex assistance; Apache-2.0.
"""
import sys
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import ast,json,copy,importlib.util,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PARENT=ROOT/'research/deferred-signed'
import moments
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
upstream=load('deferred97_verifier',PARENT/'verify.py')
original=load('deferred97_original_assembly',ROOT/'scripts/structured_bulk_assembly.py')
balanced=load('deferred_balanced_assembly',ROOT/'research/copied-fixed/balanced_assembly.py')
js=moments.arithmetic.js

def rational(x):
 if isinstance(x,dict):return {k:rational(y)for k,y in x.items()}
 if isinstance(x,list):return [rational(y)for y in x]
 if isinstance(x,str):
  try:return Q(x)
  except ValueError:return x
 return x

def required():
 return set(json.loads((PARENT/'SOURCE.json').read_text())['files'])|{
  'research/deferred-signed/SOURCE.json','research/copied-fixed/balanced_assembly.py',
  'research/copied-fixed/PROOF.md','.github/workflows/deferred-balanced.yml'}|{str(p.relative_to(ROOT)) for p in (ROOT/'references/copied-fixed/pr34').rglob('*') if p.is_file()and '__pycache__'not in p.parts and p.suffix not in('.pyc','.pyo')}|{
  str(p.relative_to(ROOT))for p in HERE.rglob('*')if p.is_file()and '__pycache__'not in p.parts and p.suffix not in('.pyc','.pyo')and p!=HERE/'SOURCE.json'and p!=HERE/'validation.json'}

def sources():
 upstream.verify_pins()
 c=json.loads((HERE/'SOURCE.json').read_text());assert required()<=set(c['files'])
 for name,digest in c['files'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
 # Only unavailable log artifacts may differ from the original PR97 manifest.
 before=json.loads((HERE/'pr97-source-manifest.json').read_text());after=json.loads((PARENT/'SOURCE.json').read_text());assert set(before['files'])==set(after['files'])
 receipt=json.loads((HERE/'log-recovery.json').read_text());assert receipt['status']=='passed'
 replaced={f'research/deferred-signed/validation-prior/{stage["name"]}-replay.log':stage for stage in receipt['stages']}
 for name,digest in before['files'].items():
  if name in replaced:
   assert replaced[name]['returncode']==0 and after['files'][name]==replaced[name]['log_sha256']
  else:assert after['files'][name]==digest,('changed original input',name)
 # Exact function bodies are copied, not silently rewritten arithmetic.
 def bodies(path):
  text=path.read_text();return {n.name:ast.get_source_segment(text,n)for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
 actual=bodies(HERE/'moments.py')
 for file,names in [('refine.py',('floor_scaled','ceiling_scaled','exact_moment')),('audit.py',('log_interval','independent_moment'))]:
  expected=bodies(HERE/'arithmetic-sources'/file)
  for name in names:assert actual[name]==expected[name],name

def physical_profiles():
 bit=upstream.read(PARENT/'round7-literal-ledger/result.json');cx=upstream.read(PARENT/'round6-complex-literal-ledger/result.json')
 assert all(bit[k]for k in('complete_forward_F2','complete_reflected_F2','reflected_frame_continuity','histogram_matches_external'))
 assert all(cx[k]for k in('actual_forward_equal_frames','reflected_continuity','actual_geometry_passed','histogram_matches_pinned'))
 H={int(t):n for t,n in bit['histogram'].items()};C={int(t):n for t,n in cx['full_histogram'].items()}
 assert sum(t*n for t,n in H.items())==57403754177 and sum(t*n for t,n in C.items())==119453132304
 return H,C

def bridge():
 c=rational(upstream.read(PARENT/'round7-balanced-assembly-candidate.json'));f=copy.deepcopy(c['bridge'])
 for kind in('bit','complex'):f[kind]['wire_bits']=f[kind]['W'].bit_length()
 f['complex']['scalar_group_upper']=c['scalar_group_bound']
 f['semantic']['induction_gap']=2*f['semantic']['B']*(f['complex']['m']-f['complex']['maxchild'])-f['complex']['s']-f['semantic']['E']
 f['rows']['suffix_slope']=4*f['rows']['degree']
 balanced.validate_bridge(f)
 return f,c

def exact(certificate=None):
 raw=certificate or upstream.read(HERE/'certificate.json');c=rational(raw);H,C=physical_profiles();f,prior=bridge();grid=Q(1,10**18)
 assert original.assembly(Q(31987,500000000),Q(36926111,500000000000),prior['bridge'],Q(63965813,10**12),eta=Q(1,10**8),beta=Q(1,10))==prior['assembly']
 for key,m,W,rows in [('bit',529,108516254,H),('complex',576,207387136,C)]:
  a=c[key]['saving'];accepted=moments.exact_moment(m,W,rows,a);rejected=moments.exact_moment(m,W,rows,a+grid)
  assert accepted['upper']<1<rejected['lower'];assert js(accepted)==raw[key]['moment'] and rejected['lower']==c[key]['rejected_lower']
  profile=dict(m=m,W=W,child_multiplicities=rows)
  independent=moments.independent_moment(profile,a,js(accepted['terms']));negative=moments.independent_moment(profile,a+grid,js(rejected['terms']))
  assert independent[1]<1<negative[0]
 a=c['bit']['saving'];ac=Q(36926111,500000000000);eta=Q(1,10**12)
 assert ac<=c['complex']['saving']
 same=original.assembly(a,ac,prior['bridge'],c['same_interface']['kappa'],eta=eta,beta=Q(1,10));assert js(same)==raw['same_interface']['assembly']
 try:original.assembly(a,ac,prior['bridge'],c['same_interface']['kappa']+grid,eta=eta,beta=Q(1,10))
 except AssertionError:pass
 else:raise AssertionError('next original-interface grid accepted')
 result=balanced.assembly(f,a,c['balanced_interface']['kappa'],beta=Q(1,10),h=eta,a_complex=ac)
 assert js(result)==raw['balanced_interface']['assembly'] and js(f)==raw['balanced_interface']['bridge']
 assert js(balanced.cutoffs(f,result))==raw['balanced_interface']['eventual_bounds']
 assert len(result['constraints'])==47 and len(result['margins'])==7
 assert all(x>0 for x in result['constraints'].values()) and all(x>c['balanced_interface']['kappa']for x in result['margins'].values())
 try:balanced.assembly(f,a,c['balanced_interface']['kappa']+grid,beta=Q(1,10),h=eta,a_complex=ac)
 except balanced.InvalidAssembly:pass
 else:raise AssertionError('next grid accepted')
 assert c['same_interface']['kappa']>c['pr97'] and c['balanced_interface']['kappa']>c['same_interface']['kappa']
 assert c['balanced_gain_percent']==100*(c['balanced_interface']['kappa']/c['pr97']-1)
 print('PASS two independent complete moments; original-interface kappa',c['same_interface']['kappa'],'balanced kappa',c['balanced_interface']['kappa'],'47 constraints, seven margins and next grids',flush=True)
 return result

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--replay',action='store_true');p.add_argument('--replay-own',action='store_true');args=p.parse_args();sources()
 command=[sys.executable,str(PARENT/'verify.py')]
 if args.replay:command.append('--replay')
 elif args.replay_own:command.append('--replay-own')
 subprocess.run(command,check=True)
 exact()
