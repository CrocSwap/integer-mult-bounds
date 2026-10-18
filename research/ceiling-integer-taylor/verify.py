"""Exact replay equivalence, independent series oracle and semantic controls."""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from math import factorial
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from adapter import replay
from integer_exp import exp, require, series


def reference(y, precision, upper):
    # Independent powers/factorials: no S/P/D recurrence from the optimized loop.
    k = 1
    while y**(k+1) / factorial(k) >= Q(1, 1 << (precision+8)):
        k += 1
    total = sum((y**j / factorial(j) for j in range(k+1)), Q(0))
    if upper:
        total += 2 * y**(k+1) / factorial(k+1)
    units = total * (1 << precision)
    rounded = -((-units.numerator)//units.denominator) if upper else units.numerator//units.denominator
    return Q(rounded, 1 << precision), k


def compute():
    fixtures = {}
    for fixture in ('levers', 'selected'):
        original_rows, optimized_rows = [], []
        original = replay('baseline', fixture, observer=original_rows.append)
        optimized = replay('optimized', fixture, observer=optimized_rows.append)
        require(original_rows == optimized_rows, 'exact ordered exp values differ: '+fixture)
        require(original == optimized, 'complete original replay differs: '+fixture)
        fixtures[fixture] = original
    points = sorted({Q(n, d) for d in range(1, 34) for n in range(d//2+1)})
    cases = [(y, precision) for y in points for precision in (0, 8, 32, 128, 256)]
    rng = random.Random(21)
    for _ in range(24):
        q = (1 << 300) + rng.getrandbits(300)
        cases.append((Q(rng.randrange(q//2+1), q), 256))
    cases.extend([(Q(1, 2)-Q(1, 1 << 400), 512), (Q(1, 1 << 600), 512)])
    boundary = []
    for precision in (0, 8, 32, 128, 256):
        y = Q(1, 1 << ((precision+8)//2))
        cases.append((y, precision))
        require(series(y, precision, False)[1] == 2, 'strict threshold equality must continue')
        boundary.append({'precision': precision, 'endpoint': str(y), 'stop_index': 2})
    digest, endpoint_checks = hashlib.sha256(), 0
    for y, precision in cases:
        for upper in (False, True):
            actual, expected = series(y, precision, upper), reference(y, precision, upper)
            require(actual == expected, 'integer recurrence or stopping mismatch')
            digest.update((repr((str(y), precision, upper, str(actual[0]), actual[1]))+'\n').encode())
            endpoint_checks += 1
    rejected = []
    for name, action in [('negative endpoint', lambda: exp(Q(-1, 9), Q(0))),
                         ('reversed interval', lambda: exp(Q(1, 3), Q(1, 4))),
                         ('outside retained range', lambda: exp(Q(0), Q(3, 4))),
                         ('negative precision', lambda: series(Q(1, 3), -1, False)),
                         ('float endpoint', lambda: series(0.25, 256, False))]:
        try:
            action()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('control accepted: '+name)
    # Executable algebraic foils, not merely alternative JSON descriptions.
    y, precision = Q(1, 3), 32
    k = series(y, precision, False)[1]
    wrong_sum = sum((y**j for j in range(k+1)), Q(0))  # Omit factorial.
    wrong_units = wrong_sum*(1 << precision)
    wrong_lower = Q(wrong_units.numerator//wrong_units.denominator, 1 << precision)
    require(wrong_lower != series(y, precision, False)[0], 'factorial omission foil')
    lower, upper = exp(y, y, precision)
    raw_upper = sum((y**j/factorial(j) for j in range(k+1)), Q(0)) + 2*y**(k+1)/factorial(k+1)
    scaled = raw_upper * (1 << precision)
    wrong_upper = Q(scaled.numerator//scaled.denominator, 1 << precision)
    require(wrong_upper != upper and lower < upper, 'upper-floor foil must differ')
    require(exp(Q(0), Q(0)) == (Q(1), Q(1)), 'zero endpoint positive')
    return {'status': 'PASS_CEILING_INTEGER_TAYLOR', 'fixtures': fixtures,
            'series_cases': len(cases), 'endpoint_checks': endpoint_checks,
            'series_trace_sha256': digest.hexdigest(), 'strict_stop_boundaries': boundary,
            'rejected_inputs': rejected, 'semantic_foils': ['omitted factorial', 'upper endpoint floored'],
            'scope': 'Exact arithmetic implementation equivalence; no new interval bound, changed mathematical premise, supplier or kappa.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    result = compute()
    if args.write:
        with args.write.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        expected = json.loads((HERE/'RESULT.json').read_text(encoding='utf-8'))
        require(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
                'typed complete receipt mismatch')
    print('PASS_CEILING_INTEGER_TAYLOR fixtures=2 exp_calls='+
          str(sum(f['exp_calls'] for f in result['fixtures'].values()))+
          ' endpoint_checks='+str(result['endpoint_checks'])+' strict_boundaries=5')


if __name__ == '__main__':
    main()
