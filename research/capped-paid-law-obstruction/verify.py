#!/usr/bin/env python3
"""True-cap stop-loss obstruction; JoyboyBrian with OpenAI Codex, Apache-2.0."""
from fractions import Fraction as Q
from hashlib import sha256
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
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'Changed source: ' + row['path'])
    retained = manifest['retained_predecessor']
    need(sha256((HERE / retained['retained_path']).read_bytes()).hexdigest() == retained['sha256'],
         'Changed retained predecessor bytes')
    modules = []
    for name, filename in [('intervals', 'intervals.py'), ('capped_pinned_compiler', 'compiler.py')]:
        path = ROOT / 'research/net-tax-rank-compiler' / filename
        module = types.ModuleType(name)
        module.__file__ = str(path)
        sys.modules[name] = module
        exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
        modules.append(module)
    return modules


def stop_loss_upper(mean, variance):
    """(x-1)+ <= (x-mean)^2 / (4*(1-mean)), for mean < 1."""
    need(0 <= mean < 1 and variance >= 0, 'Stop-loss domain')
    return variance / (4 * (1 - mean))


def completed_mean(mean, excess):
    need(0 <= mean <= 1 and excess >= 0, 'Completed mean domain')
    return (mean + excess) / (1 + excess)


def controls(E):
    # Independent enumeration: Y in {0,3}, P(Y=3)=1/4, v=2.
    law = [(Q(0), Q(3, 4)), (Q(3), Q(1, 4))]
    pairs = [((a+b)/2, p*q) for a, p in law for b, q in law]
    mean = sum(x*p for x, p in pairs)
    variance = sum((x-mean)**2*p for x, p in pairs)
    capped = sum(min(x, 1)*p for x, p in pairs)
    tail = sum(max(x-1, 0)*p for x, p in pairs)
    need((mean, variance, capped, tail) == (Q(3, 4), Q(27, 32), Q(7, 16), Q(5, 16)),
         'Independent iid cap-crossing fixture')
    need(tail <= stop_loss_upper(mean, variance), 'Second-moment tail inequality')
    need(mean-tail == capped, 'Tail expectation subtraction')
    mutations = {
        'cap before averaging': sum(min(x, 1)*p for x, p in law),
        'tail probability as expectation': mean-sum(p for x, p in pairs if x > 1),
        'omitted paid completions': capped,
        'inverted paid normalization': (capped+Q(1, 2))*(1+Q(1, 2)),
    }
    for label, value in mutations.items():
        expected = capped if label in ('cap before averaging', 'tail probability as expectation') else Q(5, 8)
        need(value != expected, 'Mutation must be rejected: ' + label)
    need(completed_mean(capped, Q(1, 2)) == Q(5, 8), 'Full paid completion positive fixture')
    third = E.rounded(Q(1, 3), Q(1, 3))
    need(third[0] < Q(1, 3) < third[1], 'Directed rational rounding')
    return list(mutations)


def run():
    E, C = load_sources()
    mutations = controls(E)
    cases = json.loads((ROOT / 'research/net-tax-rank-compiler/BENCHMARKS.json').read_text())['cases']
    case = next(row for row in cases if row['name'] == 'native-concentrated-balanced')
    w = case['witness']
    need((w['saving'], w['v'], w['cutoff'], w['floor'], w['u'], w['log_shift'], w['p']) ==
         ('90037/30000000', 260, 20, 21, '171/1000', 3900, 24), 'Fixed witness')
    source = json.loads((ROOT / case['source']).read_text())
    d = C.tax_data(source, w)
    v, c, t = d['v'], d['c'], d['t']
    logc = E.log_bounds(c)
    sums = [(Q(0), Q(0)) for _ in range(3)]
    for rank, count in d['P'].items():
        weight = E.scale(E.power(rank, t), count)
        y = E.divide(E.log_bounds(rank), logc)
        for k in range(3):
            sums[k] = E.add(sums[k], E.mul(weight, E.ipow(y, k)))
    need(max(sums[0][0], d['paid'][0]) <= min(sums[0][1], d['paid'][1]), 'Paid normalization')
    need(sums[0][1] < d['target'][0], 'Target normalization rejected')
    mean, second = [E.divide(s, d['paid']) for s in sums[1:]]
    variance = E.scale(E.sub(second, E.ipow(mean, 2)), Q(1, v))
    need(variance[0] > 0 and mean[1] < 1, 'Actual iid variance and mean domain')
    tail_upper = stop_loss_upper(mean[1], variance[1])
    capped = (mean[0]-tail_upper, mean[1])
    beta = Q(w['weighted']['floor_log_lower'])
    eta = E.scale(E.ipow(E.power(d['m'], -d['C']), v), t)
    # A rational upper barrier on the admissible mean avoids root finding.
    barrier = Q(857, 1000)
    need((barrier/beta)**23 > eta[1], 'Necessary admissible mean is strictly below barrier')
    required_correction = mean[0]-barrier
    need(tail_upper < required_correction, 'True cap cannot bridge required first-moment correction')
    optimistic_top = (capped[0]/beta)**23
    need(optimistic_top > eta[1], 'Even exact capped mean with zero excess fails j23')
    full = E.add(d['original_tax'], E.scale(E.ipow(d['delta'], v), 2))
    relative = E.divide(full, E.ipow(d['alpha'], v))
    epsilon = Q(w['weighted']['paid_excess_upper'])
    need(0 < relative[0] <= relative[1] < epsilon, 'Full completion plus splitting bill')
    completed = tuple(completed_mean(x, epsilon) for x in capped)
    amin, amax, ambient = [Q(w['weighted'][key]) for key in ('A_lower', 'A_upper', 'ambient_log_lower')]
    A = E.scale(E.divide(E.log_bounds(2), logc), Q(w['log_shift'], v))
    need(amin <= A[0] <= A[1] <= amax, 'Source shift guard')
    need(ambient <= E.divide(E.log_bounds(d['m']), logc)[0], 'Ambient guard')
    need(beta <= E.divide(E.log_bounds(d['b']), logc)[0], 'Minimum-rank guard')
    need(mean[1] < Q(w['weighted']['raw_mean_upper']) and max(d['P'])**2 < c**3,
         'Source mean and support guards')
    chord = C.concentrated_moments(24, v, Q(w['weighted']['raw_mean_upper']),
                                  Q(w['weighted']['raw_log_bound']), epsilon)
    old = C.moment_coefficients(24, chord, amax, amin+ambient, beta)
    need(old[0] < eta[0], 'Unchanged p24 positive control')
    need(old[2][24] == chord[1]**24 and old[3][24] == beta**24, 'Highest coefficient identity')
    # Small exact two-point moment lists bind the same highest-coefficient identity.
    for p in (2, 3):
        moments = [Q(1)] + [Q(1, 2)]*p
        coeffs = C.moment_coefficients(p, moments, amax, amin+ambient, beta)
        need(coeffs[2][p] == Q(1, 2)**p and coeffs[3][p] == beta**p, 'Top identity calibration')
    def bounds(x):
        return {'exact': list(map(str, x)), 'display': E.display(x)}
    return {'status': 'PASS_TRUE_CAP_DEGREE23_OBSTRUCTION', 'witness': w,
            'candidate_degree': 23, 'raw_mean': bounds(mean), 'raw_second_moment': bounds(second),
            'iid_variance': bounds(variance), 'cap_correction_upper': bounds((Q(0), tail_upper)),
            'true_capped_mean': bounds(capped), 'necessary_mean_strict_upper': str(barrier),
            'required_cap_correction_strict_lower': str(required_correction),
            'required_cap_correction_display': E.display((required_correction,)*2),
            'optimistic_top_ratio_lower': str(optimistic_top),
            'optimistic_top_ratio_display': E.display((optimistic_top,)*2),
            'source_capacity': bounds(eta), 'full_paid_relative_excess': bounds(relative),
            'completed_majorant_mean': bounds(completed),
            'unchanged_p24_max_ratio': str(old[0]), 'controls': mutations,
            'no_new_uniform_rank': True,
            'scope': 'Fixed capped-reference coefficient certificate fails; not a lower bound on the actual completed law.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = run()
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(json.loads(path.read_text()) == result, 'Exact receipt mismatch')
    print(result['status'])
    for key in ('cap_correction_upper', 'true_capped_mean', 'source_capacity'):
        print(key, result[key]['display'])


if __name__ == '__main__':
    main()
