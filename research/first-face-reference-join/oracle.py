"""Independent dense original-reference solve for the B/C join fixture.

Fixture/oracle helper, not a physical tape codec or production cost claim.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent.parent / 'shrinking-reference-halo'
PARAMETERS = (61, 3, 2, 1, 8, 32)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def fixture_words(n, q):
    """Actual grid integers, component-l1 norm below1/2 at every row."""
    if q < 9:
        raise ValueError('fixture grid')
    unit = 1 << (q - 9)
    return tuple((((37 * r + 11) % 241 - 120) * unit,
                  ((53 * r + 7) % 181 - 90) * unit) for r in range(n))


def exact_inverse_action(matrix, words, bits, normalizer):
    """Solve original H y=x/a by exact rational elimination, two RHS."""
    n = len(matrix)
    if len(words) != n or any(len(row) != n for row in matrix):
        raise ValueError('exact solve dimensions')
    scale = (1 << bits) * normalizer
    augmented = [list(row) + [Q(words[i][j], scale) for j in range(2)]
                 for i, row in enumerate(matrix)]
    for column in range(n):
        pivot = next((r for r in range(column, n) if augmented[r][column]), None)
        if pivot is None:
            raise ValueError('singular original reference')
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        value = augmented[column][column]
        augmented[column] = [entry / value for entry in augmented[column]]
        for r in range(column + 1, n):
            value = augmented[r][column]
            if value:
                augmented[r] = [x - value * y
                                for x, y in zip(augmented[r], augmented[column])]
    result = [[Q(0), Q(0)] for _ in range(n)]
    for row in range(n - 1, -1, -1):
        for part in range(2):
            result[row][part] = augmented[row][n + part] - sum(
                augmented[row][column] * result[column][part]
                for column in range(row + 1, n))
    for row in range(n):
        for part in range(2):
            if sum(matrix[row][c] * result[c][part] for c in range(n)) != Q(words[row][part], scale):
                raise ValueError('exact original-reference solve residual')
    return tuple(tuple(pair) for pair in result)


def source_fixture(package=PACKAGE):
    source = load('join_source_oracle', package / 'source.py')
    raw = source.authenticated_inputs(package)
    reference = source.make_reference(raw, PARAMETERS)
    reference.require_narrow_gap()
    n = reference.target_size
    matrix = tuple(tuple(reference.entry('narrow', r, c).value for c in range(n))
                   for r in range(n))
    E = tuple(tuple(Q(int(r == c)) - matrix[r][c] for c in range(n))
              for r in range(n))
    rho = max(sum(map(abs, row)) for row in E)
    gap = Q(int((1 - rho) * (1 << 16)), 1 << 16)
    if gap <= Q(1, 2):
        raise ValueError('fixture normalizer not funded')
    if any(E[r][c] for r in range(n) for c in range(n)
           if min((r-c) % n, (c-r) % n) > 4):
        raise ValueError('actual reference not W4 banded')
    holes = [r for r in range(n) if not any(E[r])]
    wraps = [(r, c) for r in range(n) for c in range(n)
             if E[r][c] and abs(r-c) > 4]
    return source, raw, matrix, gap, dict(
        parameters=PARAMETERS, period=n, original_entries=n*n,
        source_sha256=reference.description_hash,
        gap=[gap.numerator, gap.denominator], identity_holes=holes,
        periodic_nonzero_coordinates=wraps)


def main():
    source, raw, matrix, gap, receipt = source_fixture()
    engine = load('shrinking_halo_engine', PACKAGE / 'engine.py')
    tensor = load('join_tensor_oracle', PACKAGE / 'tensor.py')
    plan = engine.Plan(64, 4, 28, 2, 1, gap, 1)
    words = fixture_words(64, plan.bits)
    expected = exact_inverse_action(matrix, words, plan.bits, 2)
    bill = engine.Bill()
    producer = source.make_reference(raw, PARAMETERS)
    table, height = engine.prepare_table(
        plan, lambda r,c: source.source_entry(producer,r,c),
        producer.description_hash, bill)
    archive = tensor.pack_tables((table,), bill)
    pool = tensor.TensorWorkspace.create(bill)
    actual = {}
    rectangles = []
    for lower in (0, 27, 32, 59):
        targets = ((lower, 5),)
        layout = tensor.Layout.make(archive.plans, targets)
        # External fixture load only; B's streamed physical codec replaces it.
        data = (words[x % 64] for x in range(layout.lowers[0],
                                           layout.lowers[0] + layout.lengths[0]))
        tape = tensor.rectangle_input(layout, data, bill, tape=pool.rectangles[0])
        output = tensor.apply_tensor(archive, targets, tape, bill, workspace=pool)
        for _ in range(output.count):
            key, pair = tensor.get_record(output.tape, output.layout)
            coordinate = (output.layout.lowers[0] + output.layout.coordinate(key,0)) % 64
            if coordinate in actual:
                raise ValueError('overlapping first-face return')
            actual[coordinate] = pair
        output.tape.clear()
        rectangles.append(dict(lower=lower, copies=layout.volume, targets=output.count))
    if set(actual) != {r for r in range(64) if r % 32 < 5 or r % 32 >= 27}:
        raise ValueError('incomplete first-face return')
    maximum = max(sum(abs(Q(actual[r][j],1 << plan.bits) - expected[r][j])
                      for j in range(2)) for r in actual)
    bound = plan.numeric_error + plan.tail_error
    if maximum > bound:
        raise ValueError('original inverse error exceeds proved bound')
    shifted = max(sum(abs(Q(actual[r][j],1 << plan.bits) - expected[(r+1)%64][j])
                      for j in range(2)) for r in actual)
    if shifted <= bound:
        raise ValueError('wrong-return control not separated')
    receipt.update(rectangles=rectangles, checked_targets=len(actual),
                   maximum_inverse_error=float(maximum), proved_error_bound=float(bound),
                   wrong_return_error=float(shifted), source_height=height,
                   setup_source=source.source_receipt(producer),
                   physical_bit_actions=bill.reads+bill.writes+bill.moves,
                   program_sha256={name:sha256((PACKAGE/name).read_bytes()).hexdigest()
                                   for name in ('engine.py','tensor.py','source.py')})
    print('PASS_PRIME_REFERENCE64_DIRECT_SOLVE')
    print(json.dumps(receipt,sort_keys=True))


if __name__ == '__main__':
    main()
