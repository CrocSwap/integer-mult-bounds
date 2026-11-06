#!/usr/bin/env python3
"""Exact shortest/longer-word scope fixtures for the two-module obstruction.

Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The shortest-word normal form is inherited from the #6398/#6717 lineage.
"""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from saturation import add, central_product, eye, mul, need, rank


def inverse(A):
    n = len(A)
    rows = [[Q(x) for x in row] + [Q(x) for x in right]
            for row,right in zip(A,eye(n))]
    for j in range(n):
        p = next((p for p in range(j,n) if rows[p][j]), None)
        need(p is not None, 'Nonsingular exact matrix')
        rows[j],rows[p] = rows[p],rows[j]
        scale = rows[j][j]
        rows[j] = [x/scale for x in rows[j]]
        for p in range(n):
            if p != j:
                c = rows[p][j]
                rows[p] = [x-c*y for x,y in zip(rows[p],rows[j])]
    return [row[n:] for row in rows]


def word(factors):
    n = len(factors[0]); I = eye(n); Z = [[0]*n for _ in range(n)]
    result = I,Z
    for N in factors:
        result = central_product((add(I,N,-1),N),result)
    return result


def main():
    # Canonical five-query shortest word, rebuilt from its skew-sign Gram.
    B = [[int(i>j)-int(i<j) for j in range(5)] for i in range(5)]
    U = B[:4]
    last = mul([B[4][:4]],inverse([row[:4] for row in U]))[0]
    need(all(x.denominator == 1 for x in last), 'Integral canonical factor fixture')
    V = eye(4)+[[int(x) for x in last]]
    need(mul(V,U) == B, 'Exact five-factor Gram reconstruction')
    Ns = [[[U[i][k]*V[k][j] for j in range(4)] for i in range(4)] for k in range(5)]
    Z = [[0]*4 for _ in range(4)]; target = Z,eye(4)
    need(word(Ns) == target, 'Five-factor formal S I4 endpoint')
    need(all(mul(N,N) == Z for N in Ns), 'All five query factors square-zero')
    need(all(mul(A,C) != Z for i,A in enumerate(Ns) for j,C in enumerate(Ns) if i != j),
         'Every shortest-word cross-product is nonzero')
    T = inverse([[int(i==j)+2*B[i][j]*int(i>j) for j in range(5)] for i in range(5)])
    TB = mul(T,B)
    need(mul(TB,TB) == TB and rank(TB) == 4, 'Rank-four Gram projector')
    a = mul(T,[[1] for _ in range(5)])
    need(TB == add(eye(5),mul(a,[[1]*5]),-1), 'Explicit rank-one projector complement')
    for j in range(5):
        need(word(Ns[:j]+Ns[j+1:]) != target, 'Shortened five-query word rejected')
    # Removing shortestness really permits disjoint nonzero factors.
    # These are the two actual three-query binary auxiliary quotient words.
    tiny = [[[0,0],[1,0]],[[-1,-1],[1,1]],[[0,-1],[0,0]]]
    banks = []
    for offset in (0,2):
        bank = []
        for A in tiny:
            N = [[0]*4 for _ in range(4)]
            for i in range(2):
                for j in range(2):
                    N[i+offset][j+offset] = A[i][j]
            bank.append(N)
        banks.append(bank)
    need(mul(banks[0][0],banks[1][0]) == Z and mul(banks[1][0],banks[0][0]) == Z,
         'Longer-word disjoint-support scope control')
    interleavings, mutants = 0,0
    for positions in combinations(range(6),3):
        chosen = set(positions); counters = [0,0]; factors = []
        for j in range(6):
            bank = 0 if j in chosen else 1
            factors.append(banks[bank][counters[bank]]); counters[bank] += 1
        need(word(factors) == target, 'Every order-preserving six-query interleaving succeeds')
        interleavings += 1
        for j in range(6):
            need(word(factors[:j]+factors[j+1:]) != target, 'Omitted baseline query rejected')
            mutants += 1
    fields = []
    for p in (0,2,3,5):
        need(rank(B,p) == 4 and all(rank(N,p) == 1 for N in Ns), 'Field-specific rank fixtures')
        fields.append(p)
    receipt = {'schema':'two-module-interleaving-scope/1',
               'shortest_factors':5,'shortest_dimension':4,'gram':B,
               'fields':fields,'nonzero_shortest_cross_products':20,
               'valid_longer_interleavings':interleavings,
               'rejected_query_omissions':mutants+5,
               'scope_control':'Six valid factors can have disjoint zero cross-products; shortestness is essential.'}
    data = json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()
    print(json.dumps(receipt,sort_keys=True,indent=2))
    print('CERTIFICATE_SHA256',sha256(data).hexdigest())
    print('PASS_TWO_MODULE_INTERLEAVING_SCOPE_FIXTURES')


if __name__ == '__main__':
    main()
