# check the min-max: GR(B) (random eval over GF(2^16)) == min_{S,T} (v-|S|)+(v-|T|)+sum_c rank_F2 B[S&R_c, T&A_c]
import sys, random, itertools
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib')); from gr import gr
def rk(rows):
    piv=[]
    for x in rows:
        for p in piv: x=min(x,x^p)
        if x: piv.append(x); piv.sort(reverse=True)
    return len(piv)
def minmax(B, pi, sig):
    v=len(B); best=10**9
    for S in range(1<<v):
        for T in range(1<<v):
            val=2*v-bin(S).count('1')-bin(T).count('1')
            for c in range(3):
                rows=[sum(B[t][s]<<s for s in range(v) if T>>s&1 and c in sig[s]) for t in range(v) if S>>t&1 and c in pi[t]]
                val+=rk(rows)
            best=min(best,val)
    return best
random.seed(5); bad=0; dist={}
for it in range(300):
    v=random.randint(3,6)
    pi=[set(random.sample(range(3),random.randint(1,3))) for _ in range(v)]
    sig=[set(random.sample(range(3),random.randint(1,3))) for _ in range(v)]
    B=[[int(t==s or random.random()<0.5) for s in range(v)] for t in range(v)]
    g=gr(B,pi,sig,trials=6); m=minmax(B,pi,sig)
    dist[(g-v,m-v)]=dist.get((g-v,m-v),0)+1
    if g!=m: bad+=1
print('mismatch',bad, sorted(dist.items()))
