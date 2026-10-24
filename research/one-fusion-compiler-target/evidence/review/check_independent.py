#!/usr/bin/env python3
"""Independent positive-Taylor scalar audit; no author engine imports."""
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
GRID = 10**60


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def down(x):
    return Q((x * GRID).__floor__(), GRID)


def up(x):
    return Q((x * GRID).__ceil__(), GRID)


def logseries(z):
    need(0 <= z <= Q(1, 3), 'log domain')
    n = 48
    lo = sum((2*z**(2*j+1)/(2*j+1) for j in range(n)), Q(0))
    return lo, lo + 2*z**(2*n+1)/((2*n+1)*(1-z*z))


@lru_cache(None)
def ln(r):
    k = r.bit_length()-1
    x = Q(r, 2**k)
    a, b = logseries((x-1)/(x+1))
    c, d = logseries(Q(1, 3))
    return a+k*c, b+k*d


def exp_point(x):
    # Positive Taylor series with geometric upper bound on its positive tail.
    if x < 0:
        a, b = exp_point(-x)
        return down(1/b), up(1/a)
    s = 0
    while x > Q(1, 32):
        x /= 2
        s += 1
    term = total = Q(1)
    n = 24
    for j in range(1, n+1):
        term *= x/j
        total += term
    tail = (term*x/(n+1))/(1-x/(n+2))
    a, b = down(total), up(total+tail)
    for _ in range(s):
        a, b = down(a*a), up(b*b)
    return a, b


@lru_cache(None)
def rp(r, exponent):
    a, b = sorted(exponent*x for x in ln(r))
    return exp_point(a)[0], exp_point(b)[1]


def moment(profile, exponent):
    return tuple(sum((count*rp(r, exponent)[i] for r, count in profile.items()), Q(0))
                 for i in (0, 1))


def minus(a, b):
    return a[0]-b[1], a[1]-b[0]


def div(a, b):
    need(b[0] > 0, 'positive divisor')
    return a[0]/b[1], a[1]/b[0]


def scaled(a, x):
    return tuple(sorted(x*v for v in a))


def show(a):
    def fmt(q, upper=False):
        g = 10**36
        n = (q*g).__ceil__() if upper else (q*g).__floor__()
        return ('-' if n < 0 else '')+str(abs(n)//g)+'.'+str(abs(n)%g).zfill(36)
    return {'lower': fmt(a[0]), 'upper': fmt(a[1], True)}


def main():
    a = json.loads((HERE/'author/frozen/4610-round6-ARITHMETIC.json').read_text())
    t = {int(r): n for r, n in a['targets'].items()}
    p0 = {int(r): n for r, n in a['paid'].items()}
    p = p0.copy()
    p[1] -= 36
    p[2] += 18
    k, reserve = Q('.0030220'), Q(1, 10**11)
    tested = k+reserve
    need(k > Q('.0030217758'), 'candidate comparison')
    mass = lambda h: sum(r*n for r, n in h.items())
    need(mass(p) == mass(p0) and sum(p.values()) == sum(p0.values())-18,
         'full paid mass/position incidence')
    target, paid = moment(t, 1-tested), moment(p, 1-tested)
    margin = minus(target, paid)
    reserve_margin = minus(scaled(target, 1-reserve), paid)
    alpha = div(paid, target)
    gamma = div(moment(p, 1-tested+Q(1, 5)),
                (rp(20, Q(1, 5))[0]*target[0], rp(20, Q(1, 5))[1]*target[1]))
    delta = div((Q(21*sum(t.values())),)*2,
                (rp(20, tested)[0]*target[0], rp(20, tested)[1]*target[1]))
    eta = scaled(rp(145, -1024*tested), 1-tested)
    def logmoment(h, c):
        return tuple(sum((n*rp(r, 1-c)[i]*ln(r)[i] for r, n in h.items()), Q(0))
                     for i in (0, 1))
    derivative_upper = logmoment(p, Q(0))[1]-logmoment(t, tested)[0]
    need(margin[0] > 0 and reserve_margin[0] > 0 and derivative_upper < 0,
         'whole pretest monotonicity and tested reserve')
    need(alpha[1] < 1-reserve and gamma[1] < Q(97, 100)
         and delta[1] < Q(97, 100), 'contraction/tails')
    checks = {
        'normalized_paid': 1/(1+1024*reserve)+Q(4, 2**32) < 1,
        'split_round': 20**64 < 21**63,
        'two_tail_blocks': Q(97, 100)**128 < Q(1, 16),
        'shifted_exit_capacity': 2*20**(1024*64) <= 145**(1024*63),
        'eta_capacity': eta[0] > Q(63, 64)**1000,
        'initial_range': rp(145, 1024*tested)[1] < 2**1000,
    }
    gap = (tested-k)/7
    step = gap.denominator
    j, height = a['compiler']['integer_test_exponent'], a['compiler']['H']
    checks.update({
        'inherited_gap': gap == Q(a['compiler']['gap']) == Q(1, 700000000000),
        'height_encoding': height == step*j and height > 8*1024,
        'height_wins': (step*j+1)**1000 < 2**j,
        'preceding_exponent_fails': (step*(j-1)+1)**1000 >= 2**(j-1),
    })
    need(all(checks.values()), 'finite scalar capacity')
    author = json.loads((HERE/'author/COMPILER-POINT.json').read_text())
    for key, values in {'margin': margin, 'reserve_margin_M_minus_T_1e11': reserve_margin,
                        'alpha': alpha, 'gamma': gamma, 'delta': delta, 'eta': eta}.items():
        enclosure = author[key]
        need(Q(enclosure['lower']) <= values[0] <= values[1] <= Q(enclosure['upper']),
             'Independent enclosure not contained in author displayed '+key)
    ordinary = a['ordinary_BIT']
    ordinary_saving = (1-Q(ordinary['atom']))*Q(ordinary['after_cover'])+Q(ordinary['atom'])*Q('.0000384599')
    need(ordinary_saving == Q(ordinary['ordinary_saving']) > Q(ordinary['admitted']) > tested,
         'retained ordinary BIT source rational')
    outer = author['outer']
    need(len(outer['strict_checks']) == 54 and len(outer['functional_checks']) == 4
         and all(Q(v) > 0 for key in ('strict_checks', 'functional_checks')
                 for v in outer[key].values()), 'source-bound outer receipt positives')
    single = p0.copy()
    single[1] -= 2
    single[2] += 1
    free_deletion = p0.copy()
    free_deletion[1] -= 36
    # These are controls of the arithmetic premise, not physical-pair tests.
    controls = {
        'single_occurrence_is_not_18_occurrences': minus(moment(t, 1-k), moment(single, 1-k))[1] < 0,
        'deletion_without_rank2_changes_rank_mass': mass(free_deletion) != mass(p0),
        'larger_unfunded_reserve_rejected': minus(scaled(target, 1-Q(1, 10**7)), paid)[1] < 0,
        'physical_witness_still_absent': author['physical_witness_supplied'] is False,
    }
    need(all(controls.values()), 'arithmetic controls')
    print(json.dumps({
        'status': 'PASS_INDEPENDENT_CONDITIONAL_FIXED_POINT_SCALAR_REVIEW',
        'method': 'Positive Taylor exp with positive geometric tail,48-term atanh logs, '
                  'outward rational1e-60 rounding; no imports from author engines.',
        'kappa_candidate': str(k), 'tested': str(tested), 'reserve': str(reserve),
        'paid_delta': {'1': -36, '2': 18},
        'margin': show(margin), 'reserve_margin': show(reserve_margin),
        'alpha': show(alpha), 'gamma': show(gamma), 'delta': show(delta), 'eta': show(eta),
        'pretest_domain': ['0', str(tested)],
        'derivative_upper': show((derivative_upper, derivative_upper)),
        'finite_capacity': checks, 'controls': controls,
        'finite_height': height, 'integer_exponent': j,
        'outer54plus4': 'Receipt positive; formulas/source applicability separately reviewed, not a completeness certificate.',
        'scope': 'No physical witness, native/Gaussian operator execution, compiler word, Lean, root search or kappa admission.',
    }, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
