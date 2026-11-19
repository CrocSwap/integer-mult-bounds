"""Independent projective Clifford enumeration and exact width-13 spectral controls."""
from collections import Counter
from fractions import Fraction
from itertools import combinations, combinations_with_replacement
from math import isqrt

from two_site_spectrum import eigenpolynomials, normal_blocks, pair_types


def require(condition, message):
    if not condition:
        raise ValueError(message)


def projective(matrix):
    for unit in (1, -1, 1j, -1j):
        first = unit * next(x for x in matrix if x)
        if first.real > 0 and first.imag >= 0:
            return tuple(unit * x for x in matrix)
    raise ValueError("failed to fix Gaussian phase")


def all_two_qubit_gates():
    # Entries of 2V belong to Z[i] on both qubits. Dyadic real and imaginary
    # intermediates are exactly representable when computing these gate updates.
    identity = tuple(2 * int(i == k) for i in range(4) for k in range(4))
    pending, seen = [identity], {identity}
    for gate in pending:
        yield gate
        for bit in (1, 2):
            phase = tuple((1j if i & bit else 1) * gate[4*i+k]
                          for i in range(4) for k in range(4))
            h = tuple((1+1j)/2 * (gate[4*(i & ~bit)+k] +
                                 (-1 if i & bit else 1) * gate[4*(i | bit)+k])
                      for i in range(4) for k in range(4))
            for successor in (h, phase):
                new = projective(successor)
                if new not in seen:
                    pending.append(new)
                    seen.add(new)
        cnot = projective(tuple(gate[4*(i ^ (2 if i & 1 else 0))+k]
                                for i in range(4) for k in range(4)))
        if cnot not in seen:
            pending.append(cnot)
            seen.add(cnot)


def direct_two_qubit():
    # Evaluate direct matrix monomials; check every type representative, both
    # matchings, and selected blocks between different diagonal characters.
    width = 13
    types = pair_types(2)
    blocks = [(r, c) for r in types for c in types]
    expected = normal_blocks(2, width)
    total = {key: [0] * len(value) for key, value in expected.items()}
    offblock = [0j] * (len(blocks) - 1)
    group_size = 0
    for gate in all_two_qubit_gates():
        group_size += 1
        origin = gate[0]
        if not origin:
            continue
        weight = int((origin * origin.conjugate()).real)**(width - 2)
        leading = []
        for key in blocks:
            (i, h), _ = types[key[0]]
            (k, l), _ = types[key[1]]
            x = gate[4*i+k] * gate[4*h+l]
            y = gate[4*i+l] * gate[4*h+k]
            leading.append(x)
            scale = weight * (1 if (i,k) == (h,l) else 2)
            block = total[key]
            block[0] += scale * x * x.conjugate()
            if len(block) == 3:
                block[1] += scale * y * y.conjugate()
                block[2] += scale * x.conjugate() * y
        for s, (x, y) in enumerate(zip(leading, leading[1:])):
            offblock[s] += weight * x.conjugate() * y
    require(group_size == 11520 and not any(offblock), "group size or character leakage")
    for key, entries in total.items():
        require(all(z.imag == 0 and z.real.is_integer() for z in map(complex, entries)),
                "two-qubit literal entries not real integral")
        actual = tuple(Fraction(int(z.real), 4**(2*width)) for z in entries)
        require(actual == expected[key], f"two-qubit block disagrees at {key}")


def check_character_separation():
    signatures = set()
    for x, y in combinations_with_replacement(range(16), 2):
        signature = tuple((x >> i & 1) + (y >> i & 1) for i in range(4)) + tuple(
            (((x >> i) & (x >> j)) ^ ((y >> i) & (y >> j))) & 1
            for i in range(4) for j in range(i))
        signatures.add(signature)
    require(len(signatures) == 136, "diagonal Clifford characters collide")


def direct_four_qubit_interference():
    """Measure signed rectangle interference in literal partial-Hadamard matrices."""
    # Primitive polynomials in degrees 1 through 4. Multiplication by x
    # permutes all nonzero low-bit vectors transitively. Each matrix below
    # is a linear output permutation of H^{tensor j} times diagonal gates.
    for j, modulus in enumerate((0b11, 0b111, 0b1011, 0b10011), start=1):
        q = 1 << j
        row_map = list(range(q))
        both_sums = Counter()
        row_pairs = list(combinations(range(16), 2))
        phases = (1, 1j, -1, -1j)
        phases_seen = set()
        for _ in range(q - 1):
            phases_seen.add(row_map[1])
            # sqrt(q)V: Gaussian unit entries; use row/column chirps to
            # ensure that the rectangle sum tests cancellation of phases.
            gate = [[phases[((i & 3).bit_count() + (k & 7).bit_count() +
                             2 * (row_map[i % q] & k).bit_count()) % 4]
                     if i // q == k // q else 0 for k in range(16)] for i in range(16)]
            for i, h in row_pairs:
                for k, l in row_pairs:
                    x, y = gate[i][k] * gate[h][l], gate[i][l] * gate[h][k]
                    if x and y:
                        both_sums[i, h, k, l] += x * y.conjugate()
            row_map = [((v << 1) ^ (modulus if v & (q >> 1) else 0)) for v in row_map]
        expected_count = (16 // q) * (q * (q-1) // 2)**2
        require(len(phases_seen) == q-1 and len(both_sums) == expected_count,
                "incomplete four-qubit rectangle control")
        require(set(both_sums.values()) == {-1}, "four-qubit rectangle signs")


def check_four_qubit():
    blocks = normal_blocks()
    scale = 1 << 70
    lower, upper = Fraction(83059830, scale), Fraction(87222165730875, scale)
    factors = eigenpolynomials(4, blocks)
    require(len(factors) == 12 and sum((len(p)-1)*m for p,m in factors.items()) == 32896,
            "wrong nonzero characteristic factors")
    multiplicity = Counter()
    for p, count in factors.items():
        if len(p) == 2:
            root = -p[1]
            require(lower <= root <= upper, "linear root outside endpoints")
            multiplicity[root] = count
        else:
            _, b, c = p
            discriminant = b*b - 4*c
            require(discriminant > 0 and count == 225, "quadratic multiplicity")
            require(isqrt(discriminant.numerator)**2 != discriminant.numerator or
                    isqrt(discriminant.denominator)**2 != discriminant.denominator,
                    "quadratic is reducible")
            require(lower < -b/2 < upper and
                    lower**2 + b*lower + c > 0 and upper**2 + b*upper + c > 0,
                    "quadratic roots outside endpoints")
    require(multiplicity[lower] == 210 and multiplicity[upper] == 1, "endpoint multiplicity")
    require(upper/lower == Fraction(2100225, 2), "squared condition number")
    # Full-support subensemble alone has no additional null directions.
    flat = eigenpolynomials(4, normal_blocks(only_shell=4))
    require({-p[1]*scale: m for p, m in flat.items()} ==
            {315: 256, 630: 3840, 588: 14400, 672: 14400}, "flat-frame spectrum")


if __name__ == '__main__':
    check_character_separation()
    direct_two_qubit()
    check_four_qubit()
    print('PASS two-site raw spectrum, flat subframe, kernel and all 11,520 two-qubit controls')
