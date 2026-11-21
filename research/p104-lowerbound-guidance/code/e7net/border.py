from lm7 import *
import pickle,sys
kind='e7'; ports=shard(kind); nodes=pickle.load(open(sys.argv[1],'rb'))
S=Struct(ports,nodes); print('D',S.D,[(len(a),len(b)) for a,b in S.nodes],'edges',len(S.edges),flush=True)
# track cost/norm along a long LM run
for sd in (101,105):
    rng=np.random.default_rng(sd); x=rng.normal(size=S.nv)*0.5; lam=1.0
    r,F,G,H,N,M=S.res(x); c=r@r
    for it in range(4000):
        J=S.jac(F,G,H,N,M); A=J.T@J; g=J.T@r
        while True:
            dx=-np.linalg.solve(A+lam*np.eye(S.nv),g); r2,F2,G2,H2,N2,M2=S.res(x+dx); c2=r2@r2
            if c2<c: x=x+dx; r,F,G,H,N,M=r2,F2,G2,H2,N2,M2; c=c2; lam=max(lam/3,1e-12); break
            lam*=4
            if lam>1e14: break
        if lam>1e14: break
        if it%250==0: print(sd,it,'c %.3e'%c,'|x| %.1f'%np.linalg.norm(x),'|H| %.1f'%np.linalg.norm(H),'lam %.1e'%lam,flush=True)
        if c<1e-18: break
    print('final',sd,c,np.linalg.norm(x),flush=True)
