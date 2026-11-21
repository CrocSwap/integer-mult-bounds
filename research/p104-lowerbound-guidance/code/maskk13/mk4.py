"""mk4: type-level count of family members (2 hubs D=k + 1 role D=d + (2k-5) roles D=2, all IC rows incl. MAINS, invoice > bar), per d.
Mask-level verdict per d from mk2/mk2b (stage-level infeasible iff d <= k-7)."""
import sys
sys.path.insert(0,'../intcaller')
import numpy as np,ic1
from ic1 import val,partitions,rowdefs
def run(k):
    R=rowdefs(k);nr=len(R);need=ic1.BAR*k/104
    Hs=list(partitions(k,k-2));rhs=np.array([float(r[4]) for r in R]);mcs=np.array([float(r[2]) for r in R]);sense=[r[3] for r in R]
    eq=np.array([s=='==' for s in sense])
    vec=lambda D,P:np.array([float(f(D,P)) for (nm,f,mc,s,r) in R])
    VH=np.array([vec(k,P) for P in Hs]);valH=np.array([val(k,P) for P in Hs]);onesH=np.array([sum(1 for L in P if L==1) for P in Hs])
    pure=(2,(2,));chord=(2,(1,1))
    vp=vec(*pure);vc=vec(*chord);valp=val(*pure);valc=val(*chord)
    out={}
    for d in range(2,k):
        if d in (2,k) or d*(d-1)//2+2*k-5<ic1.turT(k):continue
        res=0
        for PR in partitions(d,min(d,k-2)):
            vr=vec(d,PR);valr=val(d,PR);oR=sum(1 for L in PR if L==1)
            for c in range(0,2*k-4):
                base=vr+c*vc+(2*k-5-c)*vp+mcs*(2*k)
                bval=valr+c*valc+(2*k-5-c)*valp
                # pairs i<=j
                tot=VH[:,None,:]+VH[None,:,:]+base[None,None,:]
                v=valH[:,None]+valH[None,:]+bval
                ones=onesH[:,None]+onesH[None,:]+oR+2*c
                ok=(v>need)&(ones>=2*k)
                d_=tot-rhs
                ok&=np.all(np.where(eq,np.abs(d_)<1e-7,d_>-1e-7),axis=2)
                ii,jj=np.nonzero(ok);res+=int(np.sum(ii<=jj))
        out[d]=res
    return out
if __name__=='__main__':
    for k in [int(a) for a in sys.argv[1:]]:
        o=run(k);print('k',k,'members by d',o,'dead(d<=k-7)',sum(v for d,v in o.items() if d<=k-7),'alive(d>=k-6)',sum(v for d,v in o.items() if d>k-7),flush=True)
