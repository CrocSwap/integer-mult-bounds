# orbits of the 120 lines under reflections in chain roots + roots orthogonal to all chain roots (symmetry of the p=4 instance)
import sys,itertools
sys.argv=['x','3','1','4','o']
src=open('satP1.py').read().split("nv=0; cl=[]")[0]
exec(src)
def refl(r,v):
    c=ipf(v,r)*2//ipf(r,r) if False else None
    # doubled coords: ipf = dot//4 ; roots norm 2 => <v,r>=ipf ; s_r(v)=v-<v,r> r
    k=ipf(v,r)
    return tuple(a-k*b for a,b in zip(v,r))
gens=list(ch)+[r for r in R if all(ipf(r,c)==0 for c in ch)]
idx={l:i for i,l in enumerate(L)}
perms=[]
for r in gens:
    perms.append([idx[canon(refl(r,l))] for l in L])
seen=[-1]*n;orbs=[]
for t in range(n):
    if seen[t]<0:
        o=[t];seen[t]=t;k=0
        while k<len(o):
            for p in perms:
                u=p[o[k]]
                if seen[u]<0: seen[u]=t;o.append(u)
            k+=1
        orbs.append(o)
print([(o[0],len(o)) for o in orbs])
# check label linearity: reflections act linearly on labels?  test: map lab[t]->lab[p[t]] consistent linear map on span
def check(p):
    # solve over F2 using basis of rank-9 labels
    import itertools
    rows=[(int(''.join(map(str,lab[t])),2),int(''.join(map(str,lab[p[t]])),2)) for t in range(n)]
    basis=[]  # (v,img) echelon
    for v,w in rows:
        for bv,bw in basis:
            if v^bv<v: v^=bv;w^=bw
        if v: basis.append((v,w)); basis.sort(reverse=True)
        elif w: return False
    return True
print('linear',all(check(p) for p in perms))
