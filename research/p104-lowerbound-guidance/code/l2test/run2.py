from e8net import *
import random,sys
def lr_delta(n,density=1.0,seed=0,rows=None):
    """LR network + free extra hubs (a=b=0) realising Delta on EVEN cells only (random values): rank M' up to n."""
    W,U,vs=WU(n); N=Net(n); rng=random.Random(seed)
    g=[N.add([L[t]],[],{t:1},{}) for t in range(n)]
    for h in range(8):
        N.add([vs[h],1],[vs[h]],{}, {s:int(W[s,h])%P for s in range(n) if W[s,h]}, {g[t]:int(U[t,h]) for t in range(n) if U[t,h]%P})
    for s in (range(n) if rows is None else rows):
        rel={g[t]:rng.randrange(1,P) for t in range(n) if t!=s and not Qm[s,t] and rng.random()<density}
        N.add([],[],{},{s:1},rel)
    return N
def mrank(N):
    ok,Mm=N.check(); return ok,rankp(np.array(Mm,dtype=np.int64))
for n in (96,104):
    for rows in (list(range(0,2)),list(range(0,10)),list(range(0,20)),list(range(0,40)),list(range(0,n))):
        N=lr_delta(n,rows=rows,seed=1); bad=N.legal(); ok,rk=mrank(N); r=N.report('LR+delta%d'%len(rows))
        print(n,len(rows),'legal-bad',len(bad),'decoder-ok',ok,'rank M',rk,{k:r[k] for k in('D','YC','DX','loss','junk','viol')},r['lv'][:3],flush=True)
