"""Independent exact allocation/source review. Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0."""
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
from random import Random

def need(ok, why):
    if not ok:
        raise ValueError(why)

def norm(a):
    return max(map(lambda row: sum(map(abs, row), F(0)), a))

def mul(a, b):
    return [[sum((x * y for x, y in zip(row, col)), F(0)) for col in zip(*b)] for row in a]

def subtract(a, b):
    return [[x - y for x, y in zip(row, other)] for row, other in zip(a, b)]

def inverse(a):
    """Gauss-Jordan against every identity column, independently of LU."""
    n = len(a)
    rows = [[F(x) for x in row] + [F(i == j) for j in range(n)] for i, row in enumerate(a)]
    for k in range(n):
        pivot = next((i for i in range(k, n) if rows[i][k]))
        rows[k], rows[pivot] = (rows[pivot], rows[k])
        scalar = rows[k][k]
        rows[k] = [v / scalar for v in rows[k]]
        for i in range(n):
            if i != k:
                scalar = rows[i][k]
                rows[i] = [v - scalar * w for v, w in zip(rows[i], rows[k])]
    need(all((rows[i][j] == int(i == j) for i in range(n) for j in range(n))), 'Gauss-Jordan exact identity')
    return [row[n:] for row in rows]

def action(a, x):
    return [sum((v * w for v, w in zip(row, x)), F(0)) for row in a]

def toward_zero(value, precision):
    value = F(value) * (1 << precision)
    integer = abs(value.numerator) // value.denominator
    return F(-integer if value < 0 else integer, 1 << precision)

def decode_pages(plan):
    n, b, p = (plan['n'], plan['band'], plan['precision'])
    low = [[F(i == j) for j in range(n)] for i in range(n)]
    upper = [[F(0) for _ in range(n)] for _ in range(n)]
    reciprocals = [None] * n
    for i in range(n):
        for slot in range(b):
            j = i - b + slot
            value = F(plan['lower'][i * b + slot], 1 << p)
            if j >= 0:
                low[i][j] = value
            else:
                need(value == 0, 'zero lower band padding')
    for position in range(n):
        i = n - 1 - position
        for slot in range(b):
            j = i + 1 + slot
            value = F(plan['upper'][position * (b + 1) + slot], 1 << p)
            if j < n:
                upper[i][j] = value
            else:
                need(value == 0, 'zero upper band padding')
        reciprocals[i] = F(plan['upper'][position * (b + 1) + b], 1 << p)
        upper[i][i] = 1 / reciprocals[i]
    return (low, upper, reciprocals)

def apply_rounded(plan, rhs):
    """Rational completed-row equations, not the packed-integer implementation."""
    low, upper, reciprocals = decode_pages(plan)
    n, p = (plan['n'], plan['precision'])
    b = [rhs[i] for i in plan['permutation']]
    y, x = ([F(0)] * n, [F(0)] * n)
    for i in range(n):
        y[i] = toward_zero(b[i] - sum((low[i][j] * y[j] for j in range(i))), p)
    for i in reversed(range(n)):
        x[i] = toward_zero(reciprocals[i] * (y[i] - sum((upper[i][j] * x[j] for j in range(i + 1, n)))), p)
    original = [F(0)] * n
    for i, address in enumerate(plan['permutation']):
        original[address] = x[i]
    return (original, x, y)

def check_case(module, a, target=12, radius=1):
    n = len(a)
    permutation = [j // 2 if j % 2 == 0 else n - 1 - j // 2 for j in range(n)]
    folded = [[a[i][j] for j in permutation] for i in permutation]
    band = max([1] + [abs(i - j) for i in range(n) for j in range(n) if folded[i][j]])
    plan = module.prepare(a, band, target, radius)
    need(plan['permutation'] == permutation, 'actual fold permutation')
    low, upper, reciprocals = decode_pages(plan)
    effective = mul(low, upper)
    h, d, m = (F(1, 1 << plan['precision']), plan['gap'], plan['mass'])
    need(norm(subtract(effective, folded)) <= plan['coefficient_constant'] * h, 'uniform effective-matrix perturbation')
    need(norm(inverse(effective)) <= 2 / d, 'effective inverse radius')
    need(norm(inverse(low)) <= 2 * m / d, 'rounded forward inverse radius')
    original_inverse = inverse(a)
    maximum_error = F(0)
    maximum_ratio = F(0)
    wrong_return_detected = False
    for offset in (0, 3):
        real = [F((3 * i + offset) % 7 - 3, 8) * radius for i in range(n)]
        imag = [F((5 * i + offset) % 5 - 2, 8) * radius for i in range(n)]
        need(max((abs(x) + abs(y) for x, y in zip(real, imag))) <= radius, 'input radius')
        expected = [action(original_inverse, values) for values in (real, imag)]
        computed = [apply_rounded(plan, values) for values in (real, imag)]
        error = max((abs(computed[0][0][i] - expected[0][i]) + abs(computed[1][0][i] - expected[1][i]) for i in range(n)))
        need(error <= plan['error_bound'] <= F(1, 1 << target), 'complete arbitrary-input theorem bound')
        need(max((abs(computed[0][2][i]) + abs(computed[1][2][i]) for i in range(n))) <= plan['forward_radius'], 'actual two-component forward radius')
        need(max((abs(computed[0][1][i]) + abs(computed[1][1][i]) for i in range(n))) <= plan['solution_radius'], 'actual two-component solution radius')
        residuals = [[x - y for x, y in zip(action(effective, result[1]), [values[i] for i in permutation])] for result, values in zip(computed, (real, imag))]
        need(max((abs(residuals[0][i]) + abs(residuals[1][i]) for i in range(n))) <= plan['solve_constant'] * h, 'actual completed-row residual bound')
        wrong = max((abs(computed[0][1][i] - expected[0][i]) + abs(computed[1][1][i] - expected[1][i]) for i in range(n)))
        wrong_return_detected |= wrong > plan['error_bound']
        maximum_error = max(maximum_error, error)
        maximum_ratio = max(maximum_ratio, error / plan['error_bound'])
    return ({'n': n, 'band': band, 'precision': plan['precision'], 'width': plan['width'], 'maximum_error': [maximum_error.numerator, maximum_error.denominator], 'maximum_bound_ratio': float(maximum_ratio), 'wrong_return_detected': wrong_return_detected}, plan)

def source_fixture(make_reference):
    ref = make_reference((9, 1, 1, 2, 3, 32))
    ref.require_narrow_gap()
    selected = [ref.selected[j] for j in range(9)]
    full = [[F(ref.entry('narrow', i, j).value) for j in selected] for i in selected]
    boundary = list(range(1, 9))
    schur = [[full[i][j] - full[i][0] * full[0][j] / full[0][0] for j in boundary] for i in boundary]
    return (ref, selected, full, schur)

def run(module, make_reference):
    random = Random(720053)
    results = []
    for n in range(1, 10):
        for scale in (F(1, 128), F(1), F(16)):
            a = [[F(0) for _ in range(n)] for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    if i != j and min((i - j) % n, (j - i) % n) <= 2:
                        a[i][j] = F(random.randrange(-7, 8), 8) * scale
                a[i][i] = sum(map(abs, a[i])) + F(random.randrange(1, 9), 16) * scale
            result, _ = check_case(module, a)
            results.append(result)
    ref, selected, original, schur = source_fixture(make_reference)
    source_result, plan = check_case(module, schur, target=16)
    need(source_result['wrong_return_detected'], 'original-reference return-order negative control')
    wrong_pivot_matrix = [[F(2), F(0)], [F(0), F(2)]]
    pivot_plan = module.prepare(wrong_pivot_matrix, 1, 12)
    _, effective_upper, reciprocals = decode_pages(pivot_plan)
    need(effective_upper[0][0] == 2 and reciprocals[0] == F(1, 2), 'stored reciprocal induces inverse diagonal, not itself')
    receipt = {'pages_sha256': sha256(Path(module.__file__).read_bytes()).hexdigest(), 'synthetic_cases': len(results), 'complex_rhs_per_case': 2, 'largest_observed_bound_ratio': max((r['maximum_bound_ratio'] for r in results)), 'source': {'parameters': [9, 1, 1, 2, 3, 32], 'selected_targets': selected, 'eliminated_source': [0], 'boundary_sources': list(range(1, 9)), 'reference_gap': str(ref.narrow_gap), 'result': source_result}, 'controls': ['omitted_unfold', 'reciprocal_not_effective_diagonal'], 'scope': 'Written universal bound review plus finite exact evidence; no physical execution here'}
    return receipt
