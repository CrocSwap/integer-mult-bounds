"""Exact box-truncated convolution by grade-filtered integer packing.
Related rank-filter idea: Bjorklund et al. (2007), Stoian (2024).
This mixed-radix carry-count recurrence and explicit packing are checked here.
No originality or all-size multiplication bound is claimed.
"""
from itertools import product
from math import prod


def layout(shape, mutation=None):
    assert shape and all(n>=1 for n in shape)
    D=len(shape);N=prod(shape);T=D
    if mutation=='small_modulus':T=max(1,D-1)
    weights=[1]
    for n in shape[:-1]:weights.append((n*weights[-1]-1)%T)
    if mutation=='wrong_recurrence':weights=[1]*D
    if mutation=='no_grade':weights=[0]*D
    strides=[prod(shape[:i])for i in range(D)]
    coords=list(product(*(range(n)for n in shape)))
    indices=[sum(a*s for a,s in zip(v,strides))for v in coords]
    grades=[sum(a*w for a,w in zip(v,weights))%T for v in coords]
    X=N if mutation=='no_index_padding'else 2*N-1
    slots=[i+X*r for i,r in zip(indices,grades)]
    outputs=[[i+X*r]+([i+X*(r+T)]if r+T<=2*T-2 else[])for i,r in zip(indices,grades)]
    assert len(set(slots))==N
    return dict(shape=list(shape),D=D,N=N,T=T,X=X,weights=weights,strides=strides,coordinates=coords,indices=indices,grades=grades,slots=slots,outputs=outputs)


def apply(f,g,shape,stats=None,mutation=None):
    L=layout(shape,mutation);N=L['N'];assert len(f)==len(g)==N
    assert all(isinstance(x,int)for x in f+g)
    bound=N*max(map(abs,f),default=0)*max(map(abs,g),default=0)
    width=max(1,bound.bit_length()+1)
    def pack(v,sign):return sum(max(sign*a,0)<<(width*j)for a,j in zip(v,L['slots']))
    fp,fm,gp,gm=pack(f,1),pack(f,-1),pack(g,1),pack(g,-1)
    products=[(fp*gp,1),(fm*gm,1),(fp*gm,-1),(fm*gp,-1)]
    if mutation=='missing_signed_cross':products=products[:2]
    mask=(1<<width)-1
    out=[sum(sign*((p>>(width*j))&mask)for j in js for p,sign in products)for js in L['outputs']]
    assert max(fp.bit_length(),fm.bit_length(),gp.bit_length(),gm.bit_length())<=width*(max(L['slots'])+1)
    assert 2*max(L['slots'])+1<4*L['D']*N
    if stats is not None:
        stats['integer_products']=stats.get('integer_products',0)+len(products)
        stats['convolutions']=stats.get('convolutions',0)+1
        stats['max_operand_bits']=max(stats.get('max_operand_bits',0),fp.bit_length(),fm.bit_length(),gp.bit_length(),gm.bit_length())
        stats['layout_product_slots']=2*max(L['slots'])+1
        stats['slot_bits']=max(stats.get('slot_bits',0),width)
    return out


def oracle(f,g,shape):
    coords=list(product(*(range(n)for n in shape)));by={v:i for i,v in enumerate(coords)};out=[0]*len(coords)
    for i,a in enumerate(coords):
        for j,b in enumerate(coords):
            c=tuple(x+y for x,y in zip(a,b))
            if all(x<n for x,n in zip(c,shape)):out[by[c]]+=f[i]*g[j]
    return out
