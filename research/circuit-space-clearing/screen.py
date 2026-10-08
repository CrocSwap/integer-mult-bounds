#!/usr/bin/env python3
"""Actual-word profile and exact conditional parameter screen.

Inherited PR57/62 profiling/arithmetic; PR67 baseline by Rohan Arun. New
experiment prepared with substantial OpenAI GPT-6 Astra/Codex assistance.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,importlib.util,json,math,os,shlex,subprocess,sys
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts/experiments'))
from binary_frame_profile_prepare import prepare
from binary_frame_replay import replay
spec=importlib.util.spec_from_file_location('pair_frame_verify',ROOT/'research/pair-assembly/frame/frame_verify.py')
verify=importlib.util.module_from_spec(spec);spec.loader.exec_module(verify)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--work-dir',type=Path,required=True);p.add_argument('--h',type=int,choices=(23,25),required=True);p.add_argument('--other-profile',type=Path);p.add_argument('--independent-replay',action='store_true');a=p.parse_args()
 word=a.work_dir/f'word-{a.h}.json.gz';transitions=a.work_dir/f'transitions-{a.h}.bin'
 prepared=prepare(word,transitions)
 if a.independent_replay:
  receipt=replay(word);(a.work_dir/f'replay-{a.h}.json').write_text(json.dumps(receipt,indent=2)+'\n')
 exe=a.work_dir/'profiles'
 subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),str(ROOT/'scripts/experiments/binary_frame_profiles.cpp'),'-o',str(exe)],check=True)
 subprocess.run([str(exe),str(transitions)],check=True)
 new_profile=json.loads(Path(str(transitions)+'.profiles.json').read_text())
 (a.work_dir/f'profile-{a.h}.json').write_text(json.dumps(new_profile,indent=2)+'\n')
 axes=[new_profile if h==a.h else json.loads((a.other_profile or HERE/f'pr67-profiles-{h}.json').read_text()) for h in (23,25)]
 words=json.loads((ROOT/'research/pair-assembly/frame/frame-compiler.json').read_text())
 profile=verify.profile(axes,words);m,W,rows=profile['m'],profile['W'],profile['child_multiplicities']
 lo,hi=0.,0.001
 for _ in range(60):
  mid=(lo+hi)/2
  if sum(n*(t/m)**(1-mid)/W for t,n in rows.items())<1:lo=mid
  else:hi=mid
 denom=10**14;candidate=math.floor(lo*denom)
 while verify.arithmetic.moment(m,W,rows,Q(candidate,denom))['strict_gap']<=0:candidate-=1
 AB=Q(candidate,denom);moment=verify.arithmetic.moment(m,W,rows,AB)
 bridge=json.loads((verify.OLD/'certificate.json').read_text())['finite_bridge'];bridge['bit']['W']=W
 low,high=1,candidate+1
 while low+1<high:
  mid=(low+high)//2
  try:verify.balanced.assembly(bridge,AB,Q(mid,denom),a_complex=Q(717,10**7));low=mid
  except AssertionError:high=mid
 KAPPA=Q(low,denom);assembly=verify.balanced.assembly(bridge,AB,KAPPA,a_complex=Q(717,10**7))
 result=dict(scope='Focused exact finite screen; independent serialized replay optional; inherited theorem assumptions remain.',numerical_bit_root=lo,bit_saving=AB,kappa=KAPPA,profile=profile,moment=moment,assembly=assembly,profile_reconstruction=prepared,independent_serialized_replay=a.independent_replay)
 (a.work_dir/'arithmetic.json').write_text(json.dumps(verify.arithmetic.js(result),indent=2)+'\n')
 print(json.dumps(dict(numerical_bit_root=lo,bit_saving=str(AB),kappa=str(KAPPA),kappa_float=float(KAPPA),gap=float(moment['strict_gap']),next_kappa_grid_excluded=True,independent_replay=a.independent_replay),indent=2))
