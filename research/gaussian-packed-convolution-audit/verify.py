#!/usr/bin/env python3
"""Independent finite audit of PR489 signed packed convolution (Apache-2.0).

Oracle: integer dot products and a single divmod, not packing, shifts, source
rounded(), or source bits=None. See PROOF.md for the all-length radix argument.
"""
import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SEED = 79
LENGTHS = (1, 2, 3, 4, 7, 8, 9, 15, 16, 17, 31, 32)
BITS = (0, 1, 3, 17, 64)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def trunc_integer(value, divisor):
    """Sign-symmetric integer division, independently of the source oracle."""
    quotient, _ = divmod(abs(value), divisor)
    return -quotient if value < 0 else quotient


def oracle(h, x, bits, upper=False):
    """Output GRID NUMERATORS for inputs h/2**bits and x/2**bits."""
    scale, n = 2**bits, len(x)
    require(n > 0 and len(h) == n, 'invalid oracle dimensions')
    out = []
    for i in range(n):
        terms = (h[j-i]*x[j] for j in range(i, n)) if upper else (
            h[i-j]*x[j] for j in range(i+1))
        out.append(trunc_integer(sum(terms), scale))
    return out


def load_source(text, filename):
    namespace = {'__name__': 'pinned_pr489'}
    exec(compile(text, filename, 'exec'), namespace)
    return namespace


def source_call(module, h, x, bits, upper=False, wrapper='normal'):
    scale = 2**bits
    a, b = [Fraction(v, scale) for v in h], [Fraction(v, scale) for v in x]
    counts = module['counter']()
    if upper:
        if wrapper == 'reverse-kernel':
            a = list(reversed(a))
        got = module['packed_lower'](a, list(reversed(b)), bits, counts)
        if wrapper != 'omit-output-reversal':
            got = list(reversed(got))
    else:
        got = module['packed_lower'](a, b, bits, counts)
    scaled = [v*scale for v in got]
    require(all(v.denominator == 1 for v in scaled), 'source left the output grid')
    return [int(v) for v in scaled], counts


def pin_check():
    source = json.loads((ROOT/'SOURCE.json').read_text())
    for path, metadata in source['files'].items():
        data = (ROOT/path).read_bytes()
        require(hashlib.sha256(data).hexdigest() == metadata['sha256'], 'source SHA256 mismatch: '+path)
        blob = b'blob '+str(len(data)).encode()+b'\0'+data
        require(hashlib.sha1(blob).hexdigest() == metadata['git_blob_sha1'], 'source Git blob mismatch: '+path)
    return source


def fixed_cases(n, bits):
    s, big = 2**bits, 2**127
    yield 'zero-kernel', [0]*n, [big+1]*n
    yield 'zero-input', [big-1]*n, [0]*n
    yield 'carry-positive', [big-1]*n, [big+1]*n
    yield 'carry-negative', [-(big+1)]*n, [big-1]*n
    yield 'alternating', [(-1)**i*(big+i) for i in range(n)], [(-1)**(i//2)*(big-i) for i in range(n)]
    yield 'near-cancellation', [s+1]*n, [(-1)**i*(s+(-1)**(i//2)) for i in range(n)]
    yield 'endpoint-impulses', [big if i in (0, n-1) else 0 for i in range(n)], [(-1)**i*(i+1) for i in range(n)]
    palette = (0, 1, s-1, s, s+1, big-1, big, big+1)
    def seeded(side):
        out = []
        for i in range(n):
            digest = hashlib.sha256(('%d/%d/%d/%s/%d' % (SEED, n, bits, side, i)).encode()).digest()
            out.append((-1 if digest[0] & 1 else 1)*palette[digest[1] % len(palette)])
        return out
    yield 'seeded-mixed', seeded('h'), seeded('x')


def negative_controls(text, base):
    width = 'width = max(1, (n*max(map(abs, hh))*max(map(abs, xx))).bit_length()+1)'
    rounding = 'k = abs(x.numerator*scale)//x.denominator\n    return Q(k if x >= 0 else -k, scale)'
    old_return = ('return [rounded(Q(sum(sign*((v >> (width*i)) & mask) for v, sign in products), scale*scale), bits)\n'
                  '            for i in range(n)]')
    per_product = ('return [sum((sign*rounded(Q((v >> (width*i)) & mask, scale*scale), bits)\n'
                   '                    for v, sign in products), Q(0)) for i in range(n)]')
    mutations = [
        ('insufficient-slot-width', width, width.replace('bit_length()+1', 'bit_length()-1'), [1, 1], [1, 1], 0),
        ('omit-positive-negative-product', '(hp*xm, -1)', '(hp*xm, 0)', [1, 0], [-1, 0], 0),
        ('wrong-negative-negative-sign', '(hm*xm, 1)', '(hm*xm, -1)', [-1], [-1], 0),
        ('floor-instead-of-toward-zero', rounding, 'return Q((x.numerator*scale)//x.denominator, scale)', [-1], [1], 1),
        ('round-products-before-cancellation', old_return, per_product, [1, 1], [1, -2], 1),
        ('wrong-scale-square', 'scale*scale), bits)', 'scale), bits)', [2], [2], 1),
    ]
    result = []
    for name, old, new, h, x, bits in mutations:
        require(text.count(old) == 1, 'mutation site not unique: '+name)
        mutant = load_source(text.replace(old, new), '<mutant:'+name+'>')
        want = oracle(h, x, bits)
        original, _ = source_call(base, h, x, bits)
        require(original == want, 'negative control baseline failed: '+name)
        # An exception is NOT counted as detection: each mutant must execute
        # and disagree with the independent arithmetic result.
        got, _ = source_call(mutant, h, x, bits)
        require(got != want, 'mutation unexpectedly survived: '+name)
        result.append(dict(name=name, h=h, x=x, bits=bits, upper=False,
                           expected_grid_numerators=want, mutant_grid_numerators=got))
    for name in ('omit-output-reversal', 'reverse-kernel'):
        h, x, bits = [1, 2, 4], [3, 5, 7], 0
        want = oracle(h, x, bits, upper=True)
        original, _ = source_call(base, h, x, bits, upper=True)
        require(original == want, 'upper baseline failed')
        got, _ = source_call(base, h, x, bits, upper=True, wrapper=name)
        require(got != want, 'upper mutation survived: '+name)
        result.append(dict(name=name, h=h, x=x, bits=bits, upper=True,
                           expected_grid_numerators=want, mutant_grid_numerators=got))
    return result


def run():
    require(not sys.flags.optimize, 'Run without -O: inherited source admission uses assertions')
    source = pin_check()
    text = (ROOT/'vendor/branchfree.py').read_text()
    module = load_source(text, str(ROOT/'vendor/branchfree.py'))
    require(oracle([1, 2], [3, 4], 0) == [3, 10], 'oracle hand check, lower')
    require(oracle([1, 2], [3, 4], 0, True) == [11, 4], 'oracle hand check, upper')
    require(oracle([-3, 2], [1, -2], 1) == [-1, 4], 'oracle hand check, signed rounding')
    require(oracle([-3, 2], [1, -2], 1, True) == [-3, 3], 'oracle hand check, upper rounding')
    transcript = hashlib.sha256()
    totals = dict(vector_pairs=0, source_calls=0, output_coordinates=0,
                  negative_output_coordinates=0, zero_output_coordinates=0,
                  integer_products=0, max_operand_bits=0, max_input_numerator_bits=0)
    def check(h, x, bits):
        totals['vector_pairs'] += 1
        totals['max_input_numerator_bits'] = max(totals['max_input_numerator_bits'], *(abs(v).bit_length() for v in h+x))
        for upper in (False, True):
            want = oracle(h, x, bits, upper)
            got, counts = source_call(module, h, x, bits, upper)
            require(got == want, 'coefficient mismatch: '+str((h, x, bits, upper, want, got)))
            require(counts['convolutions'] == 1 and counts['integer_products'] == 4, 'did not exercise packed path')
            totals['source_calls'] += 1
            totals['output_coordinates'] += len(got)
            totals['negative_output_coordinates'] += sum(v < 0 for v in got)
            totals['zero_output_coordinates'] += sum(v == 0 for v in got)
            totals['integer_products'] += counts['integer_products']
            totals['max_operand_bits'] = max(totals['max_operand_bits'], counts['max_operand_bits'])
            transcript.update(canonical([h, x, bits, upper, want])+b'\n')
    exhaustive = []
    for n in range(1, 5):
        for bits in (0, 1, 3):
            amplitude = max(1, 2**bits-1)
            vectors = list(itertools.product((-amplitude, 0, amplitude), repeat=n))
            for h in vectors:
                for x in vectors:
                    check(list(h), list(x), bits)
            exhaustive.append(dict(n=n, bits=bits, numerator_alphabet=[-amplitude, 0, amplitude], vector_pairs=len(vectors)**2))
    require(totals['vector_pairs'] == 22140, 'exhaustive coverage incomplete')
    stress = []
    for n in LENGTHS:
        for bits in BITS:
            names = []
            for name, h, x in fixed_cases(n, bits):
                check(h, x, bits)
                names.append(name)
            require(len(names) == 8, 'stress coverage incomplete')
            stress.append(dict(n=n, bits=bits, patterns=names))
    require(totals['vector_pairs'] == 22620, 'total coverage incomplete')
    controls = negative_controls(text, module)
    admission = []
    for name, h, x in [('off-grid-kernel', [Fraction(1, 3)], [Fraction(1)]),
                       ('off-grid-input', [Fraction(1)], [Fraction(1, 3)]),
                       ('unequal-length', [Fraction(1)], [Fraction(1), Fraction(1)])]:
        try:
            module['packed_lower'](h, x, 3, module['counter']())
        except AssertionError:
            admission.append(name)
        else:
            raise RuntimeError('source admission control survived: '+name)
    require(pin_check() == source, 'source changed during replay')
    return dict(status='PASS_INDEPENDENT_SIGNED_PACKED_CONVOLUTION', seed=SEED,
                source=source, exhaustive=exhaustive, stress=stress, totals=totals,
                transcript_sha256=transcript.hexdigest(), negative_controls=controls,
                admission_controls=admission,
                scope='Finite exact packed-convolution audit plus separate elementary radix proof; no all-size tape, Gaussian error-transfer, or kappa claim')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path, help='Explicit bootstrap: write a NEW expected receipt, without comparison')
    parser.add_argument('--output', type=Path, help='Write a NEW receipt after comparison with EXPECTED.json')
    args = parser.parse_args()
    require(not (args.record and args.output), 'choose either --record or --output')
    result = run()
    if not args.record:
        expected = json.loads((ROOT/'EXPECTED.json').read_text())
        require(result == expected, 'complete receipt differs from EXPECTED.json')
    destination = args.record or args.output
    if destination:
        with destination.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    print(result['status'])
    print(json.dumps(result['totals'], sort_keys=True))
    print('semantic mutants rejected=%d; admission controls=%d' % (len(result['negative_controls']), len(result['admission_controls'])))


if __name__ == '__main__':
    main()
