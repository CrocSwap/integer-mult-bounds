#!/usr/bin/env python3
"""Exact adaptive gate witnesses; Dillon with OpenAI Codex. Apache-2.0.

No predecessor executable is imported. Finite checks are not a proof kernel.
"""
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import hashlib
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def iroot(n, q):
    """Floor q-th root, checked against its defining inequalities."""
    require(n >= 0 and q > 0, "invalid root")
    lo, hi = 0, 1 << ((n.bit_length() + q - 1) // q)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if mid ** q <= n:
            lo = mid
        else:
            hi = mid
    require(lo ** q <= n < (lo + 1) ** q, "root bracket")
    return lo


@lru_cache(None)
def power(x, t):
    """Rational interval for positive integer x raised to rational t."""
    t = F(t)
    require(x >= 1, "positive rank required")
    if t < 0:
        low, high = power(x, -t)
        return 1 / high, 1 / low
    if t.denominator == 1:
        value = F(x ** t.numerator)
        return value, value
    scale = 2 ** 72
    radicand = x ** t.numerator * scale ** t.denominator
    lower = iroot(radicand, t.denominator)
    if lower ** t.denominator == radicand:
        return F(lower, scale), F(lower, scale)
    return F(lower, scale), F(lower + 1, scale)


def add(*intervals):
    return sum((x[0] for x in intervals), F(0)), sum((x[1] for x in intervals), F(0))


def mul(x, y):
    require(x[0] >= 0 and y[0] >= 0, "nonnegative intervals required")
    return x[0] * y[0], x[1] * y[1]


def div(x, y):
    require(y[0] > 0, "positive denominator required")
    return x[0] / y[1], x[1] / y[0]


def scale(x, c):
    return mul(x, (F(c), F(c)))


@lru_cache(None)
def log_int(x):
    """atanh series after exact binary range reduction; rational tail bound."""
    require(x >= 1, "log domain")
    exponent = x.bit_length() - 1
    y = F(x, 2 ** exponent)

    def series(z):
        # 0 <= z <= 1/3; omitted denominators are at least 2N+1.
        n = 80
        low = 2 * sum(z ** (2 * j + 1) / (2 * j + 1) for j in range(n))
        tail = 2 * z ** (2 * n + 1) / ((2 * n + 1) * (1 - z * z))
        return low, low + tail

    return add(scale(series(F(1, 3)), exponent), series((y - 1) / (y + 1)))


def exp_lower(x):
    require(x >= 0, "nonnegative exponential argument")
    term = total = F(1)
    for j in range(1, 81):
        term *= x / j
        total += term
    return total


def moment(profile, t):
    return add(*(scale(power(k, t), count) for k, count in profile.items()))


def mean(profile, t):
    numerator = add(*(scale(mul(power(k, t), log_int(k)), count)
                      for k, count in profile.items()))
    return div(numerator, moment(profile, t))


def windows(targets, paid):
    """Every mirror window is left-open/right-closed, including endpoints."""
    points = sorted({F(1, k) for k in targets} | {F(1, r) for r in paid})
    result = []
    for left, right in zip(points, points[1:]):
        z = (left + right) / 2
        sources, exits = [], []
        for k, w in targets.items():
            for r, count in paid.items():
                if k > r and F(1, k) < z <= F(1, r):
                    sources.append((r * k, w * count))
                if r > k and F(1, r) < z <= F(1, k):
                    exits.append((r * k, w * count))
        result.append((left, right, sources, exits))
    return result


def sum_terms(terms, t):
    return add(*(scale(power(rank, t), count) for rank, count in terms))


def log_factors(value):
    """Exact formal logarithm of a positive rational, in prime-log coordinates."""
    value = F(value)
    answer = {}
    for n, sign in ((value.numerator, 1), (value.denominator, -1)):
        divisor = 2
        while divisor * divisor <= n:
            while n % divisor == 0:
                answer[divisor] = answer.get(divisor, 0) + sign
                n //= divisor
            divisor += 1
        if n > 1:
            answer[n] = answer.get(n, 0) + sign
    return {p: e for p, e in answer.items() if e}


def mirror_integrals(targets, paid):
    """Exact symbolic checks of both new integral identities at t=1/2."""
    t = F(1, 2)
    lhs_log, rhs_log = {}, {}
    lhs_rank = F(0)

    def accumulate(out, weight, value):
        for prime, coefficient in log_factors(value).items():
            out[prime] = out.get(prime, F(0)) + weight * coefficient

    for left, right, sources, exits in windows(targets, paid):
        slo, shi = sum_terms(sources, t)
        elo, ehi = sum_terms(exits, t)
        require(slo == shi and elo == ehi, 'exact square-rank integral fixture')
        weight = slo - elo
        accumulate(lhs_log, weight, right / left)
        lroot, rroot = power(left.denominator, t), power(right.denominator, t)
        require(lroot[0] == lroot[1] and rroot[0] == rroot[1], 'exact endpoints')
        lhs_rank += 2 * weight * (lroot[0] - rroot[0])
    for k, w in targets.items():
        for r, count in paid.items():
            coefficient = power(k * r, t)
            require(coefficient[0] == coefficient[1], 'exact pair coefficient')
            accumulate(rhs_log, w * count * coefficient[0], F(k, r))
    clean = lambda row: {p: v for p, v in row.items() if v}
    require(clean(lhs_log) == clean(rhs_log), 'mirror log-integral identity')
    T, P = moment(targets, t)[0], moment(paid, t)[0]
    rhs_rank = (P * moment(targets, F(1))[0] - T * moment(paid, F(1))[0]) / (1 - t)
    require(lhs_rank == rhs_rank, 'mirror rank-integral identity')
    return {'log_integral_prime_coefficients': {str(p): str(v) for p, v in clean(lhs_log).items()},
            'rank_integral': str(lhs_rank)}


def certify(witness):
    targets = {int(k): v for k, v in witness['targets'].items()}
    paid = {int(k): v for k, v in witness['paid'].items()}
    require(targets and paid and min(targets) >= 2, "target domain")
    require(all(isinstance(v, int) and v > 0 for v in [*targets.values(), *paid.values()]),
            "positive multiplicities")
    m = max(targets)
    require(min(paid) >= 1 and max(paid) < m, "paid ranks must descend")
    t0, thi = F(witness['root']), F(witness['upper_exponent'])
    require(0 < t0 < thi < 1, "exponent domain")
    a, b, M = (witness[k] for k in ('a', 'b', 'M'))
    require(all(type(x) is int for x in (a, b, M)) and a > 0 and b > 0 and M > 1,
            "integer geometry")
    s, lam = F(witness['s']), F(witness['lambda'])
    require(s > 0 and lam > 0, "positive tails")
    g = a + b
    T0, P0 = moment(targets, t0), moment(paid, t0)
    require(T0[0] == T0[1] == P0[0] == P0[1], "exact moment crossing")
    d = F(witness['d'])
    require(d > 0 and mean(targets, t0)[0] - mean(paid, thi)[1] >= d,
            "uniform positive crossing derivative")
    # Tilted means are nondecreasing; rank >=1 makes all moments monotone.
    target_forward = div(moment(targets, t0 + s), moment(targets, t0))[0]
    paid_forward = div(moment(paid, thi + s), moment(paid, thi))[1]
    require(target_forward >= paid_forward, "uniform forward ordering")
    ut = div(moment(targets, thi + s), moment(targets, thi))[1]
    up = div(moment(paid, thi + s), moment(paid, thi))[1]
    U = power(M, -s)[1] * ut ** a * up ** b
    V = power(M, lam)[1] * div(moment(targets, thi - lam), P0)[1] ** g
    Q = div(moment(targets, thi), P0)[1]
    require(U < 1, "mixed tail")
    require(V < 1, "root tail")
    beta = F(witness['beta'])
    eta = t0 * power(m, t0 - 1)[0]
    require(0 <= beta < eta < 1, "strict mirror slack")
    mirror = []
    for left, right, sources, exits in windows(targets, paid):
        ehi, slo = sum_terms(exits, thi)[1], sum_terms(sources, t0)[0]
        require(ehi <= beta * slo, "uniform mirror window")
        mirror.append({'left': str(left), 'right': str(right),
                       'source_pairs': len(sources), 'exit_pairs': len(exits)})
    p, c = F(witness['p']), F(witness['c'])
    ell = witness['ell0']
    require(type(ell) is int and p > 0 and c >= p / (1 - t0) and ell >= 1,
            "concavity/base parameters")
    logn0 = add(log_int(m), scale(log_int(M), ell))
    tauhi = t0 + p / (c + logn0[0])
    require(tauhi <= thi, "local tangent exponent cover")
    denominator = c + log_int(m)[1] + (ell + 1) * log_int(M)[1] + log_int(2)[1]
    exponent = d * p * (a * ell + 1) / denominator
    lower = (1 - U ** ell) * (exp_lower(exponent) - 1) - Q * power(M, lam)[1] * V ** ell
    threshold = (1 - eta) / (eta - beta)
    require(lower >= threshold, "funded critical recurrence")

    def bracket(x, digits=6):
        factor = 10 ** digits
        low = x.numerator * factor // x.denominator
        return [str(F(low, factor)), str(F(low + 1, factor))]

    return {'root_moment': str(T0[0]), 'uniform_d': str(d),
            'U_upper_bound': bracket(U), 'V_upper_bound': bracket(V),
            'Q_upper_bound': bracket(Q),
            'beta': str(beta), 'eta_min': str(eta),
            'tau_n0_upper': bracket(tauhi), 'D_lower': bracket(lower),
            'required_D': str(threshold), 'mirror_windows': mirror,
            'mirror_integral_controls': mirror_integrals(targets, paid),
            'n0': f'{m}*{M}^{ell}',
            'scope': 'Exact finite sufficient guards; no native profile or outer admission.'}


def controls(witness):
    mutations = {
        'root equality': {'root': '65/128'},
        'derivative': {'d': '100'},
        'mixed tail': {'M': 16},
        'root tail': {'M': 2 ** 32},
        'mirror capacity': {'beta': '1/8'},
        'mirror window': {'beta': '0'},
        'tangent cover': {'ell0': 1},
        'concavity': {'c': '1'},
        'critical funding': {'p': '1'},
    }
    rejected = {}
    for name, changes in mutations.items():
        try:
            certify(dict(witness, **changes))
        except ValueError as error:
            rejected[name] = str(error)
        else:
            raise ValueError('accepted mutation: ' + name)
    for base in (1, 2, 4, 81, 256):
        for exponent in (F(-3, 4), F(0), F(1, 4), F(1, 2), F(33, 64)):
            lo, hi = power(base, exponent)
            p, q = exponent.numerator, exponent.denominator
            exact_power = F(base) ** p
            require(lo ** q <= exact_power <= hi ** q, 'power enclosure control')
    # This exact crossing has a genuinely uncovered boundary window.
    invalid = windows({4: 1, 16: 1}, {9: 2})
    require(any(sum_terms(e, F(1, 2))[0] > 0 and not s for _, _, s, e in invalid),
            'zero-source boundary control')
    return rejected


def counterexample():
    """Fixed-exponent surplus, mean separation AND mirror slack are insufficient."""
    targets, paid, t = {4: 4, 64: 17}, {1: 4, 16: 1}, F(1, 2)
    require(moment(targets, t) == (144, 144), 'counterexample target moment')
    require(moment(paid, t) == (8, 8), 'counterexample paid moment')
    require(mean(targets, t)[0] > mean(paid, t)[1], 'counterexample mean gap')
    ratios = []
    for left, right, sources, exits in windows(targets, paid):
        source, exit_ = sum_terms(sources, t), sum_terms(exits, t)
        require(source[0] == source[1] and exit_[0] == exit_[1], 'exact mirror values')
        require(source[0] > 0 or exit_[0] == 0, 'unfunded counterexample cell')
        ratios.append(exit_[0] / source[0] if source[0] else F(0))
        # Independent endpoint classification must equal each cell's interior.
        at_source, at_exit = [], []
        for k, w in targets.items():
            for r, count in paid.items():
                if k > r and F(1, k) < right <= F(1, r):
                    at_source.append((k * r, w * count))
                if r > k and F(1, r) < right <= F(1, k):
                    at_exit.append((k * r, w * count))
        require(at_source == sources and at_exit == exits, 'mirror endpoint convention')
    beta = max(ratios)
    eta = t * power(64, t - 1)[0]
    require(beta == F(1, 17) < eta == F(1, 16), 'counterexample mirror gap')
    # The single k=4 term alone gives equality at h=log4; the k=64 term
    # makes the true root-tail expression strictly larger. Jensen supplies
    # h>log4 from u<1. These arithmetic checks support the written all-lambda proof.
    require(4 * power(4, t)[0] / moment(paid, t)[0] == 1, 'obstruction coefficient')
    for lam in (F(1, 2), F(1), F(3, 2), F(2)):
        lower = power(4, lam)[0] * moment(targets, t - lam)[0] / 8
        require(lower > 1, 'root-tail obstruction fixture')
    return {'targets': targets, 'paid': paid, 't': str(t), 'T': 144, 'P': 8,
            'q': 18, 'beta': str(beta), 'eta': str(eta),
            'mirror_integral_controls': mirror_integrals(targets, paid),
            'scope': 'The written Jensen/single-term proof excludes every positive tail geometry.'}


def main():
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    sources = json.loads((package / 'SOURCES.json').read_text())
    for row in sources['files']:
        if row['usage'] == 'input':
            digest = hashlib.sha256((root / row['path']).read_bytes()).hexdigest()
            require(digest == row['sha256'], 'changed frozen input: ' + row['path'])
    witness = json.loads((package / 'WITNESS.json').read_text())
    result = certify(witness)
    result['rejections'] = controls(witness)
    result['counterexample'] = counterexample()
    # Compile the package-local checker directly: isolated Python omits this
    # directory from sys.path, and direct source loading avoids cached bytecode.
    application_path = package / 'root_application.py'
    namespace = {'__file__': str(application_path), '__name__': 'root_application'}
    exec(compile(application_path.read_bytes(), str(application_path), 'exec'), namespace)
    result['retained_profile_applications'] = namespace['run'](root)
    result['status'] = 'PASS_EXACT_ADAPTIVE_GATE_WITNESS'
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
