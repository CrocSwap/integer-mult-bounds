#!/usr/bin/env python3
"""Bounded exact evidence for PROOF.md; no predecessor code is executed.

@CubeJerry, with substantial OpenAI Codex assistance. Apache-2.0.
This program uses explicit exceptions rather than optimization-removable asserts.
It reads the local kernel's source bytes directly, avoiding Python bytecode caches.
"""
import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from math import isqrt
from pathlib import Path
import sys
from types import ModuleType

HERE = Path(__file__).resolve().parent
A = ((1, 2), (-2, 1))
CENSUS_SHA = '135a38967a4f2a811bc2ddcafe34a020e76b5a925654929d6592db4582f6d794'
CENSUS_BLOB = 'f27720ee0fe58d0f98b1f34609e25763ff27dd2b'
SOURCE_HEADS = {
    6666: '042b4ee85f64f4b3279426e2ed10191296448e6c',
    6685: '9e6c76ebf56fcd968c1383f00688152114f9dc79',
    1135: '4c35687d7c0da8e6cf33f17e418ecf31c95ff3ad',
    5615: 'd914f77d948ac377bdb9823daca93d08913c3fa7',
}
COUNTS = Counter()
CONTROLS = []


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def rejection(name, operation):
    try:
        operation()
    except (ValueError, KeyError):
        CONTROLS.append(name)
    else:
        raise ValueError('negative control was accepted: ' + name)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def load_kernel():
    name = '_coupled_reader_verified_source'
    module = ModuleType(name)
    module.__file__ = str(HERE / 'reader.py')
    sys.modules[name] = module
    exec(compile((HERE / 'reader.py').read_bytes(), module.__file__, 'exec'), module.__dict__)
    return module


R = load_kernel()


def read_literal(a, h, b):
    """Independent nearest rounding via a doubled numerator, including b=0."""
    m = 1 << b
    return tuple((2 * sum(row[j] * h[j] for j in range(2)) + m) // (2 * m)
                 for row in a)


def direct_error(a, lift, b, x, h):
    shifted = tuple(h[i] + sum(lift[i][j] * x[j] for j in range(2)) for i in range(2))
    left, right = read_literal(a, shifted, b), read_literal(a, h, b)
    return tuple(left[i] - right[i] - x[i] for i in range(2))


def residual_literal(a, lift, b):
    return tuple(tuple(sum(a[i][k] * lift[k][j] for k in range(2))
                       - (1 << b) * (i == j) for j in range(2)) for i in range(2))


def ceiling(n, m):
    return -(-n // m)


def phase_max_squared(d, x, m):
    return sum(ceiling(abs(sum(row[j] * x[j] for j in range(2))), m) ** 2 for row in d)


def histogram_formula(d, x, m):
    coordinate_counts = []
    for row in d:
        q, s = divmod(sum(row[j] * x[j] for j in range(2)), m)
        coordinate_counts.append([(q, m - s)] + ([(q + 1, s)] if s else []))
    return Counter({(left[0], right[0]): left[1] * right[1]
                    for left, right in product(*coordinate_counts)})


def check_census(raw):
    need(hashlib.sha256(raw).hexdigest() == CENSUS_SHA, 'retained census SHA256 mismatch')
    need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
         == CENSUS_BLOB, 'retained census Git blob mismatch')
    need(b'for entries in product(range(-2, 3), repeat=4):' in raw,
         'retained complete census loop missing')
    need(all(-2 <= x <= 2 for row in A for x in row), 'reader outside retained census')


def check_sources():
    pins = json.loads((HERE / 'SOURCE-PINS.json').read_text())
    need(len(pins['files']) == 5, 'unexpected source record count')
    for row in pins['files']:
        need(row['head'] == SOURCE_HEADS[row['pr']], 'wrong predecessor head')
        need(row['repository'] == 'CrocSwap/integer-mult-bounds', 'wrong source repository')
        need(row['url'].endswith('/blob/' + row['head'] + '/' + row['path']), 'source URL mismatch')
        need(len(row['sha256']) == 64 and len(row['git_blob']) == 40, 'invalid source digest')
    entry = next(row for row in pins['files'] if row.get('retained_as'))
    need(entry['retained_as'] == 'census-source.txt' and entry['sha256'] == CENSUS_SHA
         and entry['git_blob'] == CENSUS_BLOB, 'wrong retained census pin')
    raw = (HERE / entry['retained_as']).read_bytes()
    need(len(raw) == entry['bytes'], 'source length mismatch')
    check_census(raw)
    rejection('altered retained source bytes', lambda: check_census(raw + b'\n'))
    COUNTS['source_records'] = 5
    COUNTS['retained_census_matrices'] = 625


def check_residuals():
    for b in range(65):
        m = 1 << b
        for family in ('balanced', 'concentrated'):
            lift = R.lift_for(b, family)
            d = residual_literal(A, lift, b)
            need(d == R.residual(lift, b), 'residual computation disagrees')
            need(R.from_residual(d, b) == lift, 'residual lattice inverse disagrees')
            need((d[0][0] - 2 * d[1][0] + m) % 5 == 0
                 and (d[0][1] - 2 * d[1][1] - 2 * m) % 5 == 0, 'lattice congruence failed')
            j = ((0,-1),(1,0))
            commutes = R.multiply(lift,j) == R.multiply(j,lift)
            need(commutes == (family == 'balanced'), 'complex-linear lift classification failed')
            COUNTS['complex_linear_lift_cases'] += 1
            if family == 'balanced':
                need(sorted(sum(abs(row[j]) for row in d) for j in range(2)) == [1, 1]
                     and all(sum(map(abs, row)) == 1 for row in d), 'not a signed permutation')
            else:
                need(d[1] == (0, 0) and sum(map(abs, d[0])) == 3, 'bad concentration')
            gates = R.compile_word(lift, b)
            cost = R.bill(lift, b)
            need(sum(g.src is not None for g in gates) == cost['word_adds'], 'ADD bill mismatch')
            need(sum(g.src is None for g in gates) == cost['constant_translations'], 'constant bill mismatch')
            COUNTS['lift_and_bill_cases'] += 1
    rejection('unattainable zero residual',
              lambda: R.from_residual(((0, 0), (0, 0)), 3))
    # All small lattice points, independently tested for integrality.
    for b in range(4):
        m = 1 << b
        for flat in product(range(-3, 4), repeat=4):
            d = (flat[:2], flat[2:])
            congruence = ((flat[0] - 2 * flat[2] + m) % 5 == 0
                          and (flat[1] - 2 * flat[3] - 2 * m) % 5 == 0)
            try:
                lift = R.from_residual(d, b)
            except ValueError:
                need(not congruence, 'rejected an attainable residual')
            else:
                need(congruence and residual_literal(A, lift, b) == d, 'accepted false residual')
            COUNTS['residual_lattice_cases'] += 1


def check_execution_and_histograms():
    bound = 2
    for b in range(5):
        m = 1 << b
        phases = {tuple((sum(A[i][j] * h[j] for j in range(2)) + m // 2) % m
                        for i in range(2)) for h in product(range(m), repeat=2)}
        need(len(phases) == m * m, 'odd-determinant phase bijection failed')
        COUNTS['phase_classes'] += len(phases)
        for family in ('balanced', 'concentrated'):
            lift = R.lift_for(b, family)
            d = residual_literal(A, lift, b)
            gates = R.compile_word(lift, b)
            back = R.inverse(gates)
            total_max = 0
            guards = R.headroom(lift, b, bound, (m * 1010, m * 10008), (31, 47))['absolute_guards']
            for x in product(range(-bound, bound + 1), repeat=2):
                actual = Counter()
                for phase_h in product(range(m), repeat=2):
                    h = (phase_h[0] + 1009 * m, phase_h[1] - 10007 * m)
                    initial = (*x, *h, 31, -47)
                    expected_error = direct_error(A, lift, b, x, h)
                    endpoint, _ = R.execute(gates, initial, guards)
                    need(endpoint[:4] == initial[:4], 'source/helper was not restored')
                    need(endpoint[4:] == tuple(initial[4+i] + x[i] + expected_error[i]
                                                for i in range(2)), 'compiled endpoint disagrees')
                    restored, _ = R.execute(back, endpoint, guards)
                    need(restored == initial, 'literal reversed program failed')
                    actual[expected_error] += 1
                    total_max = max(total_max, sum(z*z for z in expected_error))
                    COUNTS['compiled_forward_and_reverse_fixtures'] += 1
                need(actual == histogram_formula(d, x, m), 'full joint error histogram disagrees')
                need(max(sum(z*z for z in err) for err in actual) == phase_max_squared(d, x, m),
                     'phase maximum disagrees')
                COUNTS['complete_error_histograms'] += 1
            expected = (2 * ceiling(bound, m) ** 2 if family == 'balanced'
                        else ceiling(3 * bound, m) ** 2)
            need(total_max == expected, 'attaining family sharp error disagrees')


def check_global_finite_optima():
    """Enumerate every residual capable of beating the known balanced upper bound."""
    table = []
    for b in range(5):
        m = 1 << b
        for bound in range(1, 3 * m + 1):
            upper = 2 * ceiling(bound, m) ** 2
            # Any contender with value<=upper has row l1<=N: choose its sign corner.
            n = m * isqrt(upper) // bound
            rows = [(a, d) for a in range(-n, n+1) for d in range(-n, n+1)
                    if abs(a) + abs(d) <= n]
            points = tuple(product(range(-bound, bound+1), repeat=2))
            found, candidates = upper, 0
            for first in rows:
                for second in rows:
                    if ((first[0] - 2 * second[0] + m) % 5
                            or (first[1] - 2 * second[1] - 2 * m) % 5):
                        continue
                    candidates += 1
                    worst = 0
                    for x in points:
                        worst = max(worst, phase_max_squared((first, second), x, m))
                        if worst > found:
                            break
                    found = min(found, worst)
            predicted = min(ceiling(3 * bound, m)**2, 2 * ceiling(bound, m)**2)
            need(found == predicted == R.optimum_squared(b, bound), 'finite global optimum disagrees')
            family, lift = R.optimal_lift(b, bound)
            d = residual_literal(A, lift, b)
            need(max(phase_max_squared(d, x, m) for x in points) == found,
                 'selected lift did not attain finite optimum')
            table.append([b, bound, candidates, found, family])
            COUNTS['finite_global_optimization_cases'] += 1
            COUNTS['finite_candidate_residual_matrices'] += candidates
    return table


def check_precision_and_smith():
    for b in range(25):
        m = 1 << b
        bounds = sorted({0, 1, 2, 3, m//3, m//3+1, m, m+1, 3*m, 10**30})
        for bound in bounds:
            value = R.optimum_squared(b, bound)
            need((value == 0) == (bound == 0), 'subcell obstruction failed')
            need((value <= 1) == (3*bound <= m), 'one-cell precision threshold failed')
            need((value <= 2) == (bound <= m), 'sqrt-two precision threshold failed')
            if bound:
                b_one, b_two = (3*bound-1).bit_length(), (bound-1).bit_length()
                need(R.optimum_squared(b_one, bound) <= 1, 'one-cell least precision insufficient')
                need(b_one == 0 or R.optimum_squared(b_one-1, bound) > 1,
                     'one-cell least precision not minimal')
                need(R.optimum_squared(b_two, bound) <= 2, 'sqrt-two least precision insufficient')
                need(b_two == 0 or R.optimum_squared(b_two-1, bound) > 2,
                     'sqrt-two least precision not minimal')
            COUNTS['precision_cases'] += 1
    u, v, s = ((1,0),(2,1)), ((1,-2),(0,1)), ((1,0),(0,5))
    need(R.multiply(R.multiply(u,A),v) == s, 'Smith chart identity failed')
    for b in range(5):
        m = 1 << b
        nearest = min(range(m//5-1, m//5+3), key=lambda x: abs(5*x-m))
        lift = ((m,0),(0,nearest))
        dist = abs(5*nearest-m)
        need(dist == (1 if b%2 == 0 else 2), 'Smith residual period failed')
        for bound in range(1, 4):
            value = 0
            for x in product(range(-bound,bound+1),repeat=2):
                for h in product(range(m),repeat=2):
                    error = direct_error(s,lift,b,x,h)
                    value = max(value,sum(e*e for e in error))
            need(value == ceiling(dist*bound,m)**2, 'Smith diagonal attaining error failed')
            COUNTS['smith_attainment_cases'] += 1
    need(R.optimum_squared(1,2) == 2 and ceiling(2*2,2)**2 == 4, 'first chart-order witness failed')
    need(R.optimum_squared(2,2) == 2 and ceiling(1*2,4)**2 == 1, 'reverse chart-order witness failed')


def check_headroom_and_large_words():
    for b in (0,1,3,10,64):
        for family in ('balanced','concentrated'):
            lift = R.lift_for(b,family)
            gates = R.compile_word(lift,b)
            bound, hb, yb = 7, (13,29), (17,23)
            data = R.headroom(lift,b,bound,hb,yb)
            guards, widths = data['absolute_guards'], data['signed_widths']
            for initial in product((-bound,bound),(-bound,bound),(-hb[0],hb[0]),
                                   (-hb[1],hb[1]),(-yb[0],yb[0]),(-yb[1],yb[1])):
                end, maxima = R.execute(gates,initial,guards)
                need(all(n < (1 << (w-1)) for n,w in zip(maxima,widths)), 'signed width insufficient')
                need(R.execute(R.inverse(gates),end,guards)[0] == initial, 'guarded inverse failed')
                COUNTS['headroom_corner_fixtures'] += 1
    for b in (0,17,64,257):
        for family in ('balanced','concentrated'):
            lift = R.lift_for(b,family)
            initial = (10**80,-10**79,10**100,-10**101,10**110,-10**111)
            guards = R.headroom(lift,b,10**80,(10**100,10**101),(10**110,10**111))['absolute_guards']
            word=R.compile_word(lift,b)
            end,_=R.execute(word,initial,guards)
            error=direct_error(A,lift,b,initial[:2],initial[2:4])
            need(end[:4] == initial[:4] and end[4:] == tuple(initial[4+i]+initial[i]+error[i]
                 for i in range(2)), 'large-word endpoint mismatch')
            need(R.execute(R.inverse(word),end,guards)[0] == initial, 'large-word inverse failed')
            COUNTS['large_word_fixtures'] += 1


def check_semantic_controls():
    c, lift, b, x = ((1,1),(1,-1)), ((1,0),(2,0)), 1, (1,0)
    actual={direct_error(c,lift,b,x,h) for h in product(range(2),repeat=2)}
    need(actual == {(0,-1),(1,0)}, 'even determinant control fixture wrong')
    rejection('false independent phases for even determinant',
              lambda: need((1,-1) in actual, 'unattainable product-phase error'))
    rejection('rounded reader mistaken for exact dyadic response',
              lambda: need(all(direct_error(A,R.lift_for(3,'balanced'),3,(1,1),h)==(0,0)
                               for h in product(range(8),repeat=2)), 'coarse rounding survives'))
    rejection('balanced refinement claimed to meet one-cell Euclidean budget',
              lambda: need(2*ceiling(2,8)**2 <= 1, 'two residual rows remain active'))
    j=((0,-1),(1,0)); concentrated=R.lift_for(3,'concentrated')
    rejection('concentrated lift claimed complex-linear',
              lambda: need(R.multiply(concentrated,j) == R.multiply(j,concentrated),
                           'concentrated lift does not commute with J'))
    rejection('Smith chart assumed to preserve fixed-box error',
              lambda: need(R.optimum_squared(1,2) == ceiling(4,2)**2, 'nonisometric chart changes error'))
    tie = read_literal(A,(1,0),1)
    negative = read_literal(A,(-1,0),1)
    rejection('negating input claimed to invert tie rounding',
              lambda: need(negative == tuple(-z for z in tie), 'tie rounding is not odd'))
    good = R.compile_word(R.lift_for(3,'concentrated'),3)
    initial = (2,-1,5,-7,11,-13)
    no_cleanup = good[:-1]
    rejection('missing final cleanup gate',
              lambda: need(R.execute(no_cleanup,initial)[0][:4] == initial[:4], 'helper not restored'))
    end=R.execute(good,initial)[0]
    wrong_inverse=tuple(reversed(good))
    rejection('reverse order without changing ADD signs',
              lambda: need(R.execute(wrong_inverse,end)[0] == initial, 'inverse signs missing'))
    rejection('undeclared insufficient word headroom',
              lambda: R.execute(good,initial,(2,2,7,7,13,13)))
    rejection('negative precision',lambda: R.compile_word(((1,0),(0,1)),-1))
    rejection('negative source bound',lambda: R.optimum_squared(3,-1))
    rejection('destructive same-word ADD accepted',
              lambda: R.execute((R.Gate(2,2,-1,1),),initial))


def receipt_body(table):
    # All regular package files are bound, including the written proof and metadata.
    paths=sorted(p for p in HERE.iterdir() if p.is_file())
    return {'schema_version':1,'claim_type':'scoped written proof plus bounded exact evidence',
            'counts':dict(sorted(COUNTS.items())),'negative_controls':CONTROLS,
            'finite_optimization_table_sha256':digest(table),
            'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}


def validate_receipt(envelope,expected):
    need(envelope['body_sha256'] == digest(envelope['body']), 'receipt digest mismatch')
    need(envelope['body'] == expected, 'receipt does not match current source-bound replay')
    need(envelope['marker'] == 'PASS_COUPLED_COARSE_GRID_READER', 'receipt marker mismatch')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-receipt',type=Path)
    args=parser.parse_args()
    check_sources()
    check_residuals()
    check_execution_and_histograms()
    table=check_global_finite_optima()
    check_precision_and_smith()
    check_headroom_and_large_words()
    check_semantic_controls()
    body=receipt_body(table)
    envelope={'marker':'PASS_COUPLED_COARSE_GRID_READER','body':body,'body_sha256':digest(body)}
    changed=json.loads(json.dumps(envelope))
    changed['body']['counts']['source_records'] += 1
    rejection('altered generated receipt',lambda:validate_receipt(changed,body))
    changed['body_sha256']=digest(changed['body'])
    rejection('self-consistent false receipt',lambda:validate_receipt(changed,body))
    # Include the executed receipt controls in the final source-bound receipt.
    body=receipt_body(table)
    envelope={'marker':'PASS_COUPLED_COARSE_GRID_READER','body':body,'body_sha256':digest(body)}
    validate_receipt(envelope,body)
    if args.check_receipt:
        validate_receipt(json.loads(args.check_receipt.read_text()),body)
    print(json.dumps(envelope,sort_keys=True,indent=2))


if __name__ == '__main__':
    main()
