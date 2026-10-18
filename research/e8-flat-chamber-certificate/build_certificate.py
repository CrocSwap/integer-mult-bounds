"""Produce exact finite hypotheses for the chamber proof; no Weyl library."""
from fractions import Fraction as Q
from itertools import combinations, product
from math import gcd, lcm
from pathlib import Path
import argparse
import json

SIMPLE = [[1,-1,-1,-1,-1,-1,-1,1], [2,2,0,0,0,0,0,0], [-2,2,0,0,0,0,0,0]] + [
    [-2 if i == k else 2 if i == k+1 else 0 for i in range(8)] for k in range(1,6)]


def roots():
    out = []
    for a,b in combinations(range(8),2):
        for x,y in product((-2,2), repeat=2):
            v = [0]*8
            v[a],v[b] = x,y
            out.append(v)
    return sorted(out + [list(v) for v in product((-1,1),repeat=8) if v.count(-1)%2 == 0])


def solve(matrix, vector):
    rows = [[Q(x) for x in row]+[Q(y)] for row,y in zip(matrix,vector)]
    for j in range(8):
        k = next(k for k in range(j,8) if rows[k][j])
        rows[j],rows[k] = rows[k],rows[j]
        pivot = rows[j][j]
        rows[j] = [x/pivot for x in rows[j]]
        for k in range(8):
            if k != j:
                factor = rows[k][j]
                rows[k] = [x-factor*y for x,y in zip(rows[k],rows[j])]
    return [row[-1] for row in rows]


def build():
    rr = roots()
    lookup = {tuple(v):i for i,v in enumerate(rr)}
    cc = [solve(list(zip(*SIMPLE)), r) for r in rr]
    if any(x.denominator != 1 for c in cc for x in c):
        raise ValueError('nonintegral simple coordinates')
    perms = [[lookup[tuple(x-Q(sum(a*b for a,b in zip(alpha,r)),4)*a for x,a in zip(r,alpha))]
              for r in rr] for alpha in SIMPLE]
    weights = []
    for j in range(8):
        w = solve(SIMPLE,[int(i == j) for i in range(8)])
        denominator = lcm(*(x.denominator for x in w))
        ints = [int(x*denominator) for x in w]
        common = gcd(*ints)
        weights.append([x//common for x in ints])
    flats = [[i for i,r in enumerate(rr) if sum(a*b for a,b in zip(w,r)) == 0] for w in weights]
    return dict(schema_version=1, roots=rr, simple=SIMPLE, coefficients=[[int(x) for x in c] for c in cc],
                reflections=perms, fundamental_rays=weights, flat_roots=flats)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out',required=True,type=Path)
    args = parser.parse_args()
    with args.out.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(build(),stream,separators=(',',':'))
        stream.write('\n')
