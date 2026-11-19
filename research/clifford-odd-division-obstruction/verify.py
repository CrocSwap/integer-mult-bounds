"""Check the exact coefficient-ring obstruction and its scope controls."""
from fractions import Fraction as F
from hashlib import sha1, sha256
from math import comb, lcm, prod
from pathlib import Path
import argparse
import importlib.util
import json
import time

HERE = Path(__file__).resolve().parent


def need(value, reason):
    if not value:
        raise ValueError(reason)


def read(path):
    return json.loads(path.read_text())


def valuation(n):
    need(n != 0, 'nonzero valuation input')
    return (abs(n) & -abs(n)).bit_length()-1


def evaluate(coefficients, x):
    result = F(0)
    for c in reversed(coefficients):
        result = result*x+c
    return result


def positive_certificate(coefficients, witness):
    need(len(coefficients) == len(witness) == 9 and min(witness) > 0,
         'positive degree-eight Bernstein certificate')
    expanded = [F(0)]*9
    for j, b in enumerate(witness):
        for k in range(9-j):
            expanded[j+k] += b*comb(8, j)*comb(8-j, k)*(-1)**k
    need(expanded == coefficients, 'exact Bernstein expansion')


def valuation_certificate(coefficients, expected):
    values = [valuation(c) for c in coefficients]
    need(values == expected, 'specified coefficient valuations')
    gaps = [values[r]-6*r-(values[8]-48) for r in range(8)]
    need(min(gaps) > 0, 'unique least valuation for every p>=6')
    return values, gaps


def parameters(kind, width):
    if kind == 'odd':
        need(width >= 13 and width % 2 == 1, 'odd-width domain')
        return (width-1)//2, (-1)**((width+1)//4)
    need(kind == 'bell' and width >= 14 and width % 4 == 2, 'Bell-width domain')
    p = (width-2)//2
    return p, (-1)**(p//2)


def factor(n):
    result = []
    divisor = 3
    while divisor*divisor <= n:
        exponent = 0
        while n % divisor == 0:
            exponent += 1
            n //= divisor
        if exponent:
            result.append([divisor, exponent])
        divisor += 2
    if n > 1:
        result.append([n, 1])
    return result


def spectral_obstructions():
    cases = []
    for kind, source, expected, widths in [
        ('odd', 'source7788', [0, 0, 2, 2, 6, 6, 12, 12, 16], range(13, 130, 2)),
        ('bell', 'source7789', [0, 3, 0, 3, 2, 5, 6, 9, 13], range(14, 131, 4))]:
        data = read(HERE/'retained'/source/'RESULT.json')
        row = data['rows'][0]
        need(row['row'] == 1, 'trivial source row')
        if kind == 'bell':
            need(row['kind'] == 'minus' and row['degree'] == 1, 'minus Bell trivial row')
            witness = list(map(F, data['positive_minimum_certificate']))
        else:
            need(row['quotient_degree'] == 1, 'trivial quotient row')
            cert = data['positive_endpoint_certificates'][0]
            need((cert['row'], cert['sign'], cert['scale_denominator']) == (1, -1, 64),
                 'source certificate boundary')
            witness = list(map(F, cert['bernstein']))
        coefficients = [int(c) for c in row['coefficients']]
        need(all(c > 0 for c in coefficients) and coefficients[0] == 1,
             'positive-side polynomial lower bound')
        values, gaps = valuation_certificate(coefficients, expected)
        scaled = [c*F(-1, 64)**r for r, c in enumerate(coefficients)]
        positive_certificate(scaled, witness)
        bound = min(witness)*2**(48-values[8])
        need(bound.denominator == 1 and bound > 1, 'uniform odd numerator exceeds one')
        samples = []
        for width in widths:
            p, sign = parameters(kind, width)
            eigenvalue = evaluate(coefficients, sign*F(1, 2**p))
            exponent = 8*p-values[8]
            need(eigenvalue.denominator == 2**exponent and
                 eigenvalue.numerator % 2 == 1 and eigenvalue.numerator >= bound,
                 'exact reduced eigenvalue numerator and denominator')
            need((1/eigenvalue).denominator == eigenvalue.numerator, 'odd inverse denominator')
            samples.append(dict(width=width, p=p, sign=sign, eigenvalue=str(eigenvalue),
                                mandatory_odd_denominator=eigenvalue.numerator))
        primes = factor(samples[0]['mandatory_odd_denominator'])
        need(prod(q**e for q, e in primes) == samples[0]['mandatory_odd_denominator'],
             'complete first-width factorization')
        decoder_divisor = prod(q**((e+1)//2) for q, e in primes)
        need(decoder_divisor**2 % samples[0]['mandatory_odd_denominator'] == 0 and
             all((decoder_divisor//q)**2 % samples[0]['mandatory_odd_denominator'] != 0
                 for q, _ in primes), 'least scalar divisor whose square contains numerator')
        cases.append(dict(sector=kind, coefficients=coefficients, valuations=values,
                          valuation_gaps_at_p6=gaps, gap_slopes=list(range(8, 0, -1)),
                          negative_interval_bernstein=list(map(str, witness)),
                          uniform_numerator_lower_bound=int(bound),
                          first_width_mandatory_primes=primes,
                          first_width_decoder_denominator_divisor=decoder_divisor, samples=samples))
    return cases


def one_qubit_inverse():
    path = HERE/'retained/source7772/verify.py'
    spec = importlib.util.spec_from_file_location('gaussian7772', path)
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    unit = [[g.ONE, g.ZERO], [g.ZERO, g.ONE]]
    phase = [[g.ONE, g.ZERO], [g.ZERO, (F(0), F(1))]]
    h = [[(F(1, 2), F(1, 2)), (F(1, 2), F(1, 2))],
         [(F(1, 2), F(1, 2)), (-F(1, 2), -F(1, 2))]]
    phases = [g.ONE, (F(0), F(1)), (-F(1), F(0)), (F(0), -F(1))]

    def canonical(a):
        return max(tuple(tuple(g.mul(v, t) for v in row) for row in a) for t in phases)

    elements = [canonical(unit)]
    seen = set(elements)
    for a in elements:
        for generator in (phase, h):
            b = canonical(g.product(generator, a))
            if b not in seen:
                seen.add(b)
                elements.append(b)
    need(len(elements) == 24, 'complete one-qubit projective group')
    for a in elements:
        adjoint = [[g.conj(a[j][i]) for j in range(2)] for i in range(2)]
        need(g.product(adjoint, a) == unit, 'literal unitarity')
        for b in elements:
            need(canonical(g.product(a, b)) in seen, 'literal group closure')
    gram = []
    for a in elements:
        row = []
        for b in elements:
            inner = g.sum_pair(g.mul(g.conj(u), v) for ar, br in zip(a, b, strict=True)
                               for u, v in zip(ar, br, strict=True))
            row.append(g.power((inner[0]/2, inner[1]/2), 6))
        gram.append(row)
    n = len(gram)
    identity = [[g.ONE if i == j else g.ZERO for j in range(n)] for i in range(n)]
    augmented = [a.copy()+b for a, b in zip(gram, identity, strict=True)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if augmented[i][j] != g.ZERO)
        augmented[j], augmented[pivot] = augmented[pivot], augmented[j]
        a, b = augmented[j][j]
        inverse = (a/(a*a+b*b), -b/(a*a+b*b))
        augmented[j] = [g.mul(x, inverse) for x in augmented[j]]
        for i in range(n):
            if i != j:
                coefficient = augmented[i][j]
                augmented[i] = [g.add(x, g.mul((-coefficient[0], -coefficient[1]), y))
                                for x, y in zip(augmented[i], augmented[j], strict=True)]
    inverse = [row[n:] for row in augmented]
    need([row[:n] for row in augmented] == identity, 'complete exact elimination')
    need(g.product(gram, inverse) == g.product(inverse, gram) == identity,
         'both literal inverse products')
    need(all(c.denominator & (c.denominator-1) == 0 for row in gram for x in row for c in x),
         'Gaussian-dyadic Gram coefficients')
    denominator = lcm(*(c.denominator for row in inverse for x in row for c in x))
    odd = denominator >> valuation(denominator)
    need(odd > 1, 'literal inverse requires odd division')
    witness = next((i, j, x) for i, row in enumerate(inverse) for j, x in enumerate(row)
                   if any(c.denominator & (c.denominator-1) for c in x))
    return dict(width=6, elements=n, closure_products=n*n, inverse_product_entries=2*n*n,
                coefficient_denominator_lcm=denominator, odd_part=odd,
                entry_witness=[witness[0], witness[1], list(map(str, witness[2]))])


def reject(label, operation):
    try:
        operation()
    except ValueError as error:
        return dict(control=label, rejection=str(error))
    raise ValueError('accepted mutation '+label)


def run():
    pins = read(HERE/'SOURCE-PINS.json')['sources']
    for pin in pins:
        raw = (HERE/pin['retained']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'] and
             sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'],
             'retained source bytes')
    cases = spectral_obstructions()
    c = cases[0]
    bad = c['coefficients'].copy()
    bad[-1] *= 2
    controls = [reject('alter highest coefficient', lambda: valuation_certificate(bad, c['valuations']))]
    witness = list(map(F, c['negative_interval_bernstein']))
    scaled = [a*F(-1, 64)**r for r, a in enumerate(c['coefficients'])]
    witness[-1] += 1
    controls.append(reject('positive but false certificate', lambda: positive_certificate(scaled, witness)))
    witness[-1] = -1
    controls.append(reject('nonpositive certificate', lambda: positive_certificate(scaled, witness)))
    controls.append(reject('even width in odd sector', lambda: parameters('odd', 14)))
    controls.append(reject('other even central sector', lambda: parameters('bell', 16)))
    controls.append(reject('below full-rank range', lambda: parameters('odd', 11)))
    # This exact left inverse is distinct from the canonical least-squares map.
    column, left, canonical = [F(1), F(2)], [F(1), F(0)], [F(1, 5), F(2, 5)]
    need(sum(x*y for x, y in zip(left, column, strict=True)) == 1 and
         sum(x*y for x, y in zip(canonical, column, strict=True)) == 1 and
         sum(x*x for x in canonical) == F(1, 5), 'left-inverse scope counterexample')
    need(F(1, 8)*8 == 1, 'dyadic-unit positive control')
    return dict(source_files=len(pins), sectors=cases,
                width_checks=sum(len(c['samples']) for c in cases),
                one_qubit_inverse=one_qubit_inverse(), controls=controls,
                noncanonical_left_inverse=dict(column=list(map(str, column)),
                    left_inverse=list(map(str, left)), canonical_inverse=list(map(str, canonical))),
                dyadic_unit_positive_control=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    start = time.monotonic()
    result = run()
    path = HERE/'RESULT.json'
    if args.write_result:
        path.write_text(json.dumps(result, indent=2)+'\n')
    else:
        need(result == read(path), 'computed receipt matches committed receipt')
    print('PASS_CLIFFORD_ODD_DIVISION_OBSTRUCTION', result['width_checks'],
          'widths; two infinite-width certificates;', len(result['controls']),
          'rejecting controls;', round(time.monotonic()-start, 2), 'seconds')
