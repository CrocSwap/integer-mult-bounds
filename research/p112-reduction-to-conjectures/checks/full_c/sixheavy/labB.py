# impl B data: own E8 build (doubled coords), labels via <r,alpha_i> mod 2 (unimodular dual), types via explicit h search.
import itertools, json, numpy as np
R=[]
for i,j in itertools.combinations(range(8),2):
    for a in (2,-2):
        for b in (2,-2):
            v=[0]*8; v[i]=a; v[j]=b; R.append(v)
for s in itertools.product((1,-1),repeat=8):
    if s.count(-1)%2==0: R.append(list(s))
R=np.array(R); assert len(R)==240
# one root per line: first nonzero coordinate positive
Ls=np.array([r for r in R if r[np.nonzero(r)[0][0]]>0]); assert len(Ls)==120
# Z-basis of E8 (doubled coords): simple roots (Bourbaki), different order
B=np.array([[0,0,0,0,0,-2,2,0],[0,0,0,0,-2,2,0,0],[0,0,0,-2,2,0,0,0],[0,0,-2,2,0,0,0,0],[0,-2,2,0,0,0,0,0],[-2,2,0,0,0,0,0,0],[2,2,0,0,0,0,0,0],[1,-1,-1,-1,-1,-1,-1,1]])
assert round(abs(np.linalg.det(B/2.0)))==1
ip=(Ls@B.T)//4
labels=[1+sum(int(x%2)<<(k+1) for k,x in enumerate(row)) for row in ip]
assert len(set(labels))==120
G=Ls@Ls.T
def info(h):
    p=Ls@h; perp=np.nonzero(p==0)[0]
    rk=np.linalg.matrix_rank(Ls[perp]) if len(perp) else 0
    return 120-len(perp), rk, [int(i) for i in np.nonzero(p!=0)[0]]
want={(57,7):'E7',(78,7):'D7',(83,7):'E6A1',(84,6):'E6',(92,7):'A7',(97,7):'D5A2',(98,7):'A1A6',(104,7):'A4A3',(106,7):'A1A2A4'}
found={}
rng=np.random.default_rng(1)
for t in range(200000):
    h=rng.integers(-3,4,size=8)
    o,rk,off=info(h)
    if (o,rk) in want and want[(o,rk)] not in found: found[want[(o,rk)]]=(h.tolist(),off)
    if len(found)==len(want): break
print({k:(v[0],len(v[1])) for k,v in found.items()})
json.dump({'labels':labels,'types':{k:v[1] for k,v in found.items()},'h':{k:v[0] for k,v in found.items()}},open('B.json','w'))
