#!/usr/bin/env python3
"""Exact optimistic exclusion of higher odd full-subset polynomial labels.

This is a scoped obstruction, not a construction or multiplication certificate.
It allows zero auxiliary roles, but retains three tensor factors and the h
point centers, with each center losing only its source-span dimension.
See docs/research/label-breakthrough.md for the infinite-family argument.
"""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from search_network import log_integer_bounds, log_ratio_bounds
from prepare_layers import serializable


BASELINE_BIT_SAVING = Q(325, 10**11)
BASELINE_KAPPA = Q(1624, 10**12)
RANK_TAIL = 275
GLOBAL_BIT_UPPER = Q(1, 16 * (2 * RANK_TAIL**3 - 1))


def harmonic_dimension(h, t):
    return comb(h, t) - comb(h, t - 1)


def optimistic_case(h, t):
    k = 2 * t + 1
    assert t >= 2 and h >= 2 * k
    v = comb(h, k)
    r = harmonic_dimension(h, t)
    rho = harmonic_dimension(h - 1, t)
    numerator = v - 6 * h * rho
    result = dict(h=h, k=k, vertices=v, ambient_rank_lower=r,
                  star_rank_lower=rho, deficit_numerator_upper=numerator)
    if numerator <= 0:
        result['positive_deficit_possible'] = False
        return result
    eta = Q(numerator, 2 * v * r**3)
    ln_lo, ln_hi = log_ratio_bounds(1 / (1 - eta), terms=3)
    lm_lo, lm_hi = log_integer_bounds(r**3)
    result.update(positive_deficit_possible=True, optimistic_eta=eta,
                  optimistic_saving_lower=ln_lo/lm_hi,
                  optimistic_saving_upper=ln_hi/lm_lo)
    return result


def audit():
    # A rank >= 275 alone excludes the current saving, even with zero losses.
    assert log_integer_bounds(RANK_TAIL**3)[0] > 16
    assert GLOBAL_BIT_UPPER < BASELINE_BIT_SAVING
    assert GLOBAL_BIT_UPPER / 2 < BASELINE_KAPPA

    # These are exactly the admissible (h,t) with d_t(h) < 275:
    # t=2, h=10,...,24; and t=3,h=14. For t>=4 the minimum
    # d_t(4t+2) is at least d_4(18)=2244 and increases with t.
    cases = [optimistic_case(h, 2) for h in range(10, 25)]
    cases.append(optimistic_case(14, 3))
    assert all(c['ambient_rank_lower'] < RANK_TAIL for c in cases)
    assert harmonic_dimension(25, 2) == RANK_TAIL
    assert harmonic_dimension(15, 3) > RANK_TAIL
    assert harmonic_dimension(18, 4) == 2244
    positive = [c for c in cases if c['positive_deficit_possible']]
    assert [c['h'] for c in positive] == [22, 23, 24]
    assert all(c['optimistic_saving_upper'] < GLOBAL_BIT_UPPER
               for c in positive)
    return dict(
        status='SCOPED OBSTRUCTION; NO NEW MULTIPLICATION WITNESS',
        scope='Full k-subsets, odd k>=5, h>=2k; canonical degree-(k-1)/2 '
              'rational intersection polynomial; three tensor stages; '
              'h point centers returned through zero; arbitrary side circuit.',
        optimistic_relaxation='All auxiliary roles are free; center loss '
                              'uses only a lower bound for its source span.',
        bit_saving_strict_upper=GLOBAL_BIT_UPPER,
        kappa_strict_upper=GLOBAL_BIT_UPPER/2,
        current_bit_saving=BASELINE_BIT_SAVING,
        current_kappa=BASELINE_KAPPA,
        ambient_rank_tail_start=RANK_TAIL,
        finite_small_rank_cases=cases)


if __name__ == '__main__':
    result = audit()
    output = Path(__file__).resolve().parents[2]/'certificates/polynomial-label-targets.json'
    output.write_text(json.dumps(serializable(result), indent=2, sort_keys=True)+'\n')
    print('PASS scoped polynomial-label obstruction; no new kappa')
    print('bit saving <', float(result['bit_saving_strict_upper']),
          'kappa <', float(result['kappa_strict_upper']))
