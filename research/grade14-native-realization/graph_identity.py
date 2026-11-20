"""Certify both rational transfer matrices by exact signed digit blocks."""

from fractions import Fraction
from math import lcm


def check_matrix(inputs, outputs, order, rows, expectation):
    # Build an integer circuit by assigning one common denominator to each row.
    den = dict.fromkeys(inputs, 1)
    mass = dict.fromkeys(inputs, 1)
    circuit = []
    for target in order:
        weighted = [(source, coeff / den[source]) for source, coeff in rows[target]]
        d = lcm(*(coeff.denominator for _, coeff in weighted))
        factors = [(source, int(d * c)) for source, c in weighted]
        den[target] = d
        mass[target] = sum(abs(c) * mass[source] for source, c in factors)
        circuit.append((target, factors))
    unit = lcm(*(v.denominator for row in expectation for v in row.values()))
    limit = max(
        unit * mass[o] + den[o] * sum(abs(int(unit * c)) for c in row.values())
        for o, row in zip(outputs, expectation, strict=True)
    )
    bits = max(1, limit.bit_length())
    # At this base every coefficient of the difference has absolute value < base.
    # An integer identity then proves every coefficient zero by successive reduction.
    for first in range(0, len(inputs), 64):
        end = min(len(inputs), first + 64)
        values = dict.fromkeys(inputs, 0)
        for i in range(first, end):
            values[inputs[i]] = 1 << (bits * (i - first))
        for target, factors in circuit:
            values[target] = sum(values[s] * c for s, c in factors)
        for o, row in zip(outputs, expectation, strict=True):
            predicted = sum(
                int(unit * c) << (bits * (i - first))
                for i, c in row.items()
                if first <= i < end
            )
            if unit * values[o] != den[o] * predicted:
                raise ValueError("full rational endpoint")
    return bits


def graph_identity(graph, layout):
    n = len(graph["initial"])
    first = graph["first_output"]
    inputs = [~i for i in range(n)]
    outputs = [first + i for i in range(n)]
    moves = {k: (a, b) for k, a, b in graph["moves"]}
    rows = {k: [(s, Fraction(c)) for s, c in row] for k, row in graph["forms"]}
    order = graph["schedule"]
    if (
        len(set(order)) != len(order)
        or set(rows) != set(order)
        or set(order) != moves.keys() | set(outputs)
    ):
        raise ValueError("native producer schedule")
    charts = dict(zip(inputs, graph["initial"], strict=True))
    dual = {k: [] for k in inputs + order}
    for k in order:
        a, b = moves[k] if k in moves else (graph["final"][k - first],) * 2
        for s, c in rows[k]:
            if charts[s] != a:
                raise ValueError("nonlocal scalar operand")
            dual[s].append((k, c))
        charts[k] = b
    wanted = [{i: Fraction(1)} for i in range(n)]
    hosted = set(layout["hosted"]["Dports"])
    for p, x in enumerate(layout["live"]):
        y = x + 112
        if p in hosted:
            wanted[y][x] = Fraction(1)
        else:
            wanted[x][y] = Fraction(-1)
            wanted[y] = {x: Fraction(1, 2), y: Fraction(1, 2)}
    for x, y in zip(layout["hosted"]["X2"], layout["hosted"]["Y2"], strict=True):
        wanted[x][y] = Fraction(-1)
    transpose = [{} for _ in inputs]
    for i, row in enumerate(wanted):
        for j, c in row.items():
            transpose[j][i] = c
    forward = check_matrix(inputs, outputs, order, rows, wanted)
    dual_order = [k for k in reversed(order) if k in moves] + inputs
    reverse = check_matrix(outputs, inputs, dual_order, dual, transpose)
    return dict(
        roles=n,
        coefficients_each_way=n * n,
        donors=sum(map(len, rows.values())),
        forward_digit_bits=forward,
        transpose_digit_bits=reverse,
    )
