from base import *
exec(open('cover.py').read().split("print('7-flats'")[0])
Lnp=np.array([[float(c) for c in r] for r in L])
def off(h): return sum(1<<t for t in range(v) if abs(Lnp[t]@h)>1e-9)
for name,T in {'N(f0)':off(np.array([float(c) for c in F0[0]])),'Off(r0)':off(Lnp[0])}.items():
    G={}
    for m,r in F7r:
        x=m&T
        if not x: continue
        w=rk(x); G[w]=max(G.get(w,0),pc(x))
    # monotone closure
    for w in range(1,8): G[w]=max(G.get(w,0),G.get(w-1,0))
    print(name,pc(T),G)
