#!/usr/bin/env python3
"""Small exact path-rank controls independent of all elimination routines.

Copyright 2026 Curtis Dransfield. Apache-2.0.
Prepared with substantial OpenAI Codex assistance. The audited historical
contracts retain Douglas Colkitt's authorship and Codex assistance disclosure.

This module imports neither the package's linear algebra nor repository rank
code. The bounded enumeration uses the explicit 2-by-2 determinant; exported
rank_by_minors uses permutation determinants and applies only to dimensions
at most three. Finite replay is not a proof of the unrestricted identity.
"""
from collections import Counter
from fractions import Fraction
from itertools import combinations, permutations, product
import json


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _rational(value):
    _require(type(value) in (int, str, Fraction), 'Use exact rational entries')
    return Fraction(value)


def _determinant(matrix):
    """Leibniz formula; no row reduction or division by pivots."""
    size = len(matrix)
    total = Fraction(0)
    for permutation in permutations(range(size)):
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(size) for j in range(i + 1, size))
        term = Fraction(-1 if inversions % 2 else 1)
        for i, j in enumerate(permutation):
            term *= matrix[i][j]
        total += term
    return total


def rank_by_minors(matrix):
    """Exact rank of a rectangular rational matrix with both dimensions <= 3.

    Enumerate square minors in descending size and return the first size
    having a nonzero permutation determinant. An empty matrix has rank zero.
    """
    rows = tuple(tuple(_rational(x) for x in row) for row in matrix)
    height = len(rows)
    width = len(rows[0]) if height else 0
    _require(height <= 3 and width <= 3, 'Independent minors budget is at most 3 by 3')
    _require(all(len(row) == width for row in rows), 'Ragged matrix')
    for size in range(min(height, width), 0, -1):
        for selected_rows in combinations(range(height), size):
            for selected_columns in combinations(range(width), size):
                minor = tuple(tuple(rows[i][j] for j in selected_columns)
                              for i in selected_rows)
                if _determinant(minor):
                    return size
    return 0


IDENTITY = (1, 0, 0, 1)
ZERO = (0, 0, 0, 0)


def _multiply(left, right):
    a, b, c, d = left
    e, f, g, h = right
    return a*e + b*g, a*f + b*h, c*e + d*g, c*f + d*h


def _rank_two(matrix):
    a, b, c, d = matrix
    return 2 if a*d - b*c else int(any(matrix))


def _subtract(left, right):
    return tuple(a - b for a, b in zip(left, right))


def _transpose(matrix):
    a, b, c, d = matrix
    return a, c, b, d


def _nested(matrix):
    def encode(x):
        q = Fraction(x)
        return q.numerator if q.denominator == 1 else str(q)
    return [[encode(matrix[0]), encode(matrix[1])],
            [encode(matrix[2]), encode(matrix[3])]]


def _profile(p, q):
    pq, qp = _multiply(p, q), _multiply(q, p)
    difference = _subtract(_subtract(IDENTITY, p), q)
    ranks = dict(p=_rank_two(p), q=_rank_two(q), pq=_rank_two(pq),
                 qp=_rank_two(qp), difference=_rank_two(difference))
    signed = _rank_two(_subtract(IDENTITY, q)) - ranks['p']
    return dict(P=_nested(p), Q=_nested(q), ranks=ranks,
                signed_rank_change=signed,
                direct_edge_excess=ranks['difference'] - signed)


def independent_check():
    assignment_seed = 71
    radius = assignment_seed % 4
    entries = range(-radius, radius + 1)
    labels = [p for p in product(entries, repeat=4) if _multiply(p, p) == p]
    histogram = Counter()
    checked_pairs = 0
    for p, q in product(labels, repeat=2):
        pq, qp = _multiply(p, q), _multiply(q, p)
        difference = _subtract(_subtract(IDENTITY, p), q)
        product_ranks = _rank_two(pq), _rank_two(qp)
        expected = 2 - _rank_two(p) - _rank_two(q) + sum(product_ranks)
        _require(_rank_two(difference) == expected, 'Idempotent rank identity failed')
        histogram[product_ranks] += 1
        checked_pairs += 1
    _require(len(labels) == 44 and checked_pairs == 1936,
             'Unexpected exhaustive-domain coverage')

    p = (1, 0, 0, 0)
    q = (0, 1, 0, 1)
    forward, backward = _profile(p, q), _profile(q, p)
    _require(forward['direct_edge_excess'] == backward['direct_edge_excess'] == 1,
             'One-sided-product counterexample changed')
    _require(forward['direct_edge_excess'] < 2*forward['ranks']['pq'],
             'Two-rank-PQ false lower bound was not refuted')
    _require(backward['direct_edge_excess'] < 2*backward['ranks']['qp'],
             'Two-rank-QP false lower bound was not refuted')

    half_identity = (Fraction(1, 2), 0, 0, Fraction(1, 2))
    non_idempotent = _profile(half_identity, half_identity)
    _require(_multiply(half_identity, half_identity) != half_identity,
             'Non-idempotent control became idempotent')
    false_rhs = (2 - non_idempotent['ranks']['p'] - non_idempotent['ranks']['q']
                 + non_idempotent['ranks']['pq'] + non_idempotent['ranks']['qp'])
    _require(non_idempotent['ranks']['difference'] == 0 and false_rhs == 2,
             'Dropping idempotence was not refuted')
    non_idempotent['invalid_identity_rhs'] = false_rhs

    # Equal product ranks are necessary, not sufficient, for a common
    # nondegenerate symmetric form. Derive the homogeneous equations in
    # H = [[a,b],[b,c]] for the repository's existing rank-one example.
    nonsymmetric_q = (1, 1, 0, 0)
    h_basis = ((1, 0, 0, 0), (0, 1, 1, 0), (0, 0, 0, 1))
    equations = set()
    for projector in (p, nonsymmetric_q):
        coefficients = [_subtract(_multiply(h, projector),
                                  _multiply(_transpose(projector), h)) for h in h_basis]
        for entry in range(4):
            row = tuple(coefficient[entry] for coefficient in coefficients)
            if any(row):
                first = next(x for x in row if x)
                equations.add(tuple(Fraction(x, first) for x in row))
    _require(equations == {(Fraction(1), Fraction(-1), Fraction(0)),
                           (Fraction(0), Fraction(1), Fraction(0))},
             'Common-form converse control changed')
    converse = _profile(p, nonsymmetric_q)
    _require(converse['ranks']['pq'] == converse['ranks']['qp'] == 1,
             'Converse control lost equal product ranks')
    converse.update(symmetric_form_equations=['H_00 - H_01 = 0', 'H_01 = 0'],
                    common_nondegenerate_symmetric_form_exists=False)

    # A common additive matrix cancels from a difference but need not
    # preserve endpoint-rank additivity. B=-P, Q=P gives endpoints 0,I-2P.
    shared_b = tuple(-x for x in p)
    source = tuple(x + y for x, y in zip(shared_b, p))
    target = tuple(b + identity - x for b, identity, x in zip(shared_b, IDENTITY, p))
    charge = _rank_two(_subtract(target, source))
    signed = _rank_two(target) - _rank_two(source)
    _require(source == ZERO and charge - signed == 0,
             'Unrestricted additive-block control changed')

    # Cross-check both determinant implementations on the named matrices.
    named_matrices = (p, q, _multiply(p, q), _multiply(q, p), nonsymmetric_q,
                      half_identity, source, target)
    for matrix in named_matrices:
        _require(rank_by_minors(_nested(matrix)) == _rank_two(matrix),
                 'Permutation-minor and explicit determinant ranks differ')

    return dict(
        status='PASS_EXACT_BOUNDED_IDEMPOTENT_PATH_RANK_AUDIT',
        assignment_seed=assignment_seed,
        domain=dict(dimension=2, entries_min=-radius, entries_max=radius,
                    radius_rule='assignment_seed % 4', matrices_examined=(2*radius + 1)**4,
                    idempotents=len(labels), ordered_pairs=checked_pairs,
                    stopping_rule='Exhaust every matrix and every ordered idempotent pair'),
        method='Explicit 2 by 2 determinant; no elimination or imported rank routine',
        product_rank_histogram={f'{a},{b}': count for (a, b), count in sorted(histogram.items())},
        controls=dict(
            false_excess_at_least_two_rank_pq=forward,
            false_excess_at_least_two_rank_qp=backward,
            false_identity_without_idempotence=non_idempotent,
            false_converse_equal_product_ranks_implies_common_form=converse,
            false_unrestricted_shared_additive_block=dict(
                P=_nested(p), Q=_nested(p), B=_nested(shared_b), source=_nested(source),
                target=_nested(target), direct_charge=charge, signed_rank_change=signed,
                actual_excess=charge - signed, incorrectly_transferred_bound=2)),
        scope='Finite independent evidence and explicit counterexamples to stronger statements; '
              'the unrestricted idempotent identity requires the written proof; no new kappa')


if __name__ == '__main__':
    print(json.dumps(independent_check(), indent=2, sort_keys=True))
