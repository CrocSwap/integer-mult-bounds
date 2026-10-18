exec(open((__import__('os').environ['HM_ROOT']+'/cards/B176/common.py')).read())
from fractions import Fraction as Q
import collections
rows=[dict(r) for r in rows0] if False else None
# fresh replay from initial rows
NREG=716
R=[{i:Q(1)} if i<112 else {} for i in range(NREG)]
word=[]
for ph in phases:
    for e in d[ph]: word.append((ph,e))
need={}
for t in TW: need[t[1]]=t[2]
pairs=set(need.items())
# record at each op: for reads of u (src), rows equality with P
rd=collections.defaultdict(list)
wr=collections.Counter()
for n,(ph,e) in enumerate(word):
    if e[0]=='add':
        _,t,s,a,b,*_=e
        if s in need: rd[s].append((n,ph,R[s]==R[need[s]]))
        if t in need: wr[t]+=1
        q=Q(a,b)
        for j,x in list(R[s].items()):
            z=R[t].get(j,Q(0))+q*x
            if z:R[t][j]=z
            else:R[t].pop(j,None)
    else:
        _,t,a,b,*_=e
        if t in need: wr[t]+=1
        q=Q(a,b);R[t]={j:q*x for j,x in R[t].items()}
good=0
res=[]
for bn,u,P,*_ in TW:
    allr=rd[u]; bad=[x for x in allr if not x[2]]
    badA=[x for x in bad if x[1]=='A']
    ok=not bad
    good+=ok
    res.append((bn,u,P,len(allr),len(bad),len(badA),wr[u]))
    print(bn,u,P,'reads',len(allr),'unequal reads',len(bad),'(in A',len(badA),') writes to u',wr[u])
print('value-exact twins',good,'of',len(TW))
