"""Physical replay and exact paid comparison for coordinate refinement of PR84.
Rohan Arun with OpenAI Codex assistance; Apache-2.0.
"""
import sys
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from math import comb
from hashlib import sha256
import gzip,json,subprocess,tempfile,os,shlex
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts/experiments'))
from indexed_cycle_nodeops import relabel
from indexed_cycle_compose import check_sources,finite_bridge
from indexed_cycle_compiler import compile_axis
from pin_indexed_cycle_sources import required_paths
from binary_frame_replay import replay
from binary_frame_profile_prepare import prepare
from split_pair_arithmetic import refine,audit
import binary_frame_math as arithmetic

def required():
 return required_paths()|{'research/indexed-cycle/SOURCE.json','certificates/indexed-cycle-kappa.json','.github/workflows/indexed-coordinate-refinement.yml'}|{str(p.relative_to(ROOT))for p in HERE.iterdir()if p.is_file() and p.name not in ('SOURCE.json','validation.json')}
def sources():
 check_sources();manifest=json.loads((HERE/'SOURCE.json').read_text());assert required()<=set(manifest['files'])
 for name,digest in manifest['files'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name

def combine(profiles):
 N=comb(23,3)*comb(25,3);m=575;W=2*N+sum(N//p['v']*p['R']for p in profiles);L=sum(N//p['v']*p['loss']for p in profiles)
 assert sorted(p['h']for p in profiles)==[23,25]
 rows=Counter({1:19*N,21:2*N,17:2*N,481:2*N})
 for p in profiles:
  h=p['h'];assert p['v']==comb(h,3) and p['loss']==h*(h-1) and p['crt_disagreements']==0
  assert sum(t*n for t,n in enumerate(p['blocks']))==h*p['R']+p['loss']==p['rank_sum']
  rep=N//p['v'];bank=rep*p['R'];rows.update({t:n*rep for t,n in enumerate(p['blocks'])if t and n});rows[h]+=bank;rows[m-2*h]+=bank;rows[1]+=2*N;rows[h-2]+=2*N
 bit=dict(m=m,N=N,W=W,L=L,total_rank=sum(t*n for t,n in rows.items()),child_multiplicities=dict(sorted(rows.items())))
 assert bit['total_rank']==m*W-N+L
 return bit

def exact(profiles,certificate=None):
 cert=certificate or json.loads((HERE/'certificate.json').read_text());bit=combine(profiles);assert arithmetic.js(bit)==cert['bit']
 saving=Q(cert['bit_saving']);grid=Q(1,10**18);m=bit['m'];W=bit['W'];rows=bit['child_multiplicities']
 moment=refine.exact_moment(m,W,rows,saving);rejected=refine.exact_moment(m,W,rows,saving+grid)
 assert moment['upper']<1<rejected['lower'];assert arithmetic.js(moment)==cert['exact_moment'] and str(rejected['lower'])==cert['next_grid_lower']
 independent=audit.independent_moment(arithmetic.js(bit),saving,arithmetic.js(moment['terms']));negative=audit.independent_moment(arithmetic.js(bit),saving+grid,arithmetic.js(rejected['terms']));assert independent[1]<1<negative[0]
 bridge=finite_bridge(W);assert arithmetic.js(bridge)==cert['finite_bridge'];assembly=refine.assemble(bridge,saving,Q(1,10**12),10**18);assert arithmetic.js(assembly)==cert['assembly'] and str(assembly['kappa'])==cert['kappa']
 assert len(assembly['assembly']['constraints'])==47 and all(v>0 for v in assembly['assembly']['constraints'].values())
 assert len(assembly['assembly']['margins'])==7 and all(v>assembly['kappa']for v in assembly['assembly']['margins'].values())
 prior=json.loads((ROOT/'certificates/indexed-cycle-kappa.json').read_text());old=prior['bit'];lower=refine.exact_moment(old['m'],old['W'],{int(t):n for t,n in old['child_multiplicities'].items()},saving)['lower']
 assert lower>1 and str(lower)==cert['prior_complete_profile_exclusion_lower'] and assembly['kappa']>Q(prior['kappa'])
 print('PASS exact kappa',assembly['kappa'],'47 constraints, seven margins, two next-grid controls and complete PR84 profile exclusion',flush=True)

def verify(regenerate=False):
 sources();profiles=[]
 with tempfile.TemporaryDirectory(prefix='indexed-coordinate-')as directory:
  work=Path(directory);exe=work/'profiles';subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),str(ROOT/'scripts/experiments/binary_frame_profiles.cpp'),'-o',str(exe)],check=True)
  for h in (23,25):
   parent=json.loads(gzip.decompress((ROOT/f'certificates/indexed-cycle-word-{h}.json.gz').read_bytes()))
   if regenerate:
    _,rebuilt=compile_axis(h);rebuilt_raw=(json.dumps(rebuilt,separators=(',',':'))+'\n').encode();assert rebuilt_raw==gzip.decompress((ROOT/f'certificates/indexed-cycle-word-{h}.json.gz').read_bytes()),'Inherited compiler regeneration differs'
   permutation=json.loads((HERE/f'permutation-{h}.json').read_text());word=relabel(parent,permutation);raw=(json.dumps(word,separators=(',',':'))+'\n').encode();assert raw==gzip.decompress((HERE/f'word-{h}.json.gz').read_bytes())
   path=work/f'word-{h}.json';path.write_bytes(raw);receipt=replay(path);assert arithmetic.js(receipt)==json.loads((HERE/f'replay-{h}.json').read_text())
   trans=work/f'transitions-{h}.bin';prepare(path,trans);subprocess.run([str(exe),str(trans)],check=True)
   profile=json.loads(Path(str(trans)+'.profiles.json').read_text());assert profile==json.loads((HERE/f'profiles-{h}.json').read_text());profiles.append(profile);print('PASS complete coordinate-refined axis',h,flush=True)
 exact(profiles)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--regenerate',action='store_true');a=p.parse_args();verify(a.regenerate)
