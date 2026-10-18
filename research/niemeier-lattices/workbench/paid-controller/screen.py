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

def row(stages):
 r=c.instance(N,H,HIST,stages)
 # No data hosting is assumed; pay each complete idle slot at its true rank.
 r['terms']=[(2*N*stages*(H-1),Fraction(r['m'],H-1))]+[(stages*w*n,Fraction(r['m'],w)) for w,n in HIST.items()]+[(2*N*a,Fraction(r['m'],a)) for a in c.idle_slots(stages,H-1)]
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

def rmax(stages,k,profile,virtual=False):
 r=row(stages);a=k/(1-k);lo,hi=c.pressure_bounds(r,a);slack=r['deficit']-hi,r['deficit']-lo
 terms,q,pad=unit(r,profile,virtual)
 ulo=uhi=Fraction(0)
 for mass,base in terms:
  l,h=c.power_bounds(base,a);ulo+=mass*(l-1);uhi+=mass*(h-1)
 low=slack[0]/uhi;high=slack[1]/ulo
 ml,mh=low.numerator//low.denominator,high.numerator//high.denominator
 c.require(ml==mh,'unresolved integer helper bound')
 return dict(stages=stages,m=r['m'],q=q,pad=pad,max_helpers=max(ml,0),helpers_per_port=max(ml,0)/N,stock_at_max=str(r['stock']+Fraction(stages*max(ml,0),q)),deficit=r['deficit'],profile=profile,virtual=virtual)

out={}
for fac in (Fraction(1),Fraction(101,100),Fraction(102,100),Fraction(6,5)):
 k=c.FRONTIER*fac; rr={}
 for name,profile,virtual in [('single_h',[17],False),('source_copy',[1,16],False),('split3',[1,1,15],False),('unit_steps',[1]*17,False),('virtual_width1',[1],True),('virtual_width2',[2],True)]:
  candidates=[rmax(L,k,profile,virtual) for L in range(3,102,2)]
  best=max(candidates,key=lambda d:d['max_helpers'])
  rr[name]={'best_L3_to101':best,'L3':candidates[0],'L5':candidates[1],'L9':candidates[3]}
 out[str(fac)]=rr
output_path('paid-controller/RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
for factor,cases in out.items():
 print('TARGET',factor)
 for name,d in cases.items():
  b=d['best_L3_to101']; print(name,'best',b['stages'],b['max_helpers'],round(b['helpers_per_port'],3),'L3',d['L3']['max_helpers'])
