from m19 import *
import pickle
N=load19(); H0=N.H0; U=units(N,H0)
allc=pickle.load(open('chains19.pkl','rb'))
out=[]
for sav,n_,hs in allc:
    if n_!=2 or sav<=0: continue
    u1=uvec(U,hs[0]); q=ratio(u1,uvec(U,hs[1]))
    if q!=1 and q>0 and U[hs[0]]['r']!=U[hs[1]]['r']: out.append((sav,n_,hs,q))
print(len(out),out[:5])
pickle.dump([(a,b,c) for a,b,c,_ in out[:1]],open('chains19s2.pkl','wb'))
