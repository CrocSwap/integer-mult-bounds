import sys,collections
from fractions import Fraction as F
from prog import *
w=load();prog,comp=build(w);v=112;n=704
compH={e[2] for e in comp}
centers=set(w['centers'])
def track(h):
    """returns (status, newprog_spec) ; status 'ok' or bail reason"""
    H={};g=F(1);out=[];nread=0;nwrite=0
    for idx,(tag,e) in enumerate(prog):
        if e[0]=='scale':
            if e[1]==h:
                q=F(e[2],e[3]);g*=q;H={k:q*c for k,c in H.items()}
            elif e[1] in H:
                # r scaled: h-h0 = H[r]*r_old ; r_old = r_new/q
                q=F(e[2],e[3]);H[e[1]]=H[e[1]]/q
            continue
        t,s=e[1],e[2];q=F(e[3],e[4])
        if t==h:
            nwrite+=1
            H[s]=H.get(s,F(0))+q
            if H[s]==0:del H[s]
            continue
        if s==h:
            nread+=1
            if t in H:return 'bail:read-by-source@%s'%(tag,),None
            out.append((idx,[(r,q*c) for r,c in H.items()]))
            continue
        if t in H:
            # t += q s ; t_old = t_new - q s
            c=H.pop(t)
            H[s]=H.get(s,F(0))-c*q
            if H[s]==0:del H[s]
            H[t]=c
    if H:return 'bail:final H nonzero',None
    return 'ok',(out,nread,nwrite)
if __name__=='__main__':
    res=collections.Counter();ok=[]
    for h in range(224,704):
        if h in centers:res['center']+=1;continue
        st,r=track(h)
        res[st.split('@')[0]]+=1
        if st=='ok':ok.append((h,r[1],r[2],h in compH))
    print(res)
    print(len(ok),ok[:40])
