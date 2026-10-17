import json, numpy as np, itertools
D=json.load(open('data.json')); FC=np.array(D['FC']); LAB=D['LAB']
def f2rank(vs):
    b=[]
    for x in vs:
        for y in b: x=min(x,x^y)
        if x: b.append(x)
    return len(b)
worst=9
for s in range(112):
    ip=FC@FC[s]; N=[t for t in range(112) if abs(ip[t])==2]
    for k in (2,3):
        for rem in itertools.combinations(N,k):
            r=f2rank([LAB[u] for u in N if u not in rem])
            if r<8: print('drop',s,rem,r); worst=min(worst,r)
    if s==0: print('N size',len(N))
print('min rank of N(r) minus <=3 lines:',worst if worst<9 else 8)
