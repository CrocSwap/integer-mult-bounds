import sys,collections
sys.path.insert(0,'../B256')
from lib import *
w=load(__import__('os').environ['EO_ROOT']+'/inputs/words/w1018.json.gz');P=w['ports']
def rank(vs):
    b=[]
    for v in vs:
        for x in b: v=min(v,v^x)
        if v: b.append(v)
    return len(b)
readers=collections.defaultdict(set)   # s -> targets reading s directly
tread=collections.defaultdict(list)
for part in 'AB':
    for i,e in enumerate(w[part]):
        if e[0]=='add' and V<=e[1]<2*V:
            readers[e[2]].add(e[1]-V); tread[e[1]-V].append((part,i,e[2]))
kind=lambda s:'x' if s<V else ('y' if s<2*V else 'h')
c=collections.Counter(); ex=[]
for s,T in readers.items():
    d=rank([P[t] for t in T])
    blocks=len(set(t//8 for t in T))
    c[(kind(s),len(T),d,blocks)]+=1
for k in sorted(c): print(k,c[k])
print('reads per target',collections.Counter(len(v) for v in tread.values()))
print('kinds per target', collections.Counter(tuple(sorted(collections.Counter(kind(s) for _,_,s in v).items())) for v in tread.values()).most_common(5))
