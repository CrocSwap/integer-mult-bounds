# Realisation-free deficiency test (Theorem 4'): for every label class O_z (= support of a nonzero vector in col(B), B = dense J+Abar,
# symmetric so row and column classes coincide), does O_z contain an orthogonal T-frame?  If yes for all z, no realisation of the
# pattern of rank T can have a deficient direction, so every term has full rank h under dense B.
import sys, pickle, itertools
from lib2 import *
def colspace_vectors(Brows,v):
    basis=[]  # gaussian elimination over F2 on rows (B symmetric => row space = column space)
    piv=[]
    for r in Brows:
        x=r
        for b,p in zip(basis,piv):
            if x>>p&1: x^=b
        if x:
            p=x.bit_length()-1
            for i in range(len(basis)):
                if basis[i]>>p&1: basis[i]^=x
            basis.append(x); piv.append(p)
    return basis
def run(name,L,T,live=None):
    if live is not None: L=[L[i] for i in live]
    v=len(L); G=Gmat(L); Brows=B0rows(L)
    basis=colspace_vectors(Brows,v); h=len(basis)
    og=nx.Graph(); og.add_nodes_from(range(v)); og.add_edges_from((t,s) for t in range(v) for s in range(t+1,v) if G[t][s]==0)
    frames=[frozenset(c) for c in nx.find_cliques(og) if len(c)>=T]
    alpha=max(len(c) for c in nx.find_cliques(og))
    fmasks=[sum(1<<t for t in f) for f in frames]
    bad=[]
    for coeffs in range(1,1<<h):
        w=0
        for i in range(h):
            if coeffs>>i&1: w^=basis[i]
        if not any((fm & ~w)==0 for fm in fmasks): bad.append(w)
    sizes=sorted(set(bin(w).count('1') for w in bad))
    print(name,"v",v,"T",T,"h",h,"alpha_orth",alpha,"#T-frames",len(frames),"classes without a T-frame:",len(bad),"sizes",sizes,flush=True)
    return bad
if __name__=="__main__":
    for name,L,T in [('D4',D4,4),('D5',D5,5),('D6',D6,6),('E6',E6,6),('E7',E7,7),('E8',E8,8)]:
        run(name,L,T)
