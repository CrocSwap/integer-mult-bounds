"""Check every odd-width spectral block and the uniform endpoint proof."""
from fractions import Fraction as F
from hashlib import sha1, sha256
from math import comb
from pathlib import Path
import argparse
import importlib.util
import json
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'retained/source7766'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def read(file):
    return json.loads(file.read_text())


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def evaluate(coefficients, x):
    result = F(0)
    for c in reversed(coefficients):
        result = result*x + c
    return result


def multiply(a, b):
    out = [F(0)] * (len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return out


def spectral_polynomials(data):
    order = sum(data['element_counts'])
    result = []
    for i, row in enumerate(data['rows']):
        degree = row[0]
        sums = [0] + row[1:] + [degree]
        sums[0] = (order if i == 0 else 0) - sum(sums)
        result.append([F(c, degree) for c in reversed(sums)])
    return result


def check_moments(polynomials, data):
    degrees = [row[0] for row in data['rows']]
    order = sum(data['element_counts'])
    trace = [sum(e*e*p[r] for e, p in zip(degrees, polynomials, strict=True)) for r in range(9)]
    need(trace == [order] + [0]*8, 'complete spectral trace polynomial')
    squares = [multiply(p, p) for p in polynomials]
    moment = [sum(e*e*p[r] for e, p in zip(degrees, squares, strict=True)) for r in range(17)]
    expected = [F(0)] * 17
    for r, count in enumerate(reversed(data['element_counts'])):
        expected[2*r] = order*count
    need(moment == expected, 'complete spectral second-moment polynomial')
    return trace, moment


def bernstein(coefficients):
    n = len(coefficients)-1
    return [sum(coefficients[j]*F(comb(k, j), comb(n, j)) for j in range(k+1)) for k in range(n+1)]


def check_positive(coefficients, witness):
    n = len(coefficients)-1
    need(len(witness) == n+1 and min(witness) > 0, 'strictly positive Bernstein coefficients')
    expanded = [F(0)] * (n+1)
    for j, b in enumerate(witness):
        for k in range(n-j+1):
            expanded[j+k] += b*comb(n, j)*comb(n-j, k)*(-1)**k
    need(expanded == coefficients, 'Bernstein polynomial identity')


def compare_all(polynomials):
    certificates = []
    for sign, denominator in [(1, 128), (-1, 64)]:
        low, high = (1, 0) if sign == 1 else (0, 1)
        pairs = {(low, i) for i in range(81) if i != low}
        pairs |= {(i, high) for i in range(81) if i != high}
        for a, b in sorted(pairs):
            difference = [(polynomials[b][r]-polynomials[a][r])*F(sign, denominator)**r for r in range(9)]
            need(difference[0] == 0, 'common unit limit')
            quotient = difference[1:]
            witness = bernstein(quotient)
            check_positive(quotient, witness)
            certificates.append(dict(sign=sign, scale_denominator=denominator,
                                     lower_row=a+1, upper_row=b+1,
                                     bernstein=list(map(str, witness))))
    need(len(certificates) == 318, 'every strict endpoint comparison')
    return certificates


def phase(width):
    need(width > 0 and width % 2 == 1, 'positive odd width')
    return (-1)**((width+1)//4)


def check_width(width, polynomials, data, source):
    p = (width-1)//2
    x = phase(width)*F(1, 2**p)
    values = [evaluate(row, x) for row in polynomials]
    low, high = (1, 0) if x > 0 else (0, 1)
    need(all(values[low] < v for i, v in enumerate(values) if i != low), 'unique lower block')
    need(all(values[high] > v for i, v in enumerate(values) if i != high), 'unique upper block')
    need(values[low] > 0, 'positive complete spectrum')
    order = sum(data['element_counts'])
    degrees = [row[0] for row in data['rows']]
    multiples = [v*e*2**(8*p)/order for v, e in zip(values, degrees, strict=True)]
    need(all(m.denominator == 1 and m > 0 for m in multiples), 'actual tensor multiplicities')
    need(sum(m*e for m, e in zip(multiples, degrees, strict=True)) == 2**(8*p), 'tensor dimension')
    norm = source.tuple_orbits(2*p)
    need(sum(m*m for m in multiples) == norm, 'independent tuple-orbit norm')
    need(sum(c*2**(2*p*d) for d, c in enumerate(data['element_counts'])) == order*norm,
         'independent fixed-space moment')
    return dict(width=width, sign=phase(width), parameter=str(x), lower_row=low+1,
                upper_row=high+1, minimum=str(values[low]), maximum=str(values[high]),
                gram_condition=str(values[high]/values[low]))


def one_qubit():
    g = module('gaussian7772', HERE / 'retained/source7772/verify.py')
    unit = [[g.ONE, g.ZERO], [g.ZERO, g.ONE]]
    x = [[g.ZERO, g.ONE], [g.ONE, g.ZERO]]
    z = [[g.ONE, g.ZERO], [g.ZERO, (-F(1), F(0))]]
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
    need(len(elements) == 24, 'complete literal projective group')
    for a in elements:
        adjoint = [[g.conj(a[j][i]) for j in range(2)] for i in range(2)]
        need(g.product(adjoint, a) == unit, 'literal unitarity')
        for b in elements:
            need(canonical(g.product(a, b)) in seen, 'complete literal closure')
    paulies = [unit, x, z, g.product(x, z)]
    fibre_checks = 0
    phase_control = False
    for a in elements:
        traces = [g.add(b[0][0], b[1][1]) for p in paulies for b in [g.product(p, a)]]
        sizes = {g.mul(t, g.conj(t))[0] for t in traces if t != g.ZERO}
        need(len(sizes) == 1, 'constant nonzero Pauli trace size')
        size = sizes.pop()
        need(size.denominator == 1 and size.numerator in (1, 2, 4), 'binary trace size')
        d = size.numerator.bit_length()-1
        need(sum(t != g.ZERO for t in traces) == 2**(2-d), 'Pauli fibre multiplicity')
        for width in range(1, 32, 2):
            total = g.ZERO
            for t in traces:
                factor = g.conj(t) if width % 4 == 1 else t
                total = g.add(total, g.mul(g.power(t, width), factor))
            actual = (total[0]/4, total[1]/4)
            expected = (F(phase(width)**d * 2**(((width-1)//2)*d)), F(0))
            need(actual == expected, 'actual all-residue quotient character')
            if phase(width) == -1 and d == 1:
                phase_control |= actual != (abs(actual[0]), F(0))
            fibre_checks += 1
    need(phase_control, 'unsigned phase control')
    spectra = []
    for width in (13, 15, 17, 19):
        p, sigma = (width-1)//2, phase(width)
        character = [2**(2*p), sigma*2**p, 1]
        multiples = [F(character[0]+3*character[1]+2, 6),
                     F(character[0]-3*character[1]+2, 6), F(2*character[0]-2, 6)]
        eigenvalues = [6*m/F(2**(2*p)*e) for m, e in zip(multiples, (1,1,2), strict=True)]
        dimensions = [4, 4, 16]
        gram = []
        for a in elements:
            row = []
            for b in elements:
                inner = g.sum_pair(g.mul(g.conj(u), v) for ar, br in zip(a, b, strict=True)
                                   for u, v in zip(ar, br, strict=True))
                row.append(g.power((inner[0]/2, inner[1]/2), width))
            gram.append(row)
        shifted = [g.minus_scalar(gram, e) for e in eigenvalues]
        zero = g.product(g.product(shifted[0], shifted[1]), shifted[2])
        need(all(v == g.ZERO for row in zero for v in row), 'literal complete Gram annihilator')
        need(all(gram[i][i] == g.ONE and all(gram[i][j] == g.conj(gram[j][i]) for j in range(24))
                 for i in range(24)), 'literal normalized Hermitian Gram')
        second = sum(g.mul(v, g.conj(v))[0] for row in gram for v in row)
        need(len(set(eigenvalues)) == 3 and sum(e*d for e, d in zip(eigenvalues, dimensions, strict=True)) == 24
             and sum(e*e*d for e, d in zip(eigenvalues, dimensions, strict=True)) == second,
             'literal complete spectral dimensions')
        spectra.append(dict(width=width, eigenvalues=list(map(str, eigenvalues)), dimensions=dimensions))
    return dict(elements=24, closure_products=576, quotient_fibres=fibre_checks,
                whole_gram_spectra=spectra, unsigned_phase_control=True)


def reject(label, operation):
    try:
        operation()
    except ValueError as error:
        return dict(control=label, rejection=str(error))
    raise ValueError('accepted mutation ' + label)


def run():
    pins = read(HERE / 'SOURCE-PINS.json')['sources']
    for pin in pins:
        raw = (HERE / pin['retained']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'] and
             sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'], 'retained source bytes')
    command = [sys.executable, '-W', 'error', *(['-O'] if sys.flags.optimize else []), '-B', str(SOURCE / 'verify.py')]
    replay = subprocess.run(command, check=True, capture_output=True, text=True, timeout=60)
    need('PASS_CLIFFORD_FOUR_QUBIT_THRESHOLD' in replay.stdout, 'unchanged source replay')
    source = module('threshold7766', SOURCE / 'verify.py')
    data = read(SOURCE / 'retained/source7747/PROJECTION.json')
    polynomials = spectral_polynomials(data)
    need(len(polynomials) == 81 and all(len(p) == 9 and p[0] == 1 for p in polynomials), 'complete block polynomials')
    trace, moment = check_moments(polynomials, data)
    certificates = compare_all(polynomials)
    positive_endpoints = []
    for row, sign, denominator in [(0, -1, 64), (1, 1, 128)]:
        coefficients = [c*F(sign, denominator)**r for r, c in enumerate(polynomials[row])]
        witness = bernstein(coefficients)
        check_positive(coefficients, witness)
        positive_endpoints.append(dict(row=row+1, sign=sign, scale_denominator=denominator,
                                       bernstein=list(map(str, witness))))
    widths = [check_width(f, polynomials, data, source) for f in range(13, 82, 2)]
    old = read(HERE / 'retained/source7772/RESULT.json')
    need(widths[0]['minimum'] == str(F(*old['minimum'])) and
         widths[0]['maximum'] == str(F(*old['maximum'])) and
         widths[0]['gram_condition'] == str(F(*old['gram_condition'])), 'published threshold endpoints')
    need(polynomials[0][1] == 255 and polynomials[1][1] == -153, 'sharp first-order gap 408')
    controls = []
    changed = [p.copy() for p in polynomials]
    changed[1][-1] = 0
    controls.append(reject('omit a zero-fixed-space term', lambda: check_moments(changed, data)))
    controls.append(reject('extra scalar-group factor four', lambda: check_moments([[4*c for c in p] for p in polynomials], data)))
    c = certificates[0]
    bad = [F(v) for v in c['bernstein']]
    bad[0] = -bad[0]
    a, b = c['lower_row']-1, c['upper_row']-1
    q = [(polynomials[b][r]-polynomials[a][r])*F(c['sign'], c['scale_denominator'])**r for r in range(1,9)]
    controls.append(reject('negative Bernstein coefficient', lambda: check_positive(q, bad)))
    bad = [F(v) for v in c['bernstein']]
    bad[-1] += 1
    controls.append(reject('positive but incorrect certificate', lambda: check_positive(q, bad)))
    wrong = [(polynomials[1][r]-polynomials[2][r])*F(1,128)**r for r in range(1,9)]
    controls.append(reject('wrong minimum block', lambda: check_positive(wrong, bernstein(wrong))))
    controls.append(reject('even width in odd-sector formula', lambda: phase(14)))
    return dict(source_files=len(pins), projective_order=256*sum(data['element_counts']),
                rows=[dict(row=i+1, quotient_degree=data['rows'][i][0],
                           regular_dimension=(16*data['rows'][i][0])**2,
                           coefficients=list(map(str,p))) for i,p in enumerate(polynomials)],
                comparison_certificates=certificates, bernstein_coefficients=8*len(certificates),
                positive_endpoint_certificates=positive_endpoints,
                minimum_bernstein_coefficient=str(min(F(v) for c in certificates for v in c['bernstein'])),
                trace_polynomial=list(map(str, trace)), second_moment_polynomial=list(map(str, moment)),
                width_checks=widths, condition_first_order_coefficient=408,
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
        need(result == read(HERE / 'RESULT.json'), 'deposited exact certificate')
    print('PASS_CLIFFORD_ODD_WIDTH_SPECTRUM', len(result['rows']), 'blocks',
          len(result['comparison_certificates']), 'order proofs',
          len(result['positive_endpoint_certificates']), 'positive endpoints',
          round(time.monotonic()-start, 2), 'seconds')
