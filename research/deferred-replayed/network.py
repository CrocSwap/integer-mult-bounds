#!/usr/bin/env python3
"""Exact certificate: deferred bit word (as in deferred_product_network.py) and the deferred replayed complex profile.

The bit side, coarse/stopped savings and finite bridge are those of scripts/deferred_product_network.py. The complex
profile is research/deferred-replayed/complex-profile.json (PR #110 deferral with PR #114 saturated frames on the
replayed h24 DAG). The complex scalar guard uses PR #114's conservative literal charge for expanded deferred
readouts. Grids: coarse bit 1e-10, complex 1e-12, kappa 1e-15; every next grid point is rejected.
Usage: python3 research/deferred-replayed/network.py [--write]
"""
import json
import sys
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import deferred_product_network as dpn  # noqa: E402
from certify import require  # noqa: E402
from partial_swap_network import moment  # noqa: E402
from structured_bulk_assembly import assembly, js  # noqa: E402

ATOM, OLD, BETA = dpn.ATOM, dpn.OLD, dpn.PHASE_STOP


def complex_profile():
    p = json.loads((HERE / 'complex-profile.json').read_text())
    z = {int(t): c for t, c in p['child_multiplicities'].items()}
    require(sum(t * c for t, c in z.items()) == p['total_rank'] == p['W'] * p['m'] - p['N'] + p['L'], 'Complex rank mass')
    require(all(0 < t < p['m'] and c > 0 for t, c in z.items()) and max(z) == p['maxchild'], 'Complex children')
    p['child_multiplicities'] = z
    return p


def largest_on(grid, ok, lo, hi):
    require(ok(lo) and not ok(hi), 'Bracket')
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if ok(mid) else (lo, mid)
    return lo


def certificate():
    require(not sys.flags.optimize, 'Run without -O')
    previous = json.loads((ROOT / 'certificates' / 'copied-centers-network.json').read_text())
    require(Q(previous['bit']['saving']) == OLD, 'Certified ordinary leaf saving')
    bit, phase = dpn.bit_profile(), complex_profile()
    c = dpn.largest(lambda k: dpn.coarse_ok(bit, Q(k, dpn.GRID)) is not None, dpn.GRID // 1000)
    COARSE = Q(c, dpn.GRID)
    bm = dpn.coarse_ok(bit, COARSE)
    require(bm is not None and dpn.coarse_ok(bit, Q(c + 1, dpn.GRID)) is None, 'Largest coarse grid saving')
    AB = (1 - ATOM) * COARSE + ATOM * OLD
    a = largest_on(10**12, lambda k: dpn.contracts(phase, Q(k, 10**12)), 7 * 10**7, 2 * 10**8)
    AC = Q(a, 10**12)
    cm = moment(phase['m'], phase['W'], phase['child_multiplicities'], AC, True)
    abit = min(AB, (1 - BETA) * AC - Q(1, 10**14))
    row = dict(h=phase['h'], v=phase['v'], c=phase['additions'], central_disjoint=24)
    bridge = dpn.bridge_for(bit, phase, row, previous)
    # PR #114's conservative literal charge: every expanded deferred readout is charged even if it could be
    # factored. Each row has <=c+R mixer operations and <=R leaf copies; <=R+q readouts with <=h centre and <=v
    # direct coefficients, <=4v(h+1) scalar groups each; a factor eight covers forward/inverse/reflected words.
    h, v, R, q, cc = (phase[k] for k in ('h', 'v', 'R', 'roots', 'additions'))
    local = 8 * (cc + 2 * R + (R + q) * v * (h + 1) + h * h + h + 1)
    G = phase['N'] + 2 * v * local
    m, W, s = phase['m'], phase['W'], phase['total_rank']
    E = 64 * (W + m + G + 1) ** 3
    charge = 2 * G * W * W + 8 * s + 4 * W + 4 + 32 * m
    B = s + E
    C0 = 32 * m * B * B
    require(charge < E and 2 * B * (m - phase['maxchild']) >= s + E and 2 * B + 18 < C0, 'Expanded literal charge')
    bridge['complex']['scalar_group_upper'] = G
    bridge['complex']['scalar_terms'] = [dict(h=h, v=v, c=cc, R=R, q=q, invocations=v, local_group_upper=local,
                                              description='Expanded deferred readouts and forward/inverse/reflected words')] * 2
    bridge['semantic'].update(E=E, literal_charge=charge, strict_literal_gap=E - charge, B=B, C0=C0, C1=1,
                              induction_gap=2 * B * (m - phase['maxchild']) - s - E)

    def accepts(k):
        try:
            assembly(abit, AC, bridge, Q(k, 10**15), beta=BETA)
            return True
        except AssertionError:
            return False
    k = largest_on(10**15, accepts, 7 * 10**10, int(AC * 10**15) + 1)
    KAPPA = Q(k, 10**15)
    assembled = assembly(abit, AC, bridge, KAPPA, beta=BETA)
    require(len(assembled['strict_constraints']) == 47 and len(assembled['margins']) == 7, 'Complete assembly')
    assembled['parameters']['actual_bit_saving'] = AB
    return dict(status='Conditional witness: deferred bit word and deferred replayed h24 complex network',
                kappa=KAPPA, coarse_bit_saving=COARSE, ordinary_bit_saving=AB, a_complex=AC, assembly_bit=abit,
                binding='bit' if abit == AB else 'complex',
                next_grid_rejections=dict(coarse_bit='1e-10', complex='1e-12', kappa='1e-15'),
                bit=dict(counts=bit, **bm),
                complex=dict(counts={k: phase[k] for k in ('h', 'v', 'R', 'additions', 'links', 'roots', 'm', 'N', 'W', 'L',
                                                           'total_rank', 'deficit', 'maxchild', 'deferred_roles',
                                                           'phase_one_roles')},
                             child_multiplicities=phase['child_multiplicities'], **cm),
                finite_bridge=bridge, assembly=assembled,
                complex_profile_sha256=sha256((HERE / 'complex-profile.json').read_bytes()).hexdigest())


def main():
    out = js(certificate())
    path = HERE / 'certificate.json'
    text = json.dumps(out, indent=2, sort_keys=True) + '\n'
    if '--write' in sys.argv[1:]:
        path.write_text(text)
    else:
        require(path.read_text() == text, 'Frozen exact certificate mismatch')
    print('PASS kappa=%s = %.10e (complex-bound: %s); complex saving %s; coarse bit %s; 47 constraints, 7 margins'
          % (out['kappa'], float(Q(out['kappa'])), out['binding'] == 'complex', out['a_complex'], out['coarse_bit_saving']))


if __name__ == '__main__':
    main()
