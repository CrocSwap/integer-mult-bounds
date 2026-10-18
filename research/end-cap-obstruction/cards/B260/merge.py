import sys,collections,pickle
sys.path.insert(0,'../B256')
from lib import *
w=load(__import__('os').environ['EO_ROOT']+'/inputs/words/w1018.json.gz');P=w['ports']
def basis(vs):
    b=[]
    for v in vs:
        for x in b: v=min(v,v^x)
        if v: b.append(v)
    return b
orth=lambda v,T: all(bin(v&P[t]).count('1')%2==0 for t in T)
n=2*V+w['report']['R']
anc=[basis([P[r]]) if r<V else [] for r in range(n)]
for r,f in w.get('start_extra',{}).items(): anc[int(r)]=basis(list(f))
seq=w['A']+w['B']
rows=[{r:Q(1)} if r<2*V else {} for r in range(n)]
snap={}; copies=[]; reads=collections.defaultdict(list)
for k,e in enumerate(seq):
    if e[0]=='add':
        t,s=e[1],e[2]
        if t>=2*V and not rows[t] and rows[s]:
            copies.append((k,t,s)); snap[k]=(list(anc[s]),dict(rows[s]))
        if V<=t<2*V: reads[s].append((k,t-V,list(anc[s])))
        anc[t]=basis(anc[t]+anc[s])
    G.apply_op(e,rows)
st=collections.Counter(); keep=[]
for k,h,s in copies:
    Th={t for kk,t,a in reads[h] if kk>k}; Ts={t for kk,t,a in reads[s] if kk>k}
    if not Th or not Ts: continue
    T=sorted(Th|Ts)
    a_copy,row=snap[k]
    # ancestor floor: s's ancestors at copy time already inside common perp of T?
    anc_ok=all(orth(v,T) for v in a_copy)
    # s's ancestors at the time of its own later reads (drag after copy)
    a_late=basis([v for kk,t,a in reads[s] if kk>k for v in a])
    late_ok=all(orth(v,T) for v in a_late)
    xs=[c for c,v in row.items() if c<V and v]
    val_ok=all(orth(P[c],T) for c in xs)
    st[(len(T),anc_ok,late_ok,val_ok)]+=1
    keep.append((k,h,s,T,anc_ok,late_ok,val_ok,len(xs)))
print('(|T|, anc@copy ⊆ ∩perp, anc@late reads ⊆ ∩perp, value x-support ⊆ S_T):')
for x in sorted(st.items()): print(' ',x)
pickle.dump(keep,open('merge.pkl','wb'))
