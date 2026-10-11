"""Gauge variant (entrance comps at nonzero frames on a global flag; centre copies climb the flag). Profile model on top of the exact word."""
from cxcheck import *
from gauge import prep,span,perp
import pickle
import hostmodel as HM
def gauge_profile(w,pre,start_kernel,gauge,flag):
    """gauge: {helper h: E basis tuple (member of flag)}; start_kernel: {reg: E} kernel pivots (registers absolute ids); returns profile dict + widths"""
    rep,edges=check(w,pre=pre,start=start_kernel,full=False)   # kernel/baseline chain profile (comps ignored)
    paid=Counter(rep['local_profile'])
    # remove climbs saved for gauge helpers: recompute their chains with start E
    A,B=w['A'],w['B'];P=w['ports'];R=w['report']['R'];n=240+R
    # recompute full chain simulation with gauge starts and target levels
    col,first=__import__('kern').setup(w)
    supp={h:set(col[h]) for h in range(R)}
    lev={t:() for t in range(v)}
    for h,E in gauge.items():
        for t in supp[h]:
            if len(E)>len(lev[t]):
                assert span(lev[t])<=span(E)
                lev[t]=E
    st={}
    for h,E in start_kernel.items():st[h]=E
    cur={}
    for r in range(n):
        if r<v:cur[r]=(P[r],)
        elif r<2*v:cur[r]=lev[r-v]
        else:
            h=r-2*v;cur[r]=basis(list(gauge.get(h,()))) if h in gauge else basis(list(st.get(r,())))
    paid=Counter();edges=set()
    def climb(r,F):
        F=basis(list(F));o=cur[r]
        assert basis(list(o)+list(F))==F,('frame violation',r,o,F)
        if o!=F:paid[len(F)-len(o)]+=1;cur[r]=F
    # target level climbs in D phase (stepwise through distinct levels)
    for t in range(v):
        ls=sorted({gauge[h] for h in range(R) if h in gauge and t in supp[h]},key=len)
        o=()
        for E in ls:
            assert basis(list(o)+list(E))==E
            if E!=o:paid[len(E)-len(o)]+=1;o=E
    # kernel pre-ops + A
    for part,seq in (('A',list(pre)+A),('B',B)):
        if part=='B':
            ce=w['centers'];cf=w['center_frames']
            assert all(cur[r]==basis(list(f)) for r,f in zip(ce,cf))
            # centre copies: lowered cf -> top served level -> ... -> lowest served level (mass-neutral descent)
            for r,f in zip(ce,cf):
                f=basis(list(f))
                tl={lev[e[1]-v] for e in w['cut'] if e[2]==r}
                path=sorted(tl,key=lambda L:-len(L))
                o=f
                for L in path:
                    assert basis(list(L)+list(o))==o,('centre frame does not contain served level',r,L,o)
                    if L!=o:paid[len(o)-len(L)]+=1;o=L
        for e in seq:
            for r in ([e[1]]+([e[2]] if e[0]=='add' else [])):climb(r,e[-1])
    for r in range(n):climb(r,FULL if (r<v or r>=2*v) else perp(P[r-v]))
    widths=[9-len(gauge.get(h,st.get(2*v+h,()))) for h in range(R)]
    return dict(sorted(paid.items())),widths
if __name__=='__main__':
    w=load();w['R']=w['report']['R']
    sc,flag,per=pickle.load(open('flag_best.pkl','rb'))
    col,first,cap,cands,P=prep(w);R=len(col)
    gauge={}
    for h,k in per.items():
        if k>0:
            E=[F for F in flag if len(F)==k][0];gauge[h]=E
    prof,widths=gauge_profile(w,(),{},gauge,flag)
    print('gauge helpers',len(gauge),'eps',sum(len(E) for E in gauge.values()),'profile',prof)
    r0=HM.evaluate({1:1912,2:784,3:168,4:224,5:392,8:24},[9]*560)
    r=HM.evaluate(prof,widths)
    print('b',r['b'],'%+.3f%%'%(100*(r['b']/r0['b']-1)),r['W'],r['banks'])
