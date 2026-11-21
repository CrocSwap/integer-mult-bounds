"""LINEAR56 relax_sa.py: annealing on the mod-2 relaxation (law-preserving moves). args: seed iters"""
import sys, numpy as np, math
from relax import *
rng=np.random.default_rng(int(sys.argv[1])); iters=int(sys.argv[2])
def norm(rows):
    d={}
    for q,p in rows:
        if not q.any() or not p.any(): continue
        k=(tuple(q),tuple(p)); d[k]=d.get(k,0)^1
    return [(np.array(a),np.array(b)) for (a,b),v in d.items() if v]
def rand_start():
    while True:
        Qm=rng.integers(0,2,(8,8))
        if f2rank(Qm)==8: break
    # P^T = Q^-1 B^-1
    R,_=rref(np.concatenate([Qm,np.eye(8,dtype=np.int64)],1)); Qi=R[:,8:].astype(np.int64)
    Pm=((Qi@Binv)%2).T
    return [(Qm[:,k],Pm[:,k]) for k in range(8)]
def move(rows):
    rows=[(q.copy(),p.copy()) for q,p in rows]; m=len(rows); t=rng.integers(0,5)
    if t<=1 and m>=2:
        i,j=rng.choice(m,2,replace=False); (qi,pi),(qj,pj)=rows[i],rows[j]
        if t==0: rows[i]=((qi+qj)%2,pi); rows[j]=(qj,(pi+pj)%2)
        else: rows[i]=(qi,(pi+pj)%2); rows[j]=((qi+qj)%2,pj)
    elif t==2 and m<16:
        i=rng.integers(m); q,p=rows[i]; r=rng.integers(0,2,8)
        if rng.random()<.5: rows[i]=(q,r); rows.append((q,(p+r)%2))
        else: rows[i]=(r,p); rows.append(((q+r)%2,p))
    elif t==3:
        # snap a coordinate to a Z16 point via split: (q,p)->(z,p),(q+z,p)
        i=rng.integers(m); q,p=rows[i]; z=Z16[rng.integers(16)]
        if rng.random()<.5: rows[i]=(z.copy(),p); rows.append(((q+z)%2,p))
        else: rows[i]=(q,z.copy()); rows.append((q,(p+z)%2))
    else:
        # merge rows sharing q or p
        for i in range(m):
            for j in range(i+1,m):
                if (rows[i][0]==rows[j][0]).all():
                    rows[i]=(rows[i][0],(rows[i][1]+rows[j][1])%2); rows.pop(j); return norm(rows)
                if (rows[i][1]==rows[j][1]).all():
                    rows[i]=((rows[i][0]+rows[j][0])%2,rows[i][1]); rows.pop(j); return norm(rows)
    return norm(rows)
best=99; hist={}
for start in range(4):
    rows=rand_start(); cur=f_relax(rows)[0]; T=1.5
    for it in range(iters):
        T=max(0.15,1.5*(1-it/iters))
        nr=move(rows)
        if not nr or not law_ok(nr): continue
        fv=f_relax(nr)
        if fv[0]<=cur or rng.random()<math.exp((cur-fv[0])/T):
            rows,cur=nr,fv[0]
            hist[cur]=hist.get(cur,0)+1
            if cur<best:
                best=cur; print('start',start,'it',it,'best',fv,'m',len(rows),flush=True)
                np.save(f'relax_best_s{sys.argv[1]}.npy',np.array([[*q,*p] for q,p in rows]))
print('final best',best,'hist',dict(sorted(hist.items())))
