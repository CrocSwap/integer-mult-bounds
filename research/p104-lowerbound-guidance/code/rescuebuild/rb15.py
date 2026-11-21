"""rb15: joint walk+frame LM started from the best fixed-walk stall (tests whether a design needs a SPECIAL walk)."""
import sys,ast;sys.path.insert(0,'.')
from rb13 import *
def joint(k,R,nw=4,tr=8,bw=1e-4,it=1500):
    res=[]
    for w in range(nw):
        Q=anywalk(k,w);S=FSys(k,R,Q);nr,z=S.solve(w,tries=tr)
        J=WSys2(k,R,bw=bw);qp=np.concatenate([Q[i].ravel() for i in range(1,k)])
        zz,nr2=J.lm(np.concatenate([qp,z]),it=it,tol=1e-12)
        Qn=walk_gen(zz[:J.nq],k);trs=[round(float(np.trace(-Qn[t+1]@np.linalg.inv(Qn[t]))),3) for t in range(k)]
        res.append((round(float(nr),4),float(nr2),trs))
    return res
if __name__=='__main__':
    k=int(sys.argv[2])
    for l in open(sys.argv[1]).readlines()[int(sys.argv[3]):int(sys.argv[4])]:
        d=ast.literal_eval(l.split(' ',3)[3].strip());R=roles_of(d)
        print(l.split()[1],'design',joint(k,R),flush=True);print(l.split()[1],'coord',joint(k,fullsplit(R)),flush=True)
def joint_polish(k,R,w,tr=8,bw=1e-2,it=800,rounds=5,verbose=False):
    Q=anywalk(k,w);S=FSys(k,R,Q);nr,z=S.solve(w,tries=tr)
    J=WSys2(k,R,bw=bw);zz=np.concatenate([np.concatenate([Q[i].ravel() for i in range(1,k)]),z])
    for rd in range(rounds):
        J.bw=bw/10**rd;zz,nr2=J.lm(zz,it=it,tol=1e-13)
        Qn=walk_gen(zz[:J.nq],k);Qn=[q/np.sqrt(np.linalg.det(q)) if i not in (0,k) else q for i,q in enumerate(Qn)]
        S2=FSys(k,R,Qn);z2,nr3=S2.lm(zz[J.nq:],it=400,tol=1e-13)
        trs=[round(float(np.trace(-Qn[t+1]@np.linalg.inv(Qn[t]))),4) for t in range(k)]
        if verbose:print('   round',rd,'joint %.1e'%nr2,'fixed-walk polish %.1e'%nr3,trs,flush=True)
        if nr3<1e-11:return True,S2,z2,Qn
        if any(abs(abs(x)-2)<0.05 for x in trs):return False,S2,z2,Qn
    return False,S2,z2,Qn
def good_walk(Q,k,eps=0.1):
    tr=[float(np.trace(-Q[t+1]@np.linalg.inv(Q[t]))) for t in range(k)]
    al=[np.linalg.svd(np.linalg.inv(Q[s+1])-np.linalg.inv(Q[s]),compute_uv=False).min() for s in range(k)]
    be=[np.linalg.svd(Q[t+1]-Q[t],compute_uv=False).min() for t in range(k)]
    return all(abs(x-2)>eps and abs(x+2)>eps for x in tr) and min(al+be)>1e-3, tr, min(al+be)
def jbuild(k,R,starts=4,tr=8,rounds=5):
    """joint-walk build; returns (ok, info, S, z, Q). ok requires fixed-walk residual<1e-11 AND a nondegenerate walk."""
    best=None
    for w in range(starts):
        ok,S,z,Q=joint_polish(k,R,w,tr=tr,rounds=rounds)
        if ok:
            g,trs,mab=good_walk(Q,k)
            Qs,B,A,X,Y=S.unpack(z);P,W=to_real(Qs,B,A,k)
            info=dict(walk=w,tr=[round(x,4) for x in trs],minab=mab,svB=float(np.linalg.svd(B,compute_uv=False).min()),
                      svA=float(np.linalg.svd(A,compute_uv=False).min()),prod=float(np.abs(P+np.eye(S.n)).max()))
            if g:return True,info,S,z,Q
            best=info
    return False,best,None,None,None
