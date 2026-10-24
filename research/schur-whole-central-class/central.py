"""Recover the full central class under the sharp Schur-image contract.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Matrix helpers are retained from ssafwann; see NOTICE.md.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent/'vendor'))
from block_source import add, mul, eye, zero, block, kernel, rank, rref, inverse, require


def power(a, exponent, q):
    result = eye(len(a))
    for _ in range(exponent): result = mul(result, a, q)
    return result


def column_basis(a, q):
    pivots = rref(a, q)[1]
    return tuple(tuple(row[j] for j in pivots) for row in a)


def restrict(a, basis, q):
    if not basis or not basis[0]: return ()
    indices = rref(tuple(zip(*basis)), q)[1]
    square = tuple(basis[i] for i in indices)
    image = mul(a, basis, q)
    result = mul(inverse(square, q), tuple(image[i] for i in indices), q)
    require(mul(basis, result, q) == image, 'subspace is not invariant')
    return result


def nilpotent_blocks(operator, basis, q):
    if not basis or not basis[0]: return []
    ranks = [len(basis[0])]
    current = basis
    for _ in range(len(operator)):
        current = mul(operator, current, q)
        ranks.append(rank(current, q))
        if not ranks[-1]: break
    require(ranks[-1] == 0, 'primary commutator is not nilpotent')
    ranks.append(0)
    blocks = []
    for size in range(1, len(ranks)-1):
        count = ranks[size-1]-2*ranks[size]+ranks[size+1]
        require(count >= 0, 'invalid rank sequence')
        blocks += [size]*count
    return sorted(blocks, reverse=True)


def classify(h, residual_dimension, opposite_count, q):
    """The source pair must satisfy the sharp contract in PROOF.md."""
    require(q in (2,3,5,7), 'implemented fields are F2, F3, F5 and F7')
    d = len(h)
    require(d > 0 and all(len(row) == d for row in h), 'square nonempty H required')
    require(type(residual_dimension) is int and type(opposite_count) is int and
            residual_dimension >= 2*d and 0 <= opposite_count <= residual_dimension-2*d,
            'invalid residual or sector count')
    ident = eye(d); w = add(ident,h,q,-1); j = add(h,mul(h,h,q),q,-1)
    theta = add(add(h,h,q),mul(h,h,q),q,-1)
    central = block(theta,zero(d,d),zero(d,d),theta)
    commutator = block(j,add(w,w,q),add(zero(d,d),j,q,-1),add(zero(d,d),j,q,-1))
    require(mul(commutator,commutator,q) == mul(central,add(central,eye(2*d),q,-1),q),
            'small commutator identity')
    endpoints = {}
    bblocks = {}
    for lam, count in ((0,residual_dimension-2*d-opposite_count),(1,opposite_count)):
        basis = kernel(power(add(central,eye(2*d),q,-lam),2*d,q),q)
        blocks = nilpotent_blocks(commutator,basis,q)
        require(count >= len(blocks), 'endpoint count cannot support the image')
        bblocks[str(lam)] = blocks
        parts = [part for size in blocks for part in ((size+2)//2,(size+1)//2)]
        parts += [1]*(count-len(blocks))
        endpoints[str(lam)] = sorted(parts,reverse=True)
    g = mul(central,add(central,eye(2*d),q,-1),q)
    basis = column_basis(power(g,2*d,q),q)
    nonendpoint = restrict(central,basis,q)
    require(sum(map(sum,endpoints.values()))+len(nonendpoint) == residual_dimension, 'dimension mismatch')
    return {'endpoint_blocks':endpoints,'image_commutator_blocks':bblocks,
            'nonendpoint_representative':[list(row) for row in nonendpoint],
            'opposite_count':opposite_count,'dimension':residual_dimension}


def representative(result, q):
    chunks = []
    for lam in (0,1):
        for size in result['endpoint_blocks'][str(lam)]:
            chunks.append(tuple(tuple((lam*int(i==j)+int(j==i+1))%q for j in range(size)) for i in range(size)))
    if result['nonendpoint_representative']:
        chunks.append(tuple(map(tuple,result['nonendpoint_representative'])))
    n = sum(map(len,chunks)); out = [[0]*n for _ in range(n)]; offset = 0
    for chunk in chunks:
        for i,row in enumerate(chunk):out[offset+i][offset:offset+len(chunk)] = row
        offset += len(chunk)
    return tuple(map(tuple,out))
