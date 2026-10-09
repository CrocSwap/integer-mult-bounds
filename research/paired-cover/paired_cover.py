#!/usr/bin/env python3
"""Paired lockstep vertices in the first stage of PR130's three-stage complex cover.

PR130 runs PR117's h = 24 local word at every vertex k of G = O(E), dim E = 70, inside the active space kA
(dim A = 24), with an independent auxiliary bank of R roles per stage; every role pays an exterior of width
m - h + dim(sigma). Let kappa be the coordinate involution of E exchanging e_i and e_(24+i) for i < 24. It is
orthogonal and maps A into B + C, so kA and (k kappa)A are orthogonal for every k. In the first stage the offset is
0, so a core occupies only kA. Pair the first-stage vertices k and k kappa: the paired cores share every first-stage
role stream (exterior m - 2h + 2 dim(sigma)) and run in lockstep, so each frame step of a shared stream is one nested
transition of rank 2d (PR130's general Clifford lemma: one child of width 2d). The second and third stages carry the
offsets kB and k(B + C), which leave no orthogonal room for a partner; they stay unpaired. Data streams, routing and
the bit side are PR130's, unchanged.

Inputs (pinned by SHA-256): PR130's certificates/three-stage-cover-complex-input.json (local inventory) and
certificates/three-stage-cover-network.json (its certified bit saving and per-vertex complex children, used to check
that the unpaired profile rebuilt here is PR130's). Writes certificate.json next to this file.
Usage: python3 research/paired-cover/paired_cover.py
Prepared by Avi Eisenberg (ikeboy) with Anthropic Claude assistance. Apache-2.0.
"""
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction as Q
from math import comb, prod
from pathlib import Path

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from partial_swap_network import moment                      # noqa: E402
from structured_bulk_assembly import assembly, halving, js   # noqa: E402

PINS = {'three-stage-cover-complex-input.json': 'afecf8ce2d8eb259074e61cd0c386b464ca2f57c61b00979eac808fa26e0b770',
        'three-stage-cover-network.json': 'bfca1f225394c8b50f3360b71920652baf9bd885ce84f9c0a9184c3ba7dd35ab'}
GRID = 10**10
ATOM = Q(1, 1000)                 # PR104/PR130 stopping exponent
OLD = Q(384599, 10**10)           # retained ordinary leaf saving
PHASE_STOP = Q(1, 10**6)          # beta


def require(ok, msg):
    if not ok:
        raise SystemExit('FAIL: ' + msg)


def read(name):
    raw = (ROOT / 'certificates' / name).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PINS[name], 'pinned hash of ' + name)
    return json.loads(raw)


def largest(m, W, z, lo, hi):
    def ok(a):
        try:
            moment(m, W, z, a, True); return True
        except BaseException:
            return False
    a, b = int(lo * GRID), int(hi * GRID)
    require(ok(Q(a, GRID)) and not ok(Q(b, GRID)), 'moment bracket')
    while b - a > 1:
        mid = (a + b) // 2
        a, b = (mid, b) if ok(Q(mid, GRID)) else (a, mid)
    return Q(a, GRID), moment(m, W, z, Q(a, GRID), True)


def main():
    row = read('three-stage-cover-complex-input.json')
    net = read('three-stage-cover-network.json')
    h, v, R, ell = row['h'], row['v'], row['R'], row['loss']
    require((h, v, R, ell) == (24, comb(24, 3), 28705, 552) and R == row['c'] + row['q'] - row['matched'], 'local word')
    m = 3 * h - 2
    sel = {int(a): c for a, c in row['selected_rank_histogram'].items()}; S = sum(sel.values())
    require(S == row['selected_roles'] == 4599, 'partial gauges')
    H = Counter({r: c for r, c in enumerate(row['remaining_internal_histogram']) if r and c})
    data = Counter()
    for key in ('source_data_histogram', 'target_data_histogram'):
        for r, c in row[key].items(): data[int(r)] += c

    # PR130's unpaired per-vertex profile, rebuilt and compared with its certificate
    z1 = Counter({m - h: 3 * (R - S)})
    for a, c in sel.items(): z1[m - h + a] += 3 * c
    for r, c in (H + data).items(): z1[r] += 3 * c
    require({str(t): c for t, c in sorted(z1.items())} == {str(k): c for k, c in net['complex']['per_vertex']['child_multiplicities'].items()},
            'unpaired profile equals PR130')

    # the pairing involution: exchange e_i and e_(24+i), i < 24, on E = A + B + C (dims 24, 23, 23)
    perm = list(range(m))
    for i in range(h): perm[i], perm[h + i] = h + i, i
    require(all(perm[perm[x]] == x for x in range(m)), 'involution')
    require(all(perm[i] >= h for i in range(h)), 'kappa A lies in B + C, orthogonal to A')

    # per pair of vertices: stage 1 shared and in lockstep, stages 2 and 3 as in PR130 (two banks each)
    z = Counter({m - 2 * h: R - S})
    for a, c in sel.items(): z[m - 2 * h + 2 * a] += c
    for r, c in H.items(): z[2 * r] += c
    z[m - h] += 4 * (R - S)
    for a, c in sel.items(): z[m - h + a] += 4 * c
    for r, c in H.items(): z[r] += 4 * c
    for r, c in data.items(): z[r] += 6 * c
    z = Counter({t: c for t, c in z.items() if c})
    w2 = 4 * v + 5 * R; rank2 = sum(t * c for t, c in z.items())
    require(w2 * m - rank2 == 2 * (2 * v - 3 * ell), 'paired telescoping')
    require(all(0 < t < m for t in z), 'children below m')
    ac, cm = largest(m, w2, z, Q(3, 10**4), Q(6, 10**4))

    # bit side: PR130's certified stopped saving
    coarse = Q(net['bit']['coarse_saving']); ab = Q(net['bit']['effective_saving'])
    require(ab == (1 - ATOM) * coarse + ATOM * OLD, 'PR130 stopped bit saving')
    abit = min(ab, (1 - PHASE_STOP) * ac - Q(1, GRID))

    # finite bridge, as PR130's, with the paired stream count
    n = m // 2
    vertices = 2 ** (m - 1 + (n - 1) ** 2) * prod(2 ** (2 * i) - 1 for i in range(1, n))
    require(vertices == int(net['complex']['vertices_per_stage']), 'group order')
    W = vertices * w2 // 2; srank = vertices * rank2 // 2; N = vertices * v
    local = 4 * (row['c'] + v) + 10 * v + 4 * h * v + 4 * h * h + 8 * h + 8 + 2 * h
    local += 8 * R * v * (row['total_M_operations'] + 16)
    router = 64 * (m + 1) ** 3 * W ** 2
    G = N + 3 * vertices * local + router
    E = 64 * (W + m + G + 1) ** 3
    charge = 2 * G * W * W + 8 * srank + 4 * W + 4 + 32 * m
    r = max(z); B = srank + E; C0 = 32 * m * B * B
    require(charge < E and 2 * B * (m - r) >= srank + E and 2 * B + 18 < C0, 'finite semantic charge')
    dp, wp = halving(m, r), W.bit_length()
    coefficient, degree = dp * wp + 9909 + 252, 160000
    require(Q(degree) > Q(51 * coefficient, 25), 'external product row reserve')
    bridge = dict(complex=dict(m=m, W=W, s=srank, N=N, maxchild=r, invocations_per_stage=vertices, stages=3,
                               halving_degree=dp, wire_bits=wp, scalar_group_upper=G, local_group_upper=local,
                               finite_group_router_upper=router, paired_vertices=True),
                  semantic=dict(E=E, literal_charge=charge, strict_literal_gap=E - charge, B=B, C0=C0, C1=1,
                                induction_gap=2 * B * (m - r) - srank - E, fixed_odd_divisor=h - 3),
                  rows=dict(coefficient=coefficient, complex_coefficient=dp * wp, degree=degree, suffix_slope=4 * degree,
                            degree_gap=Q(degree) - Q(51 * coefficient, 25)),
                  conservative_old_coarse_row_reserve=9909, ordinary_leaf_row_degree=252)

    def accepted(k):
        try:
            assembly(abit, ac, bridge, Q(k, GRID), beta=PHASE_STOP); return True
        except AssertionError:
            return False
    lo, hi = int(Q(3, 10**4) * GRID), int(abit * GRID) + 1
    require(accepted(lo) and not accepted(hi), 'kappa bracket')
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if accepted(mid) else (lo, mid)
    kappa = Q(lo, GRID)
    res = assembly(abit, ac, bridge, kappa, beta=PHASE_STOP)
    require(not accepted(lo + 1), 'next kappa grid point rejected')
    require(len(res['strict_constraints']) == 47 and len(res['margins']) == 7, 'complete assembly')
    res['parameters']['actual_bit_saving'] = ab
    out = dict(status='Conditional witness: paired lockstep first-stage vertices on PR130 three-stage complex cover', kappa=kappa,
               complex=dict(saving=ac, moment_gap=cm['strict_gap'], per_pair=dict(W=w2, rank=rank2, deficit=w2 * m - rank2,
                            child_multiplicities=dict(sorted(z.items()))), maxchild=r,
                            unpaired_saving_pr130=Q(net['complex'].get('saving', 0)) if 'saving' in net['complex'] else None),
               bit=dict(coarse_saving=coarse, stopped_saving=ab, source='PR130 certificates/three-stage-cover-network.json'),
               finite_bridge=bridge, assembly=res, base='PR130 head 6a9970a530119174507904e23592fd59ede19a5d')
    (HERE / 'certificate.json').write_text(json.dumps(js(out), indent=2, sort_keys=True) + '\n')
    print('PASS kappa = %s = %.10e' % (kappa, float(kappa)))
    print('paired complex saving %s = %.6e; PR130 stopped bit saving %.6e; binding side: %s' % (ac, float(ac), float(ab), 'bit' if ab < (1 - PHASE_STOP) * ac - Q(1, GRID) else 'complex'))


if __name__ == '__main__':
    main()
