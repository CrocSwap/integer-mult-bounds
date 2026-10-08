"""Preserve the actual 48-by-46 hybrid DAG's sharing at a common Pi grid.

Dumas-Pernet-Sedoglavic outer data and Rosowski leaf are inherited methods.
This interpreter applies the author's chronological refinement/late quotient
and Gaussian parity interface; its arithmetic counts exclude tape costs.
"""
from hashlib import sha256
import json
from pathlib import Path
from pi_exact import Gaussian
from gaussian_matrix import gaussian_product3

OUTER_SHA256='e04ebfffc4c2f43cb688c856f1f30e5ef1b7c215f76854ab1d75df03f4bff387'

def load_outer(path):
    raw=Path(path).read_bytes()
    if sha256(raw).hexdigest()!=OUTER_SHA256:
        raise ValueError('Pinned outer coefficient hash mismatch')
    outer=json.loads(raw)['minimal_integer_certificate']
    if outer['scale_product']!=8: raise ValueError('Wrong numerator scale')
    return outer

def multiply16_hierarchical(A,B,outer):
    if len(A)!=256 or len(B)!=256 or any(type(z) is not Gaussian for z in A+B):
        raise ValueError('Two flat canonical Gaussian matrices required')
    tag=max(z.exponent for z in A+B)
    aa=[z.aligned(tag) for z in A];bb=[z.aligned(tag) for z in B]
    component_additions=0;fixed_scales=0;products=0
    def add(x,y):
        nonlocal component_additions
        component_additions+=2
        return x[0]+y[0],x[1]+y[1]
    def sub(x,y):
        nonlocal component_additions
        component_additions+=2
        return x[0]-y[0],x[1]-y[1]
    def scale(c,x):
        nonlocal fixed_scales
        fixed_scales+=2*(abs(c)!=1)
        return c*x[0],c*x[1]
    def total(xs):
        xs=list(xs)
        if not xs: return (0,0)
        result=xs[0]
        for x in xs[1:]: result=add(result,x)
        return result
    def mul(x,y):
        nonlocal products,component_additions
        products+=1;component_additions+=5
        return gaussian_product3(x,y)
    def block_form(coeffs,source):
        return [[total(scale(c,source[16*(4*(index//4)+i)+4*(index%4)+j])
                       for index,c in enumerate(coeffs) if c)
                 for j in range(4)] for i in range(4)]
    contributions=[[] for _ in range(256)]
    for t in range(48):
        U=block_form(outer['alpha_integer'][t],aa)
        V=block_form(outer['beta_integer'][t],bb)
        P=[[mul(U[i][2*h],add(V[2*h][0],U[i][2*h+1])) for h in range(2)] for i in range(4)]
        R=[[mul(U[i][2*h+1],sub(V[2*h+1][0],U[i][2*h])) for h in range(2)] for i in range(4)]
        Q=[[None]+[mul(V[2*h+1][j],add(V[2*h][0],V[2*h][j])) for j in range(1,4)] for h in range(2)]
        M=[[[None]+[mul(add(U[i][2*h],V[2*h+1][j]),
                        add(add(U[i][2*h+1],V[2*h][0]),V[2*h][j]))
                       for j in range(1,4)] for h in range(2)] for i in range(4)]
        Z=[[total(add(P[i][h],R[i][h]) for h in range(2))]+
           [total(sub(sub(M[i][h][j],P[i][h]),Q[h][j]) for h in range(2)) for j in range(1,4)]
           for i in range(4)]
        for block,c in enumerate(outer['gamma_numerator'][t]):
            if c:
                for i in range(4):
                    for j in range(4):
                        contributions[16*(4*(block//4)+i)+4*(block%4)+j].append(scale(c,Z[i][j]))
    result=[]
    for xs in contributions:
        re,im=total(xs)
        if re%8 or im%8: raise ValueError('Exact integral late quotient failed')
        result.append(Gaussian(re//8,im//8,2*tag))
    return result,dict(common_input_pi_tag=tag,raw_product_pi_tag=2*tag,
        extra_bits_beyond_common_product_grid=0,mixed_gaussian_products=products,
        real_variable_product_slots=3*products,component_additions=component_additions,
        fixed_coefficient_scales=fixed_scales,exact_integer_quotients=512,
        scope='Complete displayed arithmetic schedule; input alignment, canonical normalization and physical tape costs separate')
