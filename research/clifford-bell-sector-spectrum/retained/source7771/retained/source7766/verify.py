#!/usr/bin/env python3
"""Check the binary geometry and literal Pauli conventions of the missing block."""
import argparse
from collections import Counter, deque
from hashlib import sha1, sha256
from itertools import combinations, product
import json
from math import prod
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parity(value):
    return value.bit_count() & 1


def omega(x, y, n):
    mask = (1 << n) - 1
    return parity((x & mask) & (y >> n)) ^ parity((y & mask) & (x >> n))


def quadratic(x, n, minus=True):
    value = parity((x & ((1 << n) - 1)) & (x >> n))
    return value ^ ((x & 1) ^ ((x >> n) & 1) if minus else 0)


def reduced(rows):
    basis = {}
    for row in rows:
        for pivot in sorted(basis, reverse=True):
            if row >> pivot & 1:
                row ^= basis[pivot]
        if row:
            pivot = row.bit_length() - 1
            for old in basis:
                if basis[old] >> pivot & 1:
                    basis[old] ^= row
            basis[pivot] = row
    return tuple(basis[p] for p in sorted(basis, reverse=True))


def rank(rows):
    return len(reduced(rows))


def span(basis):
    values = [0]
    for row in basis:
        values += [v ^ row for v in values]
    return values


def subspaces(width, dimension):
    """Generate each binary row-reduced basis once, with increasing pivots."""
    for pivots in combinations(range(width), dimension):
        free = [(i, j) for i, p in enumerate(pivots)
                for j in range(p + 1, width) if j not in pivots]
        for bits in range(1 << len(free)):
            basis = [1 << p for p in pivots]
            for bit, (i, j) in enumerate(free):
                if bits >> bit & 1:
                    basis[i] |= 1 << j
            yield tuple(basis)


def geometry():
    q = [quadratic(v, 4) for v in range(256)]
    require(Counter(q) == {0: 120, 1: 136}, 'minus zero count')
    histogram = Counter()
    chosen = Counter()
    for basis in subspaces(8, 4):
        vectors = span(basis)
        nonsingular = [v for v in vectors if q[v]]
        require(nonsingular, 'singular four-space')
        histogram[len(nonsingular)] += 1
        v = min(nonsingular)
        chosen[v] += 1
        equations = reduced([(b >> 4) | ((b & 15) << 4) for b in basis])
        pivots = {r.bit_length() - 1 for r in equations}
        perpendicular = []
        for free in range(8):
            if free not in pivots:
                u = 1 << free
                for row in equations:
                    if parity(row & u):
                        u ^= 1 << (row.bit_length() - 1)
                perpendicular.append(u)
        require(len(perpendicular) == 4 and all(not omega(u, v, 4) for u in perpendicular),
                'complement witness')
    expected_count = prod(256 - 2**i for i in range(4)) // prod(16 - 2**i for i in range(4))
    require(sum(histogram.values()) == expected_count == 200787, 'complete four-space count')
    # This second enumeration extends only singular spaces and deduplicates their bases.
    spaces = {()}
    singular_counts = [1]
    for dimension in range(1, 5):
        next_spaces = set()
        for basis in spaces:
            current = set(span(basis))
            for v in range(1, 256):
                if v not in current and not q[v] and all(not omega(v, b, 4) for b in basis):
                    next_spaces.add(reduced((*basis, v)))
        spaces = next_spaces
        singular_counts.append(len(spaces))
    require(singular_counts == [1, 119, 1071, 765, 0], 'independent singular-space census')
    # A plus-type space does have a singular four-space; it must fail the witness test.
    plus_lagrangian = [1 << i for i in range(4)]
    require(all(quadratic(v, 4, False) == 0 for v in span(plus_lagrangian)), 'plus control')
    # Five tuple vectors can also have a singular orthogonal complement in minus type.
    singular_three = (2, 4, 8)
    complement = [v for v in range(256) if all(not omega(v, b, 4) for b in singular_three)]
    require(rank(complement) == 5 and all(q[v] == 0 for v in span(singular_three)),
            'five-tuple control')
    return {'four_spaces': expected_count, 'nonsingular_histogram': {str(k): v for k, v in sorted(histogram.items())},
            'singular_space_counts': singular_counts, 'chosen_transvections': len(chosen)}


def apply(matrix, vector):
    value = 0
    while vector:
        bit = (vector & -vector).bit_length() - 1
        value ^= matrix[bit]
        vector &= vector - 1
    return value


def compose(left, right):
    return tuple(apply(left, col) for col in right)


def transvection(vector, n):
    return tuple((1 << i) ^ (vector if omega(1 << i, vector, n) else 0) for i in range(2*n))


def dickson(matrix):
    return rank([value ^ (1 << i) for i, value in enumerate(matrix)]) & 1


def sign_checks():
    generators = [transvection(v, 4) for v in range(1, 256) if quadratic(v, 4)]
    for matrix in generators:
        require(dickson(matrix) == 1, 'transvection sign')
        require(all(quadratic(apply(matrix, x), 4) == quadratic(x, 4) for x in range(256)),
                'transvection isometry')
    for a, b in product(generators, repeat=2):
        require(dickson(compose(a, b)) == 0, 'two-transvection sign')
    # Enumerate the complete minus group in dimension four as a separate character check.
    small_generators = [transvection(v, 2) for v in range(1, 16) if quadratic(v, 2)]
    identity = tuple(1 << i for i in range(4))
    group = {identity}
    queue = deque([identity])
    while queue:
        old = queue.popleft()
        for generator in small_generators:
            new = compose(generator, old)
            if new not in group:
                group.add(new)
                queue.append(new)
    require(len(group) == 120, 'small orthogonal group order')
    for a, b in product(group, repeat=2):
        require(dickson(compose(a, b)) == (dickson(a) ^ dickson(b)), 'small full sign law')
    moments = []
    for length in range(5):
        mass = sum((-1)**dickson(g) * (1 << (4 - rank([g[i] ^ (1 << i) for i in range(4)])))**length
                   for g in group)
        require(mass % 120 == 0 and mass >= 0, 'sign multiplicity')
        moments.append(mass // 120)
    require(moments[:3] == [0, 0, 0] and moments[3] > 0, 'tuple threshold control')
    return {'transvections': len(generators), 'isometry_points': 256 * len(generators),
            'transvection_pairs': len(generators)**2, 'small_group_order': len(group),
            'small_group_pairs': len(group)**2, 'small_sign_multiplicities': moments}


def pauli(label, x, n):
    a = label & ((1 << n) - 1)
    b = label >> n
    return x ^ a, ((a & b).bit_count() + 2 * parity(b & x)) % 4


def bell(label, n):
    return {(x, pauli(label, x, n)[0]): pauli(label, x, n)[1] for x in range(1 << n)}


UNITS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def gate_action(kind, i, j, x):
    if kind == 'S':
        return [(x, (x >> i) & 1)]
    if kind == 'CNOT':
        return [(x ^ ((1 << j) if x >> i & 1 else 0), 0)]
    # The Gaussian Hadamard is (1+i)/2 times the integer Hadamard.
    return [(x & ~(1 << i), 0), (x | (1 << i), 2 if x >> i & 1 else 0)]


def bell_checks():
    n = 4
    vectors = [bell(t, n) for t in range(256)]
    for label, vector in enumerate(vectors):
        for v in range(256):
            output = {}
            for (x, y), phase in vector.items():
                xx, px = pauli(v, x, n)
                yy, py = pauli(v, y, n)
                output[xx, yy] = (phase + px + py) % 4
            expected = (quadratic(v, n, False) ^ omega(v, label, n)) * 2
            require(output == {key: (phase + expected) % 4 for key, phase in vector.items()},
                    'literal Pauli character')
    norms = Counter()
    for a, b in product(range(256), repeat=2):
        real = imag = 0
        for key, phase in vectors[a].items():
            if key in vectors[b]:
                x, y = UNITS[(vectors[b][key] - phase) % 4]
                real += x
                imag += y
        require((real, imag) == ((16, 0) if a == b else (0, 0)), 'Bell basis orthogonality')
    for label, vector in enumerate(vectors):
        swap = {(y, x): p for (x, y), p in vector.items()}
        sign = 2 * quadratic(label, n, False)
        require(swap == {key: (p + sign) % 4 for key, p in vector.items()}, 'Bell exchange sign')
        norms[sign] += 1
    require(dict(norms) == {0: 136, 2: 120}, 'quadratic orbit dimensions')
    lookup = {}
    for t, vector in enumerate(vectors):
        first = vector[min(vector)]
        lookup[tuple((key, (p-first) % 4) for key, p in sorted(vector.items()))] = t
    generators = [('S', i, 0) for i in range(4)] + [('H', i, 0) for i in range(4)]
    generators += [('CNOT', i, j) for i in range(4) for j in range(4) if i != j]
    permutations = []
    character_controls = Counter()
    for kind, i, j in generators:
        permutation = []
        wedge_real = wedge_imag = 0
        for label, vector in enumerate(vectors):
            output = {}
            for (x, y), phase in vector.items():
                for (xx, px), (yy, py) in product(gate_action(kind, i, j, x), gate_action(kind, i, j, y)):
                    # Two Hadamard prefactors multiply to i/2.
                    value = UNITS[(phase + px + py + (kind == 'H')) % 4]
                    old = output.get((xx, yy), (0, 0))
                    output[xx, yy] = (old[0] + value[0], old[1] + value[1])
            output = {key: value for key, value in output.items() if value != (0, 0)}
            phases = {}
            divisor = 2 if kind == 'H' else 1
            for key, (real, imag) in output.items():
                require(real % divisor == imag % divisor == 0, 'Hadamard integral phase')
                value = (real // divisor, imag // divisor)
                require(value in UNITS, 'Bell monomial coefficient')
                phases[key] = UNITS.index(value)
            first = phases[min(phases)]
            key = tuple((position, (p-first) % 4) for position, p in sorted(phases.items()))
            require(key in lookup, 'Bell generator image')
            target = lookup[key]
            require(quadratic(target, n, False) == quadratic(label, n, False), 'Arf preservation')
            permutation.append(target)
            if target == label and quadratic(label, n, False):
                real, imag = UNITS[(first - vector[min(vector)]) % 4]
                wedge_real += real
                wedge_imag += imag
        require(len(set(permutation)) == 256, 'Bell permutation')
        permutations.append(permutation)
        linear = tuple(permutation[1 << i] ^ permutation[0] for i in range(8))
        require(all(permutation[t] == (apply(linear, t) ^ permutation[0]) for t in range(256)),
                'affine quadratic action')
        maps = [dict(gate_action(kind, i, j, x)) for x in range(16)]
        minor_real = minor_imag = 0
        for x, y in combinations(range(16), 2):
            for first_input, second_input, sign in [(x, y, 1), (y, x, -1)]:
                if x in maps[first_input] and y in maps[second_input]:
                    phase = maps[first_input][x] + maps[second_input][y] + (kind == 'H')
                    real, imag = UNITS[phase % 4]
                    minor_real += sign * real
                    minor_imag += sign * imag
        divisor = 2 if kind == 'H' else 1
        require((minor_real, minor_imag) == (divisor*wedge_real, divisor*wedge_imag),
                'literal exterior-square character')
        sign = (-1)**dickson(linear)
        character_controls[(kind, wedge_real, wedge_imag, sign*wedge_real, sign*wedge_imag)] += 1
    unseen = set(range(256))
    orbits = []
    while unseen:
        start = min(unseen)
        found = {start}
        queue = deque([start])
        while queue:
            t = queue.popleft()
            for permutation in permutations:
                new = permutation[t]
                if new not in found:
                    found.add(new)
                    queue.append(new)
        unseen -= found
        orbits.append(len(found))
    require(sorted(orbits) == [120, 136], 'actual gate quadratic orbits')
    require(dict(character_controls) == {('S', 0, 64, 0, -64): 4,
                                         ('H', 0, -8, 0, 8): 4,
                                         ('CNOT', 24, 0, 24, 0): 12}, 'explicit character controls')
    return {'character_controls': [[*key, value] for key, value in sorted(character_controls.items())],
            'pauli_character_pairs': 65536, 'bell_inner_products': 65536,
            'literal_clifford_generators': 20, 'literal_bell_images': 5120, 'orbits': sorted(orbits)}


def signed_quotient_check():
    data = json.loads((ROOT / 'retained/source7747/PROJECTION.json').read_text())
    order = sum(data['element_counts'])
    output = []
    for index, orbit_size in [(4, 120), (5, 136)]:
        row = data['rows'][index]
        require(row[0] + 1 == orbit_size, 'quadratic permutation degree')
        sums = [0] + row[1:] + [row[0]]
        sums[0] = -sum(sums)
        fixed_masses = [count + value for count, value in
                        zip(data['element_counts'], sums, strict=True)]
        terms = [(-1)**d * value * 2**(4*d) for d, value in enumerate(fixed_masses)]
        numerator = sum(terms)
        require(numerator % order == 0, 'signed quotient integrality')
        unsigned = sum(value * 2**(4*d) for d, value in enumerate(fixed_masses))
        require(unsigned % order == 0 and unsigned > 0, 'omitted sign control')
        output.append(dict(orbit_size=orbit_size, signed_terms=terms,
                           multiplicity=numerator//order, unsigned_multiplicity=unsigned//order))
    require([r['multiplicity'] for r in output] == [0, 1], 'two exact stabilizer multiplicities')
    return output


def gaussian_binomial(n, r):
    return prod(2**n - 2**i for i in range(r)) // prod(2**r - 2**i for i in range(r))


def tuple_orbits(length):
    total = 0
    for r in range(min(length, 8) + 1):
        for radical in range(r % 2, r + 1, 2):
            if r + radical > 8:
                continue
            even = r - radical
            gl = prod(2**even - 2**i for i in range(even))
            half = even // 2
            symplectic = 2**(half*half) * prod(2**(2*i)-1 for i in range(1, half+1))
            total += gaussian_binomial(length, r) * gaussian_binomial(r, radical) * (gl//symplectic)
    return total


def odd_multiplicities(data, power):
    order = sum(data['element_counts'])
    values = []
    for index, row in enumerate(data['rows']):
        degree = row[0]
        numerator = degree*(2**(8*power)-1)
        numerator += sum(value*((-1)**d * 2**(power*d)-1) for d, value in enumerate(row[1:], 1))
        quotient, remainder = divmod(numerator, order)
        require(remainder == 0 and quotient >= 0, 'odd multiplicity integrality')
        values.append(quotient + (index == 0))
        sums = [0] + row[1:] + [degree]
        sums[0] = (order if index == 0 else 0) - sum(sums)
        direct = sum(value*(-1)**d * 2**(power*d) for d, value in enumerate(sums))
        require(direct == order*values[-1], 'direct bin character sum')
    require(sum(m*r[0] for m, r in zip(values, data['rows'], strict=True)) == 2**(8*power),
            'odd multiplicity dimension')
    norm = tuple_orbits(2*power)
    require(sum(m*m for m in values) == norm, 'independent long-tuple norm')
    require(sum(count*2**(2*power*d) for d, count in enumerate(data['element_counts'])) == order*norm,
            'long-tuple histogram moment')
    return values, norm


def threshold_check():
    data = json.loads((ROOT/'retained/source7747/PROJECTION.json').read_text())
    order = sum(data['element_counts'])
    m11, norm11 = odd_multiplicities(data, 5)
    m13, norm13 = odd_multiplicities(data, 6)
    missing = [i+1 for i, m in enumerate(m11) if m == 0]
    require(missing == [9, 22] and [data['rows'][i-1][0] for i in missing] == [595, 3213],
            'width eleven support')
    require(all(m > 0 for m in m13), 'width thirteen support')
    loss = sum(data['rows'][i-1][0]**2 for i in missing)
    require(loss == 10677394, 'inflated block dimensions')
    bad = json.loads(json.dumps(data))
    bad['rows'][8][1] += 1
    try:
        odd_multiplicities(bad, 5)
    except ValueError as error:
        require(str(error) == 'odd multiplicity integrality', 'wrong character fault')
    else:
        raise ValueError('changed character sum passed')
    return dict(width11_multiplicities=m11, width13_multiplicities=m13,
                width11_missing_rows=missing, width11_missing_quotient_degrees=[595, 3213],
                width11_nullity=256*loss, width11_rank=256*order-256*loss,
                width12_nullity_lower=loss, width12_rank_upper=256*order-loss,
                width13_rank=256*order, threshold=13,
                quotient_norms=[norm11, norm13], minimum_width13_multiplicity=min(m13))


def verify(args):
    pins = json.loads((ROOT / 'SOURCE-PINS.json').read_text())['sources']
    for pin in pins:
        raw = (ROOT / pin['retained']).read_bytes()
        require(sha256(raw).hexdigest() == pin['sha256'] and
                sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'], 'source pin')
    result = {'geometry': geometry(), 'sign': sign_checks(), 'literal_bell': bell_checks(),
              'quotient_check': signed_quotient_check(), 'threshold': threshold_check()}
    order = 4**4 * 2**16 * prod(2**(2*i)-1 for i in range(1, 5))
    missing = 2**3 * (2**4-1)
    require((order, missing, missing**2) == (12128668876800, 120, 14400), 'four-qubit block dimensions')
    result['four_qubit'] = dict(projective_order=order, missing_block_degree=missing,
                               nullity_lower=missing**2, rank_upper=order-missing**2, threshold_lower=11)
    if args.collect:
        print(json.dumps(result, indent=2))
        return
    require(result == json.loads((ROOT / 'RESULT.json').read_text()), 'result certificate')
    mode = ['-O'] if sys.flags.optimize else []
    old = subprocess.run([sys.executable, '-W', 'error', *mode, '-B',
                          str(ROOT/'retained/source7747/verify.py'),
                          *(['--ctbllib-archive', str(args.ctbllib_archive)] if args.ctbllib_archive else [])], capture_output=True, text=True, timeout=30)
    require(old.returncode == 0 and 'PASS_CLIFFORD_FOUR_QUBIT_WIDTH_NINE' in old.stdout, 'source replay')
    print('PASS_CLIFFORD_FOUR_QUBIT_THRESHOLD')
    print('Sharp threshold T(4)=13; width eleven nullity 2733412864; width twelve nullity >= 10677394')
    print('Width thirteen: all 81 quotient rows occur; full Gram rank 12128668876800')
    print('Four qubits at width ten: absent degree 120, nullity >= 14400, T(4) >= 11')
    print('200787 four-spaces; independent singular-space census 1,119,1071,765,0')
    print('65536 Pauli characters; 65536 Bell inner products; 5120 literal Clifford Bell images')
    print('Independent signed quotient sums: minus multiplicity 0, plus multiplicity 1')
    print('Written extension: T(n) >= 2n+3 for every positive n divisible by four')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collect', action='store_true', help='Print the exact certificate')
    parser.add_argument('--ctbllib-archive', type=Path, help='Rebuild the retained projection from CTblLib 1.3.11')
    verify(parser.parse_args())
