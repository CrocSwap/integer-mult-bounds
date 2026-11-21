"""MERGEROWS m4: constructive normal form on Delta (six saturated rows), exact alpha/beta at explicit gauges."""
import sys,pickle,numpy as np
from nf import *
from m2 import *
rows=pickle.load(open('../iso3/hs_kind1.pkl','rb')); L=std_set('HS64'); Q=Q_std(L); n=len(Q)
six=[0,1,4,5,6,7]
new,d=normal_form(rows,six); assert check_decoder(new,Q)==0
print('elementary-divisor depths of the six-class:',d,'prices new',prices(new,Q),'C',sum(prices(new,Q)))
VW,VU=vals(new,n)
for k in range(8): print(k,'minval w',VW[:,k].min(),'minval u',VU[:,k].min())
# F2-independence of normalised reductions
def red(vecs):
    R=[]
    for v in vecs:
        m=min(v2(x) for x in v if x!=0); R.append([int(v2(x)==m) if x!=0 else 0 for x in v])
    return rk2(np.array(R))
print('rank of six w-reductions',red([new[k][0] for k in six]),' u-reductions',red([new[k][1] for k in six]),
      ' (Delta original:',red([rows[k][0] for k in six]),red([rows[k][1] for k in six]),')')
g=max((gauge_max(new,Q,1500,sd) for sd in range(3)),key=lambda x:x['gmax_sum'])
print('NF Delta: canon',g['canon'],g['canon_sum'],' gauge-climb',g['gmax'],g['gmax_sum'])
pickle.dump(new,open('delta_nf.pkl','wb'))
