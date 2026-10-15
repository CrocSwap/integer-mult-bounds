"""Exact Gaussian column products of monomial warps (numpy only).

Port of PR2226's operators.py (Cinna Davis, @1337isnot1337, with OpenAI Codex assistance; Apache-2.0): change / monomial /
apply_mono / coord / frame / check.  Shares no code with the clifford_exact phase compiler or the emitter.  Matrices are
(re, im, exp) with entries (re + i im) / 2^exp-scaled: a product of frames and warps is *exact* when every row and column has
one support entry of magnitude exactly 2^exp.
"""
if not __debug__:
    raise RuntimeError('assertions must remain enabled')   # every check of this stage is an assert
import hashlib
import numpy as np
def lin(cols,x):
    out=0
    for i,col in enumerate(cols):
        if x>>i&1:out^=col
    return out
def f2rank(xs):
    b={}
    for x in xs:
        while x:
            i=x.bit_length()
            if i not in b:b[i]=x;break
            x^=b[i]
    return len(b)
def extend(xs,hh):
    out=list(xs)
    for i in range(hh):
        if f2rank(out+[1<<i])>len(out):out.append(1<<i)
    assert len(out)==hh
    return out
def f2inverse(cols,hh):
    perm=[lin(cols,x) for x in range(1<<hh)];back=[0]*len(perm)
    assert len(set(perm))==len(perm),'non-invertible G'
    for i,j in enumerate(perm):back[j]=i
    return [back[1<<i] for i in range(hh)]
def change(source,target,hh):
    a=extend(source,hh);b=extend(target,hh);ai=f2inverse(a,hh)
    return [lin(b,x) for x in ai]
def monomial(cols,hh,qmut=None):
    gi=f2inverse(cols,hh)
    git=[sum(((gi[j]>>i)&1)<<j for j in range(hh)) for i in range(hh)]
    M=[(1<<j)^lin(git,gi[j]) for j in range(hh)]
    if qmut:M[qmut[0]]^=qmut[1]; M[qmut[1].bit_length()-1]^=1<<qmut[0]   # BW control hook: a wrong (still symmetric) quadratic form
    assert all((M[j]>>i&1)==(M[i]>>j&1) for i in range(hh) for j in range(hh))
    permv=np.array([lin(cols,x) for x in range(1<<hh)],dtype=np.int64)
    phase=np.array([sum(((M[i]>>i)&1)*(x>>i&1) for i in range(hh))+
       2*sum(((M[j]>>i)&1)*(x>>i&1)*(x>>j&1) for i in range(hh) for j in range(i+1,hh))
       for x in permv],dtype=np.int64)%4
    return permv,phase
def apply_mono(z,recipe,sign=1):
    re,im,exp=z;perm,phase=recipe;rr=np.empty_like(re);ii=np.empty_like(im)
    if sign==1:
        for p in range(4):
            mask=phase==p;r=re[mask];i=im[mask]
            if p==0:a,b=r,i
            elif p==1:a,b=-i,r
            elif p==2:a,b=-r,-i
            else:a,b=i,-r
            rr[perm[mask]]=a;ii[perm[mask]]=b
    else:
        r=re[perm];i=im[perm]
        for p in range(4):
            mask=phase==p
            if p==0:a,b=r[mask],i[mask]
            elif p==1:a,b=i[mask],-r[mask]
            elif p==2:a,b=-r[mask],-i[mask]
            else:a,b=-i[mask],r[mask]
            rr[mask]=a;ii[mask]=b
    return rr,ii,exp
def coord(z,axes,sign=1):
    re,im,exp=z
    for j in axes:
        p=np.array([x for x in range(len(re)) if not(x>>j&1)]);q=p^(1<<j)
        a,b,cc,d=re[p].copy(),im[p].copy(),re[q].copy(),im[q].copy()
        if sign==1:
            re[p]=a-b+cc+d;im[p]=a+b+d-cc
            re[q]=a+b+cc-d;im[q]=b-a+cc+d
        else:
            re[p]=a+b+cc-d;im[p]=b-a+cc+d
            re[q]=a-b+cc+d;im[q]=a+b+d-cc
        exp+=1
    return re,im,exp
def span(b):
    s={0}
    for x in b:s|={t^x for t in s}
    return s
def frame(z,bas,hh,sign=1):
    G=change([1<<i for i in range(len(bas))],bas,hh);K=monomial(G,hh)
    return apply_mono(coord(apply_mono(z,K,-1),range(len(bas)),sign),K,1)
def check_mono(z):
    re,im,exp=z;support=(re!=0)|(im!=0)
    assert np.all(support.sum(axis=0)==1) and np.all(support.sum(axis=1)==1),'not a monomial matrix'
    rr=re[support];ii=im[support];unit=1<<exp
    assert np.all(((np.abs(rr)==unit)&(ii==0))|((rr==0)&(np.abs(ii)==unit))),'entries are not unit Gaussian phases'
    return hashlib.sha256(re.astype('<i8',copy=False).tobytes()+im.astype('<i8',copy=False).tobytes()+str(exp).encode()).hexdigest()
def eye(hh):return (np.eye(1<<hh,dtype=np.int64),np.zeros((1<<hh,1<<hh),dtype=np.int64),0)
def warp_product(G,U,E,op,hh,qmut=None):
    """Z = T_E K_G^{+-1} T_U^{-1} as an exact Gaussian matrix (apply T_U^{-1} first), for a warp of sign(op) from frame U to frame E."""
    K=monomial(G,hh,qmut)
    z=frame(eye(hh),U,hh,-1);z=apply_mono(z,K,1 if op>0 else -1);return frame(z,E,hh,1)
def recipe_matrix(rec,hh):
    """Dense exact matrix (re, im, exp=0) of a serialized clifford_exact monomial (matrix_rows, quadratic_rows, linear_Z4, offset, phase):
    |x> -> i^(qvalue(x)+phase) |G x ^ offset>,  qvalue = sum alpha_i x_i + 2 sum_{i in x} parity((Q_i >> (i+1)) & (x >> (i+1)))."""
    N=1<<hh;re=np.zeros((N,N),dtype=np.int64);im=np.zeros((N,N),dtype=np.int64)
    rows,Q,alpha,b,ph=rec['matrix_rows'],rec['quadratic_rows'],rec['linear_Z4'],rec['offset'],rec['phase']
    unit=[(1,0),(0,1),(-1,0),(0,-1)]
    for x in range(N):
        y=sum(((rows[i]&x).bit_count()&1)<<i for i in range(hh))^b
        q=(sum(alpha[i] for i in range(hh) if x>>i&1)+2*sum(((Q[i]>>(i+1))&(x>>(i+1))).bit_count()&1 for i in range(hh) if x>>i&1)+ph)%4
        re[y,x],im[y,x]=unit[q]
    return re,im,0
def equal_scaled(z,m):
    """z (scaled by 2^exp) equals m (exp 0) entrywise exactly"""
    re,im,exp=z;return bool(np.array_equal(re,m[0]<<exp) and np.array_equal(im,m[1]<<exp))
