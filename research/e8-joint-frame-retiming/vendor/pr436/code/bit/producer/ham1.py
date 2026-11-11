"""Dylan Crow, with Anthropic Claude assistance; Apache-2.0. Hand-structured bit-E8 hierarchy in Hamming coordinates (E8COORD=ham)."""
import os, sys, itertools, pickle
assert os.environ.get('E8COORD')=='ham'
import e8lib as E, frames as Fm
from collections import defaultdict
V=E.V
L=E.LINES
idx={}
for i,r in enumerate(L): idx[r]=i; idx[tuple(-a for a in r)]=i
frame_line=[idx[tuple(2 if k==i else 0 for k in range(8))] for i in range(8)]
blocks=sorted(set(tuple(k for k in range(8) if r[k]) for r in L if sum(1 for a in r if a)==4))
assert len(blocks)==14
def cw_lines(c): return [i for i,r in enumerate(L) if tuple(k for k in range(8) if r[k])==c]
class SH:
    """hierarchy with XOR semantics"""
    def __init__(self):
        self.content=[1<<s for s in range(V)]; self.frame=[Fm.LINE[s] for s in range(V)]; self.dim=[1]*V
        self.kids=[None]*V; self.key={c:i for i,c in enumerate(self.content)}; self.need=[set() for _ in range(V)]
    def sym(self,parts):
        """symbol = XOR of parts (symbols), built left to right as a binary chain"""
        cur=parts[0]
        for p in parts[1:]:
            c=self.content[cur]^self.content[p]
            w=self.key.get(c)
            if w is None:
                w=len(self.content); self.content.append(c); f,d=Fm.closure(self.frame[cur]|self.frame[p])
                self.frame.append(f); self.dim.append(d); self.kids.append((cur,p)); self.key[c]=w
            cur=w
        return cur
def build(variant=0):
    h=SH()
    # relative sign of line r on pair (i,j)
    def rel(r,i,j): return 1 if r[i]*r[j]>0 else -1
    Lsym={}; Psym={}
    for c in blocks:
        ls=cw_lines(c)
        for (i,j) in itertools.combinations(c,2):
            for rho in (1,-1):
                mem=[s for s in ls if rel(L[s],i,j)==rho]
                assert len(mem)==4
                # split into two pairs: pair lines that agree on the remaining pair (k,l) relative sign
                k,l=[q for q in c if q not in (i,j)]
                a=[s for s in mem if rel(L[s],k,l)==1]; b=[s for s in mem if rel(L[s],k,l)==-1]
                pa=h.sym(sorted(a)); pb=h.sym(sorted(b))
                Lsym[(c,i,j,rho)]=h.sym([pa,pb])
    Dsym={}
    for c in blocks:
        i,j=c[0],c[1]
        Dsym[c]=h.sym([Lsym[(c,i,j,1)],Lsym[(c,i,j,-1)]]+[frame_line[q] for q in c])
    Msym={}
    for c in blocks:
        for (i,j) in itertools.combinations(c,2):
            others=[c2 for c2 in blocks if c2!=c and i in c2 and j in c2]
            assert len(others)==2
            for rho in (1,-1):
                Msym[(c,i,j,rho)]=h.sym([Lsym[(others[0],i,j,rho)],Lsym[(others[1],i,j,rho)]])
    comp={c:[c2 for c2 in blocks if not set(c)&set(c2)][0] for c in blocks}
    for c in blocks:
        cb=comp[c]
        for t in cw_lines(c):
            r=L[t]
            def rho(i,j): return -rel(r,i,j)
            i,j,k,l=c   # level-5 pair (i,j), level-6 triangle (i,j,k)
            need=[Dsym[cb], Msym[(c,i,j,rho(i,j))], h.sym([Msym[(c,i,k,rho(i,k))],Msym[(c,j,k,rho(j,k))]]),
                  Msym[(c,i,l,rho(i,l))],Msym[(c,j,l,rho(j,l))],Msym[(c,k,l,rho(k,l))]]
            need+=[s for s in cw_lines(c) if E.G[t][s]==0]
            h.need[t]=set(need)
    for m in range(8):
        t=frame_line[m]
        need=[Dsym[c] for c in blocks if m not in c]+[frame_line[q] for q in range(8) if q!=m]
        h.need[t]=set(need)
    # verify XOR
    for t in range(V):
        x=0
        for u in h.need[t]: x^=h.content[u]
        assert x==Fm.HYP[t],(t,bin(x^Fm.HYP[t]).count('1'))
    return h
if __name__=='__main__':
    h=build()
    pickle.dump(h,open('hier_ham1.pkl','wb'))
    print('symbols',len(h.content)-V,'reads',sum(len(n) for n in h.need))
