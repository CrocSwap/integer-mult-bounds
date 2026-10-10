import sys, json, importlib.util, collections, math
from fractions import Fraction as Q
PKG, DUMP = sys.argv[1], sys.argv[2]
def load(name):
    s=importlib.util.spec_from_file_location('m_'+name, PKG+'/'+name+'.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
cost=load('moment')
raw=json.load(open(DUMP+'/raw.json'))
H5=collections.Counter({int(k):v for k,v in raw['five_stage_profile']['histogram'].items()})
for a,n in {20:2200,21:266}.items(): H5[5*a]-=n
H5={k:v for k,v in H5.items() if v}
def kappa(H5p):
    mass=sum(k*n for k,n in H5p.items()); W_lit=mass//2+2200; literal={k:60*n for k,n in H5p.items()}; normalized={k:n//5 for k,n in literal.items()}; W=W_lit//5; m=120
    root=cost.certify(normalized,m,W,True); c=Q(int(Q(root['lower'])*10**18),10**18)
    chain=[Q(384599,10**10)]
    for _ in range(3): chain.append((1-c)*c+c*chain[-1])
    bit=chain[-1]; eta=Q(1,10**12); q=bit*(1-2*eta); mn=(1-eta)*q/(1+q); t=mn*10**18; return Q((t.numerator-1)//t.denominator,10**18)
pairs=json.load(open(DUMP+'/census2.json'))['pairs']
phi=lambda r: 0 if r<=0 else r*math.log(120/r)
gain=lambda p: phi(p['dima']-1)-phi(p['dima'])+phi(1)+phi(p['dimb']-1)-phi(p['dimb'])
pairs.sort(key=lambda p:(gain(p), p['a']))
print('gain by type:', sorted(collections.Counter((p['dima'],p['dimb'],round(gain(p),3)) for p in pairs).items(), key=lambda x:x[0][2]))
def apply(ps):
    H=collections.Counter(H5)
    for p in ps:
        ra,rb=p['dima'],p['dimb']; H[ra]-=5; H[ra-1]+=5; H[1]+=5; H[rb]-=5; H[rb-1]+=5
    H.pop(0,None); return {k:v for k,v in H.items() if v}
best=None
for K in range(300, 569, 4):
    k=kappa(apply(pairs[:K])); print(K, float(k))
    if best is None or k>best[1]: best=(K,k)
print('BEST', best[0], float(best[1]))
