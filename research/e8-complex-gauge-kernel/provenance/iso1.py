from kern import *
import numpy as np
def gram(E):
    return [[bin(a&b).count('1')&1 for b in E] for a in E]
def det2(G):
    n=len(G);M=[r[:] for r in G]
    for c in range(n):
        p=next((i for i in range(c,n) if M[i][c]),None)
        if p is None:return 0
        M[c],M[p]=M[p],M[c]
        for i in range(n):
            if i!=c and M[i][c]:M[i]=[x^y for x,y in zip(M[i],M[c])]
    return 1
def spanvecs(E):
    s={0}
    for b in E:s|={x^b for x in s}
    return s
ONE=511
def isometric(E):
    """E has orthonormal basis and E^perp (in F2^9) too"""
    if not E:return True
    if not det2(gram(E)):return False
    S=spanvecs(E)
    if ONE in S:return False                      # complement alternating
    if all(bin(x).count('1')%2==0 for x in S):return False   # E alternating
    # E^perp contains ONE?  ONE in E^perp iff all vectors of E even-weight -> excluded above
    return True
if __name__=='__main__':
    w=load();col,first=setup(w);R=len(col)
    # which first-frame subspaces are isometric
    cand={}
    for h,F in first.items():
        for E in subspaces(F):cand.setdefault(E,[]).append(h)
    iso={E:G for E,G in cand.items() if isometric(E)}
    print('first-frame subspaces',len(cand),'isometric',len(iso),Counter(len(E) for E in iso))
    C=np.zeros((v,R))
    for h in range(R):
        for t,x in col[h].items():C[t,h]=float(x)
    pot=[]
    for E,G in iso.items():
        if len(G)>=2:
            rk=np.linalg.matrix_rank(C[:,G]);
            if len(G)-rk>0:pot.append((len(E)*(len(G)-rk),E,len(G),rk))
    print('kernel potentials with isometric E',sorted(pot,reverse=True)[:10])
    # gauge: eligible helpers per isometric E
    from gauge import prep,span
    col2,first2,cap,cands,P=prep(w)
    best=[]
    for E in iso:
        sE=span(E)
        el=[h for h in range(R) if sE<=span(first2[h]) and all(sE<=cap[t] for t in col2[h])]
        best.append((len(E)*len(el),len(el),E))
    best.sort(reverse=True);print('gauge best isometric E (eps,n,E)',best[:8])
