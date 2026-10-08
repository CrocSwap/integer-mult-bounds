#!/usr/bin/env python3
"""Independent finite validation of a frozen compiler-exchange witness."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
from collections import Counter
from math import comb
import argparse,json,os,shlex,subprocess,sys,tempfile
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent/'round6-pr71/baseline'
sys.path.insert(0,str(BASE/'scripts/experiments'))
from binary_frame_replay import replay
from binary_frame_profile_prepare import prepare
from split_pair_arithmetic import refine,audit
from width_bridge import bridge_for_width


def main():
 p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 selected=a.bundle.resolve();manifest=json.loads((selected/'MANIFEST.json').read_text())
 for name,digest in manifest['files'].items():assert sha256((HERE/name).read_bytes()).hexdigest()==digest,name
 for name,digest in manifest['baseline_files'].items():assert sha256((BASE/name).read_bytes()).hexdigest()==digest,name
 receipts={}
 with tempfile.TemporaryDirectory(prefix='exchange-validation-')as directory:
  work=Path(directory);exe=work/'profiles'
  subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(BASE/'references/frame-compiler/pr48/scripts/partial_swap'),str(BASE/'scripts/experiments/binary_frame_profiles.cpp'),'-o',str(exe)],check=True)
  for h in(23,25):
   word=selected/f'word-{h}.json.gz';r=replay(word);transitions=work/f'word{h}.bin';prepared=prepare(word,transitions)
   subprocess.run([str(exe),str(transitions)],check=True,capture_output=True,text=True)
   actual=json.loads(Path(str(transitions)+'.profiles.json').read_text());expected=json.loads((selected/f'profile-{h}.json').read_text());assert actual==expected
   receipts[h]=dict(replay=r,transitions=prepared,actual_profiles_equal=True)
 a0=json.loads((selected/'arithmetic.json').read_text());profile=a0['profile'];rows={int(t):n for t,n in profile['child_multiplicities'].items()};bit=Q(a0['bit_saving']);kappa=Q(a0['kappa'])
 actual_axes=[json.loads((selected/f'profile-{h}.json').read_text())for h in(23,25)]
 assert profile['axes']==actual_axes
 N=comb(23,3)*comb(25,3);width=2*N;rebuilt=Counter({1:19*N,21:2*N,17:2*N,481:2*N});loss=0
 for v in actual_axes:
  h=v['h'];rep=N//v['v'];bank=rep*v['R'];width+=bank;loss+=rep*v['loss']
  rebuilt.update({t:rep*n for t,n in enumerate(v['blocks'])if t and n})
  rebuilt.update({h:bank,575-2*h:bank});rebuilt.update({1:2*N,h-2:2*N})
 assert profile['m']==575 and profile['W']==width and rebuilt==rows
 assert sum(t*n for t,n in rebuilt.items())==575*width-N+loss==profile['total_rank']
 accepted=refine.exact_moment(profile['m'],profile['W'],rows,bit);rejected=refine.exact_moment(profile['m'],profile['W'],rows,bit+Q(1,10**18));assert accepted['upper']<1<rejected['lower']
 lower,upper=audit.independent_moment(profile,bit,a0['moment']['terms']);rl,ru=audit.independent_moment(profile,bit+Q(1,10**18),a0['moment']['terms']);assert upper<1<rl
 bridge=json.loads((BASE/'references/frame-compiler/pr48/research/copied-fixed/certificate.json').read_text())['finite_bridge'];bridge=bridge_for_width(bridge,profile['W']);assembly=refine.assemble(bridge,bit,Q(1,10**12),10**18);assert assembly['kappa']==kappa
 result=dict(status='PASS finite source binding, both serialized words, all CRT profiles, rational moment and assembly',manifest_sha256=sha256((selected/'MANIFEST.json').read_bytes()).hexdigest(),axes=receipts,kappa=str(kappa),bit_saving=str(bit),strict_constraints=47,margins=7,independent_moment_and_adjacent_grid=True,scope='Finite conditional witness; inherited all-size and transfer assumptions remain.')
 a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='axes'},indent=2))

if __name__=='__main__':main()
