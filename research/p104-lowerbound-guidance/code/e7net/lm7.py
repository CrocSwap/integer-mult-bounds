# numeric LM feasibility for a chart structure (nodes (a,b), legal relay edges free): find F,G,H with G^T (I-H)^-1 F = delta on odd cells.
from lib7 import *
import random, time
class Struct:
    def __init__(s,ports,nodes,order=True):
        """nodes: list of (aB,bB) spans. sorted by dim a desc. edges j->k (j<k) iff b_j<=a_k"""
        setlabels(ports); s.ports=ports; s.n=len(ports); s.lab=NL.L
        s.nodes=sorted(nodes,key=lambda x:-len(x[0])); s.m=len(s.nodes)
        s.Q=NL.Qm
        s.Fm=np.array([[inspan(a,l) for l in s.lab] for a,b in s.nodes],dtype=bool)
        s.Gm=np.array([[all(dot(l,x)==0 for x in b) for l in s.lab] for a,b in s.nodes],dtype=bool)
        s.edges=[(j,k) for k in range(s.m) for j in range(k) if all(inspan(s.nodes[k][0],x) for x in s.nodes[j][1])]
        s.D=sum(len(a)-len(b) for a,b in s.nodes)
        s.Fi=np.argwhere(s.Fm); s.Gi=np.argwhere(s.Gm)
        s.nv=len(s.Fi)+len(s.Gi)+len(s.edges)
        s.odd=np.argwhere(s.Q==1)       # (a,b) with a deposit,b gather
        s.tgt=np.array([1.0 if a==b else 0.0 for a,b in s.odd])
    def unpack(s,x):
        m,n=s.m,s.n; F=np.zeros((m,n)); G=np.zeros((m,n)); H=np.zeros((m,m))
        i=len(s.Fi); F[s.Fi[:,0],s.Fi[:,1]]=x[:i]; j=i+len(s.Gi); G[s.Gi[:,0],s.Gi[:,1]]=x[i:j]
        for e,(a,b) in enumerate(s.edges): H[b,a]=x[j+e]
        return F,G,H
    def res(s,x):
        F,G,H=s.unpack(x); N=np.linalg.inv(np.eye(s.m)-H); M=G.T@N@F
        return M[s.odd[:,0],s.odd[:,1]]-s.tgt,F,G,H,N,M
    def jac(s,F,G,H,N,M):
        m,n=s.m,s.n; GN=G.T@N; NF=N@F  # GN: n x m ; NF: m x n
        odd=s.odd; no=len(odd); J=np.zeros((no,s.nv))
        i0=len(s.Fi)
        # F var (k,sx): dM[a,b] = GN[a,k] if b==sx
        J[:,:i0]=GN[odd[:,0][:,None],s.Fi[:,0][None,:]]*(odd[:,1][:,None]==s.Fi[:,1][None,:])
        # G var (k,t): dM[a,b]= NF[k,b] if a==t
        J[:,i0:i0+len(s.Gi)]=NF[s.Gi[:,0][None,:],odd[:,1][:,None]]*(odd[:,0][:,None]==s.Gi[:,1][None,:])
        j0=i0+len(s.Gi)
        for e,(a,b) in enumerate(s.edges):
            J[:,j0+e]=GN[odd[:,0],b]*NF[a,odd[:,1]]
        return J
    def solve(s,seed,iters=150,tol=1e-9,verbose=False):
        rng=np.random.default_rng(seed); x=rng.normal(size=s.nv)*0.5; lam=1.0
        r,F,G,H,N,M=s.res(x); c=r@r
        for it in range(iters):
            J=s.jac(F,G,H,N,M); A=J.T@J; g=J.T@r
            while True:
                try: dx=-np.linalg.solve(A+lam*np.eye(s.nv),g)
                except np.linalg.LinAlgError: lam*=10; continue
                r2,F2,G2,H2,N2,M2=s.res(x+dx); c2=r2@r2
                if c2<c: x=x+dx; r,F,G,H,N,M=r2,F2,G2,H2,N2,M2; c=c2; lam=max(lam/3,1e-9); break
                lam*=4
                if lam>1e12: return c,x
            if verbose and it%10==0: print(it,c,lam,flush=True)
            if c<tol: break
        return c,x
