"""Independent exact inverse-row check of the physical tensor consumer.

The oracle solves the original rational matrix by Gaussian elimination;
it does not evaluate a Neumann polynomial or a Horner recurrence.
"""
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import itertools
import json
from pathlib import Path
import random
import sys

PACKAGE = Path(__file__).resolve().parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def inverse_rows(matrix, which):
    """Solve H^T v=e_r, with exact rational elimination and residual checks."""
    n = len(matrix)
    targets = tuple(sorted(set(which)))
    a = [[matrix[j][i] for j in range(n)] +
         [F(int(i == r)) for r in targets] for i in range(n)]
    for column in range(n):
        pivot = next(r for r in range(column, n) if a[r][column])
        a[column], a[pivot] = a[pivot], a[column]
        divisor = a[column][column]
        a[column] = [v / divisor for v in a[column]]
        for row in range(column + 1, n):
            factor = a[row][column]
            if factor:
                a[row] = [x - factor * y for x, y in zip(a[row], a[column])]
    result = {}
    for index, target in enumerate(targets):
        row = [F(0)] * n
        for r in range(n - 1, -1, -1):
            row[r] = a[r][n + index] - sum(a[r][j] * row[j] for j in range(r + 1, n))
        for c in range(n):
            if sum(row[j] * matrix[j][c] for j in range(n)) != int(c == target):
                raise AssertionError('exact inverse-row residual')
        result[target] = row
    return result


def main():
    engine = load('shrinking_halo_engine', PACKAGE / 'engine.py')
    tensor = load('lead_tensor', PACKAGE / 'tensor.py')
    source = load('lead_source', PACKAGE / 'source.py')
    raw = source.authenticated_inputs(PACKAGE)
    reference = source.make_reference(raw, (32, 8, 2, 1, 8, 32))
    reference.require_narrow_gap()
    n = reference.target_size
    matrix = [[reference.entry('narrow', r, c).value for c in range(n)] for r in range(n)]
    rho = max(sum(abs(F(int(r == c)) - matrix[r][c]) for c in range(n)) for r in range(n))
    gap = F(int((1 - rho) * (1 << 16)), 1 << 16)
    shift = 0
    while (1 << shift) * gap < 1:
        shift += 1
    plan = engine.Plan(n, 2 * reference.spec.source_halfwidth + 2, 28, 4, shift, gap)
    targets = ((-3, 2), (39, 2))
    rows = inverse_rows(matrix, [x % n for lo, count in targets for x in range(lo, lo + count)])
    scale = 1 << plan.bits
    rng = random.Random(2026110875)
    values = [[(rng.randrange(-8, 9) * (scale // 32),
                rng.randrange(-8, 9) * (scale // 32)) for _ in range(n)] for _ in range(n)]
    exact = {}
    for r, s in itertools.product(*(range(lo, lo + count) for lo, count in targets)):
        exact[r, s] = tuple(
            sum(rows[r % n][u] * sum(rows[s % n][v] * values[u][v][part]
                                    for v in range(n)) for u in range(n)) /
            (scale * (1 << (2 * shift))) for part in (0, 1))
    bill = engine.Bill()
    production = source.make_reference(raw, (32, 8, 2, 1, 8, 32))

    def prepared():
        for _ in range(2):
            table, _ = engine.prepare_table(
                plan, lambda r, c: source.source_entry(production, r, c),
                production.description_hash, bill)
            yield table

    archive = tensor.pack_tables(prepared(), bill)
    before_archive = engine.tape_digest(archive.tape)
    pool = tensor.TensorWorkspace.create(bill)
    role_ids = tuple(map(id, pool.roles))
    original_init = engine.Tape.__init__

    def no_new_tapes(*_args, **_kwargs):
        raise AssertionError('new physical role during tensor work or reuse')

    engine.Tape.__init__ = no_new_tapes
    observations = []
    outputs = []
    try:
        for target in (targets, ((-3, 1), (39, 1))):
            layout = tensor.Layout.make(archive.plans, target)
            payloads = (values[u % n][v % n] for u, v in itertools.product(
                *(range(lo, lo + count) for lo, count in zip(layout.lowers, layout.lengths))))
            incoming = tensor.rectangle_input(layout, payloads, bill, tape=pool.rectangles[0])
            result = tensor.apply_tensor(archive, target, incoming, bill, workspace=pool)
            outputs.append(dict(tensor.consume_tensor(result)))
            observations.append({'saved_records': layout.volume, 'target_records': result.count,
                                 'retained_bits': sum(t.extent for t in pool.roles)})
            if tuple(map(id, pool.roles)) != role_ids:
                raise AssertionError('workspace roles changed')
            if not all(t.head == 0 and t.live_bits == 0 and not any(t.snapshot()) for t in pool.roles):
                raise AssertionError('nonblank workspace after return')
            if engine.tape_digest(archive.tape) != before_archive or archive.tape.head:
                raise AssertionError('borrowed archive changed')
    finally:
        engine.Tape.__init__ = original_init
    bound = 2 * (plan.numeric_error + plan.tail_error)
    errors = {}
    for key, actual in outputs[0].items():
        error = sum(abs(F(actual[p], scale) - exact[key][p]) for p in (0, 1))
        if error > bound:
            raise AssertionError(('exact original tensor inverse', key, str(error), str(bound)))
        errors[key] = error
    if outputs[1][(-3, 39)] != outputs[0][(-3, 39)]:
        raise AssertionError('nested-target or retained-history dependence')
    actual = outputs[0][(-3, 39)]
    wrong = sum(abs(F(actual[p], scale) - exact[(-2, 40)][p]) for p in (0, 1))
    if wrong <= bound:
        raise AssertionError('wrong canonical target key not distinguished')
    print('PASS_LEAD_EXACT_TENSOR_INVERSE')
    print(json.dumps({'period': n, 'original_entries': n * n,
                      'exact_inverse_rows': sorted(rows), 'checked_outputs': len(outputs[0]),
                      'maximum_inverse_error': float(max(errors.values())),
                      'proved_inverse_error_bound': float(bound),
                      'wrong_target_error': float(wrong),
                      'fixed_tape_roles': len(pool.roles), 'runs': observations,
                      'actual_bit_actions': bill.reads + bill.writes + bill.moves,
                      'source_entries': len(production.entries),
                      'sha256': {p: sha256((PACKAGE / p).read_bytes()).hexdigest()
                                 for p in ('engine.py', 'tensor.py', 'source.py')}}, sort_keys=True))


if __name__ == '__main__':
    main()
