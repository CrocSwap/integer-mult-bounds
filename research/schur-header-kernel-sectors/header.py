"""Recover the sharp Schur kernel sectors from original header factors.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The retained central classifier and matrix helpers keep their source notices.
"""
from central import classify
from block_source import eye, add, mul, rank, kernel, require


def profile(d, sizes):
    require(type(d) is int and d>0 and len(sizes)==4 and all(type(r) is int and r>=0 for r in sizes),
            'valid pivot and four sector dimensions required')
    require(all(r>=d for r in sizes[1:]), 'sharp sectors need full injection and observation')
    return (sizes[0], sizes[1]-d, sizes[2]-d, sizes[3]-d)


def central_from_header(h, sizes, q):
    """Requires an admitted sharp header with this H and original profile."""
    sectors=profile(len(h),sizes)
    return classify(h,sum(sizes)-len(h),sectors[1]+sectors[2],q)


def kernel_bases(factors, q):
    """Return original-space columns, before choice of a residual basis."""
    require(q in (2,3,5,7) and len(factors)==4, 'implemented prime field and four factors required')
    d=len(factors[0][0]);sizes=tuple(len(y) for x,y in factors)
    profile(d,sizes)
    for x,y in factors:
        require(len(x)==d and all(len(row)==len(y) for row in x) and all(len(row)==d for row in y),
                'factor shape mismatch')
    products=[mul(x,y,q) if y else tuple((0,)*d for _ in range(d)) for x,y in factors]
    h=products[3];w=add(eye(d),h,q,-1)
    require(products==[tuple(tuple(-a%q for a in row) for row in w),w,w,h], 'sector product mismatch')
    require(all(rank(x,q)==rank(y,q)==d for x,y in factors[1:]), 'sharp factor ranks required')
    inclusion=sum((y for x,y in factors),())
    projection=tuple(sum((x[i] for x,y in factors),()) for i in range(d))
    require(mul(projection,inclusion,q)==eye(d), 'split mismatch')
    n=sum(sizes);result=[]
    x00=factors[0][0]
    result.append(tuple(tuple((int(i==j)-sum(inclusion[i][k]*x00[k][j] for k in range(d)))%q
                              for i in range(n)) for j in range(sizes[0])))
    start=sizes[0]
    for size,(x,y) in zip(sizes[1:],factors[1:]):
        vectors=tuple(zip(*kernel(x,q)))
        result.append(tuple(tuple(v[i-start] if start<=i<start+size else 0 for i in range(n)) for v in vectors))
        start+=size
    return tuple(result)
