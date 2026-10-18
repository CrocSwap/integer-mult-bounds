from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from portable import PACKAGE, output_path, source_name
"""Exact all-odd-stage obstruction for the tested unfused Mobius route."""
from fractions import Fraction as F
import hashlib,importlib.util,json
from pathlib import Path
SOURCE=PACKAGE / 'code/costs.py'
s=importlib.util.spec_from_file_location('bounds',SOURCE);c=importlib.util.module_from_spec(s);s.loader.exec_module(c)

def certify(N,h,centers,copies):
 C=h*centers+copies;gap=N-C
 if gap<=0:
  return dict(N=N,h=h,center_bill=C,status='NONPOSITIVE_DEFICIT_FOR_ALL_STAGES',proof='D=L(N-C)-N<0')
 Lmin=3
 while Lmin*gap<=N:Lmin+=2
 delta=F(gap,N);d=h-1;a=c.FRONTIER/(1-c.FRONTIER)
 base=F(d*Lmin+1,d)
 p_lower,p_upper=c.power_bounds(base,a)
 forced_lower=2*d*(p_lower-1)
 c.require(forced_lower>delta,'Active climbs alone rule out every positive-deficit stage')
 # For every positive-deficit stage, active pressure/(LN) is at least
 # 2d*((Lmin+1/d)^alpha-1), while D/(LN)<delta. Solve this weaker
 # necessary condition exactly using rational logarithm enclosures.
 nlo,nhi=c.logarithm(1+delta/(2*d));dlo,dhi=c.logarithm(base)
 alo,ahi=nlo/dhi,nhi/dlo;klo,khi=alo/(1+alo),ahi/(1+ahi)
 c.require(khi<c.FRONTIER,'Global kappa upper bound below frontier')
 return dict(N=N,h=h,center_roles=centers,center_histogram={str(h):centers,'1':copies},center_bill=C,
  center_bill_per_port=str(F(C,N)),gap=gap,first_odd_stage_with_positive_deficit=Lmin,
  deficit_at_previous_odd_stage=(Lmin-2)*gap-N,frontier=str(c.FRONTIER),
  normalized_active_pressure_lower_bound_at_frontier=str(forced_lower),
  normalized_deficit_strict_upper_bound=str(delta),
  global_necessary_kappa_upper_bound_interval_scaled_1e18=c.scaled(klo,khi),
  fraction_of_frontier_upper_bound=str(khi/c.FRONTIER),
  status='FAILS_FRONTIER_FOR_EVERY_ODD_STAGE',
  scope='Necessary bound using active data climbs alone, with no helper costs, center pressure, idle pressure or physical-hosting penalties. Not the optimal root of the full necessary model.')

def run():
 result={'bit_full_shell':certify(30960,16,815,16384),
         'complex_full_shell':certify(30960,17,816,16384),
         'bit_spinor_only':certify(16384,16,576,16384)}
 # The obstruction is specifically to the added output descents: removing
 # them must not pass this same sufficient rejection test at the frontier.
 for h,centers in ((16,815),(17,816)):
  try:certify(30960,h,centers,0)
  except ValueError as error:c.require('Active climbs alone' in str(error),'Expected control failure')
  else:raise ValueError('Control unexpectedly rejects original factor by this bound')
 return dict(status='PASS_EXACT_UNFUSED_MOBIUS_OBSTRUCTION',cases=result,
  source=dict(path=source_name(SOURCE),sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest()),
  negative_controls='Removing the 16384 output descents does not satisfy this rejection test.')
if __name__=='__main__':
 out=run();output_path('paid-controller/unfused/RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 for name,r in out['cases'].items():print(name,r['status'],r.get('global_necessary_kappa_upper_bound_interval_scaled_1e18'))
