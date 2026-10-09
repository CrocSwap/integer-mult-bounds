#!/usr/bin/env python3
"""Exact selected copied-center moments and semantic assembly.

Copyright 2026 icekylinx. Apache-2.0.
Prepared with substantial OpenAI GPT-6 Astra and Codex assistance.
Two-stage topology: Aurel Prosz (Paureel), through PR29 (Zhihao Chen).
Corner method: Rohan Arun PR31, parameterized by Dominik Scholz PR33.
Semantic assembly: Zhihao Chen PR23, building on RaD (hipotures).
See SOURCES.json and references/copied-centers for pinned contributions.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path
import json
import sys

from certify import require
from copied_centers.physical import copied_histogram as physical_histogram
from partial_swap_network import moment
from structured_bulk_assembly import assembly, halving, js

ROOT = Path(__file__).resolve().parents[1]
AB = Q(384599, 10**10)
AC = Q(717, 10**7)
KAPPA = Q(384569, 10**10)
GRID = 1 << 100


def copied_histogram(row):
    require(row['v'] == comb(row['h'], 3), 'Triple count')
    return physical_histogram(row)['histogram']


def profile(rows, corner=None):
    a, b = (row['h'] for row in rows)
    m, N = a*b, rows[0]['v']*rows[1]['v']
    B1, B2 = (N//row['v']*row['R'] for row in rows)
    W = 2*N+B1+B2
    L = sum(N//row['v']*row['loss'] for row in rows)
    z = Counter()

    def ordinary(h, r, n):
        if 2*r > h:
            z[2*r-h] += n
            z[1] += (h-r)*n
        else:
            z[1] += r*n

    if corner is not None:
        require((a, b) == (25, 23), 'Selected bit dimensions')
        require(corner['dimensions'] == [a, b] and corner['m'] == m, 'Corner dimensions')
        cp = corner['data_profile']
        require(cp['singletons'] == 11 and cp['blocks'] == [21, 15, 481], 'Selected data profile')
        for h, count in ((a, B1), (b, B2)):
            z[h] += count
            z[m-2*h] += count
        z[1] += cp['singletons']*2*N
        for t in cp['blocks']:
            z[t] += 2*N
    else:
        require((a, b) == (28, 28), 'Selected complex dimensions')
        z[m-a] += B1
        z[m-b] += B2
        z[(a-1)*(b-1)] += 2*N

    copied = []
    for row in rows:
        h, copies = row['h'], N//row['v']
        hist = copied_histogram(row)
        copied.append(dict(h=h, center_ranks=[h-1]*h, histogram=hist))
        for r, n in enumerate(hist):
            if corner is not None:
                ordinary(h, r, copies*n)
            elif r:
                z[r] += copies*n
        if corner is not None:
            ordinary(h, h-1, 2*N)
        else:
            z[h-1] += 2*N
    z[1] += N  # Paid endpoint transform on the copied first output.
    z = dict(sorted((t, n) for t, n in z.items() if t and n))
    require(all(0 < t < m and n > 0 for t, n in z.items()), 'Child domains')
    s = W*m-N+L
    require(sum(t*n for t, n in z.items()) == s, 'Complete two-stage rank')
    return dict(dimensions=[a,b], m=m, N=N, B1=B1, B2=B2, W=W, L=L,
                total_rank=s, deficit=N-L, maxchild=max(z),
                copied_center_circuits=copied, child_multiplicities=z)


def grid_upper(x):
    return Q((x.numerator*GRID+x.denominator-1)//x.denominator, GRID)


def bit_moment(p):
    def log_upper(x):
        k = 0
        while x >= 2:
            x /= 2
            k += 1
        def small(y):
            z = (y-1)/(y+1)
            return 2*sum((z**(2*j+1)/(2*j+1) for j in range(24)), Q(0)) + 2*z**49/(49*(1-z*z))
        return grid_upper(k*small(Q(2))+small(x))
    total = Q(0)
    logs = {}
    for t, n in p['child_multiplicities'].items():
        logs[t] = log_upper(Q(p['m'], t))
        u = AB*logs[t]
        require(0 < u < 3, 'Bit exponential enclosure')
        total += n*t*grid_upper(1+u+u*u/(2*(1-u/3)))
    upper = total/(p['W']*p['m'])
    require(upper < 1, 'Strict bit moment')
    return dict(saving=AB, exponent=1-AB, moment_upper=upper, strict_gap=1-upper,
                logarithm_upper_bounds=logs, rounding_denominator=GRID,
                enclosure='24-term atanh log with geometric tail; exp upper 1+u+u^2/(2(1-u/3)); upward 2^-100 rounding')


def finite_bridge(bit, phase, rows):
    m, W, s, N = (phase[k] for k in ('m', 'W', 'total_rank', 'N'))
    terms = []
    for row in rows:
        h, v, c = (row[k] for k in ('h', 'v', 'c'))
        local = 4*(c+v)+10*v+4*h*v+4*h*h+8*h+8
        terms.append(dict(h=h, v=v, c=c, invocations=N//v,
                          local_group_upper=local, copied_center_extra_groups=2*h))
    G = N+sum(t['invocations']*(t['local_group_upper']+t['copied_center_extra_groups']) for t in terms)
    E = 64*(W+m+G+1)**3
    charge = 2*G*W*W+8*s+4*W+4+32*m
    B, r = s+E, phase['maxchild']
    C0 = 32*m*B*B
    require(charge < E and 2*B*(m-r) >= s+E and 2*B+18 < C0, 'Semantic induction')
    db, dc = halving(bit['m'], bit['maxchild']), halving(m, r)
    wb, wc = bit['W'].bit_length(), W.bit_length()
    coeff = wb*db+wc*dc
    degree = 1000*((coeff*51)//25000+1)
    return dict(bit=dict(m=bit['m'], W=bit['W'], maxchild=bit['maxchild'], halving_degree=db, wire_bits=wb),
        complex=dict(m=m, W=W, s=s, maxchild=r, halving_degree=dc, wire_bits=wc,
                     scalar_terms=terms, scalar_group_upper=G),
        semantic=dict(E=E, literal_charge=charge, strict_literal_gap=E-charge, B=B,
                      C0=C0, C1=1, induction_gap=2*B*(m-r)-s-E),
        rows=dict(coefficient=coeff, degree=degree, suffix_slope=4*degree,
                  degree_gap=Q(degree)-Q(coeff*51,25),
                  contract='W_complex^D_complex * W_bit^D_bit; one preceding prefix and padding; all temporary copies sequential'))


def certificate():
    require(not sys.flags.optimize, 'Run without -O')
    def read(name):
        return json.loads((ROOT/'certificates'/('copied-centers-'+name+'.json')).read_text())
    axes, row, corner, expected = map(read, ('bit-axes', 'complex-input', 'corner-25-23', 'input'))
    bit, phase = profile(axes, corner), profile([row, row])
    for label, p in (('bit', bit), ('complex', phase)):
        for key, value in expected[label].items():
            require(js(p[key]) == value, label+' saved '+key)
    bm = bit_moment(bit)
    cm = moment(phase['m'], phase['W'], phase['child_multiplicities'], AC, True)
    require(bm['strict_gap'] == Q(expected['bit_moment_gap']), 'Saved bit moment')
    require(cm['strict_gap'] == Q(expected['complex_moment_gap']), 'Saved complex moment')
    bridge = finite_bridge(bit, phase, [row, row])
    assembled = assembly(AB, AC, bridge, KAPPA)
    require(js(bridge) == expected['finite_bridge'], 'Saved finite bridge')
    require(js(assembled) == expected['assembly'], 'Saved assembly')
    require(len(assembled['strict_constraints']) == 47 and len(assembled['margins']) == 7, 'Complete assembly')
    sources = sorted(p for p in (ROOT/'certificates').glob('copied-centers-*.json') if p.name != 'copied-centers-network.json')
    sources += sorted((ROOT/'scripts').glob('copied_centers*.py'))
    sources += sorted(p for p in (ROOT/'scripts/copied_centers').rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    sources += sorted((ROOT/'notes').glob('copied-centers-*.tex'))
    sources += [ROOT/'scripts/structured_bulk_assembly.py', ROOT/'scripts/partial_swap_network.py']
    manifest = json.loads((ROOT/'references/copied-centers/MANIFEST.json').read_text())
    for name, digest in manifest['files'].items():
        require(sha256((ROOT/'references/copied-centers'/name).read_bytes()).hexdigest() == digest, 'Adopted source hash: '+name)
    sources += [ROOT/'references/copied-centers/MANIFEST.json']
    return dict(status='Conditional copied-center multiplication witness', kappa=KAPPA,
        bit=dict(counts=bit, **bm), complex=dict(counts=phase, **cm),
        finite_bridge=bridge, assembly=assembled,
        inherited_commit='0ef3aeb61f55cc0b321ce6a0ef00acee25cefe52', adopted_sources=manifest,
        source_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sources},
        scope='Exact finite moments and assembly; producer and corner certificates checked separately. '
              'Copied-stream scheduling, simultaneous basis existence, analytic and tape interfaces remain written proof dependencies.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'certificates/copied-centers-network.json')
    args = parser.parse_args()
    result = certificate()
    args.output.write_text(json.dumps(js(result), indent=2, sort_keys=True)+'\n')
    print('PASS kappa=384569/10000000000 = 3.84569e-5')
    print('Both exact moments; copied-center rank budgets; C1=1; p^2000 row stock; 47 strict constraints')


if __name__ == '__main__':
    main()
