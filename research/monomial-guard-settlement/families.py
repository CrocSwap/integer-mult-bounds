"""Construct explicit words for both sharp endpoints of the ternary envelope."""
from hashlib import sha256

from algorithms import scalar_small_field
from literal import identity_pass
from monomial import flat_rows
from settlement import Field, add_row, ternary_extra


def endpoint(r,n,upper):
    f=Field(3)
    a=min(r,n)
    slope=[v for _ in range(r) for v in (1,2)]
    if upper:
        base=[2]*(2*r)
        pure=2*r+3*n+1
    else:
        base=[1]*(2*a)+[0]*(2*(r-a))
        pure=3*n+1-2*a
    base.extend([1]*pure)
    slope.extend([0]*pure)
    u=(1,)*len(base)
    if not r:
        u+=(0,)
        base.append(0)
        slope.append(1)
    rows=(tuple(base),tuple(slope))
    raw_s=[f.mul[x][w] for x,w in zip(u,slope)]
    if sum(x!=0 for x in raw_s)-scalar_small_field(f,raw_s)!=r or ternary_extra(base)!=n:
        raise ValueError("prescribed diagnostics")
    gates=[(2*i,2*i+1,2) for i in range(r)]
    for gate in gates:
        u,rows=add_row(f,u,rows,*gate)
    vals=[f.mul[x][b] for x,b in zip(u,rows[0])]
    positive=[i for i,x in enumerate(vals) if x==1]
    for j in range(ternary_extra(vals)):
        i,k=positive[2*j:2*j+2]
        coeff=f.mul[f.neg[u[i]]][f.inv[u[k]]]
        gates.append((i,k,coeff))
        u,rows=add_row(f,u,rows,i,k,coeff)
    vals=[f.mul[x][b] for x,b in zip(u,rows[0])]
    plus=[i for i,x in enumerate(vals) if x==1]
    minus=[i for i,x in enumerate(vals) if x==2]
    if len(plus)!=len(minus)+1:
        raise ValueError("final endpoint imbalance")
    reverse=[plus[0]]
    for i,j in zip(plus[1:],minus):
        reverse.extend([i,j])
    reverse.extend(i for i,x in enumerate(vals) if not x)
    order=list(reversed(reverse))
    norm=flat_rows(f,rows[0],[rows[1]])
    for v in norm:
        partial=0
        for i in order[:-1]:
            partial=f.add[partial][f.mul[u[i]][v[i]]]
            if partial==1:
                raise ValueError("attaining word fails a proper guard")
    if len(u)<=14:
        permuted=tuple(u[i] for i in order)
        if not identity_pass(f,permuted,[tuple(v[i] for i in order) for v in norm]):
            raise ValueError("attaining word fails a literal minor")
    target=2*r+n if upper else max(r,n)
    if len(gates)!=target:
        raise ValueError("envelope attainment")
    return dict(S=r,L=n,endpoint="upper" if upper else "lower",dimension=len(u),cost=target,
                gate_order_sha256=sha256(repr((gates,order)).encode("ascii")).hexdigest())


def collect():
    return [endpoint(r,n,upper) for r in range(8) for n in range(8) for upper in (False,True)]
