import sys,numpy as np
sys.path.insert(0,'.');from rbcore import *
F=frozenset
def okwalk(Q,k):
    tr=[np.trace(-Q[t+1]@np.linalg.inv(Q[t])) for t in range(k)]
    return all(abs(x-2)>.3 and abs(x+2)>.3 and abs(x)<5 for x in tr) and all(np.linalg.cond(q)<30 for q in Q)
def rwalk(k,seed):
    rng=np.random.default_rng(seed)
    while True:
        Q=walk_mats(np.concatenate([[rng.uniform(.7,1.5),rng.normal(),rng.normal()] for _ in range(k-1)]),k)
        if okwalk(Q,k):return Q
def swalk(k,seed,tau=0.0):
    """walk with tr W_t = tau for t<k-1 (last determined)"""
    rng=np.random.default_rng(seed);Q=[np.eye(2)]
    for t in range(k-1):
        while True:
            a=rng.normal();b=rng.normal();c=rng.normal();d=tau-a
            if abs(a*d-b*c)>.2:break
        # scale to det 1 keeping trace: solve with c free
        c=(a*d-1)/b;W=np.array([[a,b],[c,d]]);Q.append(-W@Q[-1])
    Q=Q[:k]+[-np.eye(2)]
    return Q if okwalk(Q,k) else swalk(k,seed+1000,tau)
def anywalk(k,w):
    return rwalk(k,500+w) if w%2==0 else swalk(k,900+w,tau=[0.0,-1.0,1.0][(w//2)%3])
def run(name,k,roles,seeds=3,tries=10,quiet=False):
    if not quiet:print(name,'mains',check_design(k,roles),'chat',round(float(chat(k,roles)),4),flush=True)
    out=[]
    for sd in range(seeds):
        Q=rwalk(k,100+sd);S=FSys(k,roles,Q);nr,z=S.solve(sd,tries=tries)
        msg=''
        if nr<1e-9:
            P,W=to_real(*S.unpack(z)[:3],k);d=S.diag(z);msg='prod+I %.1e svB %.2e svA %.2e'%(np.abs(P+np.eye(S.n)).max(),d['svB'],d['svA'])
        if not quiet:print('  seed',sd,'res %.2e'%nr,msg,flush=True)
        out.append((nr,S,z))
    return out
C1=[(F({1,2}),[]),(F({1,2}),[]),(F({0,1,2}),[F({1}),F({2})]),(F({0,1,2}),[F({1}),F({2})])]
if __name__=='__main__':run('C1',3,C1)
