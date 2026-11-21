"""MAINPLACE mp5: cc1 + HALL_l rows [P, MP.md] (generated from cc1.py; erow takes mf)."""
"""CALLERCUT cc1: witness LP = SCHERK sk2 base (ms9 coord,pfix,shal + DYADIC_J on masks; via bl5 with no COVER rows, PC=0)
 + RC_l rows [P, CC.md] + RC2_l rows (env RC2=1 default):  sum_r ([D>=l] sum_{L<l} L(k-L)/(k-1) + [D<l](D^2-sum L^2)/(k-1)) >= 2k, l=3..k
:  sum_r ( [D_r>=l] * sum_{pieces L<l} L  +  [D_r<l] * D_r(D_r-1)/(k-1) )  >=  2k,   l in LS (default 3..k).
usage: cc1.py k..   env LS=comma list, SUP=1 prints support, RC=0 disables RC rows (reproduces sk2)."""
import os,sys,signal
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
os.environ['PC']='0'
sys.path.insert(0,'code/bilinear')
import bl5,numpy as np
NEG=bl5.NEG
class LP(bl5.LP):
    def __init__(s_,k,rls):
        super().__init__(k,[],[],[],dyeff=False,dymask=True)
        s_.rowsE+=[('R',l,float(2*k)) for l in rls]
        if os.environ.get('LA','0')=='1':s_.rowsE+=[('LA',l,0.0) for l in range(3,k+1)]
        if os.environ.get('RC2','1')=='1':s_.rowsE+=[('R2',l,float(2*k)) for l in range(3,k+1)]
        s_.rowsE+=[('H',l,0.0) for l in range(2,k+1)]
    def erow(s_,D,P,mf=0):
        k=s_.k;out=[]
        for kind,a,b in s_.rowsE:
            if kind=='dm':out.append(min(D,2**(a+1))-1)
            elif kind=='R':out.append(sum(L for L in P if L<a) if D>=a else D*(D-1)/(k-1))
            elif kind=='R2':out.append(sum(L*(k-L) for L in P if L<a)/(k-1) if D>=a else (D*D-sum(L*L for L in P))/(k-1))
            elif kind=='LA':out.append((sum(L for L in P if L<a)-1) if D>=a else 0.0)
            elif kind=='H':out.append(sum(L*(k-L) for L in P if L<a and (L>=2 or mf==0))-(D*(k-D) if D<a else 0))
            else:raise ValueError(kind)
        return np.array(out,float)
    def price6(s_,w,y,wm,wx,we):
        k,s=s_.k,s_.s;L=np.arange(1,s_.Lmax+1,dtype=float);Li=L.astype(int)
        wsep,we_,w1=w[0],w[1],w[2];wl=w[3:3+len(s_.ells)]
        W=np.zeros(len(L))
        for i,ll in enumerate(s_.ells):W[:ll-1]+=wl[i]
        cpv=np.array([sum(wx[j]*X[1](v) for j,X in enumerate(s_.X)) for v in Li]);cz=sum(wx[j]*X[3] for j,X in enumerate(s_.X))
        out=[]
        for D in range(s_.Dmin,k+1):
            Lm=min(D,s_.Lmax);Ls=L[:Lm]
            c0=sum(wx[j]*X[0](D) for j,X in enumerate(s_.X));c1=sum(wx[j]*X[2](D) for j,X in enumerate(s_.X))
            const=(8*D+1)**s+wsep*D*D/2-we_+sum(wl[i]*((ll<=D<=k-1)*D*(k-D)) for i,ll in enumerate(s_.ells))+y+c0
            g=-(8*Ls)**s-wsep*Ls*Ls/2+we_+W[:Lm]*Ls*(D-Ls)/2+cpv[:Lm];h1=0.0
            for i,(kind,a,b) in enumerate(s_.rowsE):
                if kind=='dm':const+=we[i]*(min(D,2**(a+1))-1)
                elif kind=='R':
                    if D>=a:g=g+we[i]*Ls*(Ls<a)
                    else:const+=we[i]*D*(D-1)/(k-1)
                elif kind=='LA':
                    if D>=a:g=g+we[i]*Ls*(Ls<a);const-=we[i]
                elif kind=='R2':
                    if D>=a:g=g+we[i]*Ls*(k-Ls)/(k-1)*(Ls<a)
                    else:const+=we[i]*D*D/(k-1);g=g-we[i]*Ls*Ls/(k-1)
                elif kind=='H':
                    g=g+we[i]*Ls*(k-Ls)*(Ls<a)*(Ls>=2)
                    if D<a:const-=we[i]*D*(k-D)
                    h1+=we[i]*(k-1)*(1<a)
            for mf in (0,1):
                if mf==1 and D<s_.dmin:continue
                for hasone in (0,1):
                    gg=g.copy();gg[0]+=w1+mf*wm+c1+(h1 if mf==0 else 0.0)
                    if not hasone:gg[0]=-np.inf
                    best=np.full(D+1,-np.inf);best[0]=0;arg=np.zeros(D+1,int)
                    for d in range(1,D+1):
                        m=min(d,Lm);c=best[d-np.arange(1,m+1)]+gg[:m];j=int(c.argmax());best[d]=c[j];arg[d]=j+1
                    if hasone:tot=gg[0]+best[D-1];P=[1];d=D-1
                    else:
                        if mf==1:continue
                        if os.environ.get('NOPURE')=='1':
                            m2=min(D-1,Lm);c=best[D-np.arange(1,m2+1)]+gg[:m2];j=int(c.argmax());tot=c[j]+cz;P=[j+1];d=D-(j+1)
                        else:tot=best[D]+cz;P=[];d=D
                    if not np.isfinite(tot):continue
                    while d>0:P.append(int(arg[d]));d-=arg[d]
                    out.append((tot+const,D,tuple(sorted(P)),mf))
        out.sort(reverse=True);return out

import inspect,textwrap
_src=textwrap.dedent(inspect.getsource(bl5.LP.solve)).replace("s_.erow(D,P) for D,P,mf in cols","s_.erow(D,P,mf) for D,P,mf in cols")
_ns={'np':np,'linprog':bl5.linprog};exec(_src,_ns);LP.solve=_ns['solve']
if __name__=='__main__':
    signal.alarm(3000)
    for k in [int(a) for a in sys.argv[1:]]:
        rls=[int(a) for a in os.environ['LS'].split(',')] if os.environ.get('LS') else (list(range(3,k+1)) if os.environ.get('RC','1')=='1' else [])
        r=LP(k,rls).solve()
        if r is None:print('k',k,'INFEASIBLE',flush=True);continue
        B,p,sup=r
        print('RC k',k,'cB %.3f cP %.3f'%(104*B/k,104*p/k),sup if os.environ.get('SUP') else '',flush=True)
