from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "paid-controller"))
from portable import WORKBENCH, output_path, source_name
from pathlib import Path
import sys,json
from fractions import Fraction as F

import banked as b
b.c.FRONTIER=F(1612722852614221,10**18)

def row(L,hp,R):
 r=b.base(30960,17,{17:816},L,[8,8])
 for count,profile,virtual in [(816,[17],False),(R,hp,True)]:
  terms,q,pad=b.helper(r,profile,virtual);r['terms'] +=[(count*mass,base) for mass,base in terms];r['stock'] += F(count*L,q)
 b.c.require(sum(mass for mass,_ in r['terms'])==r['m']*r['stock']-r['deficit'],'Tensor banked mass identity')
 return r
out=[]
for L in range(3,32,2):
 for hp in ([9],[1,7,1],[1]*9):
  r=row(L,hp,120960);lo,hi=b.c.bracket(r)
  base=row(L,hp,0);a=b.c.FRONTIER/(1-b.c.FRONTIER);pl,ph=b.pressure(base,a)
  u,_,_=b.helper(base,hp,True);ul,uh=b.pressure(dict(base,terms=u),a)
  ml=max((base['deficit']-ph)//uh,0);mh=max((base['deficit']-pl)//ul,0);b.c.require(ml==mh,'Exact helper threshold')
  out.append(dict(L=L,profile=hp,m=r['m'],R=120960,max_R_at_frontier=ml,kappa_interval_scaled_1e18=b.c.scaled(lo/(1+lo),hi/(1+hi))))
output_path('continuation/endpoint-costs/TENSOR-PRICE.json').write_text(json.dumps(out,indent=2)+'\n')
for hp in ([9],[1,7,1],[1]*9):
 rows=[r for r in out if r['profile']==hp];best=max(rows,key=lambda r:r['kappa_interval_scaled_1e18'][0]);maximum=max(rows,key=lambda r:r['max_R_at_frontier'])
 print('profile',hp,'best',best,'maxR',maximum['L'],maximum['max_R_at_frontier'])
