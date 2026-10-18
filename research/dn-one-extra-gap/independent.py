# SPDX-License-Identifier: Apache-2.0
"""Literal Boolean elimination, no imports from the primary checker."""
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rank(matrix):
    a = [list(row) for row in matrix]
    if not a:
        return 0
    pivot = 0
    for j in range(len(a[0])):
        found = next((i for i in range(pivot,len(a)) if a[i][j]),None)
        if found is None:
            continue
        a[pivot],a[found] = a[found],a[pivot]
        for i in range(pivot+1,len(a)):
            if a[i][j]:
                a[i] = [x != y for x,y in zip(a[i],a[pivot])]
        pivot += 1
    return pivot


def configuration(n):
    out = []
    for i,j in combinations(range(n),2):
        p = [0]*n;p[i] = p[j] = 1;out.append(p)
        q = [0]*n;q[i] = 1;q[j] = -1;out.append(q)
    return out


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def costs(n,a,lam):
    x = configuration(n)
    pairs = [[i == j or dot(r,s) == 0 for j,s in enumerate(x)] for i,r in enumerate(x)]
    p = [[r[i] for r in x] for i in range(n)]
    v = [dot(r,a) for r in x]
    q = [[p[i][j]-lam*a[i]*v[j] for j in range(len(x))] for i in range(n)]
    p.append(v);q.append([lam*z for z in v])
    for r in range(len(x)):
        for s in range(len(x)):
            require(sum(left[r]*right[s] for left,right in zip(p,q)) == dot(x[r],x[s]), 'full Gram identity')
    return [rank([[pairs[r][s] for s,z in enumerate(right) if z] for r,z in enumerate(left) if z])
            for left,right in zip(p,q)]


def main():
    receipt=json.loads((Path(__file__).resolve().parent/'RESULT.json').read_text())
    count=0
    for row in receipt['fixtures']:
        if row['n'] <= 7:
            a=list(map(Fraction,row['a']));lam=Fraction(row['lambda'])
            require(costs(row['n'],a,lam) == row['costs'],'independent complete block prices')
            count += 1
    # Validate all entries of the universal star block for both parities.
    for k in range(1,18):
        off=[[i != j for j in range(k)] for i in range(k)]
        require(rank(off) == k-(k%2),'J+I parity rank')
        block=[[i == j if (i<k)==(j<k) else (i%k != j%k) for j in range(2*k)] for i in range(2*k)]
        require(rank(block) == k+(k%2),'two-support principal block')
    print('PASS_DN_ONE_EXTRA_INDEPENDENT',count,'full Gram/bill fixtures; 34 parity blocks')


if __name__ == '__main__':
    main()
