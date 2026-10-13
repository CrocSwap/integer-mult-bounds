"""Generic line systems over an algebra A (imaginary quadratic field or quaternions) in a real model.
A system = (V, Q, basis): V integer vectors (one per line), Q integer symmetric positive-definite Gram (real model),
basis = integer matrices spanning A (identity first), acting on the left.  A-lines L = A.v.  Two lines are A-orthogonal iff
v^T Q B u = 0 for every B in the basis.  A-rank of a set = real rank of {B v} / dim A.  Everything exact."""
import itertools, sys
import numpy as np
sys.path.insert(0,'/Users/joelpulikkan/imb-main/research/format-limits/scripts')
from e8units import rank_q
import networkx as nx

class System:
    def __init__(self, name, V, Q, basis):
        self.name=name; self.V=np.array(V,dtype=np.int64); self.Q=np.array(Q,dtype=np.int64); self.basis=[np.array(B,dtype=np.int64) for B in basis]
        self.d=len(self.basis); self.v=len(self.V)
        NO=np.zeros((self.v,self.v),bool)
        for B in self.basis: NO|=(self.V@self.Q@B@self.V.T)!=0
        np.fill_diagonal(NO,False); self.NO=NO
        self.w=self.rank(range(self.v))
    def rank(self,idx):
        rows=[list(B@self.V[i]) for i in idx for B in self.basis]
        if not rows: return 0
        r=rank_q(rows); assert r%self.d==0; return r//self.d
    def graph(self):
        g=nx.Graph(); g.add_nodes_from(range(self.v))
        g.add_edges_from((i,j) for i in range(self.v) for j in range(i+1,self.v) if self.NO[i,j]); return g
    def alpha(self):
        """max pairwise A-nonorthogonal set (clique of the nonorth graph); exact (networkx max clique enumeration)."""
        K=max(nx.find_cliques(self.graph()),key=len); return len(K),sorted(K)

def dedup_lines(vecs, basis, Q=None):
    """group vectors into A-lines: u ~ v iff rank{B u, B v} = d.  Keeps the first vector of each line."""
    reps=[]; keys={}
    d=len(basis)
    for x in vecs:
        x=np.array(x,dtype=np.int64)
        orb=[]
        # line membership test via exact rank
        found=False
        for r in reps:
            if rank_q([list(B@r) for B in basis]+[list(x)])==d: found=True; break
        if not found: reps.append(x)
    return reps

# ---------------------------------------------------------------------------------------------------------------
# Eisenstein integers in real coordinates (a, b) <-> a + b w, w^2 + w + 1 = 0.  2*Re(x conj y) form per coordinate.
EIS_Q=np.array([[2,-1],[-1,2]]); EIS_W=np.array([[0,-1],[1,-1]])     # multiplication by w: (a,b) -> (-b, a-b)
def eis_system(name, vecs_complex, n):
    """vecs_complex: list of tuples of (a,b) pairs, length n."""
    V=[[c for ab in x for c in ab] for x in vecs_complex]
    Q=np.kron(np.eye(n,dtype=np.int64),EIS_Q); W=np.kron(np.eye(n,dtype=np.int64),EIS_W)
    return System(name, V, Q, [np.eye(2*n,dtype=np.int64), W])
