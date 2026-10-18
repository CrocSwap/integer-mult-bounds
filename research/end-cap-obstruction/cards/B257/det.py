from hoist import *
import collections
for mode in 'Z':
    c=collections.Counter();ex=[]
    for h in range(224,704):
        if h in centers:continue
        if track(h)[0]!='ok':continue
        np_,why=hoisted_prog([h],mode)
        if np_ is None:continue
        ok,r,_,_=simulate(np_,removed={h})
        if not ok:
            import re
            k=re.sub(r'\d+','#',r.split(' end')[0]) if 'op' in r else r
            c[k]+=1
            if len(ex)<4:ex.append((h,r))
    print(mode,c);print(ex)
