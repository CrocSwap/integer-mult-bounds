"""Order-2 jets over the full-collapse base phi0 (support indicators, defined over F2).
P~ = phi0 P + eps X1 + eps^2 X2, Q~ likewise.  Target: every incidence has eps-order >= 3, every harmonic diagonal order <= 2,
non-harmonic diagonal order 0  => cycles dominated (Lemma VCR2) => cost >= v for every B.
Reduction: (X1,Y1) in V = ker A (A = first-order incidence functionals, over F2).  Order-2 incidence eqs: A(X2,Y2) = b(X1,Y1),
b_e = X1(t_e).Y1(s_e); solvable iff q_z(X1,Y1) = sum_e z_e b_e = 0 for every left-kernel vector z of A.  For a line t whose
first-order functional d_t lies in rowspace A (d_t = c.A, 'immovable'), the order-2 diagonal is the constant
Q_t = X1(t).Y1(t) + sum_e c_e b_e (independent of X2,Y2); other lines are generic at order <= 2."""
import itertools, numpy as np
def f2_rref(rows, n):
    """rows: list of int bitmasks (n bits). returns (pivot rows list with pivots, transform) -- simple elimination."""
    piv=[]  # (col, row, combo)
    for idx,r in enumerate(rows):
        comb=1<<idx
        for c,pr,pc in piv:
            if r>>c&1: r^=pr; comb^=pc
        if r:
            c=r.bit_length()-1
            # reduce others
            newpiv=[]
            for c2,pr,pc in piv:
                if pr>>c&1: pr^=r; pc^=comb
                newpiv.append((c2,pr,pc))
            piv=newpiv+[(c,r,comb)]
        else:
            yield ('dep', comb)
    yield ('piv', piv)
def analyse(P,Q,free,H):
    v=len(P); pi=[[j for j in range(3) if P[t][j]] for t in range(v)]; sig=[[j for j in range(3) if Q[t][j]] for t in range(v)]
    idx={}
    for t in range(v):
        for j in pi[t]: idx[('X',t,j)]=len(idx)
    for s in range(v):
        for j in sig[s]: idx[('Y',s,j)]=len(idx)
    n=len(idx)
    def lin(t,s):  # phi0 p(t).Y(s) + X(t).phi0 q(s)
        r=0
        for j in set(pi[t])&set(sig[s]): r^=(1<<idx[('Y',s,j)])^(1<<idx[('X',t,j)])
        return r
    E=list(free); rows=[lin(t,s) for (t,s) in E]
    deps=[]; piv=None
    for kind,x in f2_rref(rows,n):
        if kind=='dep': deps.append(x)
        else: piv=x
    # nullspace basis of A
    pcols={c:r for c,r,_ in piv}
    freec=[c for c in range(n) if c not in pcols]
    basis=[]
    for fcol in freec:
        vec=1<<fcol
        for c,r,_ in piv:
            if r>>fcol&1: vec|=1<<c
        basis.append(vec)
    # immovable lines: d_t in rowspace(A): reduce
    imm={}
    for t in H:
        r=lin(t,t); comb=0
        for c,pr,pc in piv:
            if r>>c&1: r^=pr; comb^=pc
        if r==0: imm[t]=comb   # d_t = sum_{e in comb} row_e
    return dict(idx=idx,n=n,E=E,deps=deps,basis=basis,imm=imm,pi=pi,sig=sig)
def quad_matrix(an, pairs):
    """quadratic form u -> sum over (t,s) in pairs of X1(t).Y1(s), on basis coords: returns d x d F2 matrix M (q(u) = u^T M u)."""
    idx=an['idx']; B=an['basis']; d=len(B)
    M=np.zeros((d,d),dtype=np.uint8)
    bits=lambda vec,k: (vec>>k)&1
    for (t,s) in pairs:
        for j in set(an['pi'][t])&set(an['sig'][s]):
            kx=idx[('X',t,j)]; ky=idx[('Y',s,j)]
            ax=np.array([bits(b,kx) for b in B],dtype=np.uint8); ay=np.array([bits(b,ky) for b in B],dtype=np.uint8)
            M^=np.outer(ax,ay)
    return M
def eval_quads(Ms, d, chunk=1<<18):
    """yield (u_int, values array) over all u in F2^d."""
    for start in range(0,1<<d,chunk):
        us=np.arange(start,min(start+chunk,1<<d),dtype=np.int64)
        U=((us[:,None]>>np.arange(d))&1).astype(np.uint8)
        vals=[ (np.einsum('ni,ij,nj->n',U,M,U,dtype=np.int64)&1) for M in Ms]
        yield us, vals
