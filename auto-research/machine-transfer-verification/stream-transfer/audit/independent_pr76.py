"""Independent public PR76 scalar/paid-profile/bridge/exact arithmetic audit.

The public certificate retains its `profile` schema. Derived views are in-memory
and explicitly bound to the original Git blob plus immutable PR71 bridge bytes.
No contributor verifier, composer or arithmetic function is imported.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util,json
from math import comb
from pathlib import Path
import subprocess,sys
HERE=Path(__file__).resolve().parent;OUTPUTS=HERE.parents[1]
sys.path.insert(0,str(OUTPUTS));import independent_moment as im;import independent_assembly as ia
PIN='4b716171d4b3122d6b9db93f802751a41a209955';BASE='1bef94fd40a746452548c84a4a8f8834670a3113'
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();r=args.repo.resolve();package=r/'research/round7-scheduling/selected-both'
path=package/'arithmetic.json';raw=path.read_bytes();assert subprocess.check_output(['git','show',PIN+':'+str(path.relative_to(r))],cwd=r)==raw
c=json.loads(raw);p=c['profile'];rows={int(t):n for t,n in p['child_multiplicities'].items()};m,W=p['m'],p['W'];a,k=Q(c['bit_saving']),Q(c['kappa'])
helper=OUTPUTS/'audit/scatter_binding_audit.py';spec=importlib.util.spec_from_file_location('strict_scatter',helper);strict=importlib.util.module_from_spec(spec);spec.loader.exec_module(strict)
result=dict(pin=PIN,candidate_path=str(path.relative_to(r)),candidate_sha256=sha256(raw).hexdigest(),axes=[],payload='F2',independent_sources={str(f.relative_to(OUTPUTS)):sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),helper,Path(im.__file__),Path(ia.__file__)]})
N=comb(23,3)*comb(25,3);width=2*N;loss=0;parts={'data':Counter({1:18*N,21:2*N,17:2*N,481:2*N}),'paid_endpoint_copy':Counter({1:N})}
for h in [23,25]:
 wp=package/f'word-{h}.json.gz';wr=gzip.decompress(wp.read_bytes());w=json.loads(wr);scatter=strict.verify_scatter(w);v,R=w['v'],w['R'];initial=[1<<i for i in range(2*v+R)]
 M=[(2*v+x,2*v+y) for x,y,_ in w['ops']];J=[tuple(x) for x in w['scatter']];V=[(2*v+s,int(i)) for i,s in w['sources'].items()];word=M+J+M[::-1]+V+M+J+M[::-1]+V
 for dual in [False,True]:
  state=initial.copy()
  for t,s in reversed(word) if dual else word:
   if dual:t,s=s,t
   assert t!=s and 0<=t<len(state) and 0<=s<len(state);state[t]^=state[s]
  expected=initial.copy()
  for i in range(v):expected[i if dual else v+i]^=initial[v+i if dual else i]
  assert state==expected
 profile_path=package/f'profile-{h}.json';fp=json.loads(profile_path.read_text());assert fp==p['axes'][0 if h==23 else 1]
 assert (fp['h'],fp['v'],fp['R'],fp['loss'])==(h,comb(h,3),R,h*(h-1));assert fp['crt_disagreements']==0 and fp['field_prime']==2**61-1
 assert sum(t*n for t,n in enumerate(fp['blocks']))==h*R+h*(h-1)==fp['rank_sum'];assert fp['blocks'][0]==fp['blocks'][h]==0
 rep=N//v;assert rep*v==N;bank=rep*R;width+=bank;loss+=rep*fp['loss']
 parts[f'internal_{h}']=Counter({t:rep*n for t,n in enumerate(fp['blocks']) if t and n});parts[f'exterior_{h}']=Counter({h:bank,575-2*h:bank});parts[f'data_growth_{h}']=Counter({1:2*N,h-2:2*N})
 result['axes'].append(dict(h=h,R=R,basis_size=len(initial),complete_both_orientations=True,raw_word_sha256=sha256(wr).hexdigest(),gzip_sha256=sha256(wp.read_bytes()).hexdigest(),profile_sha256=sha256(profile_path.read_bytes()).hexdigest(),strict_scatter=scatter))
 print('PASS',h,'complete F2 input/dirty bases in both orientations and strict scatter',flush=True)
rebuilt=sum(parts.values(),Counter());mass=sum(t*n for t,n in rebuilt.items());assert rebuilt==rows and width==W and loss==p['L'] and N==p['N'];assert {n:dict(v) for n,v in parts.items()}=={n:{int(t):k for t,k in v.items()} for n,v in p['parts'].items()}
assert mass==p['total_rank']==575*W-N+loss and 575*W-mass==p['deficit']==1846900 and max(rows)==529
lo,hi=im.moment(m,W,rows,a);nlo,nhi=im.moment(m,W,rows,a+Q(1,10**18));assert hi<1<nlo
bridgepath='references/frame-compiler/pr48/research/copied-fixed/certificate.json';bridgebytes=subprocess.check_output(['git','show',BASE+':'+bridgepath],cwd=r);bridge=deepcopy(json.loads(bridgebytes)['finite_bridge'])
bridge['bit']['W']=W;bridge['bit']['wire_bits']=W.bit_length();coefficient=sum(bridge[x]['halving_degree']*bridge[x]['wire_bits'] for x in ['bit','complex']);bridge['rows']['coefficient']=coefficient;bridge['rows']['degree_gap']=Q(bridge['rows']['degree'])-Q(51,25)*coefficient
assert W.bit_length()==27 and coefficient==843 and bridge['rows']['degree_gap']==Q(7007,25)
view=dict(bit={**p,'maxchild':max(rows)},finite_bridge=bridge)
assembly=ia.assemble(view,a,k,Q(1,10**12));public=c['assembly']['assembly'];assert assembly['constraints']=={n:Q(v) for n,v in public['constraints'].items()} and assembly['margins']=={n:Q(v) for n,v in public['margins'].items()}
# A stale width-logarithm field is not silently accepted.
stale=deepcopy(view);stale['finite_bridge']['bit']['wire_bits']=28
try:ia.assemble(stale,a,k,Q(1,10**12))
except ValueError:rejected=True
else:rejected=False
assert rejected
result.update(m=m,W=W,rank_mass=mass,deficit=1846900,child_multiplicities=rows,characteristic=[lo,hi],certified_gap=1-hi,next_saving_characteristic=[nlo,nhi],bit_saving=a,kappa=k,assembly=assembly,finite_bridge=bridge,bridge_base_pin=BASE,bridge_base_path=bridgepath,bridge_base_sha256=sha256(bridgebytes).hexdigest(),stale_wire_bits_rejected=True,scope='Supplied finite words and exact profile/bridge arithmetic; CRT verified separately, all-size physical transfer remains conditional')
args.output.write_text(json.dumps(im.encode(result),indent=2)+'\n');print('PASS independent complete profile, characteristic, bridge width27 and all47 inequalities/seven margins',flush=True)
