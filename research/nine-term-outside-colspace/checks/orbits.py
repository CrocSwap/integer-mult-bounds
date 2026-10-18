# automorphisms of the P112 / P104 line system induced by reflections of E8 that preserve the removed set; orbits on label classes
from setup9 import *
from lib2 import E8, dot
from fractions import Fraction as Fr
unit=sys.argv[1]
L,v,G,frames,nbar,h,basis,cls=load(unit)
F0, F1 = load_frames()
rem=set(F0) if unit=='P112' else set(F0)|set(F1)
def canon(x):
    for c in x:
        if c!=0: return tuple(x) if c>0 else tuple(-y for y in x)
idx={canon(r):i for i,r in enumerate(E8)}
gens=[]
for a in E8:
    aa=dot(a,a)
    img=[idx[canon([ri-Fr(2*dot(r,a),aa)*ai for ri,ai in zip(r,a)])] for r in E8]
    gens.append(img)
refl=gens; gens=[]
for a in range(120):
    for b in range(120):
        g=[refl[a][refl[b][i]] for i in range(120)]
        if set(g[i] for i in rem)==rem and g not in gens: gens.append(g)
liv=[i for i in range(120) if i not in rem]; pos={x:k for k,x in enumerate(liv)}
perms=[[pos[g[i]] for i in liv] for g in gens]
print('reflection generators',len(perms))
inv={cls[c]:c for c in cls}
def img(O,p):
    r=0
    for t in range(v):
        if O>>t&1: r|=1<<p[t]
    return r
seen={}; orbs=[]
for c in sorted(cls):
    if c in seen: continue
    orb=[c]; seen[c]=len(orbs); st=[c]
    while st:
        x=st.pop()
        for p in perms:
            y=inv[img(cls[x],p)]
            if y not in seen: seen[y]=len(orbs); orb.append(y); st.append(y)
    orbs.append(orb)
print('class orbits',[(pc(cls[o[0]]),len(o)) for o in orbs])
pickle.dump({'perms':perms,'orbs':orbs},open(f'orbits_{unit}.pkl','wb'))
