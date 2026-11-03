"""Rational Euclidean guards for complete orthogonal register programs.

This contribution was produced by Nick Petalas. Apache-2.0.
The complete grammar and coarse separator are credited in PROOF.md.
"""

from dataclasses import dataclass
from fractions import Fraction as Q
from math import isqrt


@dataclass(frozen=True)
class Step:
    op: str
    dst: int
    src: int = 0
    label: int = 0
    direction: int = 1
    coefficient: Q = Q(1)
    terms: tuple = ()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def scalar(value):
    need(type(value) in (int, Q), "exact scalar required")
    result = Q(value)
    need(max(abs(result.numerator).bit_length(), result.denominator.bit_length()) <= 128,
         "scalar capacity exceeded")
    return result


def validate(program, dimension, roles, labels):
    need(type(dimension) is int and 1 <= dimension <= 16, "dimension capacity")
    need(type(roles) is int and 1 <= roles <= 4, "role capacity")
    need(type(labels) is int and 1 <= labels <= 3, "operator capacity")
    need(type(program) is tuple and len(program) == 2, "two program sides required")
    for side in program:
        need(type(side) is tuple and len(side) <= 64, "instruction capacity")
        for step in side:
            need(type(step) is Step and step.op in ("apply", "query", "linear"),
                 "invalid instruction")
            need(type(step.dst) is int and 0 <= step.dst < roles, "invalid destination")
            if step.op == "linear":
                need(type(step.terms) is tuple and len(step.terms) <= 8, "term capacity")
                for term in step.terms:
                    need(type(term) is tuple and len(term) == 2, "invalid scalar term")
                    source, coefficient = term
                    need(type(source) is int and 0 <= source < roles, "invalid term role")
                    scalar(coefficient)
            else:
                need(type(step.label) is int and 0 <= step.label < labels, "invalid operator")
                need(type(step.direction) is int and step.direction in (-1, 1), "invalid inverse")
                if step.op == "query":
                    need(type(step.src) is int and 0 <= step.src < roles, "invalid source")
                    scalar(step.coefficient)


def coefficients(step):
    if step.op == "linear":
        return tuple(Q(value) for _, value in step.terms)
    if step.op == "query":
        return (Q(step.coefficient),)
    return ()


def instruction_bounds(step, dimension):
    if step.op == "linear":
        return max(Q(1), sum(map(abs, coefficients(step)), Q(0))), Q(0)
    if step.op == "apply":
        return Q(1), Q(dimension)
    amount = abs(Q(step.coefficient))
    return 1 + amount, dimension * amount


def side_statistics(side, dimension, radius):
    gain, sensitivity = Q(1), Q(0)
    for step in side:
        beta, gamma = instruction_bounds(step, dimension)
        gain *= beta
        sensitivity += gamma / beta
    coordinate_radius = isqrt(dimension - 1) + 1
    credit = gain * (radius * sensitivity + coordinate_radius * len(side))
    return gain, sensitivity, credit


def ceil_log2(value):
    need(value > 0, "positive precision requirement")
    bits = max(0, value.numerator.bit_length() - value.denominator.bit_length())
    return bits + int(Q(1 << bits) < value)


def allocate(program, dimension, roles, labels, parameter, radius=Q(1)):
    """Fund the cited Cayley separator for integer initial banks of norm <= radius.

    Matching exact Cayley operators are a caller premise, as in PR5339.
    Nongrid input errors and noninteger-input separation are not supplied.
    """
    validate(program, dimension, roles, labels)
    parameter, radius = scalar(parameter), scalar(radius)
    need(0 < parameter <= Q(1, 4), "Cayley parameter outside contract")
    need(radius >= 1, "input radius must be at least one")
    denominator, calls, old_gain, old_gamma = 1, 0, Q(1), Q(0)
    for side in program:
        for step in side:
            beta, gamma = instruction_bounds(step, dimension)
            if step.op != "linear":
                calls += 1
                beta = Q(dimension) if step.op == "apply" else 1 + gamma
            old_gain *= beta
            old_gamma = max(old_gamma, gamma)
            for value in coefficients(step):
                denominator *= value.denominator
    separator_denominator = denominator * (3 * parameter.denominator) ** (dimension * calls)
    eta = Q(1, separator_denominator)
    statistics = tuple(side_statistics(side, dimension, radius) for side in program)
    sensitivity = max(row[1] for row in statistics)
    credit = sum((row[2] for row in statistics), Q(0))
    requirement = max(Q(1), 2 * sensitivity, 8 * credit / eta)
    bits = ceil_log2(requirement)
    old_error = sum(map(len, program)) * old_gain * (old_gamma * radius * old_gain + 1)
    old_bits = ceil_log2(4 * max(Q(1), old_error) / eta)
    error = 2 * credit / (1 << bits)
    need(sensitivity / (1 << bits) <= Q(1, 2) and error <= eta / 4,
         "unfunded Euclidean guard")
    return dict(bits=bits, old_bits=old_bits, eta=eta, error=error,
                radius=radius, statistics=statistics, calls=calls,
                steps=sum(map(len, program)), scalar_denominator=denominator)


def prefix_error(side, dimension, radius, bits):
    gain, sensitivity, credit = side_statistics(side, dimension, radius)
    del gain  # The complete credit already includes this factor.
    h = Q(1, 1 << bits)
    need(h * sensitivity < 1, "rounding sensitivity is not funded")
    return h * credit / (1 - h * sensitivity)
