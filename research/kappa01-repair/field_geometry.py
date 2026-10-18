#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact finite controls for a one-third-density port geometry; no supplier.

The maximal-arc control is based on Mubayi--Williford, Theorem 6.
The field/rank/orthogonality checks below are independently computed.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCALE = 10**40


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def power89(x):
    a, b = x.numerator**8 * SCALE**9, x.denominator**8
    lo, hi = 0, 1
    while hi**9 * b <= a:
        hi *= 2
    while hi-lo > 1:
        mid = (lo+hi)//2
        if mid**9*b <= a:
            lo = mid
        else:
            hi = mid
    require(lo**9*b <= a < hi**9*b, 'outward ninth root')
    return F(lo,SCALE), F(hi,SCALE)


def rank2(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length()-1
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
    return len(pivots)


def field(k, modulus):
    q = 1 << k
    def mul(a,b):
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a & q:
                a ^= modulus
        return r
    tab = [[mul(a,b) for b in range(q)] for a in range(q)]
    def exp(a,n):
        r = 1
        while n:
            if n & 1:
                r = tab[r][a]
            a = tab[a][a]
            n >>= 1
        return r
    inv = [0]+[exp(a,q-2) for a in range(1,q)]
    require(all(tab[a][inv[a]] == 1 for a in range(1,q)), 'field inverses')
    trace = []
    for a in range(q):
        x,t = a,0
        for _ in range(k):
            t ^= x
            x = tab[x][x]
        require(t in (0,1) and x == a, 'trace field')
        trace.append(t)
    for lam in range(q):
        gram = [sum(trace[tab[tab[1<<i][lam]][1<<j]] << j
                    for j in range(k)) for i in range(k)]
        require(rank2(gram) == (k if lam else 0), 'trace pairing rank')
    r = 1 << (k//2)
    subfield = {a for a in range(q) if exp(a,r) == a}
    require(len(subfield) == r and all(trace[a] == 0 for a in subfield), 'subfield')
    s = next(a for a in range(q) if trace[a])
    require(all(tab[x][x] ^ x ^ s for x in range(q)), 'irreducible quadratic')
    # In coordinates (a,1,b), pairing is 1+a*d+b*c.
    # Q(a,b)=b^2+a*b+s*a^2 in F_sqrt(q) gives a coclique.
    points = [(a,b) for a in range(q) for b in range(q)
              if tab[b][b] ^ tab[a][b] ^ tab[s][tab[a][a]] in subfield]
    owned = set(points)
    expected = q*r-q+r
    require(len(points) == expected, 'maximal-arc cardinality')
    probes = 0
    for a,b in points:
        if a:
            for c in range(q):
                d = tab[1 ^ tab[b][c]][inv[a]]
                require((c,d) not in owned, 'coclique forbidden edge')
                probes += 1
        elif b:
            c = inv[b]
            for d in range(q):
                require((c,d) not in owned, 'coclique forbidden edge')
                probes += 1
    # Exact C4-free and A^2=qI+J-B controls on the nonzero vectors.
    common_pairs = 0
    if q <= 16:
        nonzero = [(a,b) for a in range(q) for b in range(q) if a or b]
        neighbors = {x:set() for x in nonzero}
        for a,b in nonzero:
            if a:
                neighbors[(a,b)] = {(c,tab[1 ^ tab[b][c]][inv[a]]) for c in range(q)}
            else:
                neighbors[(a,b)] = {(inv[b],d) for d in range(q)}
            require(len(neighbors[(a,b)]) == q and (a,b) not in neighbors[(a,b)], 'simple regular graph')
        for a,b in nonzero:
            for c,d in nonzero:
                common = len(neighbors[(a,b)] & neighbors[(c,d)])
                expected_common = q if (a,b)==(c,d) else int(bool(tab[a][d]^tab[b][c]))
                require(common == expected_common, 'common-neighbor identity')
                common_pairs += 1
    return dict(k=k,q=q,h=3*k,port_rank=k,ports=q*q,modulus=modulus,
                trace_rank_cases=q,coclique_size=len(points),coclique_probes=probes,
                common_neighbor_pairs=common_pairs,
                coclique_sha256=hashlib.sha256(json.dumps(points,separators=(',',':')).encode()).hexdigest())


def show(x):
    scaled = x.numerator*10**18//x.denominator
    return str(scaled//10**18)+'.'+str(scaled%10**18).zfill(18)


def result():
    base = tuple(3*x for x in power89(F(2,7)))
    unit = power89(F(1,7))
    rows = []
    for k,poly in [(2,0x7),(4,0x13),(6,0x43),(8,0x11b)]:
        row = field(k,poly)
        c = F(3*row['coclique_size'],2*row['ports'])
        moment = tuple(base[i]+c*unit[i] for i in (0,1))
        require(moment[0] > 1, 'finite coclique excludes target')
        row['moment_lower'],row['moment_upper'] = map(str,moment)
        row['moment_display'] = show(moment[0])
        rows.append(row)
    # Counter-control: this particular independence bound alone stops excluding
    # q=1024. This is not an admissible supplier or a passing actual decoder.
    q,r = 1024,32
    c = F(3*(q*r-q+r),2*q*q)
    control = tuple(base[i]+c*unit[i] for i in (0,1))
    require(control[1] < 1, 'scope control q=1024')
    return dict(status='finite_geometry_and_scoped_obstruction_only',
                external_attribution='Mubayi--Williford, Theorem 6; independently checked finite cocliques',
                source_url='https://homepages.math.uic.edu/~mubayi/papers/erdosrenyi_revised.pdf',
                target_primitive_saving='1/9',data_moment=list(map(str,base)),
                cases=rows,q1024_coclique_only_control=list(map(str,control)),
                no_supplier=True,no_new_kappa=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    got = result()
    path = HERE/'FIELD-RESULT.json'
    if args.write:
        path.write_text(json.dumps(got,indent=2)+'\n')
    else:
        require(json.loads(path.read_text())==got,'frozen finite field receipt')
    print('PASS_KAPPA01_FIELD_GEOMETRY q=4,16,64,256 finite_target_failures=4 scope_control=1024 no_new_kappa')


if __name__=='__main__':
    main()
