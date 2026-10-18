from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from portable import PACKAGE, output_path, source_name
import banked as b
from fractions import Fraction as F
from pathlib import Path
import json
n,h,hist=30960,17,{17:256,15:560}
groups=[(28800,[1,8,8]),(1920,[9,8]),(13440,[9,6,2]),(560,[15,2]),(256,[17])]
R=sum(count for count,_ in groups)
def built(L,data):
 r=b.base(n,h,hist,L,data)
 for count,profile in groups:
  terms,q,pad=b.helper(r,profile)
  r['terms'] +=[(mass*count,base) for mass,base in terms]
  r['stock']+=F(L*count,q)
 b.c.require(sum(mass for mass,_ in r['terms'])==r['m']*r['stock']-r['deficit'],'encoder mass identity')
 return r
out=[]
for L in (3,5,7,9,11):
 for dn,dp in [('single',[16]),('split2',[1,15]),('units',[1]*16)]:
  r=built(L,dp);lo,hi=b.c.bracket(r)
  result=dict(stages=L,m=r['m'],data_path=dp,helpers=R,stock=str(r['stock']),deficit=r['deficit'],kappa_interval_scaled_1e18=b.c.scaled(lo/(1+lo),hi/(1+hi)),targets=[])
  for factor in (F(1),F(102,100),F(6,5)):
   k=b.c.FRONTIER*factor;a=k/(1-k);pl,ph=b.pressure(r,a)
   target=dict(factor=str(factor),slack_interval_scaled_1e12=b.c.scaled(r['deficit']-ph,r['deficit']-pl,10**12),extra_helpers={})
   for pn,pf in [('single',[17]),('split2',[1,16]),('units',[1]*17)]:
    terms,q,pad=b.helper(r,pf);ul,uh=b.pressure(dict(r,terms=terms),a)
    low=(r['deficit']-ph)/uh;high=(r['deficit']-pl)/ul
    ml=low.numerator//low.denominator;mh=high.numerator//high.denominator
    b.c.require(ml==mh,'exact additional helper count')
    target['extra_helpers'][pn]=max(ml,0)
   result['targets'].append(target)
  out.append(result)
output_path('paid-controller/ENCODER-CONSERVATIVE.json').write_text(json.dumps(out,indent=2)+'\n')
for r in out:
 if r['stages'] in (3,5,7):
  print('L',r['stages'],'data',r['data_path'],'nominal',r['kappa_interval_scaled_1e18'][0]/1e18)
  for t in r['targets']:print(' ',t['factor'],'slack',t['slack_interval_scaled_1e12'][0]/1e12,'extra',t['extra_helpers'])
