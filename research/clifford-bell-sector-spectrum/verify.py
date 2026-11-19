"""Check the full central-character-minus-one Clifford spectrum."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha1, sha256
from pathlib import Path
import argparse
import importlib.util
import json
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'retained/source7771'


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


v = module('polynomial7788', HERE / 'retained/source7788/verify.py')
need, read, evaluate = v.need, v.read, v.evaluate


def coefficients(row, order, trivial):
    sums = [0] + row['sums_d1_to7'] + [row['degree']]
    sums[0] = (order if trivial else 0) - sum(sums)
    return [F(c, row['degree']) for c in sums[::-1]]


def make_rows(data, quotient):
    sp = v.spectral_polynomials(quotient)
    result = []
    for group in data['groups']:
        index = 120 if group['kind'] == 'minus' else 136
        need(index*group['order'] == 47377612800, 'actual stabilizer index')
        local = []
        for i, row in enumerate(group['rows']):
            direct = coefficients(row, group['order'], i == 0)
            restricted = [sum(quotient['rows'][j-1][0]*n*sp[j-1][r] for j, n in row['restriction'])
                          / (index*row['degree']) for r in range(9)]
            need(direct == restricted, 'all-coefficient quotient restriction')
            need(direct[0] == 1, 'unit large-width limit')
            entry = dict(kind=group['kind'], row=i+1, degree=row['degree'],
                         clifford_degree=index*row['degree'], coefficients=direct)
            result.append(entry)
            local.append((row['degree'], tuple(direct)))
        reflected = [(e, tuple(c*(-1)**r for r, c in enumerate(p))) for e, p in local]
        need(Counter(local) == Counter(reflected), 'complete Dickson-twist spectral multiset')
    need(len(result) == 127 and sum(r['clifford_degree']**2 for r in result) == 12128668876800,
         'complete central-character ideal')
    return result


def moments(rows, quotient):
    trace = [sum(row['clifford_degree']**2*row['coefficients'][r] for row in rows) for r in range(9)]
    need(trace == [12128668876800] + [0]*8, 'full normalized trace polynomial')
    squared = [v.multiply(row['coefficients'], row['coefficients']) for row in rows]
    moment = [sum(row['clifford_degree']**2*p[r] for row, p in zip(rows, squared, strict=True)) for r in range(17)]
    expected = [F(0)]*17
    for r, c in enumerate(reversed(quotient['element_counts'])):
        expected[2*r] = F(12128668876800*c, 2**r)
    need(moment == expected, 'independent Pauli-lift moment polynomial')
    return trace, moment


def endpoint_proofs(rows):
    polynomials = [row['coefficients'] for row in rows]
    need(rows[0]['kind'] == rows[1]['kind'] == 'minus' and
         rows[0]['degree'] == rows[1]['degree'] == 1, 'trivial and Dickson endpoint rows')
    need(polynomials[1] == [c*(-1)**r for r, c in enumerate(polynomials[0])], 'actual Dickson endpoint polynomial')
    pairs = {(1, i) for i in range(127) if i != 1} | {(i, 0) for i in range(127) if i != 0}
    certificates = []
    for a, b in sorted(pairs):
        difference = [(polynomials[b][r]-polynomials[a][r])*F(1,64)**r for r in range(9)]
        need(difference[0] == 0, 'common constant coefficient')
        witness = v.bernstein(difference[1:])
        v.check_positive(difference[1:], witness)
        certificates.append(dict(lower=[rows[a]['kind'], rows[a]['row']],
                                 upper=[rows[b]['kind'], rows[b]['row']],
                                 bernstein=list(map(str, witness))))
    positive = [c*F(1,64)**r for r, c in enumerate(polynomials[1])]
    witness = v.bernstein(positive)
    v.check_positive(positive, witness)
    need(len(certificates) == 251, 'all strict endpoint comparisons')
    return certificates, list(map(str, witness))


def parameters(width):
    need(width >= 14 and width % 4 == 2, 'width in the declared central sector')
    p = (width-2)//2
    return p, (-1)**(p//2)


def widths(data, rows, source):
    records = []
    for width in range(14, 99, 4):
        p, sign = parameters(width)
        t = F(1, 2**p)
        values = [evaluate(row['coefficients'], sign*t) for row in rows]
        lo, hi = (1, 0) if sign == 1 else (0, 1)
        need(all(values[lo] < x for i, x in enumerate(values) if i != lo) and
             all(values[hi] > x for i, x in enumerate(values) if i != hi) and values[lo] > 0,
             'unique positive endpoint values')
        offset = 0
        for group in data['groups']:
            group_rows = rows[offset:offset+len(group['rows'])]
            group_values = values[offset:offset+len(group['rows'])]
            multiples = [x*row['degree']*2**(8*p)/group['order']
                         for row, x in zip(group_rows, group_values, strict=True)]
            need(all(m > 0 and m.denominator == 1 for m in multiples), 'actual tensor multiplicities')
            need(sum(m*row['degree'] for m, row in zip(multiples, group_rows, strict=True)) == 2**(8*p),
                 'whole restricted tensor dimension')
            need(sum(m*m for m in multiples) == source.quadratic_tuple_orbits(4, 2*p, group['kind'] == 'minus'),
                 'independent quadratic tuple norm')
            offset += len(group_rows)
        h = rows[0]['coefficients']
        need(values[lo] == evaluate(h, -t) and values[hi] == evaluate(h, t), 'phase-independent endpoint values')
        records.append(dict(width=width, sign=sign, parameter=str(sign*t),
                            minimum=str(values[lo]), maximum=str(values[hi]),
                            lower_row=lo+1, upper_row=hi+1,
                            gram_condition=str(values[hi]/values[lo])))
    return records


def one_qubit():
    g = module('gaussian7772', HERE / 'retained/gaussian7772/verify.py')
    unit = [[g.ONE, g.ZERO], [g.ZERO, g.ONE]]
    s = [[g.ONE, g.ZERO], [g.ZERO, (F(0), F(1))]]
    h = [[(F(1,2), F(1,2)), (F(1,2), F(1,2))],
         [(F(1,2), F(1,2)), (-F(1,2), -F(1,2))]]
    phases = [g.ONE, (F(0), F(1)), (-F(1), F(0)), (F(0), -F(1))]
    def canonical(a):
        return max(tuple(tuple(g.mul(v, t) for v in row) for row in a) for t in phases)
    elements = [canonical(unit)]
    seen = set(elements)
    for a in elements:
        for generator in (s, h):
            b = canonical(g.product(generator, a))
            if b not in seen:
                seen.add(b)
                elements.append(b)
    need(len(elements) == 24, 'literal projective group size')
    for a in elements:
        adjoint = [[g.conj(a[j][i]) for j in range(2)] for i in range(2)]
        need(g.product(adjoint, a) == unit, 'literal unitary')
        for b in elements:
            need(canonical(g.product(a, b)) in seen, 'literal complete closure')
    records = []
    for width in (6, 10, 14, 18):
        p = (width-2)//2
        u = (-1)**(p//2)*F(1, 2**p)
        eigenvalues = [1+3*u+2*u*u, 1-3*u+2*u*u, 1-u*u, 1+u, 1-u]
        dimensions = [1, 1, 4, 9, 9]
        gram = []
        for a in elements:
            row = []
            for b in elements:
                inner = g.sum_pair(g.mul(g.conj(x), y) for ar, br in zip(a, b, strict=True)
                                   for x, y in zip(ar, br, strict=True))
                row.append(g.power((inner[0]/2, inner[1]/2), width))
            gram.append(row)
        need(all(gram[i][i] == g.ONE and all(gram[i][j] == g.conj(gram[j][i]) for j in range(24))
                 for i in range(24)), 'literal Hermitian normalized Gram')
        polynomial = g.minus_scalar(gram, eigenvalues[0])
        for root in eigenvalues[1:]:
            polynomial = g.product(polynomial, g.minus_scalar(gram, root))
        need(all(v == g.ZERO for row in polynomial for v in row), 'literal five-root annihilator')
        need(len(set(eigenvalues)) == 5 and sum(dimensions) == 24, 'five distinct blocks')
        power = gram
        moments = []
        for k in range(1,5):
            trace = g.sum_pair(power[i][i] for i in range(24))
            expected = sum(d*e**k for d, e in zip(dimensions, eigenvalues, strict=True))
            need(trace == (expected, F(0)), 'all five spectral dimensions')
            moments.append(str(expected))
            if k < 4:
                power = g.product(power, gram)
        records.append(dict(width=width, eigenvalues=list(map(str,eigenvalues)), dimensions=dimensions, moments=moments))
    return dict(elements=24, closure_products=576, whole_gram_spectra=records)


def run():
    pins = read(HERE / 'SOURCE-PINS.json')['sources']
    for pin in pins:
        raw = (HERE / pin['retained']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'] and
             sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'], 'retained source bytes')
    command = [sys.executable, '-W', 'error', *(['-O'] if sys.flags.optimize else []), '-B', str(SOURCE / 'verify.py')]
    run = subprocess.run(command, check=True, capture_output=True, text=True, timeout=60)
    need('PASS_CLIFFORD_WIDTH_TEN_NULLITY' in run.stdout, 'unchanged stabilizer source replay')
    source = module('stabilizers7771', SOURCE / 'verify.py')
    data = read(SOURCE / 'STABILIZERS.json')
    quotient = read(SOURCE / 'retained/source7766/retained/source7747/PROJECTION.json')
    rows = make_rows(data, quotient)
    trace, moment = moments(rows, quotient)
    certificates, positive = endpoint_proofs(rows)
    evaluations = widths(data, rows, source)
    need(rows[0]['coefficients'][1] == 136, 'sharp first-order condition coefficient 272')
    controls = []
    changed = json.loads(json.dumps(data))
    changed['groups'][0]['rows'][0]['restriction'][0][1] += 1
    controls.append(v.reject('changed restriction coefficient', lambda: make_rows(changed, quotient)))
    controls.append(v.reject('omit the plus quadratic orbit', lambda: moments(rows[:60], quotient)))
    changed_rows = [row | {'coefficients': [4*c for c in row['coefficients']]} for row in rows]
    controls.append(v.reject('wrong scalar-group factor four', lambda: moments(changed_rows, quotient)))
    q = [(rows[1]['coefficients'][r]-rows[0]['coefficients'][r])*F(1,64)**r for r in range(1,9)]
    controls.append(v.reject('swap positive-parameter extrema', lambda: v.check_positive(q, v.bernstein(q))))
    q = [c*F(1,64)**r for r, c in enumerate(rows[1]['coefficients'])]
    wrong = list(map(F, positive))
    wrong[-1] += 1
    controls.append(v.reject('positive but incorrect endpoint certificate', lambda: v.check_positive(q, wrong)))
    controls.append(v.reject('wrong even central sector', lambda: parameters(16)))
    return dict(source_files=len(pins), projective_order=12128668876800,
                rows=[row | {'coefficients': list(map(str,row['coefficients']))} for row in rows],
                comparison_certificates=certificates, positive_minimum_certificate=positive,
                minimum_comparison_coefficient=str(min(F(x) for c in certificates for x in c['bernstein'])),
                minimum_endpoint_coefficient=str(min(map(F,positive))),
                restriction_coefficient_identities=127*9,
                trace_polynomial=list(map(str,trace)), second_moment_polynomial=list(map(str,moment)),
                width_checks=evaluations, condition_first_order_coefficient=272,
                endpoint_eigenspace_dimensions=[14400,14400],
                one_qubit_calibration=one_qubit(), controls=controls)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    start = time.monotonic()
    result = run()
    if args.record:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    else:
        need(result == read(HERE / 'RESULT.json'), 'deposited spectral certificate')
    print('PASS_CLIFFORD_BELL_SECTOR_SPECTRUM', len(result['rows']), 'blocks',
          len(result['comparison_certificates']), 'order proofs',
          result['restriction_coefficient_identities'], 'restriction identities',
          round(time.monotonic()-start, 2), 'seconds')
