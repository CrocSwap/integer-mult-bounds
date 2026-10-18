# Soundness test of pin.py's clauses: evaluate every clause on the true Boolean data of actual rank-9 realisations
# (E8 A2 instance, B-form instances), for many frames. Any violated clause = unsound rule.
import sys, os, random, itertools, numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import pin
from pin import *
rng=np.random.default_rng(int(sys.argv[1]) if len(sys.argv)>1 else 0)
Rr=np.array(E,float); Gm=Rr@Rr.T
def bform(S,Sb):
    A=np.hstack([Rr,np.zeros((N,1))]); B=np.hstack([Rr,np.zeros((N,1))])
    A[S,8]=rng.normal(size=len(S)); B[Sb,8]=rng.normal(size=len(Sb))
    d1=np.exp(rng.normal(size=N)*0.3); d2=np.exp(rng.normal(size=N)*0.3)
    return (A*d1[:,None])@(B*d2[:,None]).T
def a2(seed,tri):
    import a2e8
    for t in range(1000):                     # redraw until the exact iff pattern holds (an unlucky draw creates an extra zero: not a realisation)
        u,A,B=a2e8.build_a2(seed+1000*t,tri); _,bad,full=a2e8.check(A,B,'a2')
        if not bad and full: break
    else: raise RuntimeError
    A=np.array([[float(x) for x in r] for r in A]); B=np.array([[float(x) for x in r] for r in B])
    return A@B.T, u
def cliques8():
    # greedy random clique
    for _ in range(1000):
        S=[]; c=list(range(N)); random.shuffle(c)
        for u in c:
            if all(Gm[u,w]!=0 for w in S): S.append(u)
        if len(S)>=6: return S
insts=[]
u0=0; insts.append(('B single row',bform([u0],[s for s in range(N) if Gm[u0,s]!=0])))
S=cliques8(); comn=[s for s in range(N) if all(Gm[s,w]!=0 for w in S)]
insts.append(('B clique %d/%d'%(len(S),len(comn)),bform(S,comn)))
for sd,tri in [(3,0),(11,150),(12,611),(13,900),(14,1119)]:      # several A2 parameter draws on several triangles (audit fix)
    Ma,tu=a2(sd,tri); insts.append(('A2 seed %d triangle %s'%(sd,tu),Ma))
FR=frames(); tol=1e-7
def assign(M,Fr):
    off=[u for u in range(N) if u not in Fr]
    Mt=sum(np.outer(M[:,f],M[f,:])/M[f,f] for f in Fr); R=M-Mt
    U,s_,Vt=np.linalg.svd(R); x=U[:,0]*s_[0]; y=Vt[0]
    assert s_[1]<1e-8*max(1,s_[0]), s_[:3]
    sc=np.abs(M).max()
    xb={u:bool(abs(x[u])>tol*max(1,np.abs(x).max())) for u in off}; yb={u:bool(abs(y[u])>tol*max(1,np.abs(y).max())) for u in off}
    al=lambda u,f: M[u,f]/M[f,f]; be=lambda s,f: M[f,s]
    return off,x,y,xb,yb,al,be
def close(a,b): return bool(abs(a-b)<=1e-6*max(1,abs(a),abs(b)))
bad_total=0
for name,M in insts:
    s_=np.linalg.svd(M,compute_uv=False); print(name,'rank9 ratio %.1e'%(s_[8]/s_[0]), 'orth max %.1e'%np.abs(M[(Gm==0)&~np.eye(N,dtype=bool)]).max())
    for Fr in [FR[i] for i in rng.choice(len(FR),int(sys.argv[2]) if len(sys.argv)>2 else 8,replace=False)]:
        pin.cl.clear(); pin.nv[0]=0
        X,Y,EQ=pin.build(Fr,dict(residue=0,notgram=0))
        D1=pin.D1_; RQ=pin.RQ_
        off,x,y,xb,yb,al,be=assign(M,Fr)
        val={}
        for u in off: val[X[u]]=xb[u]; val[Y[u]]=yb[u]
        TT=tetrads(Fr); Tof={u:T for T in TT for u in TT[T]}
        for p,V in EQ.items():
            a,b=sorted(p)
            def v_(e):
                k,u=e
                return al(u,b)/al(u,a) if k=='r' else -be(u,a)/be(u,b)
            done=set()
            for (e1,e2),var in V.items():
                if var in done: continue
                done.add(var); val[var]=close(v_(e1),v_(e2))
        for (kind,i),Vr in RQ.items():
            for (u,w),var in Vr.items():
                if kind=='r': r1=x[u]/al(u,i) if xb[u] else 0; r2=x[w]/al(w,i) if xb[w] else 0
                else: r1=y[u]/be(u,i) if yb[u] else 0; r2=y[w]/be(w,i) if yb[w] else 0
                val[var]=close(r1,r2)
        for key,d in D1.items(): val[d]=False
        # D1 true iff its forcing condition holds: easiest: set True if any forcing clause would be violated
        for c in pin.cl:
            pos=[l for l in c if l>0 and l in D1.values()] if False else None
        dset=set(D1.values())
        for c in pin.cl:
            ds=[l for l in c if l in dset]
            if ds and all((val.get(abs(l)) if l>0 else not val.get(abs(l))) is False for l in c if abs(l) not in dset):
                for l in ds: val[l]=True
        nb=0
        for c in pin.cl:
            if not any((val[abs(l)] if l>0 else not val[abs(l)]) for l in c): 
                nb+=1
                if nb<=3: print('  VIOLATED',c[:8])
        bad_total+=nb
        print('  frame',Fr[:3],'|D|',sum(xb.values()),'|D\'|',sum(yb.values()),'violated',nb,flush=True)
print('TOTAL violated',bad_total)
