import json, numpy as np, itertools, random
D=json.load(open('../data.json')); FC=np.array(D['FC']); LAB=D['LAB']; Z=D['Z']
def basis(vs):
    b=[]
    for x in vs:
        for y in b: x=min(x,x^y)
        if x: b.append(x)
    return b
def rk(vs): return len(basis(vs))
def inspan(x,vs): return rk(list(vs)+[x])==rk(vs)
def beta(a,b):
    return (a&1)*(b&1) ^ (bin((a>>1)&(b>>1)).count('1')&1)  # assumes standard form on x -- see below
# Frame: N(f_j)
print('FC frame cols all in {0,+-1}:', set(FC.flatten()))
print('labels distinct',len(set(LAB)),'z in LAB?',[z in LAB for z in Z], 'Z indep rank',rk(Z))
for j in range(8):
    N=[t for t in range(112) if FC[t,j]!=0]
    Ls=[LAB[t] for t in N]
    print(j,len(N),'rank',rk(Ls),'z in span:',[inspan(z,Ls) for z in Z])
# gram-based: check N(f_j) in perp of z_j via span test above. coloop
def supp_rank(v): return rk([LAB[t] for t in range(112) if v[t]!=0])
# directions
dirs={}
for s in range(112): dirs[('r',s)]=FC@FC[s]
for j in range(8): dirs[('f',j)]=FC[:,j].copy()
off={k:int((v!=0).sum()) for k,v in dirs.items()}
print('Off sizes',sorted(set(off.values())))
rng=random.Random(1)
res={}
for t in range(112):
    for k,v in dirs.items():
        if off[k]>65: continue
        # candidate lambdas: 0, cancel at t, and generic
        lams=[0.0]
        if v[t]!=0: lams.append(-float(v[t]))
        lams.append(0.37)
        for lam in lams:
            w=v.astype(float).copy(); w[t]+=lam
            r=supp_rank(w)
            if r<=8:
                carry=[i for i in range(8) if inspan(Z[i],[LAB[u] for u in range(112) if w[u]!=0])]
                res.setdefault(t,[]).append((k,lam,r,tuple(carry),int((w!=0).sum())))
bad=0
for t in range(112):
    L8=[x for x in res.get(t,[])]
    nonf=[x for x in L8 if x[0][0]=='r' or x[3]]
    carr=[x for x in L8 if x[3]]
    # expected: all weight<=8 with carry is exactly swap
    ok = all(x[0]==('r',t) and x[1]!=0 and x[1]==-float(dirs[('r',t)][t]) for x in carr)
    others=[x for x in L8 if x[0][0]=='r' and not (x[0]==('r',t))]
    if not ok or others: bad+=1; print('t',t,carr,others)
print('t with deviations',bad)
# count of weight<=8 types
from collections import Counter
print(Counter((x[0][0], x[2], bool(x[3])) for t in res for x in res[t]))
# do all-direction scan for |Off|<=65 : which h among random sampling? enumerate low-Off by roots subsystem argument skipped
# rank of weight-8 swap carriers
t=0
sw=[x for x in res[t] if x[3]]; print(sw)
