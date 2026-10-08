"""Exact high-precision comparisons, compounding verified PR65 arithmetic."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from copy import deepcopy
import importlib.util,json,sys,itertools
HERE=Path(__file__).resolve().parent
BASE=HERE
AR=BASE/'research/reordered-rank-pair/arithmetic'
sys.path.insert(0,str(AR))
import refine
N=4073300;m=575

def load(path):
 f=json.loads((path/'profiles.json').read_text());r=json.loads((path/'replay.json').read_text());s=json.loads((path/'result.json').read_text())
 assert f['crt_disagreements']==0 and f['R']==r['roles']==s['roles']
 return f

def counts(profiles):
 W=2*N;L=0;hist=Counter({1:19*N,21:2*N,17:2*N,481:2*N})
 for h,f in profiles.items():
  rep=N//f['v'];bank=rep*f['R'];W+=bank;L+=rep*f['loss']
  assert sum(t*n for t,n in enumerate(f['blocks']))==h*f['R']+f['loss']==f['rank_sum']
  hist.update({t:n*rep for t,n in enumerate(f['blocks']) if t and n});hist.update({h:bank,m-2*h:bank});hist.update({1:2*N,h-2:2*N})
 mass=sum(t*n for t,n in hist.items());assert mass==m*W-N+L
 return dict(m=m,N=N,W=W,L=L,total_rank=mass,deficit=m*W-mass,maxchild=max(hist),child_multiplicities=dict(sorted(hist.items())))

def fine(profiles):
 p=counts(profiles);rows=p['child_multiplicities'];den=10**18;lo=1;hi=6*10**13
 assert refine.exact_moment(m,p['W'],rows,Q(lo,den))['upper']<1<refine.exact_moment(m,p['W'],rows,Q(hi,den))['lower']
 while lo+1<hi:
  mid=(lo+hi)//2;moment=refine.exact_moment(m,p['W'],rows,Q(mid,den))
  if moment['upper']<1:lo=mid
  elif moment['lower']>1:hi=mid
  else:raise ArithmeticError('Enclosure inconclusive')
 a=Q(lo,den);bridge=deepcopy(baseline['finite_bridge']);bridge['bit']['W']=p['W']
 bridge['bit']['wire_bits']=p['W'].bit_length()
 bridge['rows']['coefficient']=sum(bridge[name]['halving_degree']*bridge[name]['wire_bits'] for name in ('bit','complex'))
 bridge['rows']['degree_gap']=Q(bridge['rows']['degree'])-Q(51,25)*bridge['rows']['coefficient']
 bridge['rows']['suffix_slope']=4*bridge['rows']['degree']
 accepted=refine.exact_moment(m,p['W'],rows,a);rejected=refine.exact_moment(m,p['W'],rows,Q(hi,den));assert accepted['upper']<1<rejected['lower']
 ass=refine.assemble(bridge,a,Q(1,10**12),den)
 prior_moment=refine.exact_moment(m,baseline['bit']['W'],{int(t):n for t,n in baseline['bit']['child_multiplicities'].items()},a)
 return dict(kappa=ass['kappa'],bit_saving=a,bit=p,finite_bridge=bridge,accepted_moment=accepted,rejected_moment=rejected,assembly=ass,prior65_moment=prior_moment)

if __name__=='__main__':
 baseline=json.loads((BASE/'research/reordered-rank-pair/paired-candidate.json').read_text())
 original=json.loads((AR/'certificate.json').read_text());prior=Q(original['preferred']['kappa'])
 axes={h:{'anchor65':HERE.parent/'frontier65-search/split-112-anchor'/f'h{h}','anchor67+65schedule':HERE/'split-112-anchor'/f'h{h}'} for h in (23,25)}
 axes[23]['anchor67+nodeschedule']=HERE/'split-112-anchor-node/h23'
 for h in (23,25):
  pending=HERE.parent/'frontier68-search/split-112-anchor-pending'/f'h{h}'
  if (pending/'result.json').exists():axes[h]['anchor67+68+nextusecost']=pending
 rows=[]
 for a,b in itertools.product(axes[23],axes[25]):
  profiles={23:load(axes[23][a]),25:load(axes[25][b])};result=fine(profiles);result['pair']=[a,b];result['paths']={h:str(axes[h][k]) for h,k in [(23,a),(25,b)]};result['roles']={h:f['R'] for h,f in profiles.items()};rows.append(result)
  print(json.dumps({'pair':[a,b],'kappa':str(result['kappa']),'roles':result['roles']},sort_keys=True),flush=True)
 rows.sort(key=lambda r:r['kappa'],reverse=True);best=rows[0]
 assert best['kappa']>prior and best['prior65_moment']['lower']>1
 for r in rows:
  r['moment_at_best_bit']=refine.exact_moment(m,r['bit']['W'],r['bit']['child_multiplicities'],best['bit_saving'])
 output={'verified_baseline':{'pr':65,'commit':'49e84f939d15b618b50714eb039cabf97c74256a','kappa':prior},'best':best,'rows':rows,'cases':len(rows)}
 (HERE/'fine-pair-comparison.json').write_text(json.dumps(refine.arithmetic.js(output),indent=2,sort_keys=True)+'\n')
 (HERE/'selected-exact-result.json').write_text(json.dumps(refine.arithmetic.js(best),indent=2,sort_keys=True)+'\n')
 print('BEST',json.dumps({'pair':best['pair'],'kappa':str(best['kappa']),'bit_saving':str(best['bit_saving']),'W':best['bit']['W'],'gain_percent_vs_verified65':float(100*(best['kappa']/prior-1))},sort_keys=True),flush=True)
