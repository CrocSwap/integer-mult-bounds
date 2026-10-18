import sys,collections,itertools
sys.path.insert(0,'../B256')
from lib import *
w=load(__import__('os').environ['EO_ROOT']+'/inputs/words/w1018.json.gz');P=w['ports']
rows=rows_final(w)
def dot(a,b): return bin(a&b).count('1')&1
# y rows over x coords (0..111) and y coords (112..223)
supx=collections.Counter(); supy=collections.Counter(); orthviol=0; nb=collections.Counter()
for t in range(V):
    r=rows[V+t]
    xs=[k for k,v in r.items() if k<V and v!=0]; ys=[k-V for k,v in r.items() if V<=k<2*V and v!=0]
    hs=[k for k,v in r.items() if k>=2*V and v!=0]
    supx[len(xs)]+=1; supy[len(ys)]+=1
    nb[len(set(s//8 for s in xs))]+=1
    if t<3: print(t, 'x',[(s,str(r[s]),dot(P[s],P[t])) for s in xs][:20],'y',ys[:10],'h',len(hs))
print('x-support sizes',supx,'y-support',supy,'blocks touched',nb)
