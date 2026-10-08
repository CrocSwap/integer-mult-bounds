#!/usr/bin/env python3
"""Scoped screen for affine point-incidence centers; no new multiplication claim.

Run from any directory. The general span proof is in
  docs/research/bit-breakthrough.md.
Modular ranks below are lower bounds over Q, paired with exact rational
annihilators/ambient upper bounds. Numerical displays are not used in proofs.
"""
from fractions import Fraction as Q
from itertools import combinations
from math import comb
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from search_network import log_integer_bounds, log_ratio_bounds


def modular_rank(rows, prime=1000003, stop_at=None):
    basis = {}
    for row in rows:
        row = [x % prime for x in row]
        for pivot in sorted(basis):
            if row[pivot]:
                factor = row[pivot]
                row = [(x-factor*y) % prime for x, y in zip(row, basis[pivot])]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is not None:
            inverse = pow(row[pivot], prime-2, prime)
            basis[pivot] = [x*inverse % prime for x in row]
            if len(basis) == stop_at:
                return len(basis)
    return len(basis)


def predicate_span(h, mask):
    """Return exact predicted rank and a rational normal for a hyperplane.

    c + sum_{i in T} a_i equals the predicate for mask a XOR c*[h],
    because triples have odd size. Thus masks cover all affine predicates.
    """
    assert h >= 6 and 0 <= mask < (1 << h)
    selected = [i for i in range(h) if mask >> i & 1]
    omitted = [i for i in range(h) if not mask >> i & 1]
    if not selected:
        return 0, None
    if len(selected) in (1, 2):
        return h-1, tuple(3*int(i in selected)-1 for i in range(h))
    if len(omitted) == 1:
        return h-1, tuple(int(i == omitted[0]) for i in range(h))
    if len(omitted) == 2:
        return h-1, tuple(int(i == omitted[0])-int(i == omitted[1]) for i in range(h))
    return h, None


def span_controls():
    exhaustive = 0
    for h in range(6, 10):
        triples = list(combinations(range(h), 3))
        vectors = [tuple(int(i in triple) for i in range(h)) for triple in triples]
        for mask in range(1 << h):
            support = [row for triple, row in zip(triples, vectors)
                       if sum(mask >> i & 1 for i in triple) % 2]
            expected, normal = predicate_span(h, mask)
            assert modular_rank(support) == expected
            if normal is not None:
                assert any(normal)
                assert all(sum(x*y for x, y in zip(normal, row)) == 0 for row in support)
            exhaustive += 1
        # Full column rank of Q proves rank(Q Q^t)=h over F2.
        assert modular_rank(vectors, prime=2) == h
    # Larger exact integer controls include every orbit of point masks.
    orbit_controls = 0
    for h in (10, 11, 24, 38, 48, 50):
        triples = list(combinations(range(h), 3))
        for weight in range(h+1):
            mask = (1 << weight)-1
            expected, normal = predicate_span(h, mask)
            # Keep only enough rows to find the lower bound. Every row remains
            # an exact triple indicator; modular full rank implies rational rank.
            rows = (tuple(int(i in triple) for i in range(h))
                    for triple in triples if sum(i < weight for i in triple) % 2)
            assert modular_rank(rows, stop_at=expected) == expected
            if normal is not None:
                assert all(sum(normal[i] for i in triple) == 0 for triple in triples
                           if sum(i < weight for i in triple) % 2)
            orbit_controls += 1
    return dict(exhaustive_masks=exhaustive, larger_mask_orbits=orbit_controls,
                all_modular_lower_bounds_meet_exact_upper_bounds=True)


def optimistic_saving_bounds(h):
    """Grant R=v and loss=h(h-2), below any construction in the scoped class."""
    v = comb(h, 3)
    deficit_per_invocation = v-6*h*(h-2)
    if deficit_per_invocation <= 0:
        return None
    eta = Q(deficit_per_invocation, 4*h**3*v)
    num_lo, num_hi = log_ratio_bounds(1/(1-eta), terms=3)
    den_lo, den_hi = log_integer_bounds(h**3)
    return num_lo/den_hi, num_hi/den_lo, eta


def ceiling():
    rows = {h: optimistic_saving_bounds(h) for h in range(11, 200)}
    rows = {h: value for h, value in rows.items() if value is not None}
    winner = max(rows, key=lambda h: rows[h][0])
    lower, upper, eta = rows[winner]
    assert winner == 48
    assert all(value[1] < lower for h, value in rows.items() if h != winner)
    # eta < 1/(4h^3), -log(1-eta)<eta/(1-eta), log(h^3)>1.
    tail_upper = Q(1, 4*200**3-1)
    assert tail_upper < lower
    simple_kappa_upper = Q(22778, 10**12)
    assert upper/2 < simple_kappa_upper
    current = Q(1624, 10**12)
    assert simple_kappa_upper/current < Q(14027, 1000)
    return dict(status='SCOPED UPPER BOUND ONLY; NO NEW WITNESS',
                scope='Canonical B=Q Q^t over F2; affine point-incidence gather '
                      'and scatter supports; one gather/scatter passage per center; '
                      'source-span/complement frames; whole invocation factors '
                      'through R auxiliary roles; unchanged three-stage counts '
                      'and fast-Gaussian kappa<a_b/2 comparison.',
                smallest_positive_h=min(rows), optimistic_best_h=winner,
                optimistic_eta=str(eta),
                primitive_saving_lower=str(lower),
                primitive_saving_upper=str(upper),
                logarithmic_kappa_upper=str(upper/2),
                finite_candidates=len(rows),
                center_loss_floor_at_best=winner*(winner-2),
                auxiliary_role_floor_at_best=comb(winner, 3),
                kappa_upper=str(simple_kappa_upper),
                improvement_factor_upper=str(simple_kappa_upper/current),
                tail_start=200, tail_primitive_saving_upper=str(tail_upper),
                limitations='Nonlinear triple predicates, changed side correction, '
                            'interleaved centers, changed frames or tensor stages '
                            'are outside this screen.')


def certificate():
    return dict(controls=span_controls(), ceiling=ceiling())


if __name__ == '__main__':
    result = certificate()
    (ROOT / 'certificates/affine-center-targets.json').write_text(
        json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('PASS affine-center screen; no new kappa')
    print('Optimistic best h', result['ceiling']['optimistic_best_h'],
          'kappa <', result['ceiling']['kappa_upper'],
          'factor <', result['ceiling']['improvement_factor_upper'])
