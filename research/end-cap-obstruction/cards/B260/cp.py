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
n=2*V+w['report']['R']
rows=[{r:Q(1)} if r<2*V else {} for r in range(n)]   # data coords only
seq=[('A',i,e) for i,e in enumerate(w['A'])]+[('cut',i,e) for i,e in enumerate(w['cut'])]+[('B',i,e) for i,e in enumerate(w['B'])]
copies=[]; readers=collections.defaultdict(set); readinfo=collections.defaultdict(list)
for sec,i,e in seq:
    if e[0]=='add':
        t,s=e[1],e[2]
        if t>=2*V and not rows[t] and rows[s]: copies.append((sec,i,t,s))
        if V<=t<2*V and sec!='cut': readers[s].add(t-V); readinfo[s].append((sec,i,t-V,dict(rows[s])))
    G.apply_op(e,rows)
print('copy events (helper written from zero):',len(copies), collections.Counter((c[0],'x' if c[3]<V else 'y' if c[3]<2*V else 'h') for c in copies))
# content check: for each register read by >=2 targets, at each read, is x-support of content within common-orth of all its target readers?
def dot(a,b): return bin(a&b).count('1')&1
bad=collections.Counter()
for s,T in readers.items():
    if len(T)<2: continue
    T=sorted(T)
    for sec,i,t,row in readinfo[s]:
        xs=[k for k,v in row.items() if k<V and v]
        ok=all(dot(P[k],P[u])==0 for k in xs for u in T if k!=u)
        bad[(len(T),ok)]+=1
print('multi-reader reads: (|T|, content ⊆ common-orth?)',bad)
