"""E8 roots grouped into lines over an algebra A acting on R^8 (A spanned over Q by integer matrices preserving E8).
line = A-span of a root (a real subspace of dim = dim A); two lines are A-orthogonal iff <r, a s> = 0 for all basis a."""
import sys, itertools, numpy as np
sys.path.insert(0,'/Users/joelpulikkan/imb-main/research/format-limits/scripts')
from e8units import standard_e8, rank_q
import networkx as nx

def e8_roots():
    L,G=standard_e8(); return np.vstack([L,-L])          # doubled coords, norm 8

def left_quat():
    """left multiplication by i, j, k on each H-block of R^8 = H^2 (coords 1,i,j,k)."""
    Li=np.array([[0,-1,0,0],[1,0,0,0],[0,0,0,-1],[0,0,1,0]])
    Lj=np.array([[0,0,-1,0],[0,0,0,1],[1,0,0,0],[0,-1,0,0]])
    Lk=Li@Lj
    blk=lambda M: np.kron(np.eye(2,dtype=np.int64),M).astype(np.int64)
    return blk(Li),blk(Lj),blk(Lk)

def a2_rotation(roots):
    """a fixed-point-free order-3 element of W(E8): product of the Coxeter elements of 4 orthogonal A2's."""
    n8=lambda r: r@r
    def refl(a):
        return np.eye(8,dtype=np.int64)*8 - 2*np.outer(a,a)   # 8*s_a (norm 8): s_a = I - 2aa^T/8
    R=[tuple(r) for r in roots]
    chosen=[]
    def ok(a,b):
        return all(np.dot(a,x)==0 and np.dot(b,x)==0 for p in chosen for x in p)
    for a in roots:
        if len(chosen)==4: break
        if any(np.dot(a,x)!=0 for p in chosen for x in p): continue
        for b in roots:
            if np.dot(a,b)==-4 and ok(a,b):
                chosen.append((a,b)); break
    assert len(chosen)==4
    g=np.eye(8,dtype=object)
    for a,b in chosen:
        sa=np.eye(8,dtype=object)*8-2*np.outer(a,a).astype(object); sb=np.eye(8,dtype=object)*8-2*np.outer(b,b).astype(object)
        g=g.dot(sa).dot(sb)
    D=8**8//4
    assert all(x%D==0 for x in g.flatten()); g=(g//D).astype(np.int64)      # g = 4 * (order-3 isometry)
    I=np.eye(8,dtype=np.int64)
    assert (g@g@g==64*I).all() and (g@g+4*g+16*I==0).all()
    S=set(map(tuple,roots)); assert all(x%4==0 for r in roots for x in g@r) and all(tuple(g@r//4) in S for r in roots)
    return g

def lines_over(roots, basis):
    """basis: list of integer matrices (incl. identity) spanning the algebra.  Returns representative roots, the
    real span dimension d = len(basis), and the A-nonorthogonality matrix."""
    seen={}; reps=[]
    d=len(basis)
    for r in roots:
        key=None
        span=[list(B@r) for B in basis]
        assert rank_q(span)==d
        # canonical key: set of roots in the span
        found=False
        for i,rep in enumerate(reps):
            if rank_q([list(B@rep) for B in basis]+[list(r)])==d:
                found=True; break
        if not found: reps.append(r)
    reps=np.array(reps)
    v=len(reps)
    NO=np.zeros((v,v),bool)
    for B in basis:
        NO|=(reps@B@reps.T)!=0
    np.fill_diagonal(NO,False)
    return reps,NO

def clique_number(NO):
    v=len(NO); g=nx.Graph(); g.add_nodes_from(range(v))
    g.add_edges_from((i,j) for i in range(v) for j in range(i+1,v) if NO[i,j])
    K=max(nx.find_cliques(g),key=len); return len(K),sorted(K)

def arank(reps,basis,idx):
    rows=[list(B@reps[i]) for i in idx for B in basis]
    r=rank_q(rows) if rows else 0
    assert r%len(basis)==0; return r//len(basis)
