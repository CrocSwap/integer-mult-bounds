import sys,collections
from sim import *
from fractions import Fraction as Fr
def contribs(h):
    """returns (status, readers) readers: list of (ridx, x, a, [(widx,s,coef)])"""
    ent=[];out=[]
    for idx,(tag,e) in enumerate(prog):
        if e[0]=='scale':
            if e[1]==h:
                q=Fr(e[2],e[3]);ent=[(i,s,c*q) for i,s,c in ent]
            continue
        t,s=e[1],e[2];q=Fr(e[3],e[4])
        if t==h:ent.append((idx,s,q));continue
        if s==h:
            if t==h:return 'rot',None
            out.append((idx,t,q,list(ent)))
    return 'ok',out
def window_check(x,w,r):
    """returns (ok,factor,reason) factor = product of x scales in (w,r)"""
    f=Fr(1)
    for i in range(w+1,r):
        tag,e=prog[i]
        if e[0]=='scale':
            if e[1]==x:f*=Fr(e[2],e[3])
        else:
            if e[2]==x:return False,None,'read-x@%s'%(tag,)
    return True,f,None
def hoisted_prog(hs,mode='W'):
    """hs: list of helpers (assumed independent). returns (newprog or None, reason)"""
    ins=collections.defaultdict(list);drop=set()
    for h in hs:
        st,_=track(h)
        if st!='ok':return None,'alg'
        st,rd=contribs(h)
        if st!='ok':return None,st
        for idx,e in enumerate(prog):pass
        for idx,(tag,e) in enumerate(prog):
            if e[0]=='add' and h in e[1:3]:drop.add(idx)
        for ridx,x,a,ent in rd:
            for widx,s,c in ent:
                if prog[widx][0][0] in 'PC':return None,'write-in-PC'
                ok,f,why=window_check(x,widx,ridx)
                if not ok:return None,why
                co=a*c/f
                if co==0:continue
                E=prog[widx][1][5] if mode=='W' else prog[ridx][1][5] if mode=='R' else []
                ins[widx].append((prog[widx][0],['add',x,s,co.numerator,co.denominator,E]))
    new=[]
    for idx,(tag,e) in enumerate(prog):
        if idx not in drop:new.append((tag,e))
        for te in ins.get(idx,[]):new.append(te)
    return new,None
if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'W'
    cls=collections.Counter();passers=[];feas=[]
    for h in range(224,704):
        if h in centers:continue
        st,_=track(h)
        if st!='ok':continue
        np_,why=hoisted_prog([h],mode)
        if np_ is None:cls[why.split('@')[0]]+=1;continue
        passers.append(h)
        ok,r,paid,mass_=simulate(np_,removed={h})
        if ok:feas.append((h,mass_))
        else:cls['frame:'+r.split()[0]+' '+r.split()[1]]+=1
    print(mode,'alg-ok 172; window-ok',len(passers),'frame-ok',len(feas));print(cls);print(feas)
