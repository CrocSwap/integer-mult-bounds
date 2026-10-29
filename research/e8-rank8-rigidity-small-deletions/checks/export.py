import sys,pickle,json,struct
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from e8lib import N,G,frames,tetrads
R='./'
W=pickle.load(open(R+'W6.pkl','rb'))
print(N,len(W),type(W[0]))
cores=json.load(open(os.environ['DATA']+'/cores_v.json'))
imgs=set()
for c in cores:
    for p in W: imgs.add(frozenset(p[x] for x in c)-{0,2})
print('imgs',len(imgs))
def m(s):
    v=0
    for x in s: v|=1<<x
    return v
with open('imgs.bin','wb') as f:
    for s in imgs:
        v=m(s); f.write(struct.pack('<QQ',v&(2**64-1),v>>64))
# W orbits on the 118 lines
seen={};orb=[]
for x in range(N):
    if x in(0,2) or x in seen: continue
    o={p[x] for p in W}; 
    for y in o: seen[y]=len(orb)
    orb.append(sorted(o))
print('orbits',[len(o) for o in orb])
json.dump(orb,open('orbs.json','w'))
FR=frames(); print(len(FR))
with open('frames.bin','wb') as f:
    for F in FR:
        T=list(tetrads(F).values()); assert len(T)==14
        for t in T:
            v=m(t); f.write(struct.pack('<QQ',v&(2**64-1),v>>64))
print([len(t) for t in T])
