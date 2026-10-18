"""Finite rounded-leaf evidence for a clean root; no general accuracy theorem.

Uses only selected definitions of the hash-pinned PR628 dirty prototype.
The error envelope is inherited conditionally from its leaf estimates.
Prepared for FanPUYen with substantial OpenAI Codex assistance. Apache-2.0.
"""
import ast
from fractions import Fraction as F
import importlib.util
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def implementation():
    c = load_file('pinned_scan', HERE / 'vendor/pr628-scan.py')
    path = HERE / 'vendor/pr628-dirty.py'
    tree = ast.parse(path.read_text(), filename=str(path))
    names = {'scaled', 'conj', 'ordered', 'lift', 'leaf', 'compose'}
    definitions = [node for node in tree.body
                   if isinstance(node, ast.FunctionDef) and node.name in names]
    c.need({node.name for node in definitions} == names, 'vendored definitions')
    namespace = dict(F=F, c=c, itertools=itertools)
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(path), 'exec'),
         namespace)
    return c, namespace['compose']


def dense_operator(c, x, factors, phases, direction):
    """Gaussian elimination on each cyclic factor, independent of the lifts."""
    out = x[:]
    length = len(x)
    for inside, b, scale in factors:
        root = b if inside else c.div(c.ONE, b)
        matrix = [[c.ZERO for _ in range(length)] + [out[i]]
                  for i in range(length)]
        for i in range(length):
            matrix[i][i] = c.neg(root)
            j = (i - direction) % length
            matrix[i][j] = c.add(matrix[i][j], phases[i])
        for col in range(length):
            pivot = next(row for row in range(col, length)
                         if matrix[row][col] != c.ZERO)
            matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
            divisor = matrix[col][col]
            matrix[col] = [c.div(v, divisor) for v in matrix[col]]
            for row in range(length):
                if row == col:
                    continue
                coefficient = matrix[row][col]
                matrix[row] = [c.sub(v, c.mul(coefficient, w))
                               for v, w in zip(matrix[row], matrix[col])]
        out = [(row[-1][0] * scale, row[-1][1] * scale) for row in matrix]
    return out


def leaves(n):
    return 1 if n == 1 else 2 * (leaves(n // 2) + leaves(n - n // 2))


def ceil_log2(value):
    """Nonnegative ceiling, computed with integers only."""
    bits = max(0, value.numerator.bit_length() - value.denominator.bit_length())
    return bits + ((value.denominator << bits) < value.numerator)


def precision(calls, magnitude):
    beta, r = F(1, 2), 3
    a, growth = 13 * (r + 1) / beta ** 3, 2 + F(r) / beta
    numerator = calls * a * (magnitude + 1) * growth ** (calls - 1)
    bits = ceil_log2(max(a, 2 / beta ** 2, numerator * (1 << 32)))
    bound = numerator / (1 << bits)
    need(a / (1 << bits) <= 1 and F(1, 1 << bits) <= beta ** 2 / 2,
         'chosen precision satisfies inherited leaf and closure hypotheses')
    need(bound <= F(1, 1 << 32), 'chosen precision meets the error target')
    return bits, bound


def four_call(compose, x, y, factors, clean, scratch, phases, bits, d, k):
    for source, target, fs, sign in (
        (x, clean, factors[:k], 1), (clean, y, factors[k:], 1),
        (x, clean, factors[:k], -1), (clean, y, factors[k:], -1),
    ):
        compose(source, target, fs, scratch, phases, F(1, 2), bits, d, sign)


def controls(c, compose, adapter):
    factors = [(True, (F(1, 4), F(0)), F(1))] * 2
    x, y, dirty_checkpoint = [c.ONE], [c.ZERO], [c.ONE]
    before = [v[:] for v in (x, y, dirty_checkpoint)]
    try:
        adapter(compose, c, x, y, factors, dirty_checkpoint, [], [c.ONE],
                F(1, 2), 128, 1, split=1)
    except ValueError as error:
        rejected = str(error)
    else:
        raise AssertionError('nonzero checkpoint accepted')
    need([x, y, dirty_checkpoint] == before,
         'nonzero checkpoint rejection must precede mutation')
    # Deliberately bypass the clean precondition: A(z + Bx) retains A(z).
    compose(x, dirty_checkpoint, factors[:1], [], [c.ONE], F(1, 2), 128, 1)
    compose(dirty_checkpoint, y, factors[1:], [], [c.ONE], F(1, 2), 128, 1)
    compose(x, dirty_checkpoint, factors[:1], [], [c.ONE], F(1, 2), 128, 1, -1)
    ideal = dense_operator(c, x, factors, [c.ONE], 1)
    need(c.norm2(c.sub(y[0], ideal[0])) > 1 and dirty_checkpoint == [c.ONE],
         'bypassing the clean precondition must exhibit contamination')
    contamination = c.sub(y[0], ideal[0])
    # Deliberately omit the third call: the checkpoint must fail restoration.
    clean, target = [c.ZERO], [c.ZERO]
    compose(x, clean, factors[:1], [], [c.ONE], F(1, 2), 128, 1)
    compose(clean, target, factors[1:], [], [c.ONE], F(1, 2), 128, 1)
    need(clean != [c.ZERO] and x == [c.ONE],
         'omitting the restore call must leave a nonzero checkpoint')
    return [dict(name='nonzero_checkpoint', rejected=rejected,
                 unchanged_on_rejection=True,
                 bypass_error=[str(v) for v in contamination],
                 bypass_squared_error_greater_than_one=True),
            dict(name='omitted_restore', detected_nonzero_checkpoint=True,
                 checkpoint=[str(v) for v in clean[0]])]


def run():
    c, compose = implementation()
    checkpoint = load_file('clean_checkpoint', HERE / 'checkpoint.py')
    adapter = checkpoint.compose_clean
    units = [c.ONE, (F(0), F(1)), (F(3, 5), F(4, 5)),
             (F(-5, 13), F(12, 13))]
    cases, nonzero_errors = [], 0
    for n in range(2, 9):
        factors = [(i % 2 == 0, (F(1, 4), F((-1) ** i, 8)),
                    F(3) if i == 0 else F(1)) for i in range(n)]
        for k in sorted({1, n // 2, n - 1}):
            calls = 2 * leaves(k) + leaves(n - k)
            depth = (max(k, n - k) - 1).bit_length()
            for length, direction, dirt in itertools.product((1, 2, 5), (-1, 1), (0, 7)):
                x0 = [(F(i % 5 - 2, 4), F(i % 3 - 1, 8)) for i in range(length)]
                y0 = [(F(dirt + i, 4), F(dirt - i, 8)) for i in range(length)]
                s0 = [[(F(dirt + 2 * i + j, 4), F(dirt - 3 * i - j, 8))
                       for i in range(length)] for j in range(depth)]
                phases = [units[(i * i + 3 * i + 1) % 4] for i in range(length)]
                magnitude = max(abs(a) + abs(b) for v in [x0, y0] + s0 for a, b in v)
                bits, bound = precision(calls, magnitude)
                x, y, clean = x0[:], y0[:], [c.ZERO] * length
                scratch = [v[:] for v in s0]
                stats = dict(leaves=0, scalar_steps=0)
                adapter(compose, c, x, y, factors, clean, scratch, phases,
                        F(1, 2), bits, direction, split=k, stats=stats)
                need(x == x0 and scratch == s0 and clean == [c.ZERO] * length,
                     'positive word restores source, scratch and checkpoint')
                need(stats == dict(leaves=calls, scalar_steps=3 * length * calls),
                     'observed leaf and scalar-step counts match recurrence')
                need(checkpoint.plan(n, k)['leaf_calls'] == calls,
                     'planner leaf count matches independent recurrence')
                net = [c.sub(v, w) for v, w in zip(y, y0)]
                exact = dense_operator(c, x0, factors, phases, direction)
                error2 = max(c.norm2(c.sub(v, w)) for v, w in zip(net, exact))
                need(error2 <= bound ** 2, 'dense oracle error within inherited bound')
                nonzero_errors += error2 > 0
                output = y[:]
                adapter(compose, c, x, y, factors, clean, scratch, phases,
                        F(1, 2), bits, direction, split=k, sign=-1)
                need(x == x0 and y == y0 and scratch == s0 and clean == [c.ZERO] * length,
                     'negative word exactly inverts the positive word')
                # From an arbitrary original target, the inverse has net -net.
                adapter(compose, c, x, y, factors, clean, scratch, phases,
                        F(1, 2), bits, direction, split=k, sign=-1)
                need([c.sub(v, w) for v, w in zip(y0, y)] == net,
                     'standalone negative word has the opposite target increment')
                need(x == x0 and scratch == s0 and clean == [c.ZERO] * length,
                     'standalone negative word restores all auxiliary arrays')
                shifted = [c.add(v, (F(11), F(-3))) for v in y0]
                shifted0 = shifted[:]
                adapter(compose, c, x, shifted, factors, clean, scratch, phases,
                        F(1, 2), bits, direction, split=k)
                need([c.sub(v, w) for v, w in zip(shifted, shifted0)] == net,
                     'target increment is independent of the initial target')
                need(x == x0 and scratch == s0 and clean == [c.ZERO] * length,
                     'shifted-target word restores all auxiliary arrays')
                four = y0[:]
                four_call(compose, x, four, factors, clean, scratch, phases,
                          bits, direction, k)
                need(four == output and x == x0 and scratch == s0,
                     'same-split four-call word has identical result and restoration')
                need(clean == [c.ZERO] * length, 'four-call word restores checkpoint')
                cases.append(dict(factors=n, split=k, length=length,
                                  direction=direction, dirt=dirt, leaf_calls=calls,
                                  dirty_arrays=depth, clean_arrays=1, bits=bits,
                                  initial_magnitude=str(magnitude),
                                  inherited_error_bound=str(bound)))
    need(nonzero_errors > 0, 'finite cases must exercise nonzero rounding error')
    return dict(status='passed', cases=cases, case_count=len(cases),
                nonzero_rounding_error_cases=nonzero_errors,
                checks=['dense rational oracle within inherited bound',
                        'exact source, dirty scratch and clean restoration',
                        'exact inverse and standalone negative word',
                        'target independence', 'same-split four-call identity',
                        'leaf and scalar-step counts'],
                controls=controls(c, compose, adapter),
                error_envelope=dict(N='actual three-call leaf count',
                                    a='13*(r+1)/beta^3', G='2+r/beta',
                                    beta='1/2', r=3,
                                    formula='N*a*(D+1)*2^(-bits)*G^(N-1)',
                                    precision_target='2^-32'),
                scope='Finite evidence with pinned PR628 rounded leaves; inherited '
                      'leaf error estimates are assumed, not proved here. No supplier, '
                      'bit-reversible tape compiler, or multiplication theorem.')


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
