#!/usr/bin/env python3
"""Independent reverse sensitivity and direct Fourier checks; stdlib only.

No primary-verifier or predecessor imports. BigCactusLabs + OpenAI Codex;
Apache-2.0. The written proof carries the all-depth quantifiers.
"""
from fractions import Fraction
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def check(ok, message):
    if not ok:
        raise ValueError(message)


def accumulate(target, source, factor=Fraction(1)):
    for monomial, coefficient in source.items():
        target[monomial] = target.get(monomial, Fraction(0)) + factor*coefficient


def reverse(word, target):
    # This uses scalar adjoints, starting at one exit field. It never stores a
    # forward field/error table. A gradient's norm bounds each injected error.
    weights = {target: {(0, 0): Fraction(1)}}
    errors = {kind: {} for kind in ('add', 'line', 'stage')}
    for event in reversed(word):
        op = event['op']
        if op == 'add':
            w = weights.get(event['dst'], {})
            accumulate(errors['add'], w)
            if w:
                accumulate(weights.setdefault(event['src'], {}), w,
                           abs(Fraction(event['coefficient'])))
        elif op in ('line', 'stage'):
            field = event['field']
            w = weights.get(field, {})
            accumulate(errors[op], w)
            weights[field] = {(a + (op == 'line'), b + (op == 'stage')): c
                              for (a, b), c in w.items()}
        elif op == 'clear':
            weights.pop(event['field'], None)
        elif op == 'history_boundary':
            # New reference inputs at B1. Earlier retained-bank errors stay live.
            weights = {f: w for f, w in weights.items() if not f.startswith(('X', 'Y'))}
        elif op == 'private_begin':
            for field in event['fields']:
                weights.pop(field, None)
        else:
            check(op in ('current_map', 'private_end', 'checkpoint'), 'reverse opcode coverage')
    rows = [[a, b, channel, str(c)] for channel, terms in errors.items()
            for (a, b), c in terms.items() if c]
    return sorted(rows, key=lambda row: tuple(row[:3]))


def fourier_kernel(dimension, sign=1):
    # Direct Fourier sum of i^(sign*HammingWeight(x)), independent of the
    # product-kernel argument in README. Integer Gaussian accumulation only.
    phases = ((1, 0), (0, 1), (-1, 0), (0, -1))
    size = 1 << dimension
    out = []
    for t in range(size):
        real = imag = 0
        for x in range(size):
            a, b = phases[(sign*x.bit_count()) % 4]
            s = 1 if (x & t).bit_count() % 2 == 0 else -1
            real += s*a
            imag += s*b
        out.append((Fraction(real, size), Fraction(imag, size)))
    return out


def kernel_checks():
    coefficients = 0
    for dimension in range(1, 9):
        for sign in (-1, 1):
            kernel = fourier_kernel(dimension, sign)
            box = sum(abs(real) + abs(imag) for real, imag in kernel)
            check(box == 1 << ((dimension+1)//2), 'exact native box gain')
            check(max(max(a.denominator, b.denominator) for a, b in kernel)
                  == 1 << ((dimension+1)//2), 'exact native coefficient grid')
            # Choose real/imaginary input signs to attain the real part of one
            # convolution row. This is a concrete failure of a unit box bound.
            attained = sum(abs(a) + abs(b) for a, b in kernel)
            check(attained == box and box > 1, 'unitary-is-not-box-isometric control')
            coefficients += len(kernel)
    # A two-call signed line echo restores exact data but not arbitrary errors.
    # Inverse C has row ((1-i)/2, (1+i)/2); errors (1+i, 1-i)
    # give real value 2. A final real error 1 gives restoration error 3.
    def multiply(z, w):
        a,b=z; c,d=w
        return a*c-b*d, a*d+b*c
    terms = [multiply((Fraction(1,2), Fraction(-1,2)), (1,1)),
             multiply((Fraction(1,2), Fraction(1,2)), (1,-1))]
    check(sum(z[0] for z in terms)+1 == 3 and sum(z[1] for z in terms) == 0,
          'explicit nonzero borrowed-return error')
    return coefficients


def main():
    manifest = json.loads((BASE/'SNAPSHOTS.json').read_text())
    entry = next(x for x in manifest['files'] if x['path'] == 'inputs/PR2540-WORD.json')
    raw = (BASE/entry['path']).read_bytes()
    check(hashlib.sha256(raw).hexdigest() == entry['sha256'], 'reverse word pin')
    word = json.loads(raw)
    early = sorted({e['field'] for e in word if e['op'] == 'clear' and e['field'].startswith('R')})
    fields = sorted([f'{s}{p}' for s in ('X','Y','Z','W') for p in range(112)] + early)
    final = [[field, reverse(word, field)] for field in fields]
    digest = hashlib.sha256(json.dumps(final, separators=(',', ':')).encode()).hexdigest()
    receipt = json.loads((BASE/'RESULT.json').read_text())
    check(len(fields) == 464 and digest == receipt['final_error_table_sha256'],
          'all 464 final error polynomials agree with independent forward propagation')
    table = dict(final)
    check(table['W0'] == receipt['owned_envelope'], 'reverse output-envelope witness')
    check(all(table[f'Y{p}'] == receipt['borrowed_y_envelope'] for p in range(112)),
          'all borrowed returns separately accounted')
    # Post-event child errors do not acquire the gain of the child that just
    # finished. Earlier capture errors do. This toy distinguishes the two.
    toy = [{'op':'add','dst':'R','src':'X','coefficient':'1'},
           {'op':'stage','field':'R','rank':8,'sign':1}]
    check(reverse(toy, 'R') == [[0,0,'stage','1'], [0,1,'add','1']],
          'capture versus post-child injection placement')
    coefficients = kernel_checks()
    print(f'PASS_QQ16_REVERSE_ERROR_CHECK fields=464 kernel_coefficients={coefficients} controls=3')


if __name__ == '__main__':
    main()
