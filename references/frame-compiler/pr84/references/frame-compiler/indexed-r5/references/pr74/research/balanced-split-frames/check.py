#!/usr/bin/env python3
"""Screen complete paid profiles from independently replayed axis constructions."""
import sys
if sys.flags.optimize:raise ValueError('Assertions required')
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
import importlib.util,argparse,json,subprocess,tempfile,hashlib,os,shlex
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
DEP=ROOT/'references/frame-compiler/pr71'
sys.path.insert(0,str(DEP/'scripts/experiments'))
from producer import check_sources
from binary_frame_replay import replay
from binary_frame_profile_prepare import prepare
import binary_frame_math as arithmetic

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
exact=load('candidate_exact',ROOT/'research/rank-pair-refinement/refine.py')
balanced=load('candidate_assembly',DEP/'references/frame-compiler/pr48/research/copied-fixed/balanced_assembly.py')

def profile(path):
 v=json.loads(Path(path).read_text())
 return v['profile'] if 'profile' in v else v

def calculate(first,second):
 profiles=[profile(first),profile(second)]
 N=4073300;m=575
 assert [p['h'] for p in profiles]==[23,25]
 W=2*N+sum(N//p['v']*p['R'] for p in profiles)
 parts={'data':Counter({1:18*N,21:2*N,17:2*N,481:2*N}),'endpoint_copy':Counter({1:N})}
 for p in profiles:
  h=p['h'];rep=N//p['v'];bank=rep*p['R']
  assert p['crt_disagreements']==0
  assert p['rank_sum']==h*p['R']+p['loss']==sum(t*n for t,n in enumerate(p['blocks']))
  assert p['loss']==h*(h-1)
  parts[f'internal_{h}']=Counter({t:n*rep for t,n in enumerate(p['blocks']) if t and n})
  parts[f'exterior_{h}']=Counter({h:bank,m-2*h:bank})
  parts[f'growth_{h}']=Counter({1:2*N,h-2:2*N})
 rows=sum(parts.values(),Counter());assert sum(t*n for t,n in rows.items())==m*W-1846900
 lo,hi,grid=1,71700000000000,10**18
 while lo+1<hi:
  mid=(lo+hi)//2
  if exact.moment(arithmetic,m,W,rows,Q(mid,grid))['upper']<1:lo=mid
  else:hi=mid
 a=Q(lo,grid);accepted=exact.moment(arithmetic,m,W,rows,a);rejected=exact.moment(arithmetic,m,W,rows,Q(hi,grid));assert accepted['upper']<1<rejected['lower']
 bridge=json.loads((DEP/'references/frame-compiler/pr48/research/copied-fixed/certificate.json').read_text())['finite_bridge'];bridge['bit']['W']=W;bridge['bit']['wire_bits']=W.bit_length()
 coefficient=sum(bridge[n]['halving_degree']*bridge[n]['wire_bits'] for n in ('bit','complex'));bridge['rows']['coefficient']=coefficient;bridge['rows']['degree_gap']=str(Q(bridge['rows']['degree'])-Q(51,25)*coefficient)
 pre=balanced.assembly(bridge,a,Q(1,10**8),h=Q(1,grid));k=Q(exact.ceil(pre['minimum_margin']*grid)-1,grid)
 assembly=balanced.assembly(bridge,a,k,h=Q(1,grid))
 try:balanced.assembly(bridge,a,k+Q(1,grid),h=Q(1,grid))
 except balanced.InvalidAssembly:pass
 else:raise AssertionError('next kappa passed')
 result=dict(kappa=k,bit_saving=a,W=W,roles=[p['R'] for p in profiles],profiles=['profile-23.json','profile-25.json'],child_multiplicities=dict(sorted(rows.items())),parts=parts,accepted=accepted,rejected=rejected,assembly=assembly,finite_bridge=bridge)
 print('EXACT',float(k),str(k),'W',W,'roles',result['roles'],'gain71%',float((k/Q('5.1414646104039e-5')-1)*100),flush=True)
 return result


def generate(record=False):
 check_sources()
 selection=json.loads((HERE/'selection.json').read_text())
 axes={}
 with tempfile.TemporaryDirectory(prefix='balanced-split-check-') as directory:
  work=Path(directory);exe=work/'profiles'
  subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(DEP/'references/frame-compiler/pr48/scripts/partial_swap'),str(DEP/'scripts/experiments/binary_frame_profiles.cpp'),'-o',str(exe)],check=True)
  for h in (23,25):
   axis=json.loads((HERE/f'axis-{h}.json').read_text());word=HERE/f'word-{h}.json.gz'
   assert axis['configuration']==selection['axes'][str(h)]
   assert hashlib.sha256(word.read_bytes()).hexdigest()==axis['gzip_sha256']
   actual=json.loads(json.dumps(replay(word)));assert actual==axis['replay']
   assert actual['roles']==axis['compiled']['roles']
   prepared=json.loads(json.dumps(prepare(word,work/f'word-{h}.bin')))
   assert prepared==json.loads((HERE/f'transitions-{h}.json').read_text())
   assert prepared['word_sha256']==axis['word_sha256']==axis['configuration']['expected_word_sha256']
   subprocess.run([str(exe),str(work/f'word-{h}.bin')],check=True)
   physical=json.loads((work/f'word-{h}.bin.profiles.json').read_text())
   assert physical==json.loads((HERE/f'profile-{h}.json').read_text())
   assert physical['R']==actual['roles']
   arithmetic.exactness(h)
   axes[str(h)]=dict(roles=actual['roles'],full_basis_vectors=actual['full_basis_vectors'],crt_disagreements=physical['crt_disagreements'])
   print(f'PASS full dirty replay, literal transitions, exact profiles h={h}',flush=True)
 result=calculate(HERE/'profile-23.json',HERE/'profile-25.json')
 assert result['kappa']==Q('10366199626713/200000000000000000')
 assert result['bit_saving']==Q('25916842362591/500000000000000000')
 assert result['W']==133862024
 previous=json.loads((DEP/'certificates/split-pair-kappa.json').read_text())
 old=previous['bit'];old_rows={int(t):n for t,n in old['child_multiplicities'].items()}
 old_lower=exact.moment(arithmetic,old['m'],old['W'],old_rows,result['bit_saving'])['lower'];assert old_lower>1
 result.update(status='Verified finite conditional witness; inherited all-size transfer remains assumed',
               source_manifest_sha256=hashlib.sha256((HERE/'SOURCE.json').read_bytes()).hexdigest(),
               axes=axes,eventual_bounds=balanced.cutoffs(result['finite_bridge'],result['assembly']),
               comparison=dict(pr71_commit='1bef94fd40a746452548c84a4a8f8834670a3113',pr71_kappa=Q(previous['kappa']),
                               relative_gain_pr71=result['kappa']/Q(previous['kappa'])-1,
                               pr71_complete_profile_exclusion_lower=old_lower))
 result=arithmetic.js(result)
 path=HERE/'certificate.json'
 if record:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 else:assert result==json.loads(path.read_text())
 print('PASS exact moment, next-grid exclusions, 47 inequalities and seven margins',flush=True)
 return result

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--record',action='store_true');args=parser.parse_args();generate(args.record)
