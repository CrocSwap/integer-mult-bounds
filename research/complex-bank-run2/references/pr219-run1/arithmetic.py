#!/usr/bin/env python3
"""Exact paid moments, finite ordinary-leaf composition and the balanced assembly
for the rank-22-absorbed profile.

Inherited machinery (vendored byte-identically):
  interval_moment.py   - PR200's exact rational interval moment engine
  paired_cube_assembly.py - PR184/PR168-v4's unchanged 47-constraint balanced assembly
Profiles come from the pinned certificates and schedule.py's retained ledger.
"""
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)


def load(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def profile(m, W, H, delta):
    H = {int(r): int(n) for r, n in H.items()}
    return dict(m=m, W=W, child_multiplicities=H, N=delta, L=0,
                total_rank=sum(r * n for r, n in H.items()), maxchild=max(H))


def paid(im, row, a, bit):
    result = im.moment(row, a)
    if bit:
        l, u = im.log_interval(Q(row['m']))
        e, f = im.exp_interval(a * l, a * u)
        w = Q(1, 10 ** 16) * Q(32 * row['m'] * sum(row['child_multiplicities'].values()), row['W'])
        result.update(lower=result['lower'] + w * e, upper=result['upper'] + w * f)
    return result


def certify(im, row, bit):
    den = 10 ** 18
    lo = 0
    hi = den // 100
    assert paid(im, row, Q(lo, den), bit)['upper'] < 1 < paid(im, row, Q(hi, den), bit)['lower']
    while hi - lo > 1:
        mid = (lo + hi) // 2
        v = paid(im, row, Q(mid, den), bit)
        if v['upper'] < 1:
            lo = mid
        elif v['lower'] > 1:
            hi = mid
        else:
            raise AssertionError('Interval inconclusive')
    a = Q(lo, den)
    b = Q(hi, den)
    return dict(saving=a, accepted=paid(im, row, a, bit), next_excluded=paid(im, row, b, bit))


def build(schedule):
    im = load('interval_moment', HERE / 'interval_moment.py')
    assembly = load('frontier_assembly', HERE / 'paired_cube_assembly.py')
    c191 = json.loads((HERE / 'references/pr193-source-assisted-v4.certificate.json').read_text())
    b200 = json.loads((HERE / 'references/pr200-bit.certificate.json').read_text())['bit']
    pack = json.loads((HERE / 'references/pr205-packed.certificate.json').read_text())['physical']

    cp_raw = c191['complex_profile']
    cp = profile(cp_raw['m'], cp_raw['W_per_vertex'], cp_raw['child_histogram'], cp_raw['deficit_per_vertex'])
    packed = profile(72, pack['W'], pack['child_histogram'], pack['deficit'])

    kept = schedule['retained_profile']
    absorbed = profile(72, kept['W_after'], kept['histogram'], kept['deficit'])
    assert absorbed['total_rank'] == kept['rank_mass_after']
    assert absorbed['maxchild'] == kept['maxchild']

    complex_cert = certify(im, cp, False)
    before = certify(im, packed, True)
    after = certify(im, absorbed, True)
    # The engine must reproduce PR205's certified packed coarse saving exactly.
    certified_packed_saving = Q(json.loads((HERE / 'references/pr205-packed.certificate.json').read_text())
                                ['arithmetic']['bit_after']['saving'])
    assert before['saving'] == certified_packed_saving, 'engine drift: packed row not reproduced'

    old = Q(b200['coarse']['ordinary_saving'])
    coarse = after['saving']
    chain = [old]
    for _ in range(3):
        a = (1 - coarse) * coarse + coarse * chain[-1]
        assert chain[-1] < a < coarse < 1 - a
        chain.append(a)
    leaf = chain[-1]

    bridge = c191['assembly']['finite_bridge']
    bridge['rows']['degree_gap'] = Q(bridge['rows']['degree_gap'])
    beta = eta = Q(1, 10 ** 24)
    weak = Q(1, 10 ** 30)
    den = 10 ** 18

    def assemble(bit_saving):
        b = complex_cert['saving']
        a = min(bit_saving, (1 - beta) * b - weak)
        q = a * (1 - 2 * eta)
        bound = (1 - eta) * q / (1 + q)
        z = bound * den
        k = Q((z.numerator - 1) // z.denominator, den)
        out = assembly.assembly(a, b, bridge, k, eta=eta, beta=beta)
        assert len(out['strict_constraints']) == 47 and len(out['margins']) == 7
        try:
            assembly.assembly(a, b, bridge, k + Q(1, den), eta=eta, beta=beta)
        except AssertionError:
            pass
        else:
            raise AssertionError('Next final grid accepted')
        constraints = out.pop('strict_constraints')
        return dict(kappa=k, assembly=dict(out, strict_constraint_count=len(constraints),
                                           minimum_constraint=min(constraints.values())),
                    binding='complex' if a == (1 - beta) * b - weak else 'bit')

    before_assembly = assemble(chain[0])
    after_assembly = assemble(leaf)
    assert before_assembly['kappa'] < after_assembly['kappa']
    assert after_assembly['binding'] == 'complex', 'rank-22 absorption must clear the complex cap'

    return dict(
        complex_coarse=complex_cert['saving'],
        bit_coarse_before=before['saving'],
        bit_coarse_after=after['saving'],
        bit_before_next_excluded=before['next_excluded'],
        bit_after_next_excluded=after['next_excluded'],
        ordinary_seed=old, ordinary_chain=chain, ordinary_leaf=leaf,
        before_assembly=before_assembly, after_assembly=after_assembly,
        kappa_gain=after_assembly['kappa'] - before_assembly['kappa'],
    )


if __name__ == '__main__':
    sys.path.insert(0, str(HERE))
    import schedule as sched
    out = build(sched.build())
    for k, v in out.items():
        if isinstance(v, Q):
            print(k, '=', v, float(v))
        elif isinstance(v, dict) and 'kappa' in v:
            print(k, 'kappa =', v['kappa'], float(v['kappa']), 'binding', v['binding'])
