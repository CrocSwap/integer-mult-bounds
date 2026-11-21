from lm import *; from base import *; import pickle,time,sys
cls=pickle.load(open('cls_104.pkl','rb')); S=sections(104)
u=cls[list(cls)[1]][0]; X=S[u]
for r in (7,):
    t0=time.time(); b,x=fitlm(X,r,tries=25,iters=400,seed=5,verbose=True); print('r',r,'best',b,'%.0fs'%(time.time()-t0),flush=True)
