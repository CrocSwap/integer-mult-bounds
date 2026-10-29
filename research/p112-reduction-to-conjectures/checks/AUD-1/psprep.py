import sys,pickle; sys.path.insert(0,'.')
from e8 import *
F,M=pickle.load(open('fm.pkl','rb'))
gens=[refl_perm(S[i]) for i in range(8)]
def img(m,p):
    o=0
    while m:
        b=m&-m; t=b.bit_length()-1; o|=1<<p[t]; m^=b
    return o
idx={m:i for i,m in enumerate(M)}; seen=[-1]*len(M); reps=[]; sizes=[]
for i,m in enumerate(M):
    if seen[i]>=0: continue
    reps.append(i); seen[i]=i; st=[m]; c=1
    while st:
        x=st.pop()
        for p in gens:
            y=img(x,p); j=idx[y]
            if seen[j]<0: seen[j]=i; st.append(y); c+=1
    sizes.append(c)
print('7-flat mask orbits',len(reps),sizes,sum(sizes))
# candidates
cands=[]  # (offmask, [vectors])
for t in range(120): cands.append((mask(off(L[t])),[L[t]]))
e=np.zeros(8); e[6]=1; w=np.linalg.solve(S.astype(float),e); w=w/np.abs(w).max()
# W-orbit of w (as rounded tuples)
key=lambda v: tuple(np.round(v,6))
orb={key(w):w}; st=[w]
while st:
    v=st.pop()
    for s in S:
        u=v-2*np.dot(v,s)/np.dot(s,s)*s; k=key(u)
        if k not in orb: orb[k]=u; st.append(u)
dirs={}
for k,v in orb.items():
    kk=max(k,tuple(-x for x in k)); dirs[kk]=np.array(kk)
print('E6A1 vectors',len(orb),'lines',len(dirs))
for v in dirs.values(): cands.append((mask(off(v)),[v]))
planes=set()
for a in range(120):
    for b in range(a+1,120):
        if abs(np.dot(L[a],L[b]))==4:  # doubled coords: true ip +-1
            v=L[a]+L[b] if np.dot(L[a],L[b])<0 else L[a]-L[b]
            planes.add(frozenset([a,b,lines.index(max(tuple(v),tuple(-v)))]))
print('A2 planes',len(planes))
for pl in planes:
    a,b,_=sorted(pl); cands.append((mask(off(L[a]))|mask(off(L[b])),[L[a],L[b]]))
with open('ps.in','w') as f:
    f.write('%d\n'%len(reps)+' '.join(str(i) for i in reps)+'\n%d\n'%len(cands))
    for m,vs in cands:
        f.write('%d %d %d '%(m&((1<<64)-1),m>>64,len(vs))+' '.join('%.6f'%x for v in vs for x in v)+'\n')
pickle.dump((reps,sizes),open('reps.pkl','wb'))
