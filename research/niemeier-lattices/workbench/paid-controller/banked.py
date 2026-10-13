from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from portable import PACKAGE, output_path, source_name
"""Conditional complete rank invoices, not native scalar words or supplier admission."""
from fractions import Fraction as F
from pathlib import Path
import importlib.util,json,math
P=PACKAGE / 'code/costs.py'
s=importlib.util.spec_from_file_location('niemeier_costs',P);c=importlib.util.module_from_spec(s);s.loader.exec_module(c)

def parts(total,cap):
 if total==0:return []
 k=(total+cap-1)//cap
 return [total//k+(i<total%k) for i in range(k)]

def base(n,h,hist,L,data):
 c.require(sum(data)==h-1,'each data chain spans h-1')
 m=1+L*(h-1);cap=math.isqrt((m*m-1)//2)
 terms=[(F(2*n*L*r),F(m,r)) for r in data]
 terms +=[(F(L*w*count),F(m,w)) for w,count in hist.items()]
 for idle in c.idle_slots(L,h-1):
  terms +=[(F(2*n*r),F(m,r)) for r in parts(idle,cap)]
 C=sum(w*count for w,count in hist.items());W=(L-1)*n;D=W-L*C
 c.require(all(m/base<=cap for _,base in terms),'all children obey m^2>2r^2')
 c.require(sum(x for x,_ in terms)==m*W-D,'base rank-mass identity')
 return dict(ports=n,h=h,m=m,stages=L,deficit=D,stock=F(W),terms=terms,cap=cap)

def helper(r,profile,virtual=False):
 w=sum(profile);h=r['h'];m=r['m'];e=h-w
 c.require(0<w<=h,'positive helper residual')
 if not virtual:c.require(w==h,'ordinary helper runs from zero to full')
 q=(m-e)//w if virtual else m//h
 pad=m-q*w
 terms=[(F(r['stages']*a),F(m,a)) for a in profile]
 terms += [(F(r['stages']*a,q),F(m,a)) for a in parts(pad,r['cap'])]
 c.require(sum(x for x,_ in terms)==F(m*r['stages'],q),'helper stock exactly pays rank mass')
 return terms,q,pad

def count_children(r):
 return sum(mass/(r['m']/base) for mass,base in r['terms'])

def pressure(r,a,bad=False):
 lo,hi=c.pressure_bounds(r,a)
 if bad:
  # Conditional portability of the retained 1e-16 bad-branch envelope.
  pl,ph=c.power_bounds(F(r['m']),a)
  factor=F(32*r['m']**2,10**16)*count_children(r)
  lo+=factor*pl;hi+=factor*ph
 return lo,hi

def threshold(n,h,hist,L,data,hp,target,virtual=False,bad=False):
 r=base(n,h,hist,L,data);a=target/(1-target);lo,hi=pressure(r,a,bad)
 unit,q,pad=helper(r,hp,virtual)
 ur=dict(r,terms=unit);ul,uh=pressure(ur,a,bad)
 low=(r['deficit']-hi)/uh; high=(r['deficit']-lo)/ul
 lower=max(low.numerator//low.denominator,0);upper=max(high.numerator//high.denominator,0)
 c.require(lower==upper,'exact helper threshold')
 return dict(stages=L,m=r['m'],deficit=r['deficit'],max_helpers=lower,
  helpers_per_port=str(F(lower,n)),helpers_per_bank=q,pad_rank=pad,
  total_stock_at_max=str(r['stock']+F(L*lower,q)),data_path=data,helper_path=hp,
  virtual_entrance_dimension=h-sum(hp),bad_envelope=bad)

def invoice(n,h,hist,L,data,hp,R,virtual=False):
 r=base(n,h,hist,L,data);unit,q,pad=helper(r,hp,virtual)
 r['terms'] += [(R*mass,base) for mass,base in unit];r['stock']+=F(L*R,q)
 c.require(sum(x for x,_ in r['terms'])==r['m']*r['stock']-r['deficit'],'complete banked invoice')
 low,high=c.bracket(r)
 return dict(stages=L,m=r['m'],R=R,stock=str(r['stock']),deficit=r['deficit'],
  nominal_kappa_interval_scaled_1e18=c.scaled(low/(1+low),high/(1+high)),
  stock_replication_factor=q,helper_pad=pad,max_child=max(int(r['m']/base) for _,base in r['terms']))

def run():
 out={}
 for name,n,h,hist in [('complex',30960,17,{17:256,15:560}),('bit',30960,16,{16:815})]:
  rows={}
  for fac in (F(1),F(102,100),F(6,5)):
   rr={}
   for dn,dp in [('single',[h-1]),('split2',[1,h-2]),('split3',[2,2,h-5]),('units',[1]*(h-1))]:
    for hn,hp in [('single',[h]),('split2',[1,h-1]),('units',[1]*h)]:
     cand=[threshold(n,h,hist,L,dp,hp,c.FRONTIER*fac,bad=name=='bit') for L in range(3,102,2)]
     rr[dn+'__'+hn]=max(cand,key=lambda d:d['max_helpers'])
   rows[str(fac)]=rr
  inv=[]
  for dn,dp in [('single',[h-1]),('split2',[1,h-2]),('units',[1]*(h-1))]:
   for hn,hp in [('single',[h]),('split2',[1,h-1]),('units',[1]*h)]:
    cand=[invoice(n,h,hist,L,dp,hp,n) for L in range(3,12,2)]
    best=max(cand,key=lambda d:d['nominal_kappa_interval_scaled_1e18'][0]);best.update(data=dn,helpers=hn);inv.append(best)
  out[name]=dict(thresholds=rows,one_helper_per_port=inv)
 return out
if __name__=='__main__':
 out=run();output_path('paid-controller/BANKED.json').write_text(json.dumps(out,indent=2)+'\n')
 for name,data in out.items():
  print(name)
  for fac in ('1','51/50','6/5'):
   print('factor',fac)
   for key in ('single__units','split2__units','split2__split2','units__units'):
    r=data['thresholds'][fac][key];print(key,'L',r['stages'],'R',r['max_helpers'],'R/N',float(F(r['helpers_per_port'])))
  print('R=N invoices')
  for r in data['one_helper_per_port']: print(r['data'],r['helpers'],r['stages'],r['nominal_kappa_interval_scaled_1e18'])
