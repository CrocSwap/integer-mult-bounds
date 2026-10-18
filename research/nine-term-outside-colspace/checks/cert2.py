# Support-propagation certificate (IDEAL3 §2). A class O is deficient in a rank-T realisation iff some h* != 0 kills p0(O).
# For every T-frame E write h* = sum_e c_e q0(e). Facts (any realisation of the zero pattern, rank T):
#  (1) c_e = 0 for e in E ∩ O  (h*(p0(e)) = c_e M_ee).
#  (2) if supp_E(c) ⊆ S_E then h* ∈ span q0(S_E), and q0(e) has E'-support ⊆ Nbar(e) ∩ E' (Nbar = non-orthogonal or equal),
#      so supp_{E'}(c) ⊆ ∪_{e∈S_E} Nbar(e).
# Iterate to a fixed point; any S_E = ∅ certifies O non-deficient (in every rank-T realisation).
import sys, pickle
from lib2 import *
from frames import colspace_vectors
from frames_data import load_frames
def setup(L,T):
    v=len(L); G=Gmat(L)
    og=nx.Graph(); og.add_nodes_from(range(v)); og.add_edges_from((t,s) for t in range(v) for s in range(t+1,v) if G[t][s]==0)
    frames=[sum(1<<t for t in c) for c in nx.find_cliques(og) if len(c)==T]
    nbar=[sum(1<<s for s in range(v) if G[t][s]!=0) for t in range(v)]
    return v,G,frames,nbar
def propagate(O,frames,nbar,v):
    S=[E & ~O for E in frames]
    while True:
        Wg=-1
        for s in S:
            w=0; x=s
            while x:
                b=x&-x; w|=nbar[b.bit_length()-1]; x^=b
            Wg&=w
        S2=[s & Wg for s in S]
        if S2==S: return S
        S=S2
def analyse(name,L,T,classes=None):
    v,G,frames,nbar=setup(L,T)
    if classes is None:
        basis=colspace_vectors(B0rows(L),v); h=len(basis); classes=[]
        for co in range(1,1<<h):
            w=0
            for i in range(h):
                if co>>i&1: w^=basis[i]
            classes.append(w)
    res=[]
    for O in classes:
        S=propagate(O,frames,nbar,v)
        res.append((O,min(bin(s).count('1') for s in S)))
    unc=[(O,m) for O,m in res if m>0]
    print(name,"frames",len(frames),"classes",len(classes),"uncertified",len(unc),"sizes",sorted(set(bin(O).count('1') for O,_ in unc)),flush=True)
    return unc
if __name__=="__main__":
    F0, F1 = load_frames()
    P112=[E8[i] for i in range(120) if i not in set(F0)]
    P104=[E8[i] for i in range(120) if i not in set(F0)|set(F1)]
    for name,L,T in [('D4',D4,4),('D6',D6,6),('E7',E7,7),('P112',P112,8),('P104',P104,8),('E8',E8,8)]:
        analyse(name,L,T)
