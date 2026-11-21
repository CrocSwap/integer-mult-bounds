"""LINEAR56 m8tight.py: [C] all 8-row linear decoders whose 8 A-columns are tight (x = tight lift of B z, z in Z16).
For each independent 8-subset and K in {G, G+2B}: Y^T = X^{-1} K; record which Y-columns are tight, cost, f."""
import numpy as np, itertools, sys
sys.path.insert(0,'../double56'); from lin import inv4
from lcore import *
T=np.load('tightX.npy'); tl={}
for x in T:
    k=tuple(x%2)
    if k not in tl: tl[k]=x
keys=sorted(tl); Tset=set(map(tuple,T))
res={}; ex=[]
for sub in itertools.combinations(range(16),8):
    X=np.array([tl[keys[i]] for i in sub]).T
    Xi=inv4(X)
    if Xi is None: continue
    for Kn,K in (('G',G),('G+2B',G+2*Bm)):
        Y=((Xi@K)%4).T
        nt=sum(tuple(Y[:,k]) in Tset or tuple((-Y[:,k])%4) in Tset for k in range(8))
        W=C104@X; V=C104@Y; assert check_decoder(W,V)
        c=cost(W,V); fv=f_val(*UV(W,V))
        key=(Kn,nt,c,fv); res[key]=res.get(key,0)+1
        if nt==8: ex.append((sub,Kn))
for k in sorted(res): print(k,res[k])
print('fully tight examples',ex[:5],len(ex))
