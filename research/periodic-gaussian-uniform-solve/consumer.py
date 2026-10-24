"""Bind the narrow periodic Gaussian Reference to a cyclic direct solve.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Source and classical solver credit is in README.md and SOURCES.json.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'vendor'))
from solver import factor, solve, trunc, need


def dyadic_gap(gap):
    gap = Q(gap)
    need(0 < gap <= 1, 'positive source gap at most one required')
    bits = 0
    while Q(1, 1 << bits) > gap:
        bits += 1
    return Q(1, 1 << bits)


@dataclass(frozen=True)
class Prepared:
    source_hash: str
    selected: tuple
    holes: tuple
    period: int
    bits: int
    coefficient_bits: int
    radius: Q
    gap: Q
    error_terms: tuple
    factors: dict
    source_requests: int


def prepare(reference, target=20, radius=1, boundary_bits=None):
    need(type(target) is int and target >= 1 and type(radius) in (int, Q) and radius > 0,
         'positive target and rational radius required')
    boundary_bits = target + 3 if boundary_bits is None else boundary_bits
    need(type(boundary_bits) is int and boundary_bits >= target + 3, 'output grid is not funded')
    d = dyadic_gap(reference.narrow_gap)
    epsilon, radius = Q(1, 1 << target), Q(radius)
    error = reference.errors['narrow']
    need(0 <= error < d, 'analytic reference error exceeds gap')
    analytic = radius * error / (d * (d-error))
    need(analytic <= epsilon/4, 'analytic error is not funded')
    n, width = reference.spec.source_size, reference.spec.source_halfwidth
    count = 2*width
    p = boundary_bits
    while radius*count*Q(1, 1 << p)/d**2 > epsilon/4:
        p += 1
    selected = tuple(reference.selected)
    need(len(selected) == n and len(set(selected)) == n, 'selected coordinates must be distinct')
    holes = tuple(reference.holes)
    need(set(selected).isdisjoint(holes) and set(selected) | set(holes) == set(range(reference.target_size)),
         'complete coordinate partition required')
    rows, requests = [], 0
    for i, row in enumerate(selected):
        coefficients, mass = {}, Q(0)
        for h in range(-width, width+1):
            j = (i+h) % n
            value = reference.entry('narrow', row, selected[j]).value
            requests += 1
            need(value >= 0, 'source entries must be nonnegative')
            if i == j:
                need(value == 1, 'source diagonal must be one')
            else:
                mass += value
            coefficients[j] = value.numerator * (1 << p) // value.denominator
        need(mass <= 1-d, 'literal source row gap failed')
        rows.append(coefficients)
    for row in holes:
        need(reference.entry('narrow', row, row).value == 1, 'hole diagonal must be one')
        requests += 1
    factors = factor(rows, p, width, d, 2-d, radius, epsilon/4)
    coefficient = radius*count*Q(1, 1 << p)/d**2
    output = Q(2, 1 << boundary_bits)
    terms = (analytic, coefficient, factors['plan']['error'], output)
    need(sum(terms) <= epsilon, 'complete error budget failed')
    return Prepared(reference.description_hash, selected, holes, reference.target_size,
                    boundary_bits, p, radius, d, terms, factors, requests)


def execute(prepared, data):
    """Use an unchanged Prepared object returned by prepare and borrow data."""
    p = prepared
    need(type(data) is tuple and len(data) == p.period and all(
        type(z) is tuple and len(z) == 2 and all(type(x) is int for x in z)
        and sum(abs(x) for x in z) <= p.radius*(1 << p.bits) for z in data),
        'immutable complex grid input and radius required')
    gathered = tuple(data[j] for j in p.selected)
    answer, bill = solve(p.factors, gathered, p.bits)
    shift = p.factors['plan']['bits']-p.bits
    output = list(data)
    try:
        for j, z in zip(p.selected, answer):
            output[j] = tuple(trunc(x, 1 << shift) for x in z)
        result = tuple(output)
        bill.update(target_input_components=2*p.period, target_output_components=2*p.period,
                    gather_components=2*len(p.selected), scatter_components=2*len(p.selected),
                    output_roundings=2*len(p.selected), hole_copy_components=2*len(p.holes),
                    answer_clear_components=2*len(p.selected), staging_clear_components=2*p.period)
        return result, bill
    finally:
        for z in answer:
            z[:] = [0, 0]
        for j in range(len(output)):
            output[j] = (0, 0)
