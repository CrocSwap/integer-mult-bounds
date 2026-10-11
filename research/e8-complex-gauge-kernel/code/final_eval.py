import json,gzip,os
from fractions import Fraction as Q
from cxlab import *
import hostmodel as HM
from kcap import cap_from_b
res={}
r0=HM.evaluate({1:1912,2:784,3:168,4:224,5:392,8:24},[9]*560,exact=True)
res['baseline']=dict(b=r0['b'],W=r0['W'],eps=0)
for d in ('kernel79','gauge80','gauge80-kernel42'):
    w=load(os.path.join(os.environ['CXG_PKG'],'data/words',d,'FULL-WORD.json.gz'))
    prof={int(k):x for k,x in w['report']['local_profile'].items()}
    R=w['report']['R'];widths=[9]*R
    for r,E in w.get('start_extra',{}).items():widths[int(r)-2*v]=9-len(E)
    r=HM.evaluate(prof,widths,exact=True)
    res[d]=dict(b=r['b'],W=r['W'],D=r['D'],eps=sum(9-x for x in widths),banks=r['banks'],hosted=r['hosted'],gain=100*(r['b']/r0['b']-1),kappa_cap=cap_from_b(Q(r['b']).limit_denominator(10**18)),profile=prof,maxchild=max(r['profile']))
for k,x in res.items():print(k,{a:b for a,b in x.items() if a!='profile'})
json.dump(res,open(os.path.join(os.environ.get('CXG_OUT','.'),'final_eval.json'),'w'),indent=1)
