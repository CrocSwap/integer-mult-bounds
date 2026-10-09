"""Exact retained assembly for the separately checked frame candidate."""
import sys,json
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
import paired_cube_network as n
from paired_cube_assembly import assembly
row=json.loads((ROOT/'certificates/paired-cube-complex-input.json').read_text());phys=json.loads((OUT/'selected/sinks-profile.json').read_text());p=n.physical_profile(phys,row)
logs={r:n.log_upper(Q(p['m'],r)) for r in p['child_multiplicities']}
def upper(a):return sum(Q(k*r,p['W_per_vertex']*p['m'])*n.exp_upper(a*logs[r]) for r,k in p['child_multiplicities'].items())
grid=10**14;lo,hi=0,grid//100
while hi-lo>1:
 mid=(hi+lo)//2
 if upper(Q(mid,grid))<1:lo=mid
 else:hi=mid
n.AC=Q(lo,grid);assert upper(n.AC)<1 and upper(Q(hi,grid))>=1
c=n.complex_certificate(row,phys)
bitrow=json.loads((ROOT/'research/paired-cube-bit/out/profile_p12.json').read_text());bitphys=json.loads((ROOT/'certificates/paired-cube-bit-physical-input.json').read_text());b=n.bit_certificate(bitrow,bitphys)
bridge=n.finite_bridge(c,b,row)
# Retain every assembly parameter and strict backoff of PR168.
a=min(n.AB,(1-n.PHASE_STOP)*n.AC-Q(1,10**10));dummy=assembly(a,n.AC,bridge,Q(0),beta=n.PHASE_STOP);kg=10**14;mi=dummy['minimum_margin'];k=Q((mi.numerator*kg-1)//mi.denominator,kg)
audit=assembly(a,n.AC,bridge,k,beta=n.PHASE_STOP)
result=dict(kappa=k,complex_saving=n.AC,next_complex_grid=Q(hi,grid),next_complex_upper=upper(Q(hi,grid)),bit=b,complex=c,finite_bridge=bridge,assembly=audit,source_commit='4a3c769e5c5430e7114c4d3e099ff34664677f17',status='exact_arithmetic_pass_physical_check_separate')
assert n.js(result)==json.loads((OUT/'certificate.json').read_text()), 'Frozen exact arithmetic differs'
print('kappa',k,float(k),'complex',n.AC,float(n.AC),'relative_to_PR168',float(k/Q(6558894,10**10)-1))
