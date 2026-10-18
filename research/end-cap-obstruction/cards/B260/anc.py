import sys,collections
sys.path.insert(0,'../B256')
from lib import *
w=load(__import__('os').environ['EO_ROOT']+'/inputs/words/w1018.json.gz');P=w['ports']
def basis(vs):
    b=[]
    for v in vs:
        for x in b: v=min(v,v^x)
        if v: b.append(v)
    return b
def span_in_perp(vs,T):  # all vs orthogonal to all ports of T
    return all(bin(v&P[t]).count('1')%2==0 for v in vs for t in T)
n=2*V+w['report']['R']
# ancestor-source port set (as F2 span basis) per register, through A/B ADD dag (cut ignored like caps.py); frames as caps.py too
anc=[basis([P[r]]) if r<V else [] for r in range(n)]
for r,f in w.get('start_extra',{}).items(): anc[int(r)]=basis(list(f))
cur=[list(a) for a in anc]
seq=[('A',i,e) for i,e in enumerate(w['A'])]+[('B',i,e) for i,e in enumerate(w['B'])]
rows=[{r:Q(1)} if r<2*V else {} for r in range(n)]
events=[]  # (time, kind, t, s, ancbasis, curframe)
copies=[]
for k,(sec,i,e) in enumerate(seq):
    if e[0]=='add':
        t,s=e[1],e[2]
        if t>=2*V and not rows[t] and rows[s]: copies.append((k,t,s))
        if V<=t<2*V: events.append((k,t-V,s,list(anc[s]),list(cur[s])))
        anc[t]=basis(anc[t]+anc[s])
        F=basis(cur[t]+cur[s]+list(G.basis(e[-1])))
        cur[t]=list(F); cur[s]=list(F)
    else:
        F=basis(cur[e[1]]+list(G.basis(e[-1]))); cur[e[1]]=F
    G.apply_op(e,rows)
rd=collections.defaultdict(list)
for k,t,s,a,f in events: rd[s].append((k,t,a,f))
res=collections.Counter(); ex=[]
for k,h,s in copies:
    Th={t for kk,t,a,f in rd[h] if kk>k}; Ts={t for kk,t,a,f in rd[s] if kk>k}
    if not Th or not Ts: res['one side unread']+=1; continue
    T=sorted(Th|Ts); d=len(basis([P[t] for t in T]))
    # ancestor floor at merged reads: s's ancestors at each of h's reads (s would be read instead of h)
    lastk=max(kk for kk,t,a,f in rd[h])
    a_s=[a for kk,t,a,f in rd[s] if kk>k]
    ancok=span_in_perp(anc_at(lastk) if False else [], T)
    res[(len(T),d)]+=1
    ex.append((k,h,s,sorted(Th),sorted(Ts),d))
print('copies',len(copies),'merge-union reader groups (|T|,span dim):',sorted(res.items(),key=str))
for x in ex[:8]: print(x)
import pickle; pickle.dump((events,copies),open('ev.pkl','wb'))
