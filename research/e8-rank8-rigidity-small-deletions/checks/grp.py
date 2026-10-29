import sys,pickle
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from e8lib import E,N,G
idx={}
for i,r in enumerate(E): idx[r]=i; idx[tuple(-x for x in r)]=i
def refl(i):
    r=E[i]; p=[]
    for j in range(N):
        v=E[j]; d=sum(a*b for a,b in zip(v,r))
        p.append(idx[tuple(a-d*b for a,b in zip(v,r))])
    return bytes(p)
assert G[0][2]!=0
gens=[refl(i) for i in range(N) if G[0][i]==0 and G[2][i]==0]
print('E6 refl lines',len(gens))
ident=bytes(range(N)); seen={ident}; fr=[ident]
while fr:
    nf=[]
    for p in fr:
        for g in gens:
            q=bytes(g[x] for x in p)
            if q not in seen: seen.add(q); nf.append(q)
    fr=nf
print('group order',len(seen), all(p[0]==0 and p[2]==2 for p in seen))
pickle.dump(list(seen),open('W6.pkl','wb'))
g8=[refl(i) for i in range(N)]
seenp={(0,2)}; st=[(0,2)]
while st:
    a,b=st.pop()
    for g in g8:
        q=(g[a],g[b])
        if q not in seenp: seenp.add(q); st.append(q)
nn=sum(1 for a in range(N) for b in range(N) if a!=b and G[a][b]!=0)
print('W(E8)-orbit of (0,2):',len(seenp),'ordered nonorth pairs:',nn,'implied stab order',696729600//len(seenp))
