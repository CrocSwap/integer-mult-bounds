from slide import *
import re
c=collections.Counter();why_np=collections.Counter()
for h in range(224,704):
    if h in centers or track(h)[0]!='ok':continue
    items=build(h)
    if items is None:continue
    bad=[it for it in items if it[6]>it[7]]
    if bad:
        it=bad[0];ridx,x,a,widx,s,cc,lo,hi=it
        xr=lastread(x,ridx)>widx; sw=nextw(s,widx)<ridx
        why_np['x-read' if xr and not sw else 's-written' if sw and not xr else 'both']+=1;continue
    cs=[list(range(it[6],it[7]+1)) for it in items]
    first=None;reg=collections.Counter()
    for taus in [tuple(c_[0] for c_ in cs),tuple(c_[-1] for c_ in cs)]:
        ok,r,_,_=simulate(mk(h,items,taus),removed={h})
        k=re.sub(r'\d+','#',r.split(' end')[0]);
        m=re.search(r'reg (\d+)',r);rg=int(m.group(1)) if m else -1
        role='S' if rg<112 else 'Y' if rg<224 else 'H'
        c[(k,role)]+=1
print('not-placeable (first blocking class):',dict(why_np));print('frame violations over 86x2 placements:',dict(c))
