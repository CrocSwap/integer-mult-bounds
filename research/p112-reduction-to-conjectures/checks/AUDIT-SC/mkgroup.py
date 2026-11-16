# AUDIT-SC: frame stabiliser in W(E8), as permutations of the 120 lines (own construction).
import numpy as np, random, pickle, sys
import p112 as p
idx={l:i for i,l in enumerate(p.LINES)}
def perm_of(fun): return np.array([idx[p.canon(fun(np.array(l)))] for l in p.LINES],dtype=np.int16)
def refl(a):
    a=np.array(a); return perm_of(lambda v: tuple(v-((v@a)//4)*a))
REF=[refl(r) for r in p.LINES]
gens=[]
def coord(f): return perm_of(lambda v: tuple(f(list(v))))
gens.append(coord(lambda v:[v[1],v[0]]+v[2:]))
gens.append(coord(lambda v:v[2:4]+v[0:2]+v[4:]))
gens.append(coord(lambda v:v[0:2]+v[4:6]+v[2:4]+v[6:]))
gens.append(coord(lambda v:v[0:4]+v[6:8]+v[4:6]))
for k in range(7): gens.append(coord(lambda v,k=k:[(-x if i in (k,k+1) else x) for i,x in enumerate(v)]))
F=set(p.FRAME)
def pres(g): return set(g[list(F)].tolist())==F
assert all(pres(g) for g in gens)
rng=random.Random(11); cur=np.arange(120,dtype=np.int16); extra=[]
for step in range(400000):
    cur=REF[rng.randrange(120)][cur]
    if pres(cur): extra.append(cur.copy())
    if len(extra)>=6: break
print('found',len(extra),'frame-preserving random elements after',step,'steps')
gens+=extra
# closure
seen={np.arange(120,dtype=np.int16).tobytes()}; frontier=[np.arange(120,dtype=np.int16)]
while frontier:
    nf=[]
    for g in frontier:
        for h in gens:
            k=h[g]; b=k.tobytes()
            if b not in seen: seen.add(b); nf.append(k)
    frontier=nf
print('|G| =',len(seen))
Gel=np.array([np.frombuffer(b,dtype=np.int16) for b in seen])
np.save('G.npy',Gel)
# label-linearity check on generators: label(g(l)) = A label(l) for some linear A (check via rank of joint system)
