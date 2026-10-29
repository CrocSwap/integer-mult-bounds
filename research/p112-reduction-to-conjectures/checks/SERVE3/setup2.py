# SERVE2 setup: own E8 build (doubled coords: +-e_i+-e_j*2, (+-1)^8 even # of minus), own labels (class mod 2E8 via Z-basis coords), own reflections.
import numpy as np, itertools
R=[]
for i,j in itertools.combinations(range(8),2):
    for a in (2,-2):
        for b in (2,-2):
            v=[0]*8; v[i]=a; v[j]=b; R.append(tuple(v))
for s in itertools.product((1,-1),repeat=8):
    if s.count(-1)%2==0: R.append(s)
assert len(R)==240
R=np.array(R)
key=lambda v: max(tuple(v),tuple(-v))
lines=sorted({key(v) for v in R}); assert len(lines)==120
L=np.array(lines)
# basis of root lattice: Bourbaki simple roots (doubled)
B=np.array([[1,-1,-1,-1,-1,-1,-1,1],[2,2,0,0,0,0,0,0],[-2,2,0,0,0,0,0,0],[0,-2,2,0,0,0,0,0],[0,0,-2,2,0,0,0,0],[0,0,0,-2,2,0,0,0],[0,0,0,0,-2,2,0,0],[0,0,0,0,0,-2,2,0]])
C=np.rint(np.linalg.solve(B.T.astype(float),L.T.astype(float)).T).astype(int)
assert (C@B==L).all()
lab=[1|sum(int(C[t][k]%2)<<(k+1) for k in range(8)) for t in range(120)]
assert len(set(lab))==120
IP=(L@L.T)//4
def mask(bs): return sum(1<<int(i) for i in np.nonzero(bs)[0])
roots_off=[mask(IP[r]!=0) for r in range(120)]
# norm-4 vectors (doubled coords) = sum of orthogonal root pair
d7=set()
for i in range(120):
    for j in range(i+1,120):
        if IP[i,j]==0:
            for sg in (1,-1): d7.add(key(L[i]+sg*L[j]))
assert len(d7)==1080
d7=sorted(d7); D=np.array(d7)
off=(D@L.T)!=0
assert set(off.sum(1))=={78}
d7_off=[mask(off[h]) for h in range(1080)]
pos={}
for t,v in enumerate(lines): pos[v]=t
perm=[]
for g in range(8):
    p=[]
    for t in range(120):
        w=L[t]-((L[t]@B[g])//4)*B[g]; p.append(pos[key(w)])
    perm.append(p)
with open('data.txt','w') as f:
    f.write(' '.join(map(str,lab))+'\n')
    for p in perm: f.write(' '.join(map(str,p))+'\n')
    for m in roots_off+d7_off: f.write('%d %d\n'%(m&(2**64-1),m>>64))
print('ok')
