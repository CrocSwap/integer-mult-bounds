# lift-level cost-65 classification inputs: d=6,7,8 multisets with cost(T) <= 8d+1 passing DP; LP (quotient) verdict
import sys
sys.argv=['x','0']
exec(open('dpX.py').read().split("NE8=[0,1,3,6,12,20,36,63]")[0])
from symlp import lp
NE8=[0,1,3,6,12,20,36,63]
for d in range(1,9):
    surv=enum(d,8*d+2,112); need=112-(NE8[8-d] if d<8 else 0)
    for wt,ws in surv:
        val,bd=lp(Counter(ws),codim=8-d,NL=112)
        print(d,wt,ws,round(val,2),'need',need,'KILLED' if bd<need else 'SURVIVES',flush=True)
# coloop check: N(r_s)\{t} rank 8 for all s,t
import json, numpy as np
D=json.load(open('data.json')); FC=np.array(D['FC']); LAB=D['LAB']
def f2rank(vs):
    b=[]
    for x in vs:
        for y in b: x=min(x,x^y)
        if x: b.append(x)
    return len(b)
bad=0
for s in range(112):
    N=[t for t in range(112) if abs(FC[t]@FC[s])%2==1]  # <r_t,r_s> = ±1 (inner product in F0 coords /2? check)
    ip=[int(FC[t]@FC[s]) for t in range(112)]
    N=[t for t in range(112) if ip[t] in (2,-2)]
    r=f2rank([LAB[t] for t in N])
    for t in N:
        if f2rank([LAB[u] for u in N if u!=t])<r: bad+=1
print('|N(r)| =',len(N),'rank',r,'coloops found',bad)
