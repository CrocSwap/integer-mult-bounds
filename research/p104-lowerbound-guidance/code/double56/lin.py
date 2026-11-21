import sys,json,numpy as np; sys.path.insert(0,'../orbitlp')
from geo import Q, D56
from rho import *
E=json.load(open(D56+'e8base.json')); Cc=np.array(E['C'])[:104]; Gb=np.array(E['Gb'])
n=104; rng=np.random.default_rng(int(sys.argv[1]) if len(sys.argv)>1 else 0)
def inv4(P):
    # inverse mod 4 via adjugate-free gaussian elim
    m=P.shape[0]; A=np.concatenate([P%4,np.eye(m,dtype=np.int64)],1)
    for c in range(m):
        p=next((i for i in range(c,m) if A[i,c]%2),None)
        if p is None: return None
        A[[c,p]]=A[[p,c]]; A[c]=(A[c]*(1 if A[c,c]%4==1 else 3))%4
        for i in range(m):
            if i!=c: A[i]=(A[i]-A[i,c]*A[c])%4
    return A[:,m:]
if __name__=="__main__":
    W0=Cc%4; V0=(Cc@Gb)%4
    print('base decoder',check_decoder(W0,V0,Q),'C',cost(W0,V0,Q), 'rho',rhos(W0,V0,Q)[:2])
    res=[]
    for trial in range(int(sys.argv[2]) if len(sys.argv)>2 else 30):
        m=8+int(rng.integers(0,5))
        while True:
            Xm=rng.integers(0,4,(8,m))
            # need Y with X Y^T = I mod 4: pick right inverse
            Pinv=None
            sub=Xm[:,:8]; Pi=inv4(sub)
            if Pi is not None: break
        Ym=np.zeros((8,m),dtype=np.int64); Ym[:,:8]=Pi.T
        # randomize: add kernel directions: Y += K where X K^T=0 ; skip
        W=(W0@Xm)%4; V=(V0@Ym)%4
        if not check_decoder(W,V,Q): print('bad'); continue
        rb,ra,_,_=rhos(W,V,Q,2); c=cost(W,V,Q); res.append((ra+rb,c,m)); print(trial,m,'C',c,'rhoA',ra,'rhoB',rb,'sum',ra+rb,flush=True)
    print('min rho sum',min(r[0] for r in res))
    