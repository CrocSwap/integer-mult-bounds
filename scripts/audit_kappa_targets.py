#!/usr/bin/env python3
"""Optimistic ceilings that distinguish new-network targets from circuit tuning.

These are upper bounds for explicitly retained contracts, not constructions
or new multiplication witnesses. All numerical comparisons use rationals.
"""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json

from aligned_bit_network import KAPPA
from certify import require
from prepare_layers import serializable
from search_network import log_integer_bounds, log_ratio_bounds

ROOT = Path(__file__).resolve().parents[1]


def optimistic_eta(h, keep_outputs=False):
    """Retain aligned centers; discard every charge except the selected floor.

    W >= 2N, or W >= 2N+2v^2(3v+h) with the current designated-output
    compiler. Retain D=N-6v^2*h*(h-1), m=h^3 and three tensor stages.
    """
    require(h >= 39, 'Retained centers require h >= 39 for a positive deficit')
    v = comb(h, 3)
    roles = 3*v+h if keep_outputs else 0
    return Q(v-6*h*(h-1), 2*h**3*(v+roles))


def saving_enclosure(eta, m):
    require(0 < eta < Q(1, 2), 'Expected a positive deficit below one half')
    lo, hi = log_ratio_bounds(1/(1-eta), terms=4)
    log_lo, log_hi = log_integer_bounds(m)
    return lo/log_hi, hi/log_lo


def family_ceiling(keep_outputs=False, cutoff=200):
    require(cutoff >= 200, 'Tail cutoff must cover the stated finite search')
    bounds = {h: saving_enclosure(optimistic_eta(h, keep_outputs), h**3)
              for h in range(39, cutoff)}
    best = max(bounds, key=lambda h: bounds[h][0])
    lo, hi = bounds[best]
    require(all(lo > interval[1] for h, interval in bounds.items() if h != best),
            'Unique optimistic maximizer not separated')
    # eta < 1/(2*h^3), -log(1-eta) < eta/(1-eta), and log(h^3)
    # increases. This upper bound decreases for all h >= cutoff.
    log_lo, _ = log_integer_bounds(cutoff**3)
    tail = 1/((2*cutoff**3-1)*log_lo)
    require(tail < lo, 'Infinite tail not excluded')
    ceiling = hi/2  # g3 < epsilon*a, g4 = (1-epsilon)*a
    return dict(keep_designated_outputs=keep_outputs, optimistic_best_h=best,
                eta_at_best=optimistic_eta(best, keep_outputs),
                bit_saving_lower=lo, bit_saving_upper=hi,
                kappa_upper=ceiling, factor_over_baseline_upper=ceiling/KAPPA,
                tail_start=cutoff, tail_bit_saving_upper=tail,
                finite_candidates=len(bounds),
                scope=('Three tensor stages, full triple family, aligned central loss, '
                       'the retained negative-source charge and assembly. '
                       + ('Also retains q=3v+h designated outputs and the c+q compiler.'
                          if keep_outputs else 'Every auxiliary role is optimistically free.')))


def data_floor_kappa_upper(m):
    """Zero-loss, zero-scratch bound for the retained rank-one terminal scheme.

    D <= N and W >= 2N give eta <= 1/(2m). The true recurrence saving
    is at most -log(1-1/(2m))/log(m), and kappa is below half that saving.
    """
    require(m >= 2, 'Nontrivial recurrence arity required')
    _, hi = saving_enclosure(Q(1, 2*m), m)
    return hi/2


def excluded_arity_threshold(target):
    """An exact necessary arity bound, assuming the retained terminal scheme.

    The analytic bound decreases in m. Return the first integer m whose
    rational upper enclosure is <= target; every m at least this large
    is excluded. The preceding integer passes this optimistic screen only.
    """
    require(0 < target < data_floor_kappa_upper(2), 'Unsupported target')
    low, high = 2, 4
    while data_floor_kappa_upper(high) > target:
        low, high = high, 2*high
    while high-low > 1:
        mid = (low+high)//2
        if data_floor_kappa_upper(mid) <= target:
            high = mid
        else:
            low = mid
    # Use the exact lower enclosure as well at the boundary, so series slack
    # cannot move the first excluded integer in this certificate.
    lower, _ = saving_enclosure(Q(1, 2*low), low)
    require(lower/2 > target, 'Threshold boundary needs a tighter enclosure')
    return dict(target_kappa=target, first_excluded_m=high,
                necessary_m_at_most=high-1,
                upper_at_first_excluded=data_floor_kappa_upper(high),
                scope='Necessary only; even the optimistic smaller arities need a new valid network.')


def certificate():
    free = family_ceiling()
    outputs = family_ceiling(keep_outputs=True)
    require(free['kappa_upper'] < 27*KAPPA, 'Free-scratch ceiling changed')
    require(outputs['kappa_upper'] < 7*KAPPA, 'Output-floor ceiling changed')
    return dict(status='SCOPED UPPER BOUNDS AND NECESSARY TARGETS; NO NEW KAPPA',
                baseline_kappa=KAPPA,
                free_scratch=free, retained_output_compiler=outputs,
                targets={str(factor)+'x': excluded_arity_threshold(factor*KAPPA)
                         for factor in (10, 100, 1000, 10000)},
                distinction='Optimistic ceilings discard real costs. They neither supply circuits '
                            'nor exclude different terminal frames, scalar topologies or assemblies.')


if __name__ == '__main__':
    result = certificate()
    (ROOT/'certificates/kappa-targets.json').write_text(
        json.dumps(serializable(result), indent=2, sort_keys=True)+'\n')
    print('PASS scoped ceilings; no new kappa')
    for name in ('free_scratch', 'retained_output_compiler'):
        row = result[name]
        print(name, 'best h', row['optimistic_best_h'],
              'kappa <', float(row['kappa_upper']),
              'factor <', float(row['factor_over_baseline_upper']))
    for name, row in result['targets'].items():
        print(name, 'requires m <=', row['necessary_m_at_most'])
