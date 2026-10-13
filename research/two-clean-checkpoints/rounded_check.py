"""Exact-rational replay of the checkpoint words with PR628 rounded leaves.

Synthetic stable factors isolate scheduling from factor preparation. The dense
reference solves each represented factor matrix without calling the leaf.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path

import planner

ROOT = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_leaf():
    spec = importlib.util.spec_from_file_location('checkpoint_pr628', ROOT / 'vendor/pr628/dirty.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def ceil_log2(value):
    need(value > 0, 'positive logarithm argument')
    result = value.numerator.bit_length() - value.denominator.bit_length()
    while F(2) ** result < value:
        result += 1
    while F(2) ** (result - 1) >= value:
        result -= 1
    return result


def precision(calls, magnitude, target=64):
    # PR628 DIRTY-PROOF.md: beta=1/2, maximum leaf multiplier r=3.
    beta, r = F(1, 2), 3
    a, growth = 13 * (r + 1) / beta ** 3, 2 + F(r) / beta
    bits = max(ceil_log2(a), ceil_log2(2 / beta ** 2),
               target + 1 + ceil_log2(calls * a * (magnitude + 1))
               + (calls - 1) * ceil_log2(growth))
    unit = F(1, 1 << bits)
    bound = calls * a * (magnitude + 1) * unit * growth ** (calls - 1)
    need(a * unit <= 1 and unit <= beta ** 2 / 2, 'leaf precision conditions')
    need(bound <= F(1, 1 << (target + 1)), 'whole-word precision budget')
    return bits, bound


class Phases:
    """Count every indexed read, including the inherited stability validation."""

    def __init__(self, values):
        self.values, self.reads = values, 0

    def __getitem__(self, index):
        self.reads += 1
        return self.values[index]


def execute(leaf, arrays, steps, factors, phases, bits, direction):
    stats = dict(leaves=0, scalar_steps=0)
    for factor, source, target, sign in steps:
        leaf.leaf(arrays[source], arrays[target], factors[factor], phases,
                  F(1, 2), bits, direction, sign, stats)
    return stats


def case(leaf, nf, scratch, clean, length, direction, sign, dirt):
    c = leaf.c
    factors = [(i % 2 == 0, (F(1, 4), F((-1) ** i, 8)), F(3 if i == 0 else 1))
               for i in range(nf)]
    prices = tuple((6 if inside else 5) * length - 2 for inside, _, _ in factors)
    plan = planner.solve(prices, scratch, clean)
    need(plan is not None, 'rounded fixture is feasible')
    price, tree = plan
    clean_slots = tuple(range(2, 2 + clean))
    dirty_slots = tuple(range(2 + clean, 2 + scratch))
    steps = list(planner.emit(tree, 0, 1, dirty_slots, clean_slots, sign))
    inverse = list(planner.emit(tree, 0, 1, dirty_slots, clean_slots, -sign))
    need(inverse == [(f, s, t, -q) for f, s, t, q in reversed(steps)], 'inverse chronology')
    counts = Counter(f for f, _, _, _ in steps)
    need(sum(prices[i] * counts[i] for i in range(nf)) == price, 'planned phase price')

    # Include an untouched spectator beyond the supplied scratch roles.
    arrays = [[(F(2 + j + i, 8), F(3 - j + 2 * i, 8)) for i in range(length)]
              for j in range(scratch + 3)]
    for j in dirty_slots:
        arrays[j] = [(a + dirt, b - dirt) for a, b in arrays[j]]
    for j in clean_slots:
        arrays[j] = [c.ZERO] * length
    initial = [row[:] for row in arrays]
    magnitude = max(abs(a) + abs(b) for row in arrays for a, b in row)
    bits, bound = precision(len(steps), magnitude)
    units = (c.ONE, (F(0), F(1)), (F(3, 5), F(4, 5)))
    values = [units[i % len(units)] for i in range(length)]
    phases = Phases(values)
    stats = execute(leaf, arrays, steps, factors, phases, bits, direction)
    need(arrays[0] == initial[0] and arrays[2:] == initial[2:], 'exact source/scratch restoration')
    need(all(arrays[j] == [c.ZERO] * length for j in clean_slots), 'exact clean-zero restoration')
    need(phases.reads == price, 'actual phase-access invoice')
    need(stats == dict(leaves=len(steps), scalar_steps=3 * length * len(steps)), 'actual traversal invoice')

    expected = leaf.exact_operator(initial[0], factors, values, direction)
    net = [c.sub(value, start) for value, start in zip(arrays[1], initial[1])]
    need(all(c.norm2(c.sub(value, leaf.scaled(exact, sign))) <= bound ** 2
             for value, exact in zip(net, expected)), 'dense rational comparison')
    output_hash = digest([[str(a), str(b)] for a, b in net])
    execute(leaf, arrays, inverse, factors, phases, bits, direction)
    need(arrays == initial, 'exact rounded whole-word inverse')
    need(phases.reads == 2 * price, 'inverse phase-access invoice')

    # The clean connector requires exact F(0)=0, not merely a small residual.
    arrays = [row[:] for row in initial]
    arrays[0] = [c.ZERO] * length
    zero_initial = [row[:] for row in arrays]
    execute(leaf, arrays, steps, factors, Phases(values), bits, direction)
    need(arrays == zero_initial, 'exact zero-source identity')
    return dict(factors=nf, scratch=scratch, clean=clean, length=length,
                direction=direction, sign=sign, dirt=dirt, calls=len(steps),
                phase_reads=price, lift_loop_visits=3 * length * len(steps),
                working_bits=bits, target_bits=64, output_sha256=output_hash)


def dirty_as_clean_control(leaf):
    """A nonzero C connector restores its dirt but contaminates the target."""
    c = leaf.c
    tree = ('C', 0, 1)
    steps = list(planner.emit(tree, 0, 1, (), (2,)))
    factors = [(True, (F(1, 4), F(1, 8)), F(1)),
               (False, (F(1, 4), F(-1, 8)), F(1))]
    # Zero source makes the invalid clean assumption particularly observable.
    arrays = [[c.ZERO] * 3, [c.ONE] * 3,
              [(F(1), F(1, 2)), (F(-3, 4), F(1, 4)), (F(1, 2), F(-1))]]
    initial = [row[:] for row in arrays]
    values = [c.ONE, (F(0), F(1)), (F(3, 5), F(4, 5))]
    bits, bound = precision(len(steps), F(2))
    execute(leaf, arrays, steps, factors, Phases(values), bits, 1)
    need(arrays[0] == initial[0] and arrays[2] == initial[2], 'control source/dirt restoration')
    errors = [c.norm2(c.sub(x, y)) for x, y in zip(arrays[1], initial[1])]
    need(max(errors) > bound ** 2, 'dirty-as-clean mutation must fail the dense target contract')
    return dict(name='dirty_array_used_as_clean', rejected=True,
                source_and_dirt_restored=True, target_contaminated=True,
                target_error_squared=str(max(errors)))


def run_checks():
    leaf = load_leaf()
    configurations = ((1, 0, 0), (2, 1, 0), (2, 1, 1),
                      (3, 2, 0), (3, 2, 1), (3, 2, 2),
                      (5, 3, 0), (5, 3, 1), (5, 3, 2),
                      (8, 3, 0), (8, 3, 1), (8, 3, 2))
    rows = [case(leaf, nf, scratch, clean, length, direction, sign, dirt)
            for nf, scratch, clean in configurations
            for length, direction, sign, dirt in product((1, 3), (-1, 1), (-1, 1), (-7, 5))]
    controls = [dirty_as_clean_control(leaf)]
    return dict(status='passed', cases=len(rows), rows=rows, controls=controls,
                scope='Synthetic stable inside/outside factors; exact dyadic rounding; '
                      'dense represented-factor comparison. Phase generation and storage '
                      'are external costs; no root certificate or machine performance claim.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = run_checks()
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], cases=result['cases'], controls=len(result['controls']))))


if __name__ == '__main__':
    main()
