#!/usr/bin/env python3
"""Exact deterministic rounding at a source-pinned P104 native collector.

Apache-2.0. Prepared for Arham Tahir with substantial OpenAI Codex assistance.
No predecessor executable, compiler, numpy, or floating arithmetic is used.
Vectors contain Gaussian integer numerators with one power-of-two denominator.
"""
import argparse
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WIDTH = 512
ZERO = (0, 0)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rotate(z, phase):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def multiply(a, b):
    return (a[0] * b[0] - a[1] * b[1],
            a[0] * b[1] + a[1] * b[0])


def normalize(vector, exponent):
    while exponent and all(a % 2 == b % 2 == 0 for a, b in vector):
        vector = [(a // 2, b // 2) for a, b in vector]
        exponent -= 1
    return vector, exponent


@lru_cache(maxsize=4)
def monomial_plan(encoded):
    m = json.loads(encoded)
    rows, linear, quadratic = (m[k] for k in
                               ('matrix_rows', 'linear_Z4', 'quadratic_rows'))
    need(len(rows) == len(linear) == len(quadratic) == 9, 'monomial dimension')
    plan = []
    for x in range(WIDTH):
        bits = [j for j in range(9) if x & (1 << j)]
        phase = m['phase'] + sum(linear[j] for j in bits)
        phase += 2 * sum((quadratic[j] >> k) & 1
                         for j in bits for k in bits if j < k)
        target = m['offset'] ^ sum(((row & x).bit_count() % 2) << j
                                   for j, row in enumerate(rows))
        plan.append((target, phase % 4))
    need(sorted(t for t, _ in plan) == list(range(WIDTH)), 'monomial bijection')
    return tuple(plan)


def monomial(vector, record):
    out = [ZERO] * WIDTH
    for z, (target, phase) in zip(vector, monomial_plan(json.dumps(record, sort_keys=True))):
        out[target] = rotate(z, phase)
    return out


def native(vector, exponent, recipe):
    """Butterfly implementation; rounding happens after the complete child."""
    vector = monomial(vector, recipe['right'])
    for bit in range(recipe['rank']):
        step = 1 << bit
        out = [ZERO] * WIDTH
        for x in range(WIDTH):
            if x & step:
                continue
            a, b = vector[x], vector[x | step]
            out[x] = (a[0] - a[1] + b[0] + b[1],
                      a[0] + a[1] + b[1] - b[0])
            out[x | step] = (b[0] - b[1] + a[0] + a[1],
                             b[0] + b[1] + a[1] - a[0])
        vector = out
        exponent += 1
    return normalize(monomial(vector, recipe['left']), exponent)


def direct_column(address, recipe):
    """Separate tensor-product formula, without butterfly updates."""
    r = recipe['rank']
    source, phase = monomial_plan(json.dumps(recipe['right'], sort_keys=True))[address]
    left = monomial_plan(json.dumps(recipe['left'], sort_keys=True))
    result = [ZERO] * WIDTH
    for low in range(1 << r):
        value = rotate((1, 0), phase)
        for j in range(r):
            different = ((low ^ source) >> j) & 1
            value = multiply(value, (1, -1 if different else 1))
        target, power = left[(source & ~((1 << r) - 1)) | low]
        result[target] = rotate(value, power)
    return normalize(result, r)


def nearest_even(numerator, denominator):
    quotient, remainder = divmod(numerator, denominator)
    return quotient + int(2 * remainder > denominator
                          or (2 * remainder == denominator and quotient % 2))


def quantize(vector, exponent, bits):
    """Componentwise nearest-even to the real/imaginary grid 2**(-bits)."""
    need(type(bits) is int and bits >= 0, 'grid bits')
    if exponent <= bits:
        return vector, exponent
    denominator = 1 << (exponent - bits)
    return normalize([(nearest_even(a, denominator), nearest_even(b, denominator))
                      for a, b in vector], bits)


def basis(address, numerator=1, exponent=0):
    out = [ZERO] * WIDTH
    out[address] = (numerator, 0)
    return out, exponent


def subtract(a, b):
    va, ea = a
    vb, eb = b
    e = max(ea, eb)
    return normalize([(x[0] * (1 << (e - ea)) - y[0] * (1 << (e - eb)),
                       x[1] * (1 << (e - ea)) - y[1] * (1 << (e - eb)))
                      for x, y in zip(va, vb)], e)


def authenticate():
    pins = json.loads((HERE / 'PREDECESSORS.json').read_text())['files']
    for pin in pins:
        raw = (HERE / pin['local']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256 ' + pin['local'])
        need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
             == pin['git_blob'], 'source Git blob ' + pin['local'])


def load_inputs():
    authenticate()
    word = json.loads((HERE / 'inputs/WORD.json').read_text())
    data = json.loads(gzip.decompress((HERE / 'inputs/NATIVE.json.gz').read_bytes()))
    need(len(word['program']) == 5398, 'pinned event count')
    need(all(e[0] in ('transport', 'add', 'sign')
             and (e[0] != 'add' or e[1] != e[2])
             for e in word['program'][:2025]), 'invertible prefix before collector')
    local = word['program'][2025:2040]
    need(local[0] == ['zero', 'C', local[0][2]] and len(local[0][2]) == 8,
         'fresh collector frame')
    sources = ['D31', 'D30', 'D29', 'D28', 'D27']
    need(local[1:6] == [['add', 'C', s, 1, local[0][2]] for s in sources], 'five gathers')
    need(local[7] == ['add', 'Q7', 'C', '1', local[6][3]], 'one-way query')
    need(local[9:14] == [['add', 'C', s, '-1', local[0][2]] for s in reversed(sources)],
         'unchanged source cleanup')
    need(local[14] == ['erase', 'C', local[0][2]], 'erase boundary')
    recipes = []
    for index in (2031, 2033):
        event = word['program'][index]
        matches = [t for t in data['transports'] if index in t['events']]
        need(len(matches) == 1, 'unique native occurrence')
        t = matches[0]
        need(event == ['transport', 'C', t['old'], t['new'], 7]
             and t['recipe']['rank'] == 7, 'rank-seven occurrence binding')
        recipes.append(t['recipe'])
    need(word['program'][2031][2:4] == list(reversed(word['program'][2033][2:4])),
         'inverse physical frames')
    return local, recipes


def collector(local, recipes, dirty, bits=None, strict_erase=False):
    """Execute the fifteen literal physical instructions on complete arrays."""
    zero = ([ZERO] * WIDTH, 0)
    state = {s: zero for s in ('D31', 'D30', 'D29', 'D28', 'D27', 'Q7')}
    state['D31'] = dirty
    returns = []
    transport = 0
    for event in local:
        op, reg = event[:2]
        if op == 'zero':
            need(reg not in state, 'private fresh allocation')
            state[reg] = zero
        elif op == 'transport':
            exact = native(*state[reg], recipes[transport])
            state[reg] = exact if bits is None else quantize(*exact, bits)
            returns.append(subtract(state[reg], exact))
            transport += 1
        elif op == 'add':
            # Every coefficient in this pinned local word is +1 or -1.
            coefficient = int(event[3])
            need(coefficient in (-1, 1), 'local unit ADD')
            src, exponent = state[event[2]]
            negative = ([(-coefficient*a, -coefficient*b) for a, b in src], exponent)
            state[reg] = subtract(state[reg], negative)
        elif op == 'erase':
            residue = state[reg]
            need(not strict_erase or not any(z != ZERO for z in residue[0]),
                 'strict zero erase rejects deterministic residual')
            del state[reg]
        else:
            raise ValueError('unsupported collector instruction')
    need(transport == 2 and state['D31'] == dirty
         and all(state[s] == zero for s in ('D30', 'D29', 'D28', 'D27')),
         'all dirty sources unchanged')
    return residue, state['Q7'], returns


def verify(inputs):
    local, recipes = inputs
    outbound, return_child = recipes
    for address in range(WIDTH):
        original = basis(address)
        image = native(*original, outbound)
        need(image == direct_column(address, outbound), 'tensor/butterfly column')
        need(native(*image, return_child) == original, 'exact native round trip')
        need(image[1] == 4 and sum(z != ZERO for z in image[0]) == 128
             and all(a in (-1, 0, 1) and b in (-1, 0, 1) for a, b in image[0])
             and sum(a*a + b*b for a, b in image[0]) == 256,
             'flat Gaussian column and unit norm')
    records = []
    unit_image = native(*basis(0), outbound)
    for bits in (4, 5, 8, 17, 64, 256):
        # x = (1 + h) delta_0 is representable on the h=2^-bits grid.
        dirty = basis(0, (1 << bits) + 1, bits)
        exact = native(*dirty, outbound)
        rounded = quantize(*exact, bits)
        need(rounded == unit_image, 'deterministic outbound rounding')
        returned = native(*rounded, return_child)
        need(quantize(*returned, bits) == returned == basis(0), 'exact rounded return')
        residue = subtract(returned, dirty)
        need(residue == basis(0, -1, bits), 'nonzero private erasure residual')
        error = subtract(rounded, exact)
        error_numerator_norm2 = sum(a*a+b*b for a, b in error[0])
        need(error_numerator_norm2 * (1 << (2 * bits)) == 1 << (2 * error[1]),
             'completed-child defect norm is h')
        # h <= u*(1+h) with u=h, checked without roots or floating point.
        need(1 << (2 * bits) <= ((1 << bits) + 1)**2, 'state-relative defect contract')
        need(native(*exact, return_child) == dirty, 'exact arithmetic zero control')
        ideal_residual, ideal_query, _ = collector(local, recipes, dirty, strict_erase=True)
        actual_residual, actual_query, actual_defects = collector(local, recipes, dirty, bits)
        need(ideal_residual == ([ZERO] * WIDTH, 0) and ideal_query == exact,
             'literal exact collector')
        need(actual_residual == residue and actual_query == rounded
             and actual_defects == [error, ([ZERO] * WIDTH, 0)],
             'literal rounded collector and both local defects')
        # Four extra fractional output bits make this particular input exact.
        fine = quantize(*exact, bits + 4)
        need(fine == exact and native(*fine, return_child) == dirty, 'finer-grid positive control')
        records.append(dict(bits=bits, residual=f'-1/2^{bits}',
                            defect_norm=f'1/2^{bits}', return_defect='0'))
    return dict(status='PASS_P104_ROUNDED_COLLECTOR',
                source_pr=2586, collector_events=[2025, 2039],
                native_events=[2031, 2033], exact_columns=512,
                column_support=128, gaussian_column_denominator=16,
                symbolic_family='b >= 4, h=2^-b, D31=(1+h)delta_0; other D sources zero',
                local_relative_tolerance='u=h', collector_residual='-h delta_0',
                tested_grids=records,
                scope='Local deterministic collector, exact ADD/allocation and output-grid quantization; not a full rounded caller or universal cleanup impossibility.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = verify(load_inputs())
    expected = json.loads((HERE / 'RESULT.json').read_text())
    need(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
         'complete typed receipt equality')
    if args.out:
        with args.out.open('x') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
    print('PASS_P104_ROUNDED_COLLECTOR columns=512 b>=4 residual=-2^-b delta_0')


if __name__ == '__main__':
    main()
