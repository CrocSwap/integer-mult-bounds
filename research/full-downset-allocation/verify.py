"""Actual Full source execution with a sharper authenticated allocation."""
import json
import sys
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from allocation import adapted


def need(ok, why):
    if not ok:
        raise ValueError(why)


def ceil_log(value):
    value = Q(value)
    bits = value.numerator.bit_length() - value.denominator.bit_length()
    return bits + int(Q(2) ** bits < value)


def inverse(a, C):
    n = len(a)
    rows = [list(row) + [C(int(i == j)) for j in range(n)] for i, row in enumerate(a)]
    for j in range(n):
        k = next((i for i in range(j, n) if rows[i][j] != 0), None)
        need(k is not None, 'independent inverse pivot')
        rows[j], rows[k] = rows[k], rows[j]
        q = rows[j][j]
        rows[j] = [x / q for x in rows[j]]
        for i in range(n):
            if i != j:
                q = rows[i][j]
                rows[i] = [x - q * y for x, y in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def mv(a, v):
    return [sum((x * y for x, y in zip(row, v)), row[0] * 0) for row in a]


def norm2(v):
    return sum((z.norm2() for z in v), Q(0))


def execute(plan, vector, bits=None):
    out = list(vector)
    for layer in plan:
        used = set()
        for ids, a in layer:
            need(not used.intersection(ids), 'independent matching layer')
            used.update(ids)
            values = mv(a, [out[i] for i in ids])
            for i, z in zip(ids, values):
                if bits is None:
                    out[i] = z
                else:
                    def part(q):
                        x = q * (1 << bits) + Q(1, 2)
                        return Q(x.numerator // x.denominator, 1 << bits)
                    out[i] = type(z)(part(z.re), part(z.im))
    return out


def operator(plan, n, C):
    columns = [execute(plan, [C(int(i == j)) for i in range(n)]) for j in range(n)]
    return [[columns[j][i] for j in range(n)] for i in range(n)]


def mul(a, b):
    return [[sum((x * b[k][j] for k, x in enumerate(row)), row[0] * 0)
             for j in range(len(b[0]))] for row in a]


def reject(call, fragment):
    try:
        call()
    except (ValueError, TypeError) as exc:
        need(fragment in str(exc), 'unexpected control rejection: ' + str(exc))
    else:
        raise ValueError('missing rejection: ' + fragment)


def inspect(b):
    n, l, q, r = (b[k] for k in ('n', 'lam', 'inverse_bound', 'radius'))
    d, j, tau = n.bit_length() - 1, 3 * n - 2, Q(1, 1 << b['target_bits'])
    bound = 2 * (1 << ((d + 1) // 2)) * (l * q) ** 2
    need(b['completed_prefix_bound'] == bound and bound >= max(1, l, q), 'new completed bound')
    need(b['child_target_bits'] == b['target_bits'] + ceil_log(4 * j * bound ** 3 * (r + 1)),
         'rederived child target')
    eta = Q(1, 1 << b['child_target_bits'])
    theta = j * bound ** 2 * eta
    need(theta <= Q(1, 16) and eta <= 1 / (2 * q), 'normalized perturbation and scalar margin')
    e = 2 * j * bound ** 3 * eta
    need(e * r < tau / 2, 'coefficient half budget')
    need(b['execution_bound'] == 2 * max(1, l, q) * bound * b['fragment_bound'], 'physical envelope')
    f = max(b['incoming_bits'], b['target_bits'] + ceil_log(2 * b['layer_bound'] * b['execution_bound'] * n))
    need(b['data_bits'] == f, 'rederived global data grid')
    rounding = b['layer_bound'] * b['execution_bound'] * n * Q(1, 1 << f)
    need(rounding <= tau / 2 and b['total_error'] == e * r + rounding < tau, 'complete target budget')
    need(b['amplitude_bound'] == b['execution_bound'] * r +
         b['layer_bound'] * b['execution_bound'] ** 2 * n * Q(1, 1 << f), 'intermediate amplitude')


def main():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    raw = {}
    for row in sources['files']:
        if row['usage'] == 'input':
            value = (ROOT / row['path']).read_bytes()
            need(sha256(value).hexdigest() == row['sha256'], 'authenticated source bytes: ' + row['path'])
            raw[row['path']] = value
    sys.path.insert(0, str(ROOT / 'research/rational-unitary-fft'))
    from exact import C, Mat, Vec, apply as source_apply, ceil_log2, inverse_gate
    from full import Full, admission, allocation as original
    source = raw['research/rational-unitary-fft/full.py']
    allocation, binding = adapted(source, need, ceil_log2)
    parameter_cases = 0
    for d in range(21):
        for l, q, r, t, incoming in ((1, 1, 1, 1, 0), (Q(7, 3), Q(13, 5), 16, 9, 512),
                                    (1 << 20, 1 << 30, 1 << 10, 24, 0)):
            b = allocation(1 << d, l, q, r, t, incoming)
            inspect(b)
            old = original(1 << d, l, q, r, t, incoming)
            need(b['child_target_bits'] < old['child_target_bits'] and b['data_bits'] <= old['data_bits'],
                 'actual allocation lowers child target and never coarsens incoming grid')
            parameter_cases += 1
    fixtures = [
        ('complex-scalar', Mat([[C(Q(1, 3), Q(1, 7))]]), 0),
        ('small-pivot', Mat([[Q(1, 1 << 30)]]), 0),
        ('complex-two', Mat([[C(1, Q(1, 4)), C(Q(1, 8), Q(1, 16))],
                             [C(Q(-1, 16), Q(1, 8)), C(1, Q(1, 4))]]), 0),
        ('fine-grid-two', Mat([[C(1), C(Q(1, 8))], [C(Q(1, 16)), C(1)]]), 512),
        ('complex-four', Mat([[C(1, Q(1, 16)) if i == j else
                               C(Q(1, 64 * (1 + abs(i - j))), Q(i - j, 128))
                               for j in range(4)] for i in range(4)]), 0),
        ('zero-shear-four', Mat([[int(i == j) for j in range(4)] for i in range(4)]), 0),
    ]
    rows = []
    final_plan = final_matrix = None
    for label, matrix, incoming in fixtures:
        n, radius, target = len(matrix), Q(4), 10
        incoming = max(12, incoming)
        l, q, _ = admission(matrix)
        b = allocation(n, l, q, radius, target, incoming)
        inspect(b)
        old = original(n, l, q, radius, target, incoming)
        builder = Full(b, raw)
        plan = builder.plan(matrix)
        back = builder.inverse(plan)
        direct, reverse = operator(plan, n, C), operator(back, n, C)
        target_inverse = inverse(matrix, C)
        need(mul(direct, reverse) == [[C(int(i == j)) for j in range(n)] for i in range(n)],
             'same stored inverse endpoint')
        vectors = [[C(Q((-1) ** i, 2), Q(i, 8)) for i in range(n)],
                   [C(Q(1, 1 << (incoming or 12)))] + [C()] * (n - 1)]
        trajectories = 0
        for program, stored, intended in ((plan, direct, matrix), (back, reverse, target_inverse)):
            for vector in vectors:
                need(norm2(vector) <= radius ** 2, 'actual invocation radius')
                wanted = mv(intended, vector)
                output = execute(program, vector, b['data_bits'])
                actual, stats = source_apply(program, Vec(vector), b['data_bits'])
                need(output == list(actual), 'independent versus source rounded execution')
                need(norm2([x - y for x, y in zip(mv(stored, vector), wanted)]) <=
                     (b['coefficient_error'] * radius) ** 2, 'actual coefficient allowance')
                need(norm2([x - y for x, y in zip(output, wanted)]) <= b['total_error'] ** 2,
                     'actual complete target')
                need(stats['max_observed_height'] <= builder.bound['temporary_bits'] and
                     stats['max_grid_numerator_bits'] + 1 <= b['data_bits'] + b['integer_bits'],
                     'actual online grid/temporary widths')
                trajectories += 1
        rows.append(dict(label=label, n=n, trajectories=trajectories, layers=len(plan),
                         old_child_bits=old['child_target_bits'], child_bits=b['child_target_bits'],
                         old_data_bits=old['data_bits'], data_bits=b['data_bits']))
        if label == 'complex-two':
            final_plan, final_matrix = plan, matrix
    reject(lambda: adapted(source.replace(b'256 * n ** 3 * chi ** 12', b'128 * n ** 3 * chi ** 12'),
                           need, ceil_log2), 'exact original')
    for args in ((True, 1, 1, 1, 1, 0), (3, 1, 1, 1, 1, 0), (2, 1.0, 1, 1, 1, 0)):
        reject(lambda args=args: allocation(*args), 'full')
    bad = allocation(1, 1, 1 << 30, 1, 10, 0)
    bad.update(child_target_bits=4, eta=Q(1, 16))
    reject(lambda: Full(bad, raw).plan(Mat([[Q(1, 1 << 30)]])), 'stored full pivot margin')
    wrong = [[(ids, inverse_gate(gate)) for ids, gate in layer] for layer in final_plan]
    need(operator(wrong, 2, C) != inverse(final_matrix, C), 'wrong stored inverse order control')
    scalar = [[((0,), [[C(Q(1, 3))]])]]
    need(norm2([execute(scalar, [C(1)], 2)[0] - C(Q(1, 3))]) > Q(1, 1 << 20),
         'underfunded data grid actual error control')
    print(json.dumps(dict(binding=binding, parameter_cases=parameter_cases, actual_cases=rows,
                          trajectories=sum(r['trajectories'] for r in rows), controls=7), sort_keys=True))
    print('PASS_FULL_DOWNSET_ALLOCATION actual_factory_same_stored_inverse no_new_kappa')


if __name__ == '__main__':
    main()
