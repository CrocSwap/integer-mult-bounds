#!/usr/bin/env python3
"""Actual raw log moments for one fixed compiler witness; stdlib only.

JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
Retains zxv's compiler and outward interval arithmetic unchanged.
"""
from fractions import Fraction as Q
from hashlib import sha256
from math import comb, factorial
from pathlib import Path
import argparse
import json
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_sources():
    rows = json.loads((HERE / 'SOURCES.json').read_text())['files']
    for row in rows:
        if row['usage'] == 'input':
            need(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'Changed source: ' + row['path'])
    base = ROOT / 'research/net-tax-rank-compiler'
    modules = []
    for name, path in [('intervals', base / 'intervals.py'),
                       ('raw_log_pinned_compiler', base / 'compiler.py')]:
        module = types.ModuleType(name)
        module.__file__ = str(path)
        sys.modules[name] = module
        exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
        modules.append(module)
    return modules


def raw_moments(E, weights, log_values, degree, denominator):
    mass = (Q(0), Q(0))
    for weight in weights:
        mass = E.add(mass, weight)
    need(max(mass[0], denominator[0]) <= min(mass[1], denominator[1]),
         'Raw law normalization must use its paid mass')
    out = [(Q(1), Q(1))]
    for n in range(1, degree + 1):
        value = (Q(0), Q(0))
        for weight, logarithm in zip(weights, log_values):
            value = E.add(value, E.mul(weight, E.ipow(logarithm, n)))
        out.append(E.divide(value, denominator))
    return out


def iid_bell(E, raw, v):
    degree = len(raw) - 1
    zero, one = (Q(0), Q(0)), (Q(1), Q(1))
    bell = [[zero for _ in raw] for _ in raw]
    bell[0][0] = one
    falling = [1]
    for k in range(1, degree + 1):
        falling.append(falling[-1] * (v - k + 1) if k <= v else 0)
    out = [one]
    for n in range(1, degree + 1):
        for k in range(1, n + 1):
            value = zero
            for j in range(1, n - k + 2):
                value = E.add(value, E.scale(E.mul(raw[j], bell[n-j][k-1]), comb(n-1, j-1)))
            bell[n][k] = value
        value = zero
        for k in range(1, n + 1):
            value = E.add(value, E.scale(bell[n][k], falling[k]))
        out.append(E.scale(value, Q(1, v**n)))
    return out


def iid_egf(E, raw, v):
    degree = len(raw) - 1
    def multiply(a, b):
        out = [(Q(0), Q(0)) for _ in raw]
        for n in range(degree + 1):
            for j in range(n + 1):
                out[n] = E.add(out[n], E.mul(a[j], b[n-j]))
        return out
    base = [E.scale(value, Q(1, factorial(n))) for n, value in enumerate(raw)]
    power = [(Q(1), Q(1))] + [(Q(0), Q(0))] * degree
    exponent = v
    while exponent:
        if exponent & 1:
            power = multiply(power, base)
        exponent //= 2
        if exponent:
            base = multiply(base, base)
    return [E.scale(value, Q(factorial(n), v**n)) for n, value in enumerate(power)]


def completed(E, raw_tensor, epsilon):
    need(epsilon >= 0, 'Full paid excess is nonnegative')
    one = (Q(1), Q(1))
    return [one] + [tuple(min(Q(1), x) for x in
                         E.divide(E.add(value, (epsilon, epsilon)),
                                  (1 + epsilon, 1 + epsilon)))
                    for value in raw_tensor[1:]]


def controls(E):
    # Tiny exact iid law: Y in {0,2}, equal weights, two copies.
    raw = [(Q(1), Q(1))] + [(Q(2**(n-1)),) * 2 for n in range(1, 7)]
    expected = [Q(1)] + [Q(1, 2) + Q(2**n, 4) for n in range(1, 7)]
    for oracle in (iid_bell, iid_egf):
        bounds = oracle(E, raw, 2)
        need(all(lo <= exact <= hi for (lo, hi), exact in zip(bounds, expected)),
             'Exact enumerated iid positive fixture')
    need(expected[2] != raw[2][0], 'Missing average normalization changes fixture')
    perturbed = completed(E, [(Q(1),)*2, (Q(0),)*2], Q(1, 2))[1]
    need(perturbed[0] <= Q(1, 3) <= perturbed[1] and perturbed[0] > 0,
         'Full paid added mass cannot be omitted')
    exact = Q(1, 3)
    outward = E.rounded(exact, exact)
    need(outward[0] < exact < outward[1], 'Non-grid outward rounding fixture')
    def enclose(bounds):
        need(bounds[0] <= exact <= bounds[1], 'Inward rounding rejected')
    enclose(outward)
    try:
        enclose((outward[1], outward[1]))
    except ValueError as error:
        need('Inward' in str(error), 'Specific inward-rounding rejection')
    else:
        raise ValueError('Inward rounding accepted')


def run():
    E, C = load_sources()
    controls(E)
    cases = json.loads((ROOT / 'research/net-tax-rank-compiler/BENCHMARKS.json').read_text())['cases']
    case = next(row for row in cases if row['name'] == 'native-concentrated-balanced')
    witness = case['witness']
    need(witness['saving'] == '90037/30000000' and witness['v'] == 260
         and witness['cutoff'] == 20 and witness['floor'] == 21
         and witness['u'] == '171/1000' and witness['log_shift'] == 3900
         and witness['p'] == 24 and Q(witness['kappa']) == Q('.00300120'),
         'Fixed assigned witness')
    source = json.loads((ROOT / case['source']).read_text())
    data = C.tax_data(source, witness)
    options = witness['weighted']
    v, c, m, t = data['v'], data['c'], data['m'], data['t']
    logc = E.log_bounds(c)
    P = data['P']
    ranks = sorted(P)
    weights = [E.scale(E.power(rank, t), P[rank]) for rank in ranks]
    logs = [E.divide(E.log_bounds(rank), logc) for rank in ranks]
    raw = raw_moments(E, weights, logs, 24, data['paid'])
    try:
        raw_moments(E, weights, logs, 1, data['target'])
    except ValueError as error:
        need('normalization' in str(error), 'Specific paid/target mass rejection')
    else:
        raise ValueError('Wrong raw paid normalization accepted')
    bell, egf = iid_bell(E, raw, v), iid_egf(E, raw, v)
    need(all(max(a[0], b[0]) <= min(a[1], b[1]) for a, b in zip(bell, egf)),
         'Independent Bell/EGF interval agreement')
    tensor = [(max(a[0], b[0]), min(a[1], b[1])) for a, b in zip(bell, egf)]
    second = E.scale(E.add(raw[2], E.scale(E.ipow(raw[1], 2), v-1)), Q(1, v))
    need(max(tensor[1][0], raw[1][0]) <= min(tensor[1][1], raw[1][1])
         and max(tensor[2][0], second[0]) <= min(tensor[2][1], second[1]),
         'Independent first and second iid moment formulas')
    full_excess = E.add(data['original_tax'], E.scale(E.ipow(data['delta'], v), 2))
    relative_excess = E.divide(full_excess, E.ipow(data['alpha'], v))
    epsilon = Q(options['paid_excess_upper'])
    need(0 < relative_excess[0] <= relative_excess[1] < epsilon, 'Full paid excess retained')
    mu = completed(E, tensor, epsilon)
    A = E.scale(E.divide(E.log_bounds(2), logc), Q(witness['log_shift'], v))
    amin, amax, ambient, beta = [Q(options[key]) for key in
                                ('A_lower', 'A_upper', 'ambient_log_lower', 'floor_log_lower')]
    need(amin <= A[0] <= A[1] <= amax, 'Same normalized log shift')
    need(ambient <= E.divide(E.log_bounds(m), logc)[0], 'Same ambient log bound')
    need(beta <= E.divide(E.log_bounds(data['b']), logc)[0], 'Same minimum rank log bound')
    need(raw[1][1] < Q(options['raw_mean_upper']), 'Source raw mean bound')
    need(max(P)**2 < c**3, 'Source raw support bound')
    eta = E.scale(E.ipow(E.power(m, -data['C']), v), t)
    low = C.moment_coefficients(23, [x[0] for x in mu[:24]], amax, amin + ambient, beta)
    high = C.moment_coefficients(23, [x[1] for x in mu[:24]], amax, amin + ambient, beta)
    ratios = [(a / d, b / d) for a, b, d in zip(low[2], high[2], high[3])]
    need(ratios[23] == ((mu[1][0]/beta)**23, (mu[1][1]/beta)**23),
         'Highest coefficient depends only on first moment')
    failed = [j for j, bounds in enumerate(ratios) if bounds[0] > eta[1]]
    need(23 in failed, 'Fixed degree23 certificate has rigorous coefficient obstruction')
    chord = C.concentrated_moments(24, v, Q(options['raw_mean_upper']), Q(options['raw_log_bound']), epsilon)
    need(mu[0] == (Q(1), Q(1)) and chord[0] == 1, 'Normalized zeroth moments')
    need(all(bounds[1] < old for bounds, old in zip(mu[1:], chord[1:])),
         'Actual moments strictly sharpen every positive chord moment')
    old24 = C.moment_coefficients(24, chord, amax, amin + ambient, beta)
    need(old24[0] < eta[0], 'Unchanged degree24 positive certificate')
    optimistic_top = E.ipow(E.scale(raw[1], 1/beta), 23)
    need(optimistic_top[0] > eta[1], 'Even zero paid excess leaves top coefficient obstruction')
    base_cost = E.ipow(E.power(m, data['C']), v)
    base_factor = E.ipow(E.add((Q(1),)*2, E.scale(E.scale(E.divide(E.log_bounds(m), E.log_bounds(2)), v), Q(1, witness['log_shift']))), 23)
    return {'status': 'PASS_FIXED_RAW_MOMENT_DEGREE23_OBSTRUCTION',
            'scope': 'Fixed sufficient coefficient certificate, not impossibility of the compiler or actual completed law',
            'witness': witness, 'candidate_degree': 23, 'interval_grid_bits': 192,
            'raw_paid_histogram': {str(rank): P[rank] for rank in ranks},
            'raw_log_moments': [list(map(str, x)) for x in raw],
            'iid_average_bell_moments': [list(map(str, x)) for x in bell],
            'iid_average_egf_moments': [list(map(str, x)) for x in egf],
            'completed_capped_reference_moments': [list(map(str, x)) for x in mu],
            'full_paid_relative_excess': E.display(relative_excess),
            'source_complement_capacity': E.display(eta),
            'coefficient_ratios': [{'j': j, 'exact_lower': str(bounds[0]), 'exact_upper': str(bounds[1]),
                                    'display': E.display(bounds),
                                    'comparison': 'FAIL' if bounds[0] > eta[1] else ('PASS' if bounds[1] < eta[0] else 'UNDECIDED')}
                                   for j, bounds in enumerate(ratios)],
            'strictly_failed_coefficients': failed,
            'top_coefficient_gap': E.display(E.sub(ratios[23], eta)),
            'optimistic_zero_excess_top_ratio': E.display(optimistic_top),
            'source_degree24_chord_ratio': E.display((old24[0],)*2),
            'degree23_base_range_passes': base_cost[1] < base_factor[0],
            'net_tax_charge': E.display(data['bound']),
            'new_uniform_N': None, 'final_rank_and_outer_guard_status': 'NOT_REACHED: exit coefficient certificate fails',
            'controls': ['exact enumerated two-point iid law', 'paid versus target mass normalization rejected',
                         'full added paid mass retained', 'inward rounding rejected', 'unchanged p24 chord certificate passes']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = run()
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(path.read_text()) == result, 'Changed exact receipt')
    print(result['status'], 'failed coefficients:', result['strictly_failed_coefficients'])


if __name__ == '__main__':
    main()
