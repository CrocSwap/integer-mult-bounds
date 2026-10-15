import json,sys,copy
sys.argv=sys.argv
import prelife2 as P, repair2
from collections import Counter
w=P.load(sys.argv[1]);P.TRACE,_=repair2.run(copy.deepcopy(w),None)
b0={int(k):v for k,v in w['report']['local_profile'].items()}
why=Counter();ok=[]
for h,L,E in json.load(open(sys.argv[2])):
    try:w2=P.build(w,L,h,E)
    except AssertionError as e:why[str(e)[:30]]+=1;continue
    lp={int(k):v for k,v in w2['report']['local_profile'].items()}
    ok.append((h,L,E,P.price_root(b0,lp)['kappa'],lp,w2['report']['width_inventory']));print(ok[-1],flush=True)
print(why,len(ok));json.dump(ok,open(sys.argv[3],'w'))
