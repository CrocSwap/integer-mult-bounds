"""rb18: walks with prescribed Delta-zero pairs (Ghat_st = Ghat_ts), then fixed-walk frame solve."""
import sys,ast;sys.path.insert(0,'.')
from rb15 import *
from scipy.optimize import least_squares
def dz_walk(k,pairs,seed):
    rng=np.random.default_rng(seed)
    def res(qp):
        Q=walk_gen(qp,k);out=[np.linalg.det(Q[i])-1 for i in range(1,k)]
        inv=[np.linalg.inv(q) for q in Q];al=[inv[s+1]-inv[s] for s in range(k)];be=[Q[t+1]-Q[t] for t in range(k)]
        for s,t in pairs:out+=list((al[s]@be[t]+al[t]@be[s]).ravel())
        return np.array(out)
    for _ in range(50):
        qp=rng.normal(size=4*(k-1))
        r=least_squares(res,qp,xtol=1e-15,ftol=1e-15,gtol=1e-15,max_nfev=3000)
        if np.abs(res(r.x)).max()<1e-12:
            Q=walk_gen(r.x,k);Q=[q/np.sqrt(np.linalg.det(q)) if 0<i<k else q for i,q in enumerate(Q)]
            g,trs,mab=good_walk(Q,k)
            if g and all(np.linalg.cond(q)<50 for q in Q):return Q,trs
    return None,None
def dz_build(k,R,pairs,walks=4,tries=10):
    best=9
    for w in range(walks):
        Q,trs=dz_walk(k,pairs,100+w)
        if Q is None:print('   no good DZ walk',flush=True);continue
        S=FSys(k,R,Q);nr,z=S.solve(w,tries=tries);best=min(best,nr)
        if nr<1e-10:
            Qs,B,A,X,Y=S.unpack(z);P,W=to_real(Qs,B,A,k)
            return True,dict(tr=[round(x,3) for x in trs],prod=float(np.abs(P+np.eye(S.n)).max()),svB=float(np.linalg.svd(B,compute_uv=False).min()),svA=float(np.linalg.svd(A,compute_uv=False).min())),S,z
    return False,best,None,None
if __name__=='__main__':
    k=int(sys.argv[1]);d=ast.literal_eval(open(sys.argv[2]).readlines()[1].strip());pairs=ast.literal_eval(sys.argv[3])
    R=roles_of(d);ok,info,S,z=dz_build(k,R,pairs);print(sys.argv[2],'DZ',pairs,'BUILDS' if ok else 'stall',info,flush=True)
