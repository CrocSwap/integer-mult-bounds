"""Exact local bank audit. Ali Romman, with OpenAI Codex. Apache-2.0."""

from collections import Counter, defaultdict
from fractions import Fraction
from math import gcd, lcm
from pathlib import Path
import heapq
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'retained'))
import construction


class CapturedGraph(Exception):
    """Stop the source observer before edit 26 changes its input graph."""

    def __init__(self, net, event):
        self.net, self.event = net, event


def snapshot():
    def observe(index, net, event):
        if index == 25:
            raise CapturedGraph(net, event)

    try:
        construction.build(observer=observe)
    except CapturedGraph as captured:
        return captured.net, captured.event
    raise ValueError('missing edit 26')


def expand(net, targets, impulses):
    """Propagate integer numerator vectors through the complete required DAG."""
    required, todo = set(), list(targets)
    while todo:
        key = todo.pop()
        if key < 0 or key in required:
            continue
        required.add(key)
        todo.extend(net.forms[key])
    dependencies = {key: {j for j in net.forms[key] if j >= 0} for key in required}
    readers = defaultdict(list)
    for key, parents in dependencies.items():
        chart = net.moves[key][0] if key < net.first_output else net.final[key - net.first_output]
        for donor in net.forms[key]:
            donor_chart = net.initial[~donor] if donor < 0 else net.moves[donor][1]
            if donor_chart != chart:
                raise ValueError('nonlocal donor')
        for donor in parents:
            readers[donor].append(key)
    degree = {key: len(parents) for key, parents in dependencies.items()}
    queue = [key for key in required if not degree[key]]
    heapq.heapify(queue)
    remaining = Counter(j for parents in dependencies.values() for j in parents)
    values, visited = {}, []
    products, peak = 0, 0
    public = len(net.initial)
    while queue:
        key = heapq.heappop(queue)
        parts = []
        for donor, coefficient in net.forms[key].items():
            row, denominator = ({~donor: 1}, 1) if donor < 0 else values[donor]
            parts.append((row, denominator * coefficient.denominator, coefficient.numerator))
        for index, pulse in enumerate(impulses):
            coefficient = pulse.get(key, Fraction(0))
            if coefficient:
                parts.append(({public + index: 1}, coefficient.denominator, coefficient.numerator))
        denominator = lcm(*(den for _, den, _ in parts))
        result = {}
        for row, den, numerator in parts:
            factor = numerator * (denominator // den)
            for index, value in row.items():
                result[index] = result.get(index, 0) + factor * value
                products += 1
        result = {j: value for j, value in result.items() if value}
        divisor = gcd(denominator, *result.values())
        values[key] = ({j: value // divisor for j, value in result.items()}, denominator // divisor)
        visited.append(key)
        for donor in dependencies[key]:
            remaining[donor] -= 1
            if not remaining[donor] and donor not in targets:
                del values[donor]
        for reader in readers[key]:
            degree[reader] -= 1
            if not degree[reader]:
                heapq.heappush(queue, reader)
        peak = max(peak, len(values))
    if len(visited) != len(required):
        raise ValueError('cyclic source graph')
    output = {}
    for key in targets:
        row, denominator = ({~key: 1}, 1) if key < 0 else values[key]
        output[key] = {j: Fraction(value, denominator) for j, value in row.items()}
    return output, dict(nodes=len(required), integer_products=products, peak_vectors=peak)


def eliminate(matrix, width):
    """Return reduced rows, pivot columns and the selected original row indices."""
    rows = [list(map(Fraction, row)) for row in matrix]
    labels = list(range(len(rows)))
    pivots = []
    for column in range(width):
        index = len(pivots)
        chosen = next((j for j in range(index, len(rows)) if rows[j][column]), None)
        if chosen is None:
            continue
        rows[index], rows[chosen] = rows[chosen], rows[index]
        labels[index], labels[chosen] = labels[chosen], labels[index]
        factor = rows[index][column]
        rows[index] = [value / factor for value in rows[index]]
        for j, row in enumerate(rows):
            if j != index and row[column]:
                factor = row[column]
                rows[j] = [x - factor * y for x, y in zip(row, rows[index], strict=True)]
        pivots.append(column)
        if len(pivots) == len(rows):
            break
    return rows[:len(pivots)], pivots, labels[:len(pivots)]


def nullspace(matrix, width):
    rows, pivots, selected = eliminate(matrix, width)
    result = []
    for column in range(width):
        if column in pivots:
            continue
        vector = [Fraction(int(j == column)) for j in range(width)]
        for row, pivot in zip(rows, pivots, strict=True):
            vector[pivot] = -row[column]
        result.append(vector)
    return result, pivots, selected


def determinant(matrix):
    """Use the fraction-free determinant after clearing each input row."""
    scale = 1
    rows = []
    for row in matrix:
        denominator = lcm(*(value.denominator for value in row))
        scale *= denominator
        rows.append([int(value * denominator) for value in row])
    sign, previous = 1, 1
    for index in range(len(rows) - 1):
        pivot = next((j for j in range(index, len(rows)) if rows[j][index]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != index:
            rows[index], rows[pivot] = rows[pivot], rows[index]
            sign = -sign
        value = rows[index][index]
        for j in range(index + 1, len(rows)):
            for k in range(index + 1, len(rows)):
                numerator = value * rows[j][k] - rows[j][index] * rows[index][k]
                quotient, remainder = divmod(numerator, previous)
                if remainder:
                    raise ValueError('inexact determinant division')
                rows[j][k] = quotient
            rows[j][index] = 0
        previous = value
    return Fraction(sign * rows[-1][-1], scale)
