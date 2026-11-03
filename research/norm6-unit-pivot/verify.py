"""Check the new unit pivot, compressed endpoints and rejecting controls.

Produced by Nick Petalas. Apache-2.0. No predecessor executable is imported.
"""

from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compression as c

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
GRAM_PATH = 'research/norm6-dyadic-decoder/sources/P48p-GRAM.json'
GRAM_HASH = 'e25d51a0a9cdbc897d5db39fb698aa9bbc2f4ce29e8d7add2a44bae8f086add2'


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def load_gram():
    with (ROOT / GRAM_PATH).open('rb') as stream:
        raw = stream.read(65537)
    check(len(raw) <= 65536 and sha256(raw).hexdigest() == GRAM_HASH,
          'Gram source hash or size')
    return json.loads(raw)


def determinant(matrix):
    """Separate exact elimination, without a triangular-form assumption."""
    a = [[Fraction(x) for x in row] for row in matrix]
    result = Fraction(1)
    for j in range(48):
        pivot = next((i for i in range(j, 48) if a[i][j]), None)
        check(pivot is not None, 'singular pivot')
        if pivot != j:
            a[pivot], a[j] = a[j], a[pivot]
            result = -result
        diagonal = a[j][j]
        result *= diagonal
        for i in range(j+1, 48):
            if not a[i][j]:
                continue
            scale = a[i][j]/diagonal
            for k in range(j, 48):
                a[i][k] -= scale*a[j][k]
    return result


def pivot_certificate(plan):
    pivots = c.pivot_keys(plan)
    check(len(pivots) == len(set(pivots)) == 48, 'pivot cardinality')
    parents = (12, 3, 3, 2, 10, 3, 3, 2, 3, 2, 8, 15, 2, 2, 3, 2, 2, 2, 3, 2, 8, 10)
    check(tuple(p for p in plan.parents if p >= 0) == parents, 'written parent certificate')
    # Direct relation-monomial coefficients of the new pivot, separately built.
    independent = [[0]*48 for _ in range(48)]
    for j, key in enumerate(pivots):
        if key[0] == 'l':
            independent[key[1]][j] = plan.gram[key[1]][key[1]]//2-3
        else:
            _, i, p = key
            independent[i][j] = plan.gram[i][p]
            independent[p][j] = plan.gram[i][i]//2
    for j, key in enumerate(pivots):
        column = dict(c.relation_column(plan, key))
        check(all(independent[i][j] == column.get(i, 0) for i in range(48)),
              'pivot relation column')
    det = determinant(independent)
    check(abs(det) == 1, 'pivot is not unimodular')
    for j in range(48):
        rhs = [int(i == j) for i in range(48)]
        lam = solve_pivot(plan, rhs)
        check(all(sum(independent[i][k]*lam[i] for i in range(48)) == rhs[k]
                  for k in range(48)), 'integral inverse column')
    return det, pivots


def solve_pivot(plan, rhs):
    lam = [0]*48
    for j, r in enumerate(plan.roots):
        lam[r] = rhs[j]
    offset = len(plan.roots)
    for i, p in enumerate(plan.parents):
        if p >= 0:
            lam[i] = plan.gram[i][p]*(rhs[offset]-plan.gram[i][i]//2*lam[p])
            offset += 1
    return lam


def target_certificates(plan, pivots):
    targets = []
    for i in range(48):
        for value in (-2, -1, 1, 2):
            targets.append(tuple(value if j == i else 0 for j in range(48)))
    targets += [tuple((i*seed+3) % 11-5 for i in range(48)) for seed in range(1, 13)]
    zero = (0,)*48
    for v in targets:
        lam = c.multipliers(plan, v)
        rhs = [c.raw_pair(key, zero, v)[1] for key in pivots]
        check(tuple(solve_pivot(plan, rhs)) == lam, 'multiplier solve')
        for key in pivots:
            psi = c.raw_pair(key, zero, v)[1]
            check(psi == sum(a*lam[i] for i, a in c.relation_column(plan, key)),
                  'nonzero eliminated coefficient')
    return len(targets)


def endpoint_certificates(plan):
    sources = [tuple(int(j == i) for j in range(48))
               for i in range(48) if plan.gram[i][i] == 6]
    targets = [(0,)*48, tuple((7*i+2) % 9-4 for i in range(48)),
               tuple((11*i+3) % 7-3 for i in range(48))]
    count, record_count, omissions = 0, 0, 0
    all_keys = tuple(c.keys())
    check(len(all_keys) == len(set(all_keys)) == 19648, 'feature inventory')
    pivots = set(c.pivot_keys(plan))
    expected_order = tuple(key for key in all_keys if key not in pivots)
    for x in sources:
        for y in targets + [x]:
            before_x, before_y = tuple(x), tuple(y)
            rows = tuple(c.records(plan, x, y))
            check(tuple(key for key, _, _ in rows) == expected_order, 'record order')
            check(len(rows) == 19600, 'retained term count')
            check(all(type(a) is int and type(b) is int for _, a, b in rows),
                  'nonintegral factor')
            actual = sum(a*b for _, a, b in rows)
            inner = sum(x[i]*plan.gram[i][j]*y[j]
                        for i in range(48) for j in range(48))
            check(Fraction(actual, c.DENOMINATOR) == Fraction(inner**3-4*inner, 192),
                  'compressed kernel endpoint')
            check((x, y) == (before_x, before_y), 'input mutation')
            if actual:
                nonzero = next((a*b for _, a, b in rows if a*b), None)
                check(nonzero is not None and 3*(actual-nonzero) != inner**3-4*inner,
                      'deleted nonzero term was accepted')
                omissions += 1
            count += 1
            record_count += len(rows)
    return count, record_count, omissions


def off_shell_certificates(plan):
    """Exercise every feature family against the independent defect formula."""
    cases, record_count = 0, 0
    for seed in range(1, 25):
        x = tuple((i*seed+5) % 7-3 for i in range(48))
        v = tuple((i*(seed+1)+2) % 9-4 for i in range(48))
        lam = c.multipliers(plan, v)
        rows = tuple(c.coefficient_records(plan, x, v))
        total = sum(a*b for _, a, b in rows)
        inner = sum(a*b for a, b in zip(x, v))
        defect = sum(a*b for a, b in zip(lam, x))*(c.norm(plan, x)-6)
        expected = Fraction(inner**3-4*inner, 192)-Fraction(defect, 128)
        check(Fraction(total, c.DENOMINATOR) == expected, 'off-shell polynomial identity')
        check(all(any(a*b != 0 for key, a, b in rows if key[0] == kind)
                  for kind in ('f', 'l', 's', 't')), 'unexercised feature family')
        cases += 1
        record_count += len(rows)
    return cases, record_count


def expect_reject(kind, value):
    try:
        if kind == 'gram':
            c.make_plan(value)
        elif kind == 'vector':
            c.integer_vector(value)
        else:
            tuple(c.records(value, (0,)*48, (0,)*48))
    except ValueError:
        return
    raise RuntimeError('invalid boundary accepted')


def controls(plan):
    g = [list(row) for row in plan.gram]
    bad_symmetric = [row[:] for row in g]
    bad_symmetric[0][1] += 1
    no_roots = [[6 if i == j else 0 for j in range(48)] for i in range(48)]
    no_edge = [[8 if i == j else 0 for j in range(48)] for i in range(48)]
    no_edge[0][0] = 6
    cases = [('gram', g[:-1]), ('gram', bad_symmetric), ('gram', no_roots),
             ('gram', no_edge), ('vector', (0,)*47),
             ('vector', (True,)+(0,)*47), ('vector', (2**20+1,)+(0,)*47),
             ('source', plan)]
    for kind, value in cases:
        expect_reject(kind, value)
    v = tuple(1 if i in plan.roots else 2 for i in range(48))
    lam = list(c.multipliers(plan, v))
    lam[plan.roots[0]] += 1
    check(any(c.raw_pair(key, (0,)*48, v)[1]
              != sum(a*lam[i] for i, a in c.relation_column(plan, key))
              for key in c.pivot_keys(plan)), 'corrupt solve accepted')
    return len(cases)+1


def main():
    plan = c.make_plan(load_gram())
    det, pivots = pivot_certificate(plan)
    target_count = target_certificates(plan, pivots)
    endpoints, records, omissions = endpoint_certificates(plan)
    off_shell, off_records = off_shell_certificates(plan)
    rejected = controls(plan)
    files = tuple(sorted(p for p in PACKAGE.iterdir() if p.is_file()))
    check(len(files) == 7, 'unexpected package file inventory')
    check(all(p.stat().st_size <= 1 << 20 for p in files), 'package source size limit')
    receipt = {'status': 'PASS_NORM6_UNIT_PIVOT', 'determinant': str(det),
               'diagonal_eight_roots': len(plan.roots), 'unit_edges': 48-len(plan.roots),
               'retained_features': 19600, 'common_target_denominator': c.DENOMINATOR,
               'pivot_inverse_entries': 48*48, 'target_cases': target_count,
               'kernel_endpoints': endpoints, 'emitted_records': records,
               'off_shell_cases': off_shell, 'off_shell_records': off_records,
               'term_omission_controls': omissions, 'boundary_controls': rejected,
               'gram_sha256': GRAM_HASH,
               'package_sha256': {p.name: sha256(p.read_bytes()).hexdigest() for p in files}}
    print(json.dumps(receipt, sort_keys=True))
    print('PASS_NORM6_UNIT_PIVOT')


if __name__ == '__main__':
    main()
