import sys
DD=int(sys.argv[1])
src=open('ind2.py').read().split("t0 = time.time(); nres")[0]
sys.argv=['ind2.py',str(DD)]
exec(src)
import collections
nS0=0; mx=collections.Counter(); mx0=collections.Counter()
for Z in level:
    X0=Cset(Z)
    S0=[s for s in surv if blkrank(FULL^X0,FULL^cls[s])==8-DD]
    nS0+= bool(S0)
    Ks=enumK(X0,S0,0); mx0[max(len(K) for K in Ks)]+=1
    if S0:
        Ks=enumK(X0,S0,1); mx[max(len(K) for K in Ks)]+=1
print('Z with S0 nonempty',nS0,'of',len(level)); print('max k tau0=0',sorted(mx0.items())); print('max k tau0=1 (when S0)',sorted(mx.items()))
