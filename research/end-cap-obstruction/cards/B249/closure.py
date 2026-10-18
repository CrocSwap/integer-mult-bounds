import sys,collections
from sim import *
import scan
def track_p(P,h):
    H={};out={}
    for idx,(tag,e) in enumerate(P):
        if e[0]=='scale':
            if e[1]==h:
                q=F(e[2],e[3]);H={k:q*c for k,c in H.items()}
            elif e[1] in H:
                q=F(e[2],e[3]);H[e[1]]=H[e[1]]/q
            continue
        t,s=e[1],e[2];q=F(e[3],e[4])
        if t==h:
            H[s]=H.get(s,F(0))+q
            if H[s]==0:del H[s]
            continue
        if s==h:
            if t in H:return None
            out[idx]=[(r,q*c) for r,c in H.items()];continue
        if t in H:
            c=H.pop(t);H[s]=H.get(s,F(0))-c*q
            if H[s]==0:del H[s]
            H[t]=c
    return out if not H else None
def remove(P,h):
    out=track_p(P,h)
    if out is None:return None,None
    new=[];srcs=set()
    for idx,(tag,e) in enumerate(P):
        if e[0]=='add' and h in e[1:3]:
            if e[2]==h:
                for rr,c in out[idx]:
                    new.append((tag,['add',e[1],rr,c.numerator,c.denominator,e[5]]));srcs.add(rr)
            continue
        new.append((tag,e))
    return new,srcs
def closure(h,maxn=16):
    P=prog;rem=[];todo=[h]
    while todo:
        x=todo.pop()
        if x in rem:continue
        if x in centers or x<224:return None,'nonremovable src %d'%x
        P2,srcs=remove(P,x)
        if P2 is None:return None,'bail %d'%x
        P=P2;rem.append(x)
        for s in srcs:
            if s>=224 and s not in rem:todo.append(s)
        if len(rem)>maxn:return None,'too big'
    return (P,rem),'ok'
if __name__=='__main__':
    stat=collections.Counter();best=[]
    for h in range(224,704):
        if h in centers:continue
        r,why=closure(h)
        if r is None:stat[why.split()[0]]+=1;continue
        P,rem=r
        ok,why2,paid,mass=simulate(P,removed=set(rem))
        stat['feasible' if ok else 'infeasible']+=1
        if ok:best.append((h,rem,mass,dict(paid)))
    print(stat)
    for b in best:print(b)
