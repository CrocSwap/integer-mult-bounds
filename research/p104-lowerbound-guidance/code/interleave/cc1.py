# INTERLEAVE cc1: test Lemma CC on t7669. For every chart F (span set) with no public intermediate stop,
# check span(arrival rows into F) == span(final rows of the registers that arrive at F). Rank mod 2 primes.
import sys, signal; signal.alarm(1200)
sys.path.insert(0,'code/fewstops')
from load import *
from fractions import Fraction as Q
from collections import defaultdict
N=n+W['owned_fields']; frames=W['frames']
rows=[{r:Q(1)} if r<n else {} for r in range(N)]
cur=list(W['initial'])+[None]*W['owned_fields']
chain=defaultdict(list)
for r in range(n): chain[r].append(SP[cur[r]])
arr=defaultdict(list)          # F -> [(r,row)]
ownvis=defaultdict(int)        # F -> # owned events at F
ownsup=set()                   # charts visited by owned
for i,e in enumerate(P):
    op,r=e[0],e[1]
    if op=='MOVE':
        b=e[3]; cur[r]=b
        if r<n: chain[r].append(SP[b]); arr[SP[b]].append((r,dict(rows[r])))
        else: ownsup.add(SP[b])
    elif op=='INIT': rows[r]={}; cur[r]=e[2]; ownsup.add(SP[e[2]])
    elif op=='CLEAR': rows[r]={}; cur[r]=None
    elif op=='SCALE':
        q=Q(e[2]); rows[r]={k:v*q for k,v in rows[r].items()}
    else:
        s=e[2]; q=Q(e[3]); R=rows[r]
        if r>=n or s>=n: ownvis[SP[e[4]]]+=1
        for k,v in rows[s].items():
            nv=R.get(k,0)+q*v
            if nv: R[k]=nv
            else: R.pop(k,None)
fin={r:rows[r] for r in range(n)}
stopat=defaultdict(int)
for r in range(n):
    for c in chain[r][1:-1]: stopat[c]+=1
def rank(vecs,p):
    piv={}; rk=0
    for v in vecs:
        w={k:(x.numerator*pow(x.denominator,-1,p))%p for k,x in v.items()}
        w={k:x for k,x in w.items() if x}
        while w:
            k=max(w)
            if k in piv:
                pv=piv[k]; f=w[k]
                for kk,xx in pv.items():
                    w[kk]=(w.get(kk,0)-f*xx)%p
                    if not w[kk]: del w[kk]
            else:
                inv=pow(w[k],-1,p); piv[k]={kk:(xx*inv)%p for kk,xx in w.items()}; rk+=1; break
    return rk
stats=defaultdict(int); fails=[]
for F,L in arr.items():
    if stopat[F]: stats['stopF']+=1; continue
    regs=[r for r,_ in L]
    assert len(set(regs))==len(regs)
    A=[v for _,v in L]; Fi=[fin[r] for r in regs]
    ok=True
    for p in (1000000007,998244353):
        ra,rf,rb=rank(A,p),rank(Fi,p),rank(A+Fi,p)
        if not (ra==rf==rb==len(regs)): ok=False
    key=('own' if (F in ownsup or ownvis[F]) else 'noown')
    stats[key+('_ok' if ok else '_FAIL')]+=1
    print("stopfree chart dimlog2",len(F).bit_length()-1,"arrivals",len(regs),"ownsup",F in ownsup,"ownev",ownvis[F])
    if not ok: fails.append((len(F),len(regs),ra,rf,rb,key))
print(dict(stats)); print('fails sample',fails[:10])
print('charts with arrivals',len(arr),' stop charts',sum(1 for F in arr if stopat[F]))
