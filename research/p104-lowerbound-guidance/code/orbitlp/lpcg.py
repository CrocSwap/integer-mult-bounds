"""ORBITLP lpcg.py: column generation for  min price.x  s.t.  Acols x >= b  over profile matrix P (rows=columns of LP).
Usage: lpcg.py prof.npy [cols...]  ; families selected by column index list. Exact dual check in integers."""
import numpy as np, sys
from scipy.optimize import linprog
from fractions import Fraction as Fr
def load_orbits():
    L=open('geo.txt').read().split('\n'); NA=int(L[1]); NF=int(L[2+NA])
    fo=[int(L[3+NA+i].split()[-1]) for i in range(NF)]; po=list(map(int,L[3+NA+NF].split()))
    return np.bincount(fo), np.bincount(po)
def solve(P, price, b, verbose=True, maxit=200):
    m=P.shape[1]
    # init: columns with best ratio per constraint
    idx=set()
    for j in range(m):
        r=P[:,j]/np.maximum(price,1e-9); idx|=set(np.argsort(-r)[:50].tolist())
    idx|=set(np.argsort(-(P.sum(1)/np.maximum(price,1e-9)))[:200].tolist())
    for it in range(maxit):
        I=np.array(sorted(idx))
        res=linprog(price[I], A_ub=-P[I].T.astype(float), b_ub=-b.astype(float), bounds=(0,None), method='highs')
        y=-res.ineqlin.marginals
        rc=price - P@y
        k=np.argsort(rc)[:300]
        if verbose: print('it',it,'cols',len(I),'obj',res.fun,'min rc',rc[k[0]])
        if rc[k[0]]>-1e-9: break
        idx|=set(k[rc[k]<-1e-9].tolist())
    return res, y, I
def exact_dual(P, price, b, y, D=10**7):
    """y -> floor(y*D)/D, then scale by max ratio so every column is exactly feasible; bound as Fraction"""
    yi=np.array([max(0,int(np.floor(v*D))) for v in y],dtype=np.int64)
    lhs=P.astype(np.int64)@yi
    pr=price.astype(np.int64)
    assert (lhs[pr==0]<=0).all(), 'price-0 column with positive lhs'
    pos=pr>0
    k=np.argmax(lhs[pos]/pr[pos]); ratio=Fr(int(lhs[pos][k]), int(pr[pos][k])*D)
    scale=max(ratio,Fr(1))
    yf=[Fr(int(v),D)/scale for v in yi]
    bound=sum(v*int(bb) for v,bb in zip(yf,b))
    return bound, yf
if __name__=='__main__':
    P=np.load('prof.npy'); fos,pos=load_orbits()
    price=P[:,23].astype(float)
    fams=sys.argv[1] if len(sys.argv)>1 else 'FD'
    cols=[]; b=[]
    if 'F' in fams: cols+=list(range(20)); b+=list(8*fos)
    if 'D' in fams: cols+=[20,21,22]; b+=list(pos)
    A=P[:,cols]; b=np.array(b)
    res,y,I=solve(A.astype(float),price,b)
    bound,yf=exact_dual(A,P[:,23],b,y)
    print('LP',res.fun,'exact dual bound',bound,float(bound))
    xs=res.x; 
    for i,v in zip(I,xs):
        if v>1e-9: print('  x=%.4f price %d prof %s'%(v,P[i,23],P[i,:23].tolist()))
    # save dual and check E8 rows against it
    import json
    json.dump({'fams':fams,'cols':cols,'b':[int(x) for x in b],'y':[str(v) for v in yf],'bound':str(bound)},open('dual_%s.json'%fams,'w'))
    W=np.load('e8W.npy'); V=np.load('e8V.npy')
    L=open('geo.txt').read().split('\n'); NA=int(L[1]); NF=int(L[2+NA])
    frs=[list(map(int,L[3+NA+i].split()[:8])) for i in range(NF)]; fo=[int(L[3+NA+i].split()[-1]) for i in range(NF)]; po=list(map(int,L[3+NA+NF].split()))
    for k in range(8):
        D=set(np.nonzero(W[:,k])[0]); S=set(np.nonzero(V[:,k])[0]); prof=[0]*23
        for T,o in zip(frs,fo):
            if D&set(T) and S&set(T): prof[o]+=1
        for t in D&S: prof[20+po[t]]+=1
        lhs=sum(Fr(prof[c])*v for c,v in zip(cols,yf))
        print('E8 row',k,'dual lhs',lhs,float(lhs),'<= price 7:',lhs<=7, 'frame-active all:',sum(prof[:20])==NF,'|D∩S|',sum(prof[20:]))
