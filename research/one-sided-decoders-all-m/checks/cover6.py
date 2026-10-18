# can targets N(f0), Off(r0) be covered by flats of dim<=6 using few pieces? exact search of minimal weight with pieces dim<=6
from base import *
par=lambda x: bin(x).count('1')&1
mask={z:sum(1<<t for t in range(v) if not par(z&LAB[t])) for z in range(1,512)}
pc=lambda m: bin(m).count('1')
def rk(m): return f2rank([LAB[t] for t in range(v) if m>>t&1])
Lnp=np.array([[float(c) for c in r] for r in L])
def off(h): return sum(1<<t for t in range(v) if abs(Lnp[t]@h)>1e-9)
targets={'N(f0)':off(np.array([float(c) for c in F0[0]])),'Off(r0)':off(Lnp[0])}
F6=set()
for a in range(1,512):
  for b in range(a+1,512):
    mab=mask[a]&mask[b]
    if pc(mab)<6: continue
    for c in range(b+1,512):
      if c==a^b: continue
      m=mab&mask[c]
      if pc(m)>=6: F6.add(m)
print('6-flats',len(F6),flush=True)
for name,T in targets.items():
    P={}
    for m in F6:
        x=m&T
        if pc(x)>=6:
            P[x]=min(P.get(x,9),rk(x))
    P=sorted(P.items(),key=lambda kv:-pc(kv[0]))
    print(name,'pieces',len(P),'max',pc(P[0][0]),flush=True)
    sizes=[pc(x) for x,_ in P]
    # 3-cover by dim<=6 pieces
    found=0
    for i,(x,w) in enumerate(P):
        if pc(x)*3<pc(T): break
        r1=T&~x
        for j in range(i,len(P)):
            y,w2=P[j]
            if pc(y)*2<pc(r1&~0): pass
            r2=r1&~y
            if pc(r2)>pc(y): 
                if pc(y)*2<pc(r1): break
                continue
            for z,w3 in P:
                if pc(z)<pc(r2): break
                if r2&~z==0: found+=1; print(name,'3-cover',w,w2,w3,pc(x),pc(y),pc(z)); break
            if found: break
        if found: break
    print(name,'3-cover by dim<=6 exists:',bool(found),flush=True)
