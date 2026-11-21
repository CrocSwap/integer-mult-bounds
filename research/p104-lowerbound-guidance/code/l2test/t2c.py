from lm import *; from base import *; import pickle,time,sys
from collections import Counter
cls=pickle.load(open('cls_104.pkl','rb')); S=sections(104)
for k0 in list(cls)[:15]:
    u=cls[k0][0]; X=S[u]; q=Q[np.ix_(X,X)]; print(u,len(X),Counter((q.sum(1)-1).tolist()))
