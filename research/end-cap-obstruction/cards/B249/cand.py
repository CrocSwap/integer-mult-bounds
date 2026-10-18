import sys,collections,json
from sim import *
def newprog_for(hs):
    """hs: list of helpers removed jointly (must be independent: each tracked separately on the ORIGINAL prog; only valid singly)."""
    h=hs[0];st,r=track(h)
    assert st=='ok',st
    out,nr,nw=r;outd=dict(out)
    new=[]
    for idx,(tag,e) in enumerate(prog):
        if e[0]=='add' and h in e[1:3]:
            if e[2]==h:
                x=e[1]
                for rr,c in outd[idx]:
                    ne=['add',x,rr,c.numerator,c.denominator,e[5]]
                    new.append((tag,ne))
            continue
        new.append((tag,e))
    return new
if __name__=='__main__':
    res=[]
    for h in range(224,704):
        if h in centers:continue
        st,r=track(h)
        if st!='ok':continue
        ok,why,paid,mass=simulate(newprog_for([h]),removed={h})
        res.append((h,ok,why,mass,dict(paid) if paid else None))
    n_ok=[r for r in res if r[1]]
    print(len(res),'candidates;',len(n_ok),'feasible')
    for r in n_ok:print(r)
    c=collections.Counter(r[2].split(' reg')[0].split(' ')[0]+' '+(r[2].split()[1][0] if len(r[2].split())>1 else '') for r in res if not r[1])
    print(c)
    for r in res[:10]:print(r[:3])
