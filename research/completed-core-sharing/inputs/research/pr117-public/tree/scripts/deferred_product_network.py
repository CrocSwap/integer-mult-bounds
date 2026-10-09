#!/usr/bin/env python3
"""Deferred bit word (#97, Swapnil Jain round 7) under PR #104's one-child stopped-product rule, with the
complex row of the selected h24 producer; exact moments, stopped saving, bridge and assembly.

Every bit residual of the frozen round-seven schedule (gauged and plain exteriors, slot chain steps, centre
copies, y_T and X_S chain steps, data connectors, copy corrections) is a nested projector residual and becomes
ONE child of its rank (notes/stopped-product-factorization.tex; research/deferred-product/PROOF.md). The
complex row uses the unchanged #104 profile. Constants and enclosures are those of stopped_product_network.py.
"""
import sys, json
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
DR = ROOT / 'research/deferred-signed/swapnil-round7/independent/deferred-readout'
sys.path[:0] = [str(DR), str(DR.parent / 'two-stage-bit'), str(DR.parents[1] / 'scripts')]
import stopped_product_network as spn
import deferred as dr
from certify import require
from copied_centers_network import finite_bridge as copied_bridge
from partial_swap_network import moment
from structured_bulk_assembly import assembly, js

GRID = 10**10
ATOM, OLD, PHASE_STOP = spn.ATOM, spn.OLD, spn.PHASE_STOP


def bit_profile():
    """One-child list of the round-seven deferred word (both stages, all invocations)."""
    h = 23
    W, D = dr.load(h)
    S = dr.Schedule(W, D)
    v, R, m = S.v, S.R, h * h
    rk = dr.chain_ranks(S)                       # recorded exact dims, checked by check_frames.py (part X)
    yl = S.ylevels(S.adjoint())                  # Z supports, as in the pinned round-seven histogram
    xd = S.xdata()
    z = Counter()
    for _ in range(2):                           # stage two: complement time-reversal, same residual multiset
        for s in range(R):
            z[m - (h - S.f[s])] += v              # exterior of rank m - r_u (plain slots: r_u = h)
        for r, c in rk.items():
            z[r] += v * c                         # slot chain steps
        z[h - 1] += v * h                         # centre copies U_c -> 0
        for t in range(v):
            ds = sorted(set([0] + yl[t] + [h - 1]))
            for a, b in zip(ds, ds[1:]):
                z[b - a] += v                     # y_T chain steps
        for xs in xd:
            for x in xs:
                z[x] += v                         # X_S chain steps
    N = v * v
    z[(h - 1) ** 2] += 2 * N                      # data connectors (I-P)(x)(I-Q)
    z[1] += N                                     # copy corrections
    Wb, L = 2 * N + 2 * v * R, 2 * v * h * (h - 1)
    s = Wb * m - N + L
    require(sum(t * n for t, n in z.items()) == s, 'Complete rank mass')
    require(all(0 < t < m and n > 0 for t, n in z.items()), 'Shrinking children')
    z = dict(sorted(z.items()))
    return dict(dimensions=[h, h], m=m, N=N, B1=v * R, B2=v * R, W=Wb, L=L, total_rank=s, deficit=N - L,
                maxchild=max(z), child_multiplicities=z, roles=R)


def coarse_ok(p, saving):
    spn.COARSE = saving
    spn.AB = (1 - ATOM) * saving + ATOM * OLD
    try:
        return spn.coarse_moment(p)
    except Exception as error:
        if 'moments' in str(error) or 'enclosure' in str(error):
            return None
        raise


def largest(predicate, hi):
    lo = 0
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if predicate(mid):
            lo = mid
        else:
            hi = mid
    return lo


def contracts(phase, a):
    try:
        moment(phase['m'], phase['W'], phase['child_multiplicities'], a, True)
        return True
    except ValueError as error:
        if 'does not contract' in str(error):
            return False
        raise


def bridge_for(bit, phase, row, previous):
    bridge = copied_bridge(bit, phase, [row, row])
    old_bit = previous['finite_bridge']['bit']
    old_degree = old_bit['halving_degree'] * old_bit['wire_bits']
    require(old_degree == 252, 'Inherited ordinary leaf row stock')
    coarse = bridge.pop('bit')
    c = bridge['complex']
    coefficient = coarse['halving_degree'] * coarse['wire_bits'] + old_degree + c['halving_degree'] * c['wire_bits']
    degree = 1000 * ((coefficient * 51) // 25000 + 1)            # smallest sufficient multiple of 1000
    require(Q(degree) > Q(51 * coefficient, 25), 'Product stock strictly sufficient')
    bridge.update(bit_coarse=coarse, ordinary_leaf_row_degree=old_degree)
    bridge['rows'] = dict(coefficient=coefficient, degree=degree, suffix_slope=4 * degree,
                          degree_gap=Q(degree) - Q(51 * coefficient, 25),
                          contract='W_complex^D_complex * W_coarse^D_coarse * W_old^D_old; one preceding prefix and one padding; sequential reuse')
    require(row['h'] == row['central_disjoint'] == 24 and row['h'] - 3 == 21, 'Selected all-disjoint centers')
    bridge['semantic'].update(fixed_odd_divisor=21,
                              exact_grid='One common dyadic grid times the fixed odd divisor to K=G*(D_complex+1); no child rounding')
    return bridge


def certificate(complex_row_path):
    require(not sys.flags.optimize, 'Run without -O')
    read = lambda name: json.loads((ROOT / 'certificates' / name).read_text())
    previous = read('copied-centers-network.json')
    require(Q(previous['bit']['saving']) == OLD, 'Certified ordinary leaf saving')
    bit = bit_profile()
    complex_row = json.loads(Path(complex_row_path).read_text())
    phase = spn.profile(complex_row)
    c = largest(lambda k: coarse_ok(bit, Q(k, GRID)) is not None, GRID // 1000)
    COARSE = Q(c, GRID)
    bm = coarse_ok(bit, COARSE)
    require(bm is not None and coarse_ok(bit, Q(c + 1, GRID)) is None, 'Largest coarse grid saving')
    AB = (1 - ATOM) * COARSE + ATOM * OLD
    a = largest(lambda k: contracts(phase, Q(k, GRID)), GRID // 1000)
    AC = Q(a, GRID)
    cm = moment(phase['m'], phase['W'], phase['child_multiplicities'], AC, True)
    require(not contracts(phase, Q(a + 1, GRID)), 'Next complex grid point must fail')
    assembly_bit = min(AB, (1 - PHASE_STOP) * AC - Q(1, GRID))
    bridge = bridge_for(bit, phase, complex_row, previous)
    eta = Q(1, 10**8)
    q = assembly_bit * (1 - 2 * eta)
    eps = (1 - eta) / (1 + q * (1 + eta) + q)
    k = (eps * q * GRID).__floor__()
    if Q(k, GRID) >= eps * q:
        k -= 1
    KAPPA = Q(k, GRID)
    assembled = assembly(assembly_bit, AC, bridge, KAPPA, beta=PHASE_STOP)
    require(len(assembled['strict_constraints']) == 47 and len(assembled['margins']) == 7, 'Complete assembly')
    rejection = None
    try:
        assembly(assembly_bit, AC, bridge, KAPPA + Q(1, GRID), beta=PHASE_STOP)
    except Exception as error:                   # the inherited assembly rejects by assertion
        rejection = str(error)
    require(rejection is not None, 'Next kappa grid point must fail')
    assembled['parameters']['actual_bit_saving'] = AB
    return dict(status='Conditional stopped product-ring multiplication witness: deferred bit word, selected complex row',
                kappa=KAPPA, next_kappa_rejection=rejection, coarse_bit_saving=COARSE, ordinary_bit_saving=AB,
                a_complex=AC, assembly_bit=assembly_bit, binding='bit' if assembly_bit == AB else 'complex',
                bit=dict(counts=bit, **bm), complex=dict(counts=phase, **cm), finite_bridge=bridge, assembly=assembled,
                complex_row_sha256=sha256(Path(complex_row_path).read_bytes()).hexdigest())


if __name__ == '__main__':
    out = certificate(sys.argv[1])
    Path(sys.argv[2]).write_text(json.dumps(js(out), indent=2, sort_keys=True) + '\n')
    print('PASS kappa=%s = %.7e; coarse bit %s (%.7e), ordinary bit %.7e, complex %s (%.7e), binding %s, maxchild %d, row degree %d'
          % (out['kappa'], float(out['kappa']), out['coarse_bit_saving'], float(out['coarse_bit_saving']),
             float(out['ordinary_bit_saving']), out['a_complex'], float(out['a_complex']), out['binding'],
             out['bit']['counts']['maxchild'], out['finite_bridge']['rows']['degree']))
