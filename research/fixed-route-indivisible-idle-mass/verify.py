"""Exact bin-pattern dual and interval moment cap. Apache-2.0."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from itertools import product
import json,hashlib,subprocess,importlib.util,sys
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
WIDTHS=(4,5,7,8,9); WEIGHTS=(1,41,15,2,-11); CAP_WEIGHTS={8:-2,16:-4,32:-8,48:41}
def need(ok,msg):
 if not ok: raise ValueError(msg)
def check_pins():
 pins=json.loads((HERE/'SOURCES.json').read_text())
 for s in pins['files']:
  b=subprocess.check_output(['git','cat-file','blob',s['git_blob']],cwd=ROOT)
  need(hashlib.sha256(b).hexdigest()==s['sha256'],'Git pin')
  if s['usage']=='input':need((ROOT/s['path']).read_bytes()==b,'source drift')
def load(n):return json.loads((ROOT/n).read_bytes())
def pattern_audit(widths=WIDTHS,weights=WEIGHTS,coefficient=1961):
 count=0; minimum={}; equality=[]
 for C,cw in CAP_WEIGHTS.items():
  for a in product(*(range(C//w+1) for w in widths)):
   r=C-sum(x*w for x,w in zip(a,widths))
   if r<0:continue
   count+=1
   potential=48*(cw+sum(x*w for x,w in zip(a,weights)))-41*r
   small=r if 0<r<48 else 0
   need(potential>=-coefficient*small,'bin dual inequality')
   minimum[r]=min(potential,minimum.get(r,potential))
   if potential==-1961*small and small:equality.append([C,list(a),r])
 return count,minimum,equality
def main():
 check_pins()
 prefix='research/complex-t16-rare-pattern-exchanges/data/'
 plan=load(prefix+'PLAN.json');spec=load(prefix+'SPEC.json')
 manifest=load('research/community-frontier1094-audit/SELECTED-SOURCE.json')['files']
 for name in (prefix+'PLAN.json',prefix+'SPEC.json'):
  need(manifest[name]==hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),'selected binding')
 calls=len(plan['order']); ports=112
 capacities=Counter()
 for C,times in plan['windows'].values(): capacities[C]+=ports
 inventory={int(w):calls*n for w,n in spec['providers']['gauge44']['inventory'].items()}
 need(dict(capacities)=={8:10752,16:7168,32:7168,48:7168},'capacity inventory')
 need(inventory=={4:8064,5:4608,7:4320,8:17568,9:34560},'helper inventory')
 M=sum(C*n for C,n in capacities.items())-sum(w*n for w,n in inventory.items())
 need(M==237024 and M%48==0,'idle mass')
 n,minimum,equality=pattern_audit()
 aggregate=48*(sum(CAP_WEIGHTS[C]*n for C,n in capacities.items())+sum(q*inventory[w] for w,q in zip(WIDTHS,WEIGHTS)))-41*M
 need(aggregate==-4767456,'aggregate dual')
 mass_lower=Q(-aggregate,1961)
 bound=48*((mass_lower.numerator+48*mass_lower.denominator-1)//(48*mass_lower.denominator))
 need(mass_lower==Q(89952,37) and bound==2448,'integer mass bound')
 # Every nonempty48-bin uses at least4 cells; other capacities are at most32.
 need(min(inventory)==4 and max(c for c in capacities if c<48)==32,'small residual rank cap')
 modulepath=ROOT/'research/complex-local-word-ceiling/ceiling.py'
 s=importlib.util.spec_from_file_location('pinned_ceiling',modulepath); c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
 local={int(k):v for k,v in spec['providers']['gauge44']['expected_profile'].items()}
 # Provider profile includes centre copies through its local-profile definition.
 need(local=={1:2412,2:418,3:432,4:142,5:82,8:8},'local profile')
 def moment(a,forced):
  lo=hi=Q(0)
  for r,num in local.items():
   x,y=c.child_cost(r,73,a);lo+=calls*num*x;hi+=calls*num*y
  for r,mass in [(48,M-forced),(44,forced)]:
   x,y=c.child_cost(r,73,a);lo+=Q(mass,r)*x;hi+=Q(mass,r)*y
  return lo/plan['live'],hi/plan['live']
 def root(forced):
  lo=0;hi=2*10**12
  while hi-lo>1:
   mid=(hi+lo)//2;v=moment(Q(mid,10**15),forced)
   if v[1]<1:lo=mid
   elif v[0]>1:hi=mid
   else:raise ValueError('interval unresolved')
  return [str(Q(lo,10**15)),str(Q(hi,10**15))]
 old=root(0);new=root(bound)
 need(Q(new[1])<Q(old[0]),'strict ceiling improvement')
 baseline=load('research/community-frontier1094-audit/REPLAY.json')
 actual_small=sum(int(r)*n for r,n in baseline['idle_remainder_profile'].items() if int(r)<48)
 need(actual_small==3456 and actual_small>=bound,'selected positive fixture')
 for kwargs in ({'weights':(1,41,15,2,-12)},{'coefficient':1960}):
  try:pattern_audit(**kwargs)
  except ValueError as e:need(str(e)=='bin dual inequality','wrong control rejection')
  else:raise ValueError('unsound dual accepted')
 # Independent exact occupation-count DP checks all reachable widths and minimum weights.
 dp_checks=0
 for C,cw in CAP_WEIGHTS.items():
  dp=[None]*(C+1);dp[0]=0
  for used in range(1,C+1):
   candidates=[dp[used-w]+q for w,q in zip(WIDTHS,WEIGHTS) if used>=w and dp[used-w] is not None]
   if candidates:dp[used]=min(candidates)
  for used,v in enumerate(dp):
   if v is not None:
    r=C-used;small=r if 0<r<48 else 0
    need(48*(cw+v)-41*r>=-1961*small,'independent coin DP');dp_checks+=1
 # Meaningful falsification: a unit helper may occupy47 cells of a48-bin,
 # invalidating the claimed maximum44 for a positive non48 remainder.
 need(48-1>44,'min-width control')
 need(equality and equality[0][2]==1,'sharp per-mass dual control')
 # Rounded-up245? Reject falsely asserting the same bound without indivisibility:
 # fractionally fill every small bin and2230large bins, leaving4938large empty.
 need(sum(C*n for C,n in capacities.items() if C!=48)+2230*48==sum(w*n for w,n in inventory.items()),'fractional all48 fixture')
 payload={'capacity_inventory':dict(sorted(capacities.items())),'helper_inventory':inventory,'idle_mass':M,'patterns':n,'independent_dp_states':dp_checks,'weights':dict(zip(map(str,WIDTHS),WEIGHTS)),'capacity_weights':CAP_WEIGHTS,'aggregate_scaled_potential':aggregate,'unrounded_small_mass_lower':str(mass_lower),'small_mass_lower':bound,'max_small_rank':44,'rank48_root_bracket':old,'indivisible_root_bracket':new,'kappa_upper':str(Q(new[1])/(1+Q(new[1]))),'dual_equality_patterns':equality,'controls':5,'selected_small_mass':actual_small}
 if '--write' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(payload,indent=2)+'\n')
 else:need(json.loads((HERE/'RESULT.json').read_text())==json.loads(json.dumps(payload)),'result mismatch')
 print('PASS_INDIVISIBLE_IDLE_MASS patterns='+str(n)+' small_mass>=2448 root='+str(new))
if __name__=='__main__':main()
