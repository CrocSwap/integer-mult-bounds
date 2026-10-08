#!/usr/bin/env python3
"""Actual paid transition profiles and PR71 exact conditional assembly."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from math import comb
from hashlib import sha256
import argparse,gzip,json,math,os,shlex,subprocess,sys
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE/'baseline'
sys.path.insert(0,str(BASE/'scripts/experiments'))
from binary_frame_profile_prepare import prepare
from binary_frame_replay import replay
import binary_frame_math as arithmetic
from split_pair_arithmetic import refine,audit


def main():
 p=argparse.ArgumentParser();p.add_argument('--h',type=int,choices=(23,25),required=True);p.add_argument('--work-dir',type=Path,required=True);p.add_argument('--other-profile',type=Path);p.add_argument('--independent-replay',action='store_true');a=p.parse_args()
 word=a.work_dir/f'word-{a.h}.json.gz';transitions=a.work_dir/f'transitions-{a.h}.bin'
 prepared=prepare(word,transitions)
 if a.independent_replay:
  receipt=replay(word);(a.work_dir/f'replay-{a.h}.json').write_text(json.dumps(receipt,indent=2)+'\n')
 exe=a.work_dir/'profiles'
 subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(BASE/'references/frame-compiler/pr48/scripts/partial_swap'),str(BASE/'scripts/experiments/binary_frame_profiles.cpp'),'-o',str(exe)],check=True)
 subprocess.run([str(exe),str(transitions)],check=True)
 f=json.loads(Path(str(transitions)+'.profiles.json').read_text());(a.work_dir/f'profile-{a.h}.json').write_text(json.dumps(f,indent=2)+'\n')
 axes=[f if h==a.h else json.loads((a.other_profile or BASE/f'certificates/split-pair-profiles-{h}.json').read_text())for h in(23,25)]
 m=575;N=comb(23,3)*comb(25,3);W=2*N+sum(N//v['v']*v['R']for v in axes);L=sum(N//v['v']*v['loss']for v in axes)
 parts={'data':Counter({1:18*N,21:2*N,17:2*N,481:2*N}),'paid_endpoint_copy':Counter({1:N})}
 for v in axes:
  h=v['h'];rep=N//v['v'];bank=rep*v['R']
  assert v['crt_disagreements']==0 and v['field_prime']==2**61-1
  assert v['v']==comb(h,3)and v['loss']==h*(h-1)
  assert v['rank_sum']==sum(t*n for t,n in enumerate(v['blocks']))==h*v['R']+v['loss']
  assert v['blocks'][0]==v['blocks'][h]==0
  parts[f'internal_{h}']=Counter({t:n*rep for t,n in enumerate(v['blocks'])if t and n})
  parts[f'exterior_{h}']=Counter({h:bank,m-2*h:bank})
  parts[f'data_growth_{h}']=Counter({1:2*N,h-2:2*N})
 rows=sum(parts.values(),Counter());mass=sum(t*n for t,n in rows.items());assert mass==m*W-N+L
 low,high=0.,0.001
 for _ in range(60):
  mid=(low+high)/2
  if sum(n*(t/m)**(1-mid)/W for t,n in rows.items())<1:low=mid
  else:high=mid
 den=10**18;k=math.floor(low*den)
 while refine.exact_moment(m,W,rows,Q(k,den))['upper']>=1:k-=1
 while refine.exact_moment(m,W,rows,Q(k+1,den))['upper']<1:k+=1
 bit=Q(k,den);accepted=refine.exact_moment(m,W,rows,bit);excluded=refine.exact_moment(m,W,rows,bit+Q(1,den));assert accepted['upper']<1<excluded['lower']
 bridge=json.loads((BASE/'references/frame-compiler/pr48/research/copied-fixed/certificate.json').read_text())['finite_bridge'];bridge['bit']['W']=W
 assembly=refine.assemble(bridge,bit,Q(1,10**12),den)
 profile=dict(m=m,N=N,W=W,L=L,total_rank=mass,deficit=m*W-mass,child_multiplicities=dict(sorted(rows.items())),parts=parts,axes=axes)
 result=dict(scope='Finite conditional screen; inherited all-size and transfer hypotheses remain.',kappa=assembly['kappa'],bit_saving=bit,profile=profile,moment=accepted,excluded_next_bit=excluded,assembly=assembly,independent_serialized_replay=a.independent_replay,profile_reconstruction=prepared,comparison_pr71=assembly['kappa']-Q(51414646104039,10**18))
 (a.work_dir/'arithmetic.json').write_text(json.dumps(arithmetic.js(result),indent=2)+'\n')
 print(json.dumps(dict(kappa=str(assembly['kappa']),bit_saving=str(bit),kappa_float=float(assembly['kappa']),gain_over_pr71=str(result['comparison_pr71']),roles={v['h']:v['R']for v in axes},W=W,all_47_constraints_and_7_margins=True,independent_serialized_replay=a.independent_replay),indent=2),flush=True)

if __name__=='__main__':main()
