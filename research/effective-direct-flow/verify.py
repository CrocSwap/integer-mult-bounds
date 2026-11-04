#!/usr/bin/env python3
"""Exact hypotheses and finite controls for the effective direct-flow proof.

Prepared for @alephnan with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor numerical engine is imported. The all-size conclusion rests on
the written proofs and their stated classical Fourier approximation theorem.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import ast
import hashlib
import json
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRID = 1 << 128
S = Q(99739, 100000)
ALPHA_LO = Q('0.98981438244597')
ALPHA_HI = Q('0.98981438244599')
ONSET_EXPONENT = 10**12


def need(condition, message):
    if not condition:
        raise ValueError(message)


def ceiling(a, b):
    return -((-a)//b)


class Box:
    """Integer endpoints on a dyadic grid, with directed rounding."""
    def __init__(self, value=0, upper=None, *, raw=False):
        if raw:
            self.l, self.h = value, upper
        else:
            lo, hi = Q(value), Q(value if upper is None else upper)
            self.l = lo.numerator*GRID//lo.denominator
            self.h = ceiling(hi.numerator*GRID, hi.denominator)
        need(self.l <= self.h, 'reversed interval')

    @staticmethod
    def cast(value):
        return value if isinstance(value, Box) else Box(value)

    @property
    def lo(self):
        return Q(self.l, GRID)

    @property
    def hi(self):
        return Q(self.h, GRID)

    def __add__(self, other):
        v = self.cast(other)
        return Box(self.l+v.l, self.h+v.h, raw=True)

    __radd__ = __add__

    def __neg__(self):
        return Box(-self.h, -self.l, raw=True)

    def __sub__(self, other):
        return self + -self.cast(other)

    def __rsub__(self, other):
        return self.cast(other) + -self

    def __mul__(self, other):
        v = self.cast(other)
        products = (self.l*v.l, self.l*v.h, self.h*v.l, self.h*v.h)
        return Box(min(products)//GRID, ceiling(max(products), GRID), raw=True)

    __rmul__ = __mul__

    def __truediv__(self, other):
        v = self.cast(other)
        need(v.l*v.h > 0, 'division interval contains zero')
        return self*Box(GRID*GRID//v.h, ceiling(GRID*GRID, v.l), raw=True)

    def __pow__(self, degree):
        need(type(degree) is int and 0 <= degree <= 8, 'power domain')
        result = Box(1)
        for _ in range(degree):
            result = result*self
        return result

    def display(self, digits=10):
        scale = 10**digits
        def fmt(value):
            sign = '-' if value < 0 else ''
            whole, frac = divmod(abs(value), scale)
            return f'{sign}{whole}.{frac:0{digits}d}'
        return [fmt(self.l*scale//GRID), fmt(ceiling(self.h*scale, GRID))]


def reduced_log(x):
    """2 atanh((x-1)/(x+1)), 80 positive terms and geometric tail."""
    need(Q(1) <= x <= 2, 'reduced logarithm domain')
    z = Box((x-1)/(x+1))
    z2, term, result = z*z, z, Box(0)
    for j in range(80):
        result += 2*term/(2*j+1)
        term *= z2
    remainder = 2*term/(161*(1-z2))
    return Box(result.l, result.h+remainder.h, raw=True)


@lru_cache(None)
def log_integer(rank):
    need(type(rank) is int and 1 <= rank <= 121, 'logarithm rank domain')
    power = rank.bit_length()-1
    return reduced_log(Q(rank, 1 << power)) + power*reduced_log(Q(2))


def exponential_point(x):
    x = Q(x)
    need(-6 <= x <= 6, 'exponential domain')
    if x < 0:
        return Box(1)/exponential_point(-x)
    z = Box(x/16)
    term, result = Box(1), Box(1)
    for j in range(1, 49):
        term = term*z/j
        result += term
    # Remaining terms start at 49; successive ratios are at most z/50.
    tail = term*z/49/(1-z/50)
    result = Box(result.l, result.h+tail.h, raw=True)
    for _ in range(4):
        result *= result
    return result


def power(rank, exponent):
    z = log_integer(rank)*Box.cast(exponent)
    return Box(exponential_point(z.lo).l, exponential_point(z.hi).h, raw=True)


def authenticate():
    manifest = json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))
    inputs = {}
    for entry in manifest['files']:
        if entry['usage'] == 'input':
            path = ROOT/entry['path']
            data = path.read_bytes()
            need(hashlib.sha256(data).hexdigest() == entry['sha256'],
                 'source SHA256 mismatch: '+entry['path'])
            blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            need(blob == entry['git_blob'], 'source Git blob mismatch')
            inputs[entry['path']] = data
    return inputs


def inventory(data):
    values = {}
    for node in ast.parse(data).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            name = getattr(node.targets[0], 'id', None)
            if name in ('P', 'W', 'M'):
                values[name] = ast.literal_eval(node.value)
    need(set(values) == {'P', 'W', 'M'}, 'literal inventory missing')
    need(values['M'] == 121, 'wrong historical width')
    return values['P'], values['W'], values['M']


def certify_law(paid, targets, width):
    alpha = Box(ALPHA_LO, ALPHA_HI)
    centre = log_integer(5)
    need(centre.hi < 2 and log_integer(121).hi < 5, 'source shift bounds')
    need(Q(2, 3) < log_integer(2).lo and log_integer(2).hi < Q(7, 10),
         'log two frequency bounds')
    need(1 < log_integer(3).lo and log_integer(3).hi < Q(11, 10)
         and log_integer(6).hi < 2, 'log three and six frequency bounds')
    for endpoint, direction in ((ALPHA_LO, -1), (ALPHA_HI, 1)):
        mean_residual = sum((c*power(r, endpoint)*(log_integer(r)-centre)
                             for r, c in paid.items()), Box())
        need(mean_residual.h < 0 if direction < 0 else mean_residual.l > 0,
             'tilted-mean root not bracketed')
    ranks = sorted(set(paid)|set(targets))
    pa = {r: power(r, alpha) for r in ranks}
    ps = {r: power(r, S) for r in ranks}
    mass = sum((c*pa[r] for r, c in paid.items()), Box())
    target_mass = sum((c*pa[k] for k, c in targets.items()), Box())
    probabilities = {r: c*pa[r]/mass for r, c in paid.items()}
    for r, bound in ((1, Q(1, 4)), (2, Q(1, 8)), (3, Q(1, 16))):
        need(r in probabilities and probabilities[r].lo > bound, 'missing atom mass')
    variance, third = Box(), Box()
    for r, probability in probabilities.items():
        distance = log_integer(r)-centre if r >= 5 else centre-log_integer(r)
        need(distance.lo >= -Q(1, 10**30) and distance.hi < 3, 'centred support bound')
        variance += probability*distance**2
        third += probability*distance**3
    need(2 < variance.lo < variance.hi < Q(5, 2), 'variance bound')
    need(third.hi < 5, 'third absolute moment bound')
    gap, ratio, tau = mass-target_mass, target_mass/mass, Box(S)-alpha
    need(0 < gap.lo < gap.hi < 2000, 'tilted gap')
    need(ratio.hi < Q(247, 250), 'geometric layer ratio')
    need(tau.lo > Q(3, 400), 'leaf decay rate')
    terminal = sum((c*ps[r] for r, c in paid.items()), Box())/ps[width]
    need(terminal.hi < 2000, 'complete terminal leaf coefficient')

    # Exact positive-binomial lower sum for the full source capacity.
    # Its omitted tail is NONNEGATIVE, so it is not needed for this lower bound.
    weights = {r: Box() for r in ranks}
    boundary = Box()
    for r, pr in paid.items():
        for k, tk in targets.items():
            if k > r:
                weights[k] += pr*tk*pa[r]
                weights[r] -= pr*tk*pa[k]
            elif r > k:
                boundary += pr*tk*(pa[k]*ps[r]-pa[r]*ps[k])
    powers = {r: Box(1) for r in ranks}
    coefficient, capacity = Box(S), Box()
    for j in range(1, 513):
        for r in ranks:
            powers[r] *= Q(r, width)
        integral = sum((weights[r]*powers[r] for r in ranks), Box())/(j-alpha)
        need(integral.lo > 0, 'positive integrated binomial term')
        capacity += coefficient*integral
        coefficient *= Q(j-S, j+1)
    exit_value = (gap*terminal+boundary/ps[width])/tau
    margin = capacity-exit_value
    need(margin.lo > 40000, 'full complement margin too small')
    return {'alpha': alpha.display(14), 'probabilities': {
        str(r): probabilities[r].display(12) for r in (1, 2, 3)},
        'variance': variance.display(12), 'third_absolute_moment': third.display(12),
        'tilted_gap': gap.display(8), 'tilted_target_ratio': ratio.display(12),
        'full_margin_lower_sum': margin.display(6), 'binomial_terms': 512}


def constant_certificate(paid, targets, onset_exponent=ONSET_EXPONENT):
    need(type(onset_exponent) is int and onset_exponent >= 10**12, 'onset too small')
    qbound = Q(247, 250)
    total_variation = 121*sum(paid.values())*sum(targets.values())
    need(total_variation == 52092027504, 'kernel multiplier')
    need(sum(r*c for r, c in targets.items())-sum(r*c for r, c in paid.items()) == 608,
         'rank-one conservation surplus')
    # No huge integer 2**onset_exponent is constructed. LOCAL_LIMIT.md reduces
    # the remaining analytic terms to these small exact endpoint inequalities.
    need(Q(15, onset_exponent) < Q(1, 10**8), 'uniform LLT accuracy')
    need(2**100 > 10**18 and onset_exponent >= 100, 'G0 dominates coarse cutoff')
    retained = 3*total_variation*Q(1, 10**8)
    middle = 17*total_variation*qbound**3001
    high = 8*total_variation/(Q(3, 500)**2*10**18)
    leaf = Q(1, 5)
    tails = Q(2, 10**7)
    need(retained < 1563 and middle < Q(1, 1000) and high < 1, 'mixed error budget')
    need(retained+middle+high+leaf+tails < 1600, 'complete error budget')
    need(Q(8, 3)**36 > 10**15, 'geometric elementary exponential bound')
    need(Q(163, 60)**37 > 10**16, 'leaf elementary exponential bound')
    need(Q(30010+5*15010**2, 10**18) < Q(1, 10**8), 'mixed Gaussian flattening')
    need(Q(1, 10**8)+Q(5000*5002**2, 4*10**18) < Q(5, 10**8),
         'leaf Gaussian flattening')
    return {'onset_log2': str(onset_exponent), 'n_LLT': '2^'+str(onset_exponent),
            'G0': '2*2^'+str(onset_exponent)+'+2', 'N0': '121*5^G0',
            'kernel_multiplier': total_variation, 'normalized_error_upper': 1600,
            'normalized_capacity_margin_lower': 38400,
            'majorant': 'L(n) <= N0^(261/100000) * n^(99739/100000), n>=1'}


def words(law, length, cap):
    result = Counter({1: 1})
    for _ in range(length):
        following = Counter()
        for product, count in result.items():
            for rank, multiplicity in law.items():
                if product*rank <= cap:
                    following[product*rank] += count*multiplicity
        result = following
    return result


def decomposition(paid, targets, n, truncate_terminal=False, omit_layer=False):
    cap, height, least = n//121, 0, 1
    while 5*least <= cap:
        height, least = height+1, 5*least
    source, boundary, leaf = Counter(), Counter(), Counter()
    for z, count in words(targets, height, cap).items():
        for k, c in targets.items():
            source[k*z] += count*c
    for z, count in words(paid, height, cap).items():
        for r, c in paid.items():
            if not truncate_terminal or r*z <= cap:
                leaf[r*z] += count*c
    for h in range(height):
        if omit_layer and h == 0:
            continue
        for x, cx in words(targets, h, cap).items():
            for y, cy in words(paid, height-1-h, cap).items():
                z = x*y
                for r, pr in paid.items():
                    for k, tk in targets.items():
                        count = cx*cy*pr*tk
                        if r*z <= cap < k*z:
                            source[r*k*z] += count
                        elif k*z <= cap < r*z:
                            boundary[r*k*z] += count
    return source, boundary+leaf, boundary


def finite_controls(inputs, paid, targets):
    module = types.ModuleType('authenticated_historical_flow')
    path = 'research/direct-mixed-flow/flow.py'
    exec(compile(inputs[path], path, 'exec'), module.__dict__)
    ranks = (121, 122, 604, 605, 606, 3024, 3025, 3026, 15124, 15125)
    for n in ranks:
        actual = module.Flow(targets, paid, n).merged()
        independent = decomposition(paid, targets, n)
        need(independent == tuple(actual[k] for k in ('sources', 'exits', 'boundary_exits')),
             'complete ordered-word decomposition mismatch')
        need(all(n < 121*z and z <= n for z in actual['sources']), 'source rank contract')
        need(all(121*e <= 48*n and e < n for e in actual['exits']), 'exit rank contract')
    reference = decomposition(paid, targets, 3025)
    need(decomposition(paid, targets, 3025, truncate_terminal=True) != reference,
         'unpaid terminal truncation escaped control')
    need(decomposition(paid, targets, 3025, omit_layer=True) != reference,
         'missing mixed layer escaped control')
    rejected = 0
    for action in (lambda: constant_certificate(paid, targets, 100),
                   lambda: Box(1)/Box(-1, 1),
                   lambda: log_integer(0), lambda: exponential_point(7)):
        try:
            action()
        except ValueError:
            rejected += 1
        else:
            raise ValueError('invalid hypothesis escaped control')
    # Exact exponentials at zero and log-additivity provide different endpoint
    # identities, while signed interval products challenge rounding direction.
    need(exponential_point(0).lo <= 1 <= exponential_point(0).hi, 'exp zero')
    log4 = log_integer(4)-2*log_integer(2)
    need(log4.lo <= 0 <= log4.hi, 'logarithm additive control')
    product = Box(-2, 3)*Box(-5, 7)
    need(product.lo == -15 and product.hi == 21, 'signed interval product control')
    return {'complete_histogram_fixtures': len(ranks), 'semantic_mutations': 2,
            'domain_rejections': rejected, 'arithmetic_controls': 3}


def main():
    inputs = authenticate()
    paid, targets, width = inventory(inputs['research/direct-flow-leaf-walk/verify.py'])
    result = {'status': 'PASS_EFFECTIVE_DIRECT_FLOW', 'numerical_hypotheses':
              certify_law(paid, targets, width), 'uniform_constants':
              constant_certificate(paid, targets), 'finite_controls':
              finite_controls(inputs, paid, targets), 'no_new_kappa': True,
              'scope': 'Exact finite numerical premises and controls; written Fourier and full-flow proofs establish the universal bound.'}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
