# KILL-ALL7 gen (impl A input): E8 lines+labels (CARRIER lib), 7-flat masks, W(E8)-orbit reps of masks, candidate directions.
import sys,itertools; sys.path.insert(0,'../CARRIER')
from lib import lines,lab,n,simple
assert n==120
par=lambda x: bin(x).count('1')&1
ip=lambda a,b: sum(x*y for x,y in zip(a,b))  # lines scaled by 2: roots have norm 8
masks=set()
for a in range(1,512):
    for b in range(a+1,512):
        m=0
        for t in range(n):
            if not par(a&lab[t]) and not par(b&lab[t]): m|=1<<t
        masks.add(m)
masks=sorted(masks); idx={m:i for i,m in enumerate(masks)}
print('distinct 7-flat masks',len(masks),'max size',max(bin(m).count('1') for m in masks))
def canon(v):
    for x in v:
        if x: return tuple(v) if x>0 else tuple(-y for y in v)
LI={l:i for i,l in enumerate(lines)}
gens=[]
for s in simple:
    perm=[LI[canon([x-(ip(l,s)*2//ip(s,s))*y for x,y in zip(l,s)])] for l in lines]; gens.append(perm)
def img(m,p):
    o=0; t=0
    while m:
        if m&1: o|=1<<p[t]
        m>>=1; t+=1
    return o
seen=[-1]*len(masks); reps=[]
for i in range(len(masks)):
    if seen[i]>=0: continue
    reps.append(i); seen[i]=i; st=[masks[i]]; sz=1
    while st:
        m=st.pop()
        for p in gens:
            q=img(m,p); j=idx[q]   # KeyError => not W-closed
            if seen[j]<0: seen[j]=i; st.append(q); sz+=1
    print('orbit rep',i,'size',sz,'|mask|',bin(masks[i]).count('1'))
# candidates: roots, A2 planes (2 vectors), E6A1 directions
cands=[]  # (offmask, [vectors])
off=lambda h: sum(1<<t for t in range(n) if ip(h,lines[t])!=0)
for r in lines: cands.append((off(r),[r]))
A2=set()
for i,j in itertools.combinations(range(n),2):
    if abs(ip(lines[i],lines[j]))==4:
        s=canon([x-y if ip(lines[i],lines[j])>0 else x+y for x,y in zip(lines[i],lines[j])]); k=LI[s]
        A2.add(tuple(sorted((i,j,k))))
print('A2 planes',len(A2))
for (i,j,k) in A2:
    a,b=lines[i],lines[j]
    g=[3*x+3*y for x,y in zip(a,b)]  # generic-ish; Off of generic = lines not orth to both a,b
    om=sum(1<<t for t in range(n) if ip(a,lines[t])!=0 or ip(b,lines[t])!=0)
    cands.append((om,[a,b]))
    for (u,v) in ((i,j),(j,k),(i,k)):  # E6A1: vector in plane orth to root lines[w] (w = third)
        w=({i,j,k}-{u,v}).pop(); x,y=lines[u],lines[v]
        # h = alpha x + beta y with <h,w>=0
        al,be=ip(y,lines[w]),-ip(x,lines[w]); h=[al*p+be*q for p,q in zip(x,y)]
        assert ip(h,lines[w])==0 and any(h)
        cands.append((off(h),[h]))
from collections import Counter
print('cands',len(cands),Counter(bin(c[0]).count('1') for c in cands))
with open('ka.in','w') as f:
    f.write('%d %d %d\n'%(len(masks),len(reps),len(cands)))
    for m in masks: f.write('%x\n'%m)
    f.write(' '.join(map(str,reps))+'\n')
    for om,vs in cands:
        f.write('%x %d %s\n'%(om,len(vs),' '.join(' '.join(map(str,v)) for v in vs)))
