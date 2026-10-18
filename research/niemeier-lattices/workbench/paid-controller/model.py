from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from portable import PACKAGE, output_path, source_name
from fractions import Fraction
from pathlib import Path
import importlib.util,json,math
p=PACKAGE / 'code/costs.py'
s=importlib.util.spec_from_file_location('costs',p);c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
N,H,HIST=30960,17,{17:256,15:560}

def row(stages, data_unit=False):
 r=c.instance(N,H,HIST,stages)
 # No data hosting is assumed; pay each complete idle slot at its true rank.
 r['terms']=[(2*N*stages*(H-1),Fraction(r['m'],1 if data_unit else H-1))]+[(stages*w*n,Fraction(r['m'],w)) for w,n in HIST.items()]+[(2*N*a,Fraction(r['m'],a)) for a in c.idle_slots(stages,H-1)]
 return r

def unit(r,profile,virtual=False):
 width=sum(profile); e=H-width
 if virtual:
  q=(r['m']-e)//width
 else:
  c.require(width==H,'ordinary helper must telescope through H')
  q=r['m']//width
 pad=r['m']-q*width
 # Replicas divisible by q allow no fractional physical families.
 return [(Fraction(r['stages']*v),Fraction(r['m'],v)) for v in profile]+([(Fraction(r['stages']*pad,q),Fraction(r['m'],pad))] if pad else []),q,pad

def rmax(stages,k,profile,virtual=False,data_unit=False):
 r=row(stages,data_unit);a=k/(1-k);lo,hi=c.pressure_bounds(r,a);slack=r['deficit']-hi,r['deficit']-lo
 terms,q,pad=unit(r,profile,virtual)
 ulo=uhi=Fraction(0)
 for mass,base in terms:
  l,h=c.power_bounds(base,a);ulo+=mass*(l-1);uhi+=mass*(h-1)
 low=slack[0]/uhi;high=slack[1]/ulo
 ml,mh=low.numerator//low.denominator,high.numerator//high.denominator
 c.require(ml==mh,'unresolved integer helper bound')
 return dict(stages=stages,m=r['m'],q=q,pad=pad,max_helpers=max(ml,0),helpers_per_port=max(ml,0)/N,stock_at_max=str(r['stock']+Fraction(stages*max(ml,0),q)),deficit=r['deficit'],profile=profile,virtual=virtual)
