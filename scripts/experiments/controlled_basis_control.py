#!/usr/bin/env python3
"""Finite control of PR #10's simultaneous basis and contiguous pivot blocks.

Provenance: IceKylin's PR #10, research/batched-23, pinned head
62691e395a0458ce089a1c7b5d89e74291e95e29. This independently implements a
small control of the argument in its controlled-projector-basis and
projector-batching working sources. It does not materialize the h=28 basis,
prove the general existence theorem, or certify a multiplication exponent.

One integer parameter tuple is tested against all 57 h=3 projectors. Matrix
arithmetic is exact modulo a fixed prime. Nonzero modular determinants of
the integer basis and its rationally conjugated corner matrices certify that
the corresponding rational determinants are nonzero. Pivot profiles are
checked over the finite field; the rational profile follows from the retained
projector/Schur-complement argument, not from inferring rational zeros from
modular zeros.
"""
from collections import Counter
from hashlib import sha256
from math import isqrt
from pathlib import Path
from random import Random
import argparse
import json

PRIME = 1000003
SEED = 101026
PREDECESSOR = dict(
    url='https://github.com/CrocSwap/integer-mult-bounds/pull/10',
    head='62691e395a0458ce089a1c7b5d89e74291e95e29',
    author='IceKylin', branch='research/batched-23')


class SingularMatrix(ValueError):
    pass


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b, prime=PRIME):
    columns = list(zip(*b))
    return [[sum(x*y for x,y in zip(row,column)) % prime for column in columns]
            for row in a]


def inverse(matrix, prime=PRIME):
    n = len(matrix)
    a = [[x % prime for x in row]+tail for row,tail in zip(matrix,identity(n))]
    for j in range(n):
        pivot = next((i for i in range(j,n) if a[i][j]), None)
        if pivot is None:
            raise SingularMatrix('Singular matrix modulo the control prime')
        a[j],a[pivot] = a[pivot],a[j]
        scale = pow(a[j][j],prime-2,prime)
        a[j] = [x*scale % prime for x in a[j]]
        for i in range(n):
            if i != j:
                factor = a[i][j]
                a[i] = [(x-factor*y) % prime for x,y in zip(a[i],a[j])]
    return [row[n:] for row in a]


def lower_pivots(matrix, prime=PRIME):
    """Top row first, rightmost active pivot, lower row/column operations."""
    a = [[x % prime for x in row] for row in matrix]
    n = len(a)
    active = set(range(n))
    pivots = []
    for i in range(n):
        columns = [j for j in active if a[i][j]]
        if not columns:
            continue
        j = max(columns)
        scale = pow(a[i][j],prime-2,prime)
        a[i] = [x*scale % prime for x in a[i]]
        for k in range(i+1,n):
            factor = a[k][j]
            a[k] = [(x-factor*y) % prime for x,y in zip(a[k],a[i])]
        # Add the pivot column only to columns on its left. These and the
        # preceding lower row operations are the permitted triangular maps.
        for k in active:
            if k < j:
                factor = a[i][k]
                for row in range(n):
                    a[row][k] = (a[row][k]-factor*a[row][j]) % prime
        active.remove(j)
        pivots.append((i,j))
    return pivots


def check_projector(matrix, nullity, aligned_corner=False, prime=PRIME):
    """Check a known idempotent's corner and complete lower pivot profile."""
    m,r = len(matrix),nullity
    if not 0 < 2*r < m:
        raise ValueError('The selected projector must have rank between m/2 and m')
    corner = [row[-r:] for row in matrix[:r]]
    inverse(corner,prime)
    if aligned_corner and any(corner[i][j] % prime for i in range(r) for j in range(r) if i != j):
        raise ValueError('The stage-two corner is not diagonal in physical order')
    pivots = lower_pivots(matrix,prime)
    if len(pivots) != m-r:
        raise ValueError('Projector rank does not equal m-nullity')
    if [i for i,j in pivots[:r]] != list(range(r)):
        raise ValueError('Corner pivots do not use the initial rows')
    if {j for i,j in pivots[:r]} != set(range(m-r,m)):
        raise ValueError('Corner pivots do not use the final columns')
    if pivots[r:] != [(i,i) for i in range(r,m-r)]:
        raise ValueError('The middle pivots are not one contiguous diagonal block')
    if aligned_corner and pivots[:r] != [(i,m-r+i) for i in range(r)]:
        raise ValueError('The corner pivots require an unsupported field permutation')
    return dict(nullity=r, rank=m-r, middle_width=m-2*r,
                corner_width=r if aligned_corner else 0,
                singleton_corner_pivots=0 if aligned_corner else r)


def projector_family(h=3):
    """Coordinate representatives of A1,A2,A3, varied over all t and q.

    A1=I-I_F tensor Pi_q-Pi_t tensor Pi_U, with q outside U;
    A2=(I_F-Pi_t) tensor I_V;
    A3=(I_F-Pi_t) tensor (I_V-Pi_q).
    Conjugation supplies non-coordinate examples without altering these forms.
    """
    if h < 3:
        raise ValueError('All three large-rank classes require h >= 3')
    H = h*h
    family = []
    for t in range(h):
        for q in range(H):
            U = {(q+j+1) % H for j in range(h)}
            if q in U:
                raise ValueError('The bank-matching line lies in the paired subspace')
            ones1 = {a*H+i for a in range(h) for i in range(H)
                     if i != q and not (a == t and i in U)}
            ones3 = {a*H+i for a in range(h) for i in range(H)
                     if a != t and i != q}
            family.extend([('A1',2*h,ones1),('A3',H+h-1,ones3)])
        ones2 = {a*H+i for a in range(h) for i in range(H) if a != t}
        family.append(('A2',H,ones2))
    return family


def certificate(h=3, seed=SEED, maximum_trials=100):
    if any(PRIME % d == 0 for d in range(2,isqrt(PRIME)+1)):
        raise ValueError('The finite control modulus is not prime')
    H,m = h*h,h**3
    rng = Random(seed)
    family = projector_family(h)
    for trial in range(maximum_trials):
        try:
            K = [[rng.randrange(-50,51) for _ in range(H)] for _ in range(H)]
            inverse(K)
            G = [[[rng.randrange(-50,51) for _ in range(h)] for _ in range(h)]
                 for _ in range(H)]
            for block in G:
                inverse(block)
            # This is the reduction of the integer matrix T(I_F tensor K).
            # The unreduced integer parameter matrices are retained below.
            S = [[G[i][a][b]*K[i][j] % PRIME for b in range(h) for j in range(H)]
                 for a in range(h) for i in range(H)]
            S_inverse = inverse(S)
            profiles = {}
            for name,nullity,ones in family:
                if len(ones) != m-nullity:
                    raise ValueError('The original diagonal projector has the wrong rank')
                matrix = multiply([[x if j in ones else 0 for j,x in enumerate(row)]
                                   for row in S],S_inverse)
                result = check_projector(matrix,nullity,aligned_corner=name == 'A2')
                if name in profiles and profiles[name] != result:
                    raise ValueError('A geometric class has inconsistent pivot profiles')
                profiles[name] = result
            parameters = dict(K=K,G=G)
            return dict(
                status='FINITE CONTROL; GENERAL H28 BASIS THEOREM REMAINS A PROOF DEPENDENCY',
                predecessor=PREDECESSOR, h=h, H=H, m=m, prime=PRIME,
                seed=seed, accepted_trial=trial, projectors_checked=len(family),
                class_counts=dict(Counter(name for name,_,_ in family)),
                profiles=profiles, one_common_integer_parameter_tuple=True,
                rational_corner_nonsingularity_certified=True,
                pivot_profiles_checked_over=f'F_{PRIME}',
                parameter_sha256=sha256(json.dumps(parameters,sort_keys=True).encode()).hexdigest(),
                parameters=parameters,
                scope='Nonzero modular determinants certify the corresponding rational corner '
                      'conditions for this finite family. The elimination profiles are checked '
                      'over the stated finite field. General rational profile, simultaneous h28 '
                      'basis existence, tensor-edge counts, row recursion and multiplication '
                      'assembly remain separate proof obligations.')
        except SingularMatrix:
            # Reject the whole tuple. Never choose a different basis for an
            # individual projector or accept a vanishing modular determinant.
            continue
    raise ValueError('No successful common-basis tuple within the control search budget')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    result = certificate()
    if args.output:
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS one common basis:',result['projectors_checked'],'projectors;',
          result['class_counts'],'; stage-two corner and all middle blocks aligned')
