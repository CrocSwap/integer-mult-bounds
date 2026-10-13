#!/usr/bin/env python3
"""Independent exact audit of the endpoint-to-kappa reduction of the selected
frontier799 assembly (research/community-frontier799-audit/ASSEMBLY.json).

Scope: the accounting step that turns the recorded moment endpoints
(complex_lower b, bit_lower c) and the guard parameters into the headline
kappa on the 1e-18 grid. Everything is recomputed with fractions from the
formulae in research/gauge44-frames-x/code/assemble.py (outer_witness) and
research/complex-k492-owner-repair/vendor/multicold/engines/outer.py; this
script imports none of the repository engines and re-derives every value.

Findings (see AUDIT.md):
  F1 kappa is the unique largest 1e-18 grid point strictly below the binding
     margin minimum = eps*q (the compact_phase_layer margin).
  F2 at kappa + 1e-18 exactly the guard cluster of margins co-fails:
     compact_phase_layer (the minimum), balanced_prefix (+eta),
     Gaussian_arithmetic (+3eta/8) and scalar_work (+7eta/8); every other
     strict slack stays positive.
  F3 kappa - conservative_kappa = 2881809/10^18 exactly, and the only input
     difference between the two reductions is the complex endpoint, so that
     entire increment is the complex surcharge removal (PR559 exact-cover).
  F4 the guard parameters (eta = beta = 1e-24, s-floor 1e-27) cost at most
     a recorded, exact amount of cap headroom.

Reproduce: python research/audit-kappa-floor-seed67/audit_kappa_reduction.py
Requires CPython >= 3.8, standard library only, no -O.
"""
import json
from decimal import Decimal
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSEMBLY = ROOT / 'research/community-frontier799-audit/ASSEMBLY.json'

# Reduction constants, transcribed from assemble.py outer_witness.
A0 = Q(384599, 10**10)
ETA = BETA = Q(1, 10**24)
SFLOOR = Q(1, 10**27)
TICK = Q(1, 10**18)
BRIDGE = {'literal_scalar_guard': Q(1),
          'row_product_gap': Q(10**6) - Q(51 * 20161, 25)}  # [5329, 4608] halving pair


def ceil(x):
    return -(-x.numerator // x.denominator)


def reduce_endpoint(b, c, eta=ETA, beta=BETA, sfloor=SFLOOR):
    """The complete endpoint -> kappa reduction, exact rationals only."""
    s = min(c, (1 - beta) * b) - sfloor
    chain = [A0]
    cuts = []
    for _ in range(7):
        old = chain[-1]
        a = (1 - s) * s + s * old
        gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s)
        assert gap > 0, 'bootstrap gap closed'
        cut = max(ceil(Q(36) / gap**2), ceil(Q(2 * (4 + 512)) / gap))
        assert cut * gap**2 >= 36 and cut * gap >= 2 * (4 + 512)
        cuts.append({'exponent': str(a), 'gap': str(gap), 'cutoff_log2': str(cut)})
        chain.append(a)
    qw = chain[-1] * (1 - 2 * eta)          # outer_witness q
    margin = (1 - eta) * qw / (1 + qw)      # = eps*qo = minimum margin
    ticks = margin * 10**18
    k = Q((ticks.numerator - 1) // ticks.denominator, 10**18)
    return {'kappa': k, 'margin': margin, 's': s, 'a7': chain[-1], 'cuts': cuts,
            'bit_binds': c < (1 - beta) * b,
            'endpoint_slack': abs(c - (1 - beta) * b)}


def slacks(a, b, kappa, eta=ETA, beta=BETA):
    """The 47 strict outer slacks, transcribed from engines/outer.py."""
    tau, sigma = 1 - a, 1 - b
    qo = a * (1 - 2 * eta)                  # outer.py q
    lp = 1 - qo
    lam = (tau + lp) / 2
    c_par = qo + eta / 4
    eps = (1 - eta) / (1 + qo)
    minimum = eps * qo
    r = (minimum + 1 - eps) / 2
    delta = eta / 8
    internal = tau + (1 - beta) * max(sigma - tau, Q(0))
    leaf = sigma + beta * (1 - sigma)
    margins = {'balanced_prefix': 1 - eps, 'coordinate_movement': a,
               'compact_phase_layer': minimum, 'bulk_exposure': a,
               'Gaussian_arithmetic': min(1 - eps - delta, r - delta),
               'scalar_work': 1 - eps - delta, 'dimension': eps}
    out = {'bit_positive': a, 'complex_above_bit': b - a,
           'complex_below_one_over32': Q(1, 32) - b, 'beta_positive': beta,
           'beta_below_one': 1 - beta, 'leaf_saving_above_bit': (1 - beta) * b - a,
           'q_positive': qo, 'q_below_internal': 1 - internal - qo,
           'q_below_leaf': 1 - leaf - qo, 'c_positive': c_par,
           'c_below_one': 1 - c_par, 'q_below_reservations': c_par - qo,
           'lambda_above_tau': lam - tau, 'lambda_above_sigma': lam - sigma,
           'lambda_above_internal': lam - internal,
           'lambda_prime_above_lambda': lp - lam, 'compact_leaf': lp - leaf,
           'compact_reservations': lp - (1 - c_par), 'lambda_prime_below_one': qo,
           'epsilon_positive': eps, 'epsilon_below_one': 1 - eps,
           'guard_width': 1 - eps, 'K_geometry': 1 - eps * (1 + c_par),
           'K_dominates_log': eps * c_par, 'record_suffix': 1 - eps,
           'phase_local': 1 - eps - delta, 'phase_boundary': r - delta,
           'gamma_sublinear': 1 - eps - r, 'cell_above_band': eps - (1 - r) / 2,
           'prime_interval_packing': 1 - eps, 'alpha_positive': r,
           'alpha_below_one': 1 - r, 'alpha_below_one_fourth': Q(1, 4) - r,
           'delta_positive': delta, 'delta_below_one_eighth': Q(1, 8) - delta,
           'short_record_fallback': eps - a, 'small_field_exposure': 1 - eps - minimum,
           'artificial_boundary': 8 - eps + r - delta - minimum,
           'literal_scalar_guard': BRIDGE['literal_scalar_guard'],
           'row_product_gap': BRIDGE['row_product_gap']}
    out.update({name + '_above_kappa': val - kappa for name, val in margins.items()})
    assert len(out) == 47 and len(margins) == 7
    assert min(margins.values()) == minimum
    return out, margins


def q_from_decimal_string(text):
    return Q(Decimal(text))


def check(asm):
    """Assert every audited identity against the committed assembly record."""
    b, c = Q(asm['complex_lower']), Q(asm['bit_lower'])
    k_rec = Q(asm['kappa'])
    red = reduce_endpoint(b, c)
    k, margin = red['kappa'], red['margin']

    # F1: the recorded headline equals the strict grid floor of the margin.
    assert k == k_rec, 'recomputed kappa differs from recorded'
    assert q_from_decimal_string(asm['kappa_decimal']) == k_rec
    assert q_from_decimal_string(asm['complex_decimal']) == b
    assert q_from_decimal_string(asm['bit_decimal']) == c
    assert k < margin < k + TICK, 'kappa is not the unique largest grid point below margin'

    # The transcribed 47 slacks must equal the recorded ones exactly.
    outer, margins = slacks(red['a7'], b, k)
    assert set(outer) == set(asm['outer'])
    for name, val in outer.items():
        assert val == Q(asm['outer'][name]), 'outer slack mismatch: ' + name

    # Bootstrap table recomputation (accepted row).
    assert red['cuts'] == asm['bootstrap'], 'bootstrap table mismatch'

    # F2: kappa + one tick fails on exactly the margins within one tick above
    # the minimum margin: compact_phase_layer (the minimum itself) and the
    # guard-cluster balanced_prefix (+eta), Gaussian_arithmetic (+3eta/8),
    # scalar_work (+7eta/8). No other strict slack turns non-positive.
    outer_next, margins_next = slacks(red['a7'], b, k + TICK)
    failing = sorted(n for n, v in outer_next.items() if v <= 0)
    assert failing == ['Gaussian_arithmetic_above_kappa', 'balanced_prefix_above_kappa',
                       'compact_phase_layer_above_kappa', 'scalar_work_above_kappa'], failing
    minimum = min(margins_next.values())
    cluster = {n: m - minimum for n, m in margins_next.items() if m - minimum < TICK}
    assert sorted(n + '_above_kappa' for n in cluster) == failing
    assert max(cluster.values()) < TICK, 'guard cluster exceeds one tick'
    outer_prev, _ = slacks(red['a7'], b, k - TICK)
    assert all(v > 0 for v in outer_prev.values()), 'kappa - one tick should stay admitted'

    # F3: the whole accepted-over-conservative increment is the surcharge removal.
    cb = Q(asm['conservative_complex_lower'])
    ck_rec = Q(asm['conservative_kappa'])
    cred = reduce_endpoint(cb, c)
    assert cred['kappa'] == ck_rec, 'recomputed conservative kappa differs'
    assert q_from_decimal_string(asm['conservative_kappa_decimal']) == ck_rec
    assert cred['cuts'] == asm['conservative_bootstrap'], 'conservative bootstrap mismatch'
    couter, _ = slacks(cred['a7'], cb, ck_rec)
    for name, val in couter.items():
        assert val == Q(asm['conservative_outer'][name]), 'conservative slack mismatch: ' + name
    gain = k - ck_rec
    assert gain == Q(2881809, 10**18), 'conservative-to-accepted gap changed'
    assert gain == q_from_decimal_string(asm['native_correction_gain'])
    assert asm['surcharge_model'] == {'complex': False, 'bit': True}

    # F4: exact guard cost, guards -> 0 (headroom only: eta, beta must stay > 0
    # for the strict outer set, so this is an upper envelope, not a witness).
    ideal = reduce_endpoint(b, c, eta=Q(0), beta=Q(0), sfloor=Q(0))
    assert ideal['margin'] > margin and ideal['kappa'] >= k

    return {'kappa': k, 'margin': margin, 'margin_over_kappa': margin - k,
            'next_tick_over_margin': k + TICK - margin, 's': red['s'], 'a7': red['a7'],
            'bit_binds': red['bit_binds'], 'endpoint_slack': red['endpoint_slack'],
            'conservative_kappa': ck_rec, 'gain': gain,
            'endpoint_gain': b - cb, 'transfer': gain / (b - cb),
            'guard_cap_cost': ideal['margin'] - margin,
            'guard_grid_cost': ideal['kappa'] - k,
            'cluster': sorted(cluster.items()),
            'tightest': sorted(((v, n) for n, v in outer.items()))[:5],
            'cutoff_log2': [cut['cutoff_log2'] for cut in red['cuts']]}


def controls():
    """Negative controls: each tampered record must fail the audit identities."""
    asm = json.loads(ASSEMBLY.read_text())
    for label, mutate in [
        ('next_tick', lambda d: d.__setitem__('kappa', str(Q(d['kappa']) + Q(1, 10**18)))),
        ('gain_tamper', lambda d: d.__setitem__('native_correction_gain', '2.88181E-12')),
        ('endpoint_swap', lambda d: (d.__setitem__('complex_lower', d['bit_lower']),
                                     d.__setitem__('bit_lower', '1/2'))),
        ('slack_tamper', lambda d: d['outer'].__setitem__('bit_positive', '1/1000000000000000000')),
    ]:
        bad = json.loads(json.dumps(asm))
        mutate(bad)
        try:
            check(bad)
        except AssertionError:
            pass
        else:
            raise AssertionError('negative control not detected: ' + label)
    # Upward rounding would pick the next tick here and violate the
    # compact-phase-layer margin; the strict floor must not.
    red = reduce_endpoint(Q(asm['complex_lower']), Q(asm['bit_lower']))
    upward = red['kappa'] + TICK   # margin - kappa = 7.58e-20 < half a tick
    assert red['margin'] - red['kappa'] < TICK / 2
    assert slacks(red['a7'], Q(asm['complex_lower']), upward)[0]['compact_phase_layer_above_kappa'] <= 0
    return 4


def main():
    assert __debug__, 'Do not run with python -O'
    asm = json.loads(ASSEMBLY.read_text())
    rep = check(asm)
    n = controls()
    print('PASS endpoint-to-kappa reduction audit (seed 67)')
    print('  kappa                        =', asm['kappa'])
    print('  margin - kappa               = %.6e' % float(rep['margin_over_kappa']))
    print('  (kappa + 1e-18) - margin     = %.6e' % float(rep['next_tick_over_margin']))
    print('  binding endpoint             =', 'bit' if rep['bit_binds'] else 'complex')
    print('  endpoint slack c-(1-beta)b   = %.6e' % float(rep['endpoint_slack']))
    print('  conservative -> accepted gap =', rep['gain'], '(=%.6e)' % float(rep['gain']))
    print('  endpoint gap b - b_c         = %.6e' % float(rep['endpoint_gain']))
    print('  transfer factor              = %.12f' % float(rep['transfer']))
    print('  guard cap cost (guards->0)   = %.6e' % float(rep['guard_cap_cost']))
    print('  guard grid cost              = %s' % rep['guard_grid_cost'])
    print('  tightest outer slacks        =', [(n, '%.3e' % float(v)) for v, n in rep['tightest']])
    print('  margin cluster above minimum =', [(n, '%.3e' % float(v)) for n, v in rep['cluster']])
    print('  bootstrap cutoff_log2        =', rep['cutoff_log2'])
    print('  negative controls detected   = %d' % n)


if __name__ == '__main__':
    main()
