#!/usr/bin/env python3
"""Higher-moment strictification and a polynomial-logarithm compiler bound.

New arithmetic is independent of predecessor interval code. The unchanged
invoice replay and two outer ledgers are credited, byte-pinned oracles.
zxv with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
from collections import Counter
from contextlib import redirect_stdout
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256, sha1
import io
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRID = 2**192
C = Q('0.00268648')
KAPPA = Q('0.00268647')
T = {5:420, 6:270, 7:840, 8:1395, 9:3195,
     25:448, 41:448, 57:448, 121:224}
P = {1:37305, 2:10695, 3:3360, 4:1530, 5:300,
     8:1464, 16:448, 32:448, 48:448}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def down(x):
    return Q((x*GRID).__floor__(), GRID)


def up(x):
    return Q(-((-x*GRID).__floor__()), GRID)


def rounded(lo, hi):
    return down(lo), up(hi)


def mul(a, b):
    products = [x*y for x in a for y in b]
    return rounded(min(products), max(products))


def scale(a, x):
    return mul(a, (x, x))


def divide(a, b):
    need(b[0] > 0, 'positive interval denominator')
    return mul(a, rounded(1/b[1], 1/b[0]))


@lru_cache(None)
def log_bounds(n):
    """Exact atanh series, binary reduction; round only the final interval."""
    need(isinstance(n, int) and n >= 1, 'positive integer logarithm')

    def series(x):
        u = (x-1)/(x+1)
        term, total = u, Q(0)
        for j in range(80):
            total += 2*term/(2*j+1)
            term *= u*u
        tail = 2*term/(161*(1-u*u))
        return total, total+tail

    k = n.bit_length()-1
    a, b = series(Q(2))
    c, d = series(Q(n, 2**k))
    return rounded(k*a+c, k*b+d)


def exp_point(x):
    """Outward fixed-point Taylor enclosure, with binary scaling/squaring."""
    need(abs(x) < 16, 'bounded exponential argument')
    if x < 0:
        a, b = exp_point(-x)
        return rounded(1/b, 1/a)
    divisions = 0
    while x > Q(1, 2):
        x /= 2
        divisions += 1
    term = total = (Q(1), Q(1))
    for j in range(1, 65):
        term = scale(term, x/j)
        total = rounded(total[0]+term[0], total[1]+term[1])
    following = scale(term, x/65)
    # Every remaining ratio is <= 1/132. Twice the next term is safe.
    result = rounded(total[0], total[1]+2*following[1])
    for _ in range(divisions):
        result = mul(result, result)
    return result


def exp_interval(a):
    return exp_point(a[0])[0], exp_point(a[1])[1]


@lru_cache(None)
def power(n, exponent):
    return exp_interval(scale(log_bounds(n), exponent))


def moment(histogram, exponent):
    low = high = Q(0)
    for n, count in histogram.items():
        a, b = power(n, exponent)
        low += count*a
        high += count*b
    return rounded(low, high)


def display(a):
    unit = 10**30

    def fixed(n):
        sign = '-' if n < 0 else ''
        s = str(abs(n)).rjust(31, '0')
        return sign+s[:-30]+'.'+s[-30:]

    return {'lower': fixed((a[0]*unit).__floor__()),
            'upper': fixed(-((-a[1]*unit).__floor__()))}


def encoded(x):
    if isinstance(x, Q):
        return str(x)
    if isinstance(x, dict):
        return {str(k): encoded(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [encoded(v) for v in x]
    return x


def source_environment(path):
    env = {'__file__': str(path), '__name__': 'pinned_source_oracle'}
    exec(compile(path.read_bytes(), str(path), 'exec'), env)
    return env


def authenticate():
    result = {}
    for row in json.loads((HERE/'VENDOR.json').read_text())['files']:
        path = HERE/'vendor'/Path(row['path']).relative_to(
            'research/higher-moment-strictification/vendor')
        digest = sha256(path.read_bytes()).hexdigest()
        need(digest == row['sha256'], 'changed source: '+row['path'])
        raw = path.read_bytes()
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
             == row['git_blob'], 'changed Git source blob')
        result[row['path']] = digest
    return result


def invoice_oracle():
    """Run #4426 unchanged, rebinding only its two file-location globals."""
    path = HERE/'vendor/invoice-review/verify.py'
    env = source_environment(path)
    env.update(ROOT=path.parent, PHASES='DATA-PHASES.json')
    output = io.StringIO()
    with redirect_stdout(output):
        env['main']()
    result = json.loads(output.getvalue())
    need(result['status'] == 'PASS_PR4416_INVOICE_REBUILD', 'source invoice oracle')
    need({int(k): v for k, v in result['targets'].items()} == T
         and {int(k): v for k, v in result['paid'].items()} == P,
         'exact literal-word invoice')
    return result


def tail_certificate(v=150, cutoff=10, floor=15, u=Q(3, 10)):
    t = 1-C
    need(v >= 1 and 1 < cutoff < floor < 121, 'strict finite ranks')
    need(t+u >= 1, 'tail moment exponent at least one')
    target, paid = moment(T, t), moment(P, t)
    alpha = divide(paid, target)
    gamma = divide(moment(P, t+u), mul(power(cutoff, u), target))
    delta = divide((Q(sum(T.values())*floor),)*2,
                   mul(power(cutoff, C), target))
    limits = (1-Q(1, 10**8), Q(181, 200), Q(439, 500))
    for name, bounds, limit in zip(('alpha', 'gamma', 'delta'),
                                  (alpha, gamma, delta), limits):
        need(0 < bounds[0] <= bounds[1] < limit < 1, name+' certified limit')
    a, g, d = limits
    bound = 1/(1+v*(1-a))+2*g**v+2*d**v
    need(bound < 1, 'complete charged normalized moment')
    old_gamma = divide((Q(sum(k*n for k, n in P.items())),)*2,
                       mul(power(cutoff, C), target))
    old_lower = alpha[0]**v+2*old_gamma[0]**v
    need(old_lower > 1, 'rank-one-tail estimate fails at this tensor power')
    return {'tensor_power': v, 'cutoff_base': cutoff, 'floor_base': floor,
            'paid_moment_exponent': t+u, 'tail_offset_u': u,
            'tested_saving': C, 'alpha': display(alpha), 'gamma': display(gamma),
            'delta': display(delta), 'rational_upper_limits': limits,
            'normalized_paid_upper': bound, 'strict_moment_gap': display((1-bound,)*2),
            'old_rank_one_gamma': display(old_gamma),
            'old_rank_one_bound_lower': display((old_lower, old_lower)),
            'ambient': '121^'+str(v), 'minimum_target': str(floor)+'^'+str(v),
            'maximum_paid': str(cutoff)+'^'+str(v),
            'productive_fields_before_uniform_compiler': '7688^'+str(v),
            'rank_one_surplus': '131723^'+str(v)+'-131115^'+str(v),
            'materialized_product_or_uniform_word': False}


def uniform_rank(v):
    t, p, theta = 1-C, 13, Q(6, 7)
    gap = (C-KAPPA)/7
    uniform_saving = C-gap
    need(10**7 < 15**6, 'theta upper bound')
    need(2*(10**v)**7 <= (121**v)**6, 'shifted logarithm inequality')
    eta = scale(exp_interval(scale(log_bounds(121), -v*C)), t)
    need(eta[0] > theta**p, 'exit contraction below complement capacity')
    base = exp_interval(scale(log_bounds(121), v*C))
    need(base[1] < 2**p, 'entire ordinary base range fits')
    # Integer grid: gap*H is integral, avoiding enormous rational powers.
    step = gap.denominator
    need(gap.numerator == 1, 'chosen rational gap grid')

    def passes(j):
        H = step*j
        return (H+1)**p < 2**j

    lo, hi = 1, 2
    while not passes(hi):
        lo, hi = hi, 2*hi
    while hi-lo > 1:
        mid = (lo+hi)//2
        if passes(mid):
            hi = mid
        else:
            lo = mid
    H = step*hi
    need(H > 7*v and passes(hi) and not passes(hi-1), 'final integer comparison')
    need(eta[1] < theta**(p-1), 'one smaller logarithmic power fails')
    return {'t': t, 'uniform_saving': uniform_saving, 'gap': gap,
            'logarithm_power': p, 'theta_upper': theta, 'eta': display(eta),
            'eta_minus_theta_to_p': display((eta[0]-theta**p, eta[1]-theta**p)),
            'm_to_saving': display(base), 'H': H, 'N': '2^'+str(H),
            'integer_test': {'left_base': H+1, 'left_exponent': p,
                             'right_base': 2, 'right_exponent': hi},
            'grid_step': step, 'previous_grid_point_rejected': True,
            'smaller_logarithmic_power_rejected': True}


def power_majorant_comparison(v, uniform_saving):
    """Retain #4416's older power proof, changing only the new unit's ranks."""
    t, z, h = 1-C, 1-uniform_saving, Q(1, 7)
    z0 = (t+z)/2
    delta = z0-t
    B, debt = (4+7*h)*v, 1+7*v*(1-z0)
    ratio = (delta*B+debt)/(h*delta)
    H0 = -((-ratio.numerator)//ratio.denominator)
    ratio = H0*(1-z0)/(z-z0)
    H1 = ratio.numerator//ratio.denominator+1
    need(H0 >= 7*v and H0*h*delta >= delta*B+debt, 'power majorant threshold')
    need((H0-1)*h*delta < delta*B+debt, 'previous power threshold rejected')
    need(H1*(z-z0) > H0*(1-z0) >= (H1-1)*(z-z0),
         'strict power-majorant comparison and previous-rank control')
    return {'H0': H0, 'H1': H1, 'N': '2^'+str(H1), 'theta_upper': 1-h,
            'scope': 'Tail transformation alone, retaining the older power majorant.'}


def outer_ledger(uniform_saving):
    d = (C-KAPPA)/7
    params = {'kappa': KAPPA, 'tested_saving': C,
              'complex_uniform_saving': uniform_saving, 'b': KAPPA+5*d,
              'a': KAPPA+4*d, 'q': KAPPA+3*d, 'bit_saving': Q('0.0027'),
              'epsilon': 1-d, 'beta': 1-3*d, 'r0': d/10,
              'stop': d, 'layout': d, 'd': d}
    env = source_environment(HERE/'vendor/outer_endpoint.py')
    row = env['ledger'](params)
    need(len(row['strict_checks']) == 54 and len(row['functional_checks']) == 3,
         'complete first outer ledger')
    need(all(v > 0 for group in ('strict_checks', 'functional_checks')
             for v in row[group].values()), 'all outer predicates')
    frozen = json.loads((HERE/'vendor/p7-RESULT.json').read_text())['endpoint']['outer']
    need(encoded(row) == frozen, 'unchanged full p7 endpoint ledger')
    parsed = ast.parse((HERE/'vendor/check_ledger.py').read_bytes())
    function = next(n for n in parsed.body
                    if isinstance(n, ast.FunctionDef) and n.name == 'ledger')
    constants = [n for n in parsed.body if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id.startswith('KAPPA_')
                         for t in n.targets)]
    eps, beta, q, a = (params[k] for k in ('epsilon', 'beta', 'q', 'a'))
    grid = 10**10
    backoff = Q((eps*q*grid).__floor__(), grid)-KAPPA
    need(backoff > 0, 'strict derived oracle grid backoff')
    oracle = {'Q': Q, 'R0': params['r0'], 'ZETA': Q(1, 10**8),
              'SLACK': d, 'STOP': d, 'FLOOR': grid, 'BACKOFF': backoff,
              'EPS': eps, 'BETA': beta, 'THETA_POWER': Q(2),
              'HALO_POWER': 48, 'CORE_POWER': 128, 'STRASSEN_TAU': Q(45, 16),
              'b': params['b'], 'q': q, 'a': a, 'bit': params['bit_saving'],
              'online': Q('0.001730970419199163702738'),
              'old': Q('0.001730970419199163702738')}
    code = ast.fix_missing_locations(ast.Module(body=constants+[function], type_ignores=[]))
    exec(compile(code, 'pinned 63-predicate ledger', 'exec'), oracle)
    second = oracle['ledger']('higher_moment_smaller_ranks')
    need(second['kappa'] == KAPPA and second['margins'] == row['margins'],
         'all nine rows match both ledgers')
    need(len(second['strict_checks']) == 63 and
         all(v > 0 for v in second['strict_checks'].values()), 'all 63 legacy predicates')
    controls = {}
    for name, updates in [('closed_epsilon', {'epsilon': Q(1)}),
                          ('missing_layout', {'layout': Q(0)}),
                          ('unfunded_kappa', {'kappa': C}),
                          ('closed_uniform_gap', {'complex_uniform_saving': params['b']}),
                          ('insufficient_BIT', {'bit_saving': Q('0.0023')})]:
        bad = env['ledger'](dict(params, **updates))
        failed = sorted(k for k, v in bad['strict_checks'].items() if v <= 0)
        need(failed, 'outer control rejected: '+name)
        controls[name] = failed
    for name, options in [('old_per_axis_scan', {'old_scan': True}),
                          ('group_equals_dimension', {'beta_': eps})]:
        bad = oracle['ledger']('reject_'+name, **options)
        failed = sorted(k for k, v in bad['strict_checks'].items() if v <= 0)
        need(failed, 'legacy control rejected: '+name)
        controls[name] = failed
    return {'ledger': row, 'legacy_63_checks': second['strict_checks'],
            'legacy_grid': grid, 'legacy_backoff': backoff,
            'minimum_margin_minus_kappa': min(row['margins'].values())-KAPPA,
            'rejected_controls': controls}


def finite_controls():
    def tensor(histogram):
        out = Counter()
        for k, n in histogram.items():
            for h, b in histogram.items():
                out[k*h] += n*b
        return out

    def split(histogram, cutoff):
        out = Counter()
        for k, n in histogram.items():
            q, r = divmod(k, cutoff)
            out[cutoff] += q*n
            if r:
                out[r] += n
        return +out

    target, paid = tensor({2:1, 5:1}), tensor({1:2, 4:1})
    padded, completion = Counter(), Counter()
    for k, n in target.items():
        padded[max(k, 9)] += n
        if k < 9:
            completion[9-k] += n
    final = split(paid+completion, 4)
    mass = lambda x: sum(k*n for k, n in x.items())
    need(mass(padded)-mass(final) == 7**2-6**2 == 13, 'exact paid padding mass')
    need(min(padded) > max(final), 'exact toy separation')
    need(final == Counter({1:5, 4:9}), 'literal toy expanded inventory')
    # t=1/2, sigma=3/4, R=100, J=1 refutes a sublinear tail extension.
    invalid = power(100, Q(1, 2))[1]+2*power(100, Q(3, 4))[1]
    need(invalid < 100, 'sublinear upper-tail moment cannot bound splitting')
    return {'toy_targets': padded, 'toy_paid': final, 'rank_one_surplus': 13,
            'sublinear_tail_counterexample': {'R': 100, 'J': 1, 't': '1/2',
                                             'sigma': '3/4', 'actual_charge': 100,
                                             'invalid_upper': display((invalid, invalid))}}


def verify():
    sources = authenticate()
    invoice = invoice_oracle()
    tail = tail_certificate()
    rank = uniform_rank(tail['tensor_power'])
    endpoint = outer_ledger(rank['uniform_saving'])
    controls = finite_controls()
    rejected = []
    for name, updates, expected in [
        ('too_short_product', {'v': 100}, 'complete charged normalized moment'),
        ('sublinear_tail', {'u': C/2}, 'tail moment exponent at least one'),
        ('lost_separation', {'floor': 10}, 'strict finite ranks'),
    ]:
        try:
            tail_certificate(**updates)
        except ValueError as error:
            need(str(error) == expected, 'wrong rejection: '+name)
            rejected.append({'mutation': name, 'failed_at': str(error)})
        else:
            raise ValueError('accepted mutation: '+name)
    old = json.loads((HERE/'vendor/p7-RESULT.json').read_text())['endpoint']['compiler']
    return encoded({'schema': 'higher-moment-native-strictification/1',
                    'status': 'PASS_HIGHER_MOMENT_STRICTIFICATION', 'kappa': KAPPA,
                    'invoice_oracle': invoice, 'strictification': tail,
                    'uniform_rank': rank, 'outer': endpoint,
                    'tail_only_power_majorant': power_majorant_comparison(
                        tail['tensor_power'], rank['uniform_saving']),
                    'finite_controls': controls, 'rejected_mutations': rejected,
                    'predecessor_H': old['H1'],
                    'rank_exponent_reduction_factor': Q(old['H1'], rank['H']),
                    'tensor_power_reduction_factor': Q(6240, tail['tensor_power']),
                    'source_sha256': sources,
                    'verifier_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
                    'scope': 'Conditional charged transformation and finite compiler rank. Native all-column, physical, analytic, precision, storage, fixed-tape and recovery premises remain inherited. No new kappa, selected frontier or practical word.'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = verify()
    if args.out:
        need(not args.out.exists(), 'new output path required')
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(json.loads((HERE/'RESULT.json').read_text()) == result, 'changed saved receipt')
    print(json.dumps({'status': result['status'], 'tensor_power': result['strictification']['tensor_power'],
                      'uniform_rank': result['uniform_rank']['N'],
                      'strict_moment_gap': result['strictification']['strict_moment_gap'],
                      'kappa': result['kappa']}))


if __name__ == '__main__':
    main()
