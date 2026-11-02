#!/usr/bin/env python3
"""Exact nonnegative-combination reduction of one frozen280-row real system.

Source: Nick Petalas/PR6425 and retained PR1422/support lineage. New certificate
generator: ToikY with OpenAI Codex assistance. Simplex/Farkas methods classical.
Apache-2.0. No author executable, optional dependency or floating LP is used.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
MANIFEST_SHA = 'd9d9e3785d6496adf112ccafbe25689057e9a1f28384ca28a536660c9f55f6e9'
DIMENSION, ROWS, OUTSIDE = 14, 280, 8
CAPS = {'seconds': 120, 'per_target_pivots': 2000, 'total_pivots': 100000,
        'coefficient_bits': 4096}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def decode(raw):
    def unique(items):
        out = {}
        for key, value in items:
            require(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    def bad(value):
        raise ValueError('nonfinite JSON value: ' + value)
    return json.loads(raw, object_pairs_hook=unique, parse_constant=bad)


def source():
    manifest = (HERE / 'SOURCE-PINS.json').read_bytes()
    require(hashlib.sha256(manifest).hexdigest() == MANIFEST_SHA, 'source manifest SHA256')
    pins = decode(manifest)['files']
    require(set(pins) == {'README-6425.md', 'RESULT-6425.json'}, 'two frozen source objects')
    raw = {}
    for name, pin in pins.items():
        data = (HERE / 'sources' / name).read_bytes()
        require(len(data) == pin['bytes'], 'source byte length: ' + name)
        require(hashlib.sha256(data).hexdigest() == pin['sha256'], 'source SHA256: ' + name)
        require(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == pin['git_blob'], 'source Git blob: ' + name)
        raw[name] = data
    obj = decode(raw['RESULT-6425.json'])
    require(type(obj.get('kernel_rows')) is int and obj['kernel_rows'] == ROWS, '280 original rows')
    require(type(obj.get('alphabet')) is list and len(obj['alphabet']) == DIMENSION, '14-variable source alphabet')
    for rectangle in obj['alphabet']:
        require(type(rectangle) is list and len(rectangle) == 2, 'source rectangle pair')
        for cap in rectangle:
            require(type(cap) is str and cap == hex(int(cap, 16)) and int(cap, 16) > 0, 'canonical nonempty cap')
    rows = {}
    require(type(obj['kernel']) is list and len(obj['kernel']) == ROWS, 'literal kernel array')
    for entry in obj['kernel']:
        require(type(entry) is list and len(entry) == 3, 'source row/witness schema')
        text, demand, witness = entry
        require(type(text) is str and text == hex(int(text, 16)), 'canonical source support')
        mask = int(text, 16)
        require(0 < mask < (1 << DIMENSION) and mask not in rows, 'unique nonempty14-bit support')
        require(type(demand) is int and 1 <= demand <= OUTSIDE, 'integer source demand1..8')
        require(type(witness) is str and witness == hex(int(witness, 16)) and int(witness, 16) > 0, 'literal source witness identifier')
        rows[mask] = demand
    return rows


def order(mask):
    return mask.bit_count(), mask


def bits(mask):
    return [k for k in range(DIMENSION) if mask & (1 << k)]


def dot(mask, x):
    return sum((x[k] for k in bits(mask)), F(0))


class Budget:
    def __init__(self):
        self.started = time.monotonic()
        self.total = 0
        self.counts = []

    def check(self, target_count):
        require(time.monotonic() - self.started <= CAPS['seconds'], 'UNKNOWN: exact solver time cap')
        require(target_count <= CAPS['per_target_pivots'] and self.total <= CAPS['total_pivots'], 'UNKNOWN: exact solver pivot cap')

    def pivot(self, tableau, count):
        self.total += 1
        self.check(count)
        require(all(max(abs(x.numerator).bit_length(), x.denominator.bit_length()) <= CAPS['coefficient_bits'] for row in tableau for x in row), 'UNKNOWN: coefficient bit cap')


def pivot(tableau, costs, basis, leaving, entering):
    factor = tableau[leaving][entering]
    row = [x / factor for x in tableau[leaving]]
    tableau[leaving] = row
    for k in range(len(tableau)):
        if k != leaving and tableau[k][entering]:
            multiplier = tableau[k][entering]
            tableau[k] = [a - multiplier * b for a, b in zip(tableau[k], row)]
    multiplier = costs[entering]
    increment = multiplier * row[-1]
    costs[:] = [a - multiplier * b for a, b in zip(costs, row[:-1])]
    basis[leaving] = entering
    return increment


def packing(mask, demand, donors, rows, budget):
    coordinates = bits(mask)
    m, n = len(coordinates), len(donors)
    tableau = [[F(int(bool(donor & (1 << k)))) for donor in donors] +
               [F(int(j == r)) for j in range(m)] + [F(1)]
               for r, k in enumerate(coordinates)]
    costs = [F(rows[donor]) for donor in donors] + [F(0)] * m
    basis, value, count = list(range(n, n + m)), F(0), 0
    while True:
        budget.check(count)
        weights = {donors[v]: tableau[r][-1] for r, v in enumerate(basis) if v < n and tableau[r][-1]}
        require(all(weight > 0 for weight in weights.values()), 'feasible basic weights')
        require(value == sum((rows[d] * w for d, w in weights.items()), F(0)), 'exact primal objective accounting')
        if value >= demand:
            budget.counts.append((mask, count))
            return weights, None
        entering = next((j for j, c in enumerate(costs) if j not in basis and c > 0), None)
        if entering is None:
            dual = [-costs[n + r] for r in range(m)]
            require(all(x >= 0 for x in dual), 'dual nonnegative')
            require(all(sum((dual[r] for r, k in enumerate(coordinates) if d & (1 << k)), F(0)) >= rows[d] for d in donors), 'dual covers every retained donor')
            require(sum(dual, F(0)) == value < demand, 'exact primal-dual optimum and strict gap')
            budget.counts.append((mask, count))
            return None, dual
        choices = [(row[-1] / row[entering], basis[r], r) for r, row in enumerate(tableau) if row[entering] > 0]
        require(choices, 'UNKNOWN: unexpected unbounded nonempty-support packing')
        leaving = min(choices)[2]
        value += pivot(tableau, costs, basis, leaving, entering)
        require(all(row[-1] >= 0 for row in tableau), 'primal feasibility after exact pivot')
        count += 1
        budget.pivot(tableau + [costs + [value]], count)


def deletion_check(target, multipliers, retained, rows):
    require(target in rows and target not in retained, 'deletion target outside retained set')
    coverage = [F(0)] * DIMENSION
    demand = F(0)
    for donor, weight in multipliers.items():
        require(donor in retained and donor in rows and donor != target and weight >= 0, 'nonnegative final-retained donor')
        demand += weight * rows[donor]
        for k in bits(donor):
            coverage[k] += weight
    require(all(x <= int(bool(target & (1 << k))) for k, x in enumerate(coverage)), 'Farkas coefficient overflow')
    require(demand >= rows[target], 'Farkas demand shortfall')
    return coverage, demand


def separator_check(target, x, rows):
    require(target in rows and len(x) == DIMENSION and all(value >= 0 for value in x), 'nonnegative14-variable separator')
    require(all(dot(mask, x) >= demand for mask, demand in rows.items() if mask != target), 'separator violates another original row')
    require(dot(target, x) < rows[target], 'separator must strictly violate target')


def generate(rows):
    retained, deletions, separators = [], [], []
    budget = Budget()
    for mask in sorted(rows, key=order):
        donors = [d for d in retained if d != mask and d & mask == d]
        weights, dual = packing(mask, rows[mask], donors, rows, budget)
        if weights is not None:
            deletion_check(mask, weights, set(retained), rows)
            deletions.append((mask, weights))
        else:
            x = [F(OUTSIDE)] * DIMENSION
            for k, value in zip(bits(mask), dual):
                x[k] = value
            separator_check(mask, x, rows)
            retained.append(mask)
            separators.append((mask, x))
    final = set(retained)
    require(len(retained) + len(deletions) == len(rows), 'complete source row partition')
    for mask, weights in deletions:
        deletion_check(mask, weights, final, rows)
    for mask, x in separators:
        separator_check(mask, x, rows)
    return retained, deletions, separators, budget


def rejects(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('corrupted certificate accepted')


def controls(rows, retained, deletions, separators):
    toy = {1: 1, 2: 1, 3: 2}
    weights, dual = packing(3, 2, [1, 2], toy, Budget())
    require(weights == {1: F(1), 2: F(1)} and dual is None, 'nontrivial two-row combination fixture')
    deletion_check(3, weights, {1, 2}, toy)
    toy = {1: 1, 3: 1}
    weights, dual = packing(1, 1, [], toy, Budget())
    require(weights is None and dual == [F(0)], 'restricted support fixture optimum')
    x = [F(8)] * DIMENSION
    x[0] = F(0)
    separator_check(1, x, toy)
    outside_error = rejects(lambda: separator_check(1, [F(0)] * DIMENSION, toy))
    target, original = separators[0]
    changed = list(original)
    k = bits(target)[0]
    changed[k] += rows[target]
    strict_error = rejects(lambda: separator_check(target, changed, rows))
    result = {'two_row_combination': {'target': '0x3', 'multipliers': [['0x1', '1'], ['0x2', '1']]},
              'outside_extension_required': {'restricted_zero_point_error': outside_error},
              'actual_separator_made_target_feasible': {'target': hex(target), 'coordinate': k, 'observed_error': strict_error}}
    if deletions:
        target, original = deletions[0]
        total = sum((rows[d] * w for d, w in original.items()), F(0))
        changed = {d: w * F(rows[target], 2) / total for d, w in original.items()}
        error = rejects(lambda: deletion_check(target, changed, set(retained), rows))
        coverage, _total = deletion_check(target, original, set(retained), rows)
        factor = F(2) / max(coverage)
        excessive = {d: w * factor for d, w in original.items()}
        overflow = rejects(lambda: deletion_check(target, excessive, set(retained), rows))
        result['actual_combination_half_demand'] = {'target': hex(target), 'observed_error': error, 'mutant_rhs': str(F(rows[target], 2))}
        result['actual_combination_coefficient_overflow'] = {'target': hex(target), 'observed_error': overflow}
    return result


def run():
    rows = source()
    retained, deletions, separators, budget = generate(rows)
    return {'schema_version': 1, 'source_manifest_sha256': MANIFEST_SHA,
            'dimension': DIMENSION, 'source_rows': len(rows),
            'retained': [hex(mask) for mask in retained],
            'deletions': [{'target': hex(mask), 'multipliers': [[hex(d), str(w)] for d, w in sorted(weights.items(), key=lambda item: order(item[0]))]} for mask, weights in deletions],
            'separators': [{'target': hex(mask), 'x': list(map(str, x))} for mask, x in separators],
            'counts': {'retained': len(retained), 'deleted': len(deletions), 'strict_separators': len(separators)},
            'pivot_statistics': {'total': budget.total, 'maximum_per_target': max((n for _mask, n in budget.counts), default=0),
                                 'per_target': [[hex(mask), n] for mask, n in budget.counts]},
            'declared_caps': CAPS, 'controls': controls(rows, retained, deletions, separators),
            'method': 'Exact Fraction packing simplex; feasible slack basis and Bland entering/leaving rules, including nonbasic slacks. Early feasible deletion certificates need no optimality claim.',
            'limits': ['Equivalence and irredundancy of this frozen real nonnegative-variable system only; retained separators may be fractional, so integer irredundancy is not claimed.',
                       'Original clique census, support geometry and source280-row equivalence remain credited PR6425 premises, not independently replayed here.',
                       'No globally smallest arbitrary inequality description, new cap alphabet, coefficients/decoder, physical COPY bound, kappa, native/outer admission or frontier change.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = run()
    if args.emit:
        print(canonical(result))
    else:
        path = HERE / 'RESULT.json'
        require(path.is_file(), 'retained RESULT.json required')
        observed = decode(path.read_bytes())
        require(type(observed) is dict and type(observed.get('schema_version')) is int and observed['schema_version'] == 1, 'typed certificate receipt schema')
        require(canonical(observed) == canonical(result), 'strict retained complete certificate')
        print('PASS_P112_FARKAS_KERNEL')


if __name__ == '__main__':
    main()
