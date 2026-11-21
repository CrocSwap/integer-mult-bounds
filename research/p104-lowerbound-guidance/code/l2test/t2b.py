from lm import *; from base import *; import pickle,time,sys
cls=pickle.load(open('cls_104.pkl','rb')); S=sections(104)
k0=list(cls)[1]; u=cls[k0][0]; X=S[u]; print(u,len(X),'omega 4')
for r in (8,7,6,5,4):
    t0=time.time(); b,x=fitlm(X,r,tries=3,iters=200); print('r',r,'best resid',b,'found',x is not None,'%.1fs'%(time.time()-t0),flush=True)
