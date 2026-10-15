#!/usr/bin/env python3
"""Exact Gaussian-integer checks of every nominated rank-zero handoff.

Each complete512-column operator is evaluated with a shared power-of-two
denominator. No floating approximation or binary-frame equality is substituted
for the actual Gaussian operator product.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np


def linear(cols,x):
    out=0
    for i,c in enumerate(cols):
        if x>>i&1:out^=c
    return out


def rank(xs):
    b={}
    for x in xs:
        while x:
            i=x.bit_length()
            if i not in b:b[i]=x;break
            x^=b[i]
    return len(b)


def extend(xs,h):
    out=list(xs)
    for i in range(h):
        if rank(out+[1<<i])>len(out):out.append(1<<i)
    assert len(out)==h
    return out


def inverse(cols,h):
    perm=[linear(cols,x) for x in range(1<<h)];back=[0]*len(perm)
    assert len(set(perm))==len(perm)
    for i,j in enumerate(perm):back[j]=i
    return [back[1<<i] for i in range(h)]


def change(source,target,h):
    a=extend(source,h);b=extend(target,h);ai=inverse(a,h)
    return [linear(b,x) for x in ai]


def monomial(cols,h):
    gi=inverse(cols,h)
    git=[sum(((gi[j]>>i)&1)<<j for j in range(h)) for i in range(h)]
    M=[(1<<j)^linear(git,gi[j]) for j in range(h)]
    assert all((M[j]>>i&1)==(M[i]>>j&1) for i in range(h) for j in range(h))
    perm=np.array([linear(cols,x) for x in range(1<<h)],dtype=np.int64)
    phase=np.array([sum(((M[i]>>i)&1)*(x>>i&1) for i in range(h))+
       2*sum(((M[j]>>i)&1)*(x>>i&1)*(x>>j&1) for i in range(h) for j in range(i+1,h))
       for x in perm],dtype=np.int64)%4
    return perm,phase


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
        a,b,c,d=re[p].copy(),im[p].copy(),re[q].copy(),im[q].copy()
        if sign==1:
            re[p]=a-b+c+d;im[p]=a+b+d-c
            re[q]=a+b+c-d;im[q]=b-a+c+d
        else:
            re[p]=a+b+c-d;im[p]=b-a+c+d
            re[q]=a-b+c+d;im[q]=a+b+d-c
        exp+=1
    return re,im,exp


def frame(z,basis,h,sign=1):
    G=change([1<<i for i in range(len(basis))],basis,h);K=monomial(G,h)
    return apply_mono(coord(apply_mono(z,K,-1),range(len(basis)),sign),K,1)


def check(z):
    re,im,exp=z;support=(re!=0)|(im!=0)
    assert np.all(support.sum(axis=0)==1) and np.all(support.sum(axis=1)==1)
    rr=re[support];ii=im[support];unit=1<<exp
    assert np.all(((np.abs(rr)==unit)&(ii==0))|((rr==0)&(np.abs(ii)==unit)))
    return hashlib.sha256(re.astype('<i8',copy=False).tobytes()+im.astype('<i8',copy=False).tobytes()+str(exp).encode()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--replay',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();data=json.loads(a.replay.read_text())
    h=9;size=1<<h;records=[];negative_rejected=False
    for handoff in data['symbolic_warps']:
        U=handoff['from_basis'];E=handoff['to_basis'];assert len(U)==len(E)
        G=change(U,E,h);K=monomial(G,h)
        z=(np.eye(size,dtype=np.int64),np.zeros((size,size),dtype=np.int64),0)
        z=frame(z,U,h,-1);z=apply_mono(z,K);z=frame(z,E,h,1)
        handhash=check(z)
        if not negative_rejected:
            zbad=(np.eye(size,dtype=np.int64),np.zeros((size,size),dtype=np.int64),0)
            zbad=frame(zbad,U,h,-1);zbad=frame(zbad,E,h,1)
            try:check(zbad)
            except AssertionError:negative_rejected=True
        z=(np.eye(size,dtype=np.int64),np.zeros((size,size),dtype=np.int64),0)
        z=coord(z,range(h),-1);z=apply_mono(z,K,-1);z=coord(z,range(h),1)
        exit_hash=check(z)
        records.append({'operator':handoff['operator'],'G_columns':G,
          'handoff_exact_monomial_sha256':handhash,'full_exit_exact_monomial_sha256':exit_hash})
    assert negative_rejected
    out={'status':'PASS_EXACT_GAUSSIAN_BORROW_HANDOFFS','operators':len(records),
      'omitted_logical_basis_map_rejected':negative_rejected,
      'columns_per_operator':size,'physical_rank_zero_products_checked':2*len(records),
      'records':records,'scope':'exact local adapter products only; no hosting or new kappa'}
    a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:x for k,x in out.items() if k!='records'}))


if __name__=='__main__':main()
