from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from portable import PACKAGE, output_path, source_name
import banked as b
from fractions import Fraction as F
from pathlib import Path
import json

def built(h,centers,L,target):
 n=30960;r=b.base(n,h,{h:centers},L,[h-1])
 r['terms'][0:1]=[(F(n*L*(h-1)),F(r['m'],h-1))]+[(F(n*L*a),F(r['m'],a)) for a in target]
 terms,q,pad=b.helper(r,[h]);r['terms'] +=[(mass*centers,base) for mass,base in terms];r['stock']+=F(L*centers,q)
 b.c.require(sum(x for x,_ in r['terms'])==r['m']*r['stock']-r['deficit'],'full center invoice')
 return r
out=[]
for name,h,centers in [('complex',17,816),('bit',16,815)]:
 for L in (3,5,7,9):
  for tn,target in [('single',[h-1]),('split2',[1,h-2]),('split3',[1,7,h-9]),('units',[1]*(h-1))]:
   r=built(h,centers,L,target);lo,hi=b.c.bracket(r)
   result=dict(supplier=name,stages=L,m=r['m'],target=tn,source_path=[h-1],target_path=target,center_roles=centers,center_bill=h*centers,stock=str(r['stock']),deficit=r['deficit'],nominal_kappa_interval_scaled_1e18=b.c.scaled(lo/(1+lo),hi/(1+hi)),targets=[])
   for factor in (F(1),F(102,100),F(6,5),F(3,2)):
    k=b.c.FRONTIER*factor;a=k/(1-k);pl,ph=b.pressure(r,a,bad=name=='bit')
    rec=dict(factor=str(factor),slack_interval_scaled_1e12=b.c.scaled(r['deficit']-ph,r['deficit']-pl,10**12),compensation_helpers={})
    for pn,pf in [('root_path',[1,7,h-9,1]),('coarse',[1,h-2,1]),('units',[1]*h)]:
     terms,q,pad=b.helper(r,pf);ul,uh=b.pressure(dict(r,terms=terms),a,bad=name=='bit')
     low=(r['deficit']-ph)/uh;high=(r['deficit']-pl)/ul
     ml=low.numerator//low.denominator;mh=high.numerator//high.denominator;b.c.require(ml==mh,'exact integer compensation budget')
     rec['compensation_helpers'][pn]=max(ml,0)
    result['targets'].append(rec)
   out.append(result)
output_path('paid-controller/FULL-CENTERS.json').write_text(json.dumps(out,indent=2)+'\n')
for r in out:
 if r['stages'] in (3,5) and r['target'] in ('single','split3','units'):
  print(r['supplier'],'L',r['stages'],'target',r['target'],'nom',r['nominal_kappa_interval_scaled_1e18'][0]/1e18)
  for t in r['targets']:print(' ',t['factor'], t['compensation_helpers'])
