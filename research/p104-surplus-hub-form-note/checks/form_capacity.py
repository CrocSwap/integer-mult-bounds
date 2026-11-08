"""Numerical test of the form-capacity lemma (Theorem 5 of the note).
Constrain ONLY the Y outputs (Y'_t = x_t exactly: T[Y,X]=I, T[Y,Y]=0, T[Y,K]=0); X', K' free.
Lemma: then the pi-rank (forms mod span x) of (X',K') is <= |K| + ku, for every kd.
Target needs v+|K|.  So generic solutions must have pirank <= |K|+ku  (and ku<v makes full J/W impossible).
Solve with masked Gauss-Newton/LM; report pirank of X',K' via SVD and of all public outputs."""
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from stop_solver import forward,backward
from stop_family import skel
def solve_masked(rows,T,stops,nreg,npub,rng,iters=400,sigma=.4,tol=1e-11):
    Ms=[np.eye(len(r))+rng.normal(0,sigma,(len(r),len(r))) for f,r in stops]
    lam=1e-1;S,pres=forward(Ms,stops,nreg,npub);R=(S[:npub]-T)[rows];c=np.sum(R*R);nr=len(rows)
    for it in range(iters):
        if c<tol*tol:break
        posts=[p[rows] for p in backward(Ms,stops,nreg,npub)]
        G=np.zeros((nr*npub,nr*npub))
        for P,Q in zip(posts,pres):G+=np.kron(P@P.T,Q.T@Q)
        while True:
            W=np.linalg.solve(G+lam*np.eye(nr*npub),R.ravel()).reshape(nr,npub)
            new=[M-P.T@W@Q.T for M,P,Q in zip(Ms,posts,pres)]
            S2,pres2=forward(new,stops,nreg,npub);R2=(S2[:npub]-T)[rows];c2=np.sum(R2*R2)
            if c2<c:Ms,pres,R,c=new,pres2,R2,c2;lam=max(lam/3,1e-13);break
            lam*=4
            if lam>1e8:return Ms,np.sqrt(c),S
    S,_=forward(Ms,stops,nreg,npub)
    return Ms,np.sqrt(c),S
def pirank(S,v,npub,nk,tol=1e-7):
    # public register order: X(v), Y(v), K(nk). columns = inputs x(v),y(v),k(nk). pi: drop x columns
    XK=np.vstack([S[:v],S[2*v:npub]])[:,v:]
    return np.linalg.matrix_rank(XK,tol=tol)
def run(v,kd,ku,dbl,rs,fam='onepass',seed=0):
    names,npub,stops,nk=skel(v,kd,ku,fam,dbl);nreg=len(names);rng=np.random.default_rng(seed)
    T=np.eye(npub);T[v:2*v,:]=0;T[v:2*v,:v]=np.eye(v)
    rows=list(range(v,2*v));out=[]
    for i in range(rs):
        Ms,res,S=solve_masked(rows,T,stops,nreg,npub,rng)
        if res<1e-9:out.append(pirank(S,v,npub,nk))
        else:out.append(None)
    return nk,out
if __name__=='__main__':
    v=int(sys.argv[1]);rs=int(sys.argv[2]);dbl=sys.argv[3]=='dbl'
    for kd,ku in [(int(a),int(b)) for a,b in (s.split(',') for s in sys.argv[4:])]:
        nk,out=run(v,kd,ku,dbl,rs,fam=os.environ.get('FAM','onepass'),seed=kd*10+ku)
        ok=[o for o in out if o is not None]
        print(f'v={v} dbl={dbl} kd={kd} ku={ku} |K|={nk} bound |K|+ku={nk+ku} need v+|K|={v+nk}: solved {len(ok)}/{rs} pirank max={max(ok) if ok else None} all={out}',flush=True)
