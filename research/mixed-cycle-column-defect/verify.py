"""Check the mixed-cycle column-defect proof with exact arithmetic.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha1, sha256
import importlib.util
from itertools import product
import json
from math import isqrt
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ArithmeticError(message)


def sources():
    pins = json.loads((ROOT / 'SOURCE-PINS.json').read_text())['sources']
    for pin in pins:
        data = (ROOT / pin['retained']).read_bytes()
        require(sha256(data).hexdigest() == pin['sha256'], 'source SHA256')
        require(sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                == pin['git_blob'], 'source Git blob')
    source = ROOT / 'retained/source7762'
    args = [sys.executable, '-W', 'error', *(['-O'] if sys.flags.optimize else []),
            '-B', str(source / 'verify.py')]
    replay = subprocess.run(args, capture_output=True, text=True, check=True, timeout=60)
    require('PASS_MIXED_CYCLE_COLUMN_OBSTRUCTION' in replay.stdout, 'source replay')
    spec = importlib.util.spec_from_file_location(
        'retained_cyclotomic', source / 'retained/two-prime/verify.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return len(pins), module


def evaluate(terms, bases):
    (xd, xp), (yd, yp) = bases
    result = [[0] * yd for _ in range(xd)]
    for coefficient, x, y in terms:
        for i, a in xp[x % len(xp)]:
            for j, b in yp[y % len(yp)]:
                result[i][j] += coefficient * a * b
    return tuple(map(tuple, result))


def block_checks(source):
    records = []
    faults = {'conjugation': 0, 'linear coefficient': 0, 'missing R': 0,
              'wrong diagonal phase': 0}
    for q, b in product((5, 7, 11), (1, 2)):
        order, n = q ** b, q + 3
        bases = source.powers(3, 3), source.powers(q, order)
        zero = evaluate((), bases)
        for m, orientation in product((4, n - 1, n), (1, 2)):
            d = n - m
            k = [[0] * m for _ in range(m)]
            for i in range(m):
                for j in range(i + 1, m):
                    k[i][j] = (i + 2) * (j + 3) % order
                    k[j][i] = -k[i][j] % order
            r = [[(a + 3) * (j + 2) % order for j in range(m)] for a in range(d)]
            a = [[(orientation if i == j else 0, e) for j, e in enumerate(row)]
                 for i, row in enumerate(k)] + [[(0, e) for e in row] for row in r]
            for i, j in product(range(m), repeat=2):
                direct = [(1, row[j][0] - row[i][0], row[j][1] - row[i][1]) for row in a]
                direct.append((-n * (i == j), 0, 0))
                square = [(1, 0, k[i][t] + k[t][j]) for t in range(m)]
                remainder = [(1, 0, row[j] - row[i]) for row in r]
                rhs = square + remainder + [(-3, 0, k[i][j]), (-q * (i == j), 0, 0)]
                expected = evaluate(direct, bases)
                require(expected == evaluate(rhs, bases), 'rectangular block identity')
                wrong_conjugate = [(1, row[j][0] + row[i][0], row[j][1] + row[i][1]) for row in a]
                wrong_conjugate.append((-n * (i == j), 0, 0))
                faults['conjugation'] += evaluate(wrong_conjugate, bases) != expected
                faults['linear coefficient'] += evaluate(rhs + [(1, 0, k[i][j])], bases) != expected
                faults['missing R'] += evaluate(square + [(-3, 0, k[i][j]), (-q * (i == j), 0, 0)], bases) != expected
                wrong_a = [(x if t != i else (0, x[1]), y if t != j else (0, y[1]))
                           for t, (x, y) in enumerate((row[i], row[j]) for row in a)]
                wrong_terms = [(1, y[0] - x[0], y[1] - x[1]) for x, y in wrong_a]
                wrong_terms.append((-n * (i == j), 0, 0))
                faults['wrong diagonal phase'] += evaluate(wrong_terms, bases) != expected
            cycle = [(1, x, 0) for x in range(3)] + [(1, 0, j * order // q) for j in range(q)]
            require(evaluate(cycle, bases) == zero, 'two-column positive control')
            require(evaluate(cycle[:-1], bases) != zero, 'deleted root control')
            records.append({'q': q, 'b': b, 'rows': n, 'columns': m,
                            'orientation': orientation, 'entries': m * m})
    require(all(faults.values()), 'a fault survived all block checks')
    return {'fixtures': records, 'fault_differences': faults,
            'two_column_controls': len(records), 'deleted_root_controls': len(records)}


def polynomial_checks():
    # Each identity has degree at most four in each variable. A five-point
    # grid in each variable determines all coefficients over Q.
    count = 0
    for n, m, h in product(range(5), repeat=3):
        d = n - m
        t = Fraction(3 * h - m, 2)
        e = m * m - Fraction((m - h) * (2 * n + 3), 2)
        f = (4 * n - 3) * h * h - 4 * m * d * h - m * m
        require(4 * (h * e - t * t) == f, 'Cauchy polynomial identity')
        fd = d * d * (4 * d - 3) - m * m
        require((4 * n - 3) * d * d - 4 * m * d * d - m * m == fd,
                'endpoint polynomial identity')
        require(h * fd + (d - h) * (-m * m) - d * f
                == (4 * n - 3) * d * h * (d - h), 'chord polynomial identity')
        count += 1
    return {'grid_points': count, 'degree_limit_per_variable': 4,
            'identities': ['Cauchy', 'endpoint', 'convex chord']}


def bound_checks():
    primes = [q for q in range(5, 102) if all(q % p for p in range(2, isqrt(q) + 1))]
    rows, cases, equalities = [], 0, []
    for q in primes:
        n = q + 3
        require((4 * q + 9) % 8 == 5 and (4 * q + 9) % q != 0,
                'quadratic square-class hypotheses')
        for m in range(4, n + 1):
            d = n - m
            endpoint = d * d * (4 * d - 3) - m * m
            for k in range(m // 2 + 1):
                h = m - 2 * k
                if h > d:
                    continue
                t = m - 3 * k
                e = m * m - k * (2 * q + 9)
                cauchy = e >= 0 and t * t <= h * e
                f = (4 * n - 3) * h * h - 4 * m * d * h - m * m
                require((t * t <= h * e) == (f >= 0), 'independent multiplicity calculation')
                if endpoint < 0:
                    require(not cauchy, 'excluded multiplicity passed')
                if endpoint == 0 and cauchy:
                    require(h == d and t * t == h * e, 'equality propagation')
                    beta = Fraction(t, h)
                    require(beta * beta - 3 * beta - q == -m, 'equality Gram eigenvalue')
                    require(m % q != 0, 'prime-power row orthogonality contradiction')
                    equalities.append({'q': q, 'm': m, 'd': d, 'root_multiplicity': k,
                                       'other_eigenvalue': str(beta)})
                cases += 1
        d0 = next(d for d in range(n + 1) if (n - d) ** 2 < d * d * (4 * d - 3))
        allowed = [m for m in range(1, n + 1)
                   if m * m < (n - m) ** 2 * (4 * (n - m) - 3)]
        require(max(allowed) == n - d0 and min(allowed) == 1, 'direct bound enumeration')
        rows.append({'q': q, 'rows': n, 'minimum_defect': d0, 'maximum_columns_bound': n - d0})
    require(equalities == [{'q': 101, 'm': 91, 'd': 13, 'root_multiplicity': 39,
                           'other_eigenvalue': '-2'}], 'equality boundary control')
    require(rows[0]['maximum_columns_bound'] == 5 and rows[-1]['maximum_columns_bound'] == 90,
            'small and equality endpoint controls')
    require(6 ** 2 >= 2 ** 2 * (4 * 2 - 3), 'eight-by-six exclusion')
    return {'prime_bounds': rows, 'multiplicity_cases': cases,
            'excluded_equality_cases': equalities,
            'claim': 'strict necessary bound only; no attainment claim'}


def collect():
    count, source = sources()
    return {'source_files': count, 'block_checks': block_checks(source),
            'polynomial_checks': polynomial_checks(), 'bound_checks': bound_checks()}


def main():
    actual = collect()
    require(actual == json.loads((ROOT / 'RESULT.json').read_text()), 'saved result mismatch')
    print('PASS_MIXED_CYCLE_COLUMN_DEFECT')
    print('Strict bound m^2 < d^2(4d-3), d=q+3-m: written proof')
    print('36 exact block fixtures; 125 polynomial grid points; 24 prime bounds')
    print('Eight rows permit at most five columns; 104 rows permit at most ninety')
    print('Equality obstruction, positive controls, fault controls and unchanged source replay pass')


if __name__ == '__main__':
    main()
