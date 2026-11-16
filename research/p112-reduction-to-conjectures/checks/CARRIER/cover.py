from lib import *
import pickle, itertools, sys
from collections import Counter
sets=pickle.load(open('offsets80.pkl','rb'))
Pidx={t:i for i,t in enumerate(P)}
# functional masks over P112 (bit i for P[i]) : lines in ker a
Z=[0]*512
for a in range(1,512):
    m=0
    for i,t in enumerate(P):
        if not par(a&lab[t]): m|=1<<i
    Z[a]=m
full=(1<<112)-1
Z[0]=full
masks7=set()
for a in range(1,512):
    for b in range(a+1,512):
        if (a^b)<b: continue
        masks7.add(Z[a]&Z[b])
masks7=sorted(masks7)
print('7-flat Lambda masks',len(masks7),flush=True)
labP=[lab[t] for t in P]
def bits(m):
    i=0
    while m:
        if m&1: yield i
        m>>=1; i+=1
def rk(m):
    return f2rank([labP[i] for i in bits(m)])
def offmask(o):
    m=0
    for t in o: m|=1<<Pidx[t]
    return m
pc=lambda m: bin(m).count('1')
def cover(off, w2, s, w1=7):
    """exists 7-flat V1 and set of <=s lines such that rest has label rank <= w2 ; returns list of witnesses (limit)"""
    om=offmask(off); res=[]
    for M in masks7:
        R=om&~M
        if pc(R)>20 + s and w2<=6: 
            continue
        if rk(R)<=w2: res.append((M,R,0)); 
        elif s>0:
            # remove up to s lines
            L=list(bits(R))
            for k in range(1,s+1):
                ok=False
                for rem in itertools.combinations(L,k):
                    R2=R
                    for i in rem: R2&=~(1<<i)
                    if rk(R2)<=w2: ok=True; break
                if ok: break
            if ok: res.append((M,R,k))
        if len(res)>=3: break
    return res
if __name__=='__main__':
    import time
    for name,(w2,s,lim) in {'(7,6)+2':(6,2,58),'(7,7)+1':(7,1,73),'(7,7)':(7,0,72)}.items():
        t0=time.time(); out=Counter(); exs={}
        for off,v in sets.items():
            if len(off)>lim: continue
            r=cover(off,w2,s)
            out[(len(off),bool(r))]+=1
        print(name,dict(out),round(time.time()-t0),flush=True)
