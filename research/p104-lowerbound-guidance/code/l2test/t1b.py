from base import *
import pickle
for n in (96,104):
    rows=pickle.load(open('t1_%d.pkl'%n,'rb')); S=sections(n)
    inv={}
    for u,sz,w,r8 in rows:
        if w<r8:
            X=S[u]; q=Q[np.ix_(X,X)]
            deg=tuple(sorted(q.sum(1)-1)); 
            key=(sz,w,r8,deg,tuple(sorted(L[p].bit_count() for p in X)),bin(u).count('1')%2, u in set(L))
            inv.setdefault(key,[]).append(u)
    print(n,len(inv),'classes',[ (k[0],k[1],k[2],k[5],k[6],len(v)) for k,v in inv.items()])
    pickle.dump({k:v for k,v in inv.items()},open('cls_%d.pkl'%n,'wb'))
