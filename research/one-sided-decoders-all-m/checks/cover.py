# exact min weight cover of target line sets by label flats of dim<=7 (pairs/triples search)
from base import *
par=lambda x: bin(x).count('1')&1
mask={z:sum(1<<t for t in range(v) if not par(z&LAB[t])) for z in range(1,512)}
pc=lambda m: bin(m).count('1')
def rk(m): return f2rank([LAB[t] for t in range(v) if m>>t&1])
# all 7-flat line sets (codim 2) and 6-flat line sets (codim 3) with >=8 lines; keep (lines, dim=rank)
F7=set()
for a in range(1,512):
    for b in range(a+1,512):
        m=mask[a]&mask[b]
        if pc(m)>=4: F7.add(m)
F7=list(F7)
F7r=[(m,rk(m)) for m in F7]
print('7-flats',len(F7),flush=True)
Lnp=np.array([[float(c) for c in r] for r in L])
def off(h): return sum(1<<t for t in range(v) if abs(Lnp[t]@h)>1e-9)
targets={'N(f0)':off(np.array([float(c) for c in F0[0]])),'Off(r0)':off(Lnp[0])}
for name,T in targets.items():
    # restrict flats to T, keep maximal pieces: piece = flat ∩ T, weight = rank of labels(flat∩T)
    pieces={}
    for m,r in F7r:
        x=m&T
        if pc(x)<4: continue
        w=rk(x)
        if x not in pieces or pieces[x]>w: pieces[x]=w
    P=sorted(pieces.items(),key=lambda kv:-pc(kv[0]))
    best=99
    big=[(x,w) for x,w in P if pc(x)>=17]
    for i,(x,w) in enumerate(big):
        rest=T&~x
        for y,w2 in P:
            if w+w2>=best: continue
            if rest&~y==0: best=w+w2; print(name,'pair',w,w2,pc(x),pc(y),flush=True)
    print(name,'|T|',pc(T),'best pair cover',best,flush=True)
# triple cover for Off(r0)
T=targets['Off(r0)']
pieces={}
for m,r in F7r:
    x=m&T
    if pc(x)<2: continue
    w=rk(x)
    if x not in pieces or pieces[x]>w: pieces[x]=w
# add singletons / small
for t in range(v):
    if T>>t&1: pieces.setdefault(1<<t,1)
P=sorted(pieces.items(),key=lambda kv:-pc(kv[0]))
print('pieces',len(P),'max',pc(P[0][0]),flush=True)
best=22
for i,(x,w) in enumerate(P):
    if pc(x)*3<pc(T): break
    r1=T&~x
    for j in range(i,len(P)):
        y,w2=P[j]
        if w+w2+1>=best: continue
        r2=r1&~y
        if pc(r2)> pc(y): continue
        if r2==0: best=w+w2; print('pair!',w,w2); continue
        # need third piece covering r2
        for z,w3 in P:
            if w+w2+w3>=best: continue
            if r2&~z==0: best=w+w2+w3; print('triple',w,w2,w3,pc(x),pc(y),pc(z),flush=True); break
print('Off(r0) best <=3-cover',best)
