# BILINEAR bl8 (float SCOUT): can three pairs of a stage triple all be Delta-zero (Ghat_st = Ghat_ts)?  Delta-zero is what a pair served ONLY by
# degree-2 roles must satisfy (PAIR-SYMMETRY law).  Minimise sum |Delta|^2 over walks with margins: sv(A_t), sv(Lam_t) >= MG.
import os,sys
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
import numpy as np
from scipy.optimize import least_squares
I=np.eye(2);MG=float(os.environ.get('MG','0.2'))
def walk(z,k):
    As=[z[4*i:4*i+4].reshape(2,2) for i in range(k-1)];P=I.copy()
    for a in As:P=a@P
    return As+[(-1)**(k+1)*np.linalg.inv(P)]
def Gh(As):
    k=len(As);Q=[I];[Q.append(-a@Q[-1]) for a in As]
    al=[np.linalg.inv(Q[s+1])-np.linalg.inv(Q[s]) for s in range(k)];be=[Q[t+1]-Q[t] for t in range(k)]
    return lambda s,t:0.25*(1 if s<=t else -1)*al[s]@be[t]
def res(z,k,pairs):
    As=walk(z,k);G=Gh(As);r=[]
    for s,t in pairs:r+=list((G(s,t)-G(t,s)).ravel()/max(1e-9,np.abs(G(s,t)).max()))
    pen=[max(0,MG-np.linalg.svd(a)[1][-1]) for a in As]+[max(0,MG-np.linalg.svd(a+I)[1][-1]) for a in As]+[max(0,np.abs(a).max()-20) for a in As]
    return np.r_[r,10*np.array(pen)]
rng=np.random.default_rng(int(sys.argv[3]) if len(sys.argv)>3 else 0)
k=int(sys.argv[1]);tri=[int(c) for c in sys.argv[2]];pairs=[(tri[0],tri[1]),(tri[1],tri[2]),(tri[0],tri[2])]
best=9
for st in range(int(os.environ.get('NS','60'))):
    s=least_squares(res,rng.normal(size=4*(k-1)),args=(k,pairs),xtol=1e-15,ftol=1e-15,gtol=1e-15,max_nfev=4000)
    v=np.abs(s.fun).max();best=min(best,v)
    if v<1e-10:
        As=walk(s.x,k);G=Gh(As)
        print('FOUND start',st,'max|res| %.1e'%v,'min sv A %.3f'%min(np.linalg.svd(a)[1][-1] for a in As),'min sv Lam %.3f'%min(np.linalg.svd(a+I)[1][-1] for a in As),
              'commute? %.2e'%max(np.abs(As[i]@As[j]-As[j]@As[i]).max() for i in range(k) for j in range(k)),'other pairs Delta!=0:',sum(1 for a in range(k) for b in range(a+1,k) if np.abs(G(a,b)-G(b,a)).max()>1e-6));break
print('k',k,'triple',tri,'best %.2e'%best)
