"""Exact finite corroboration of the two-image inverse input lattice."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from math import lcm
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def base_map(x, letter):
    require(0 <= x < 8 and letter in ("U", "V", "R"), "base address")
    if letter == "U":
        return x ^ ((x & 1) << 2)
    if letter == "V":
        return (x & 4) | ((x & 1) << 1) | ((x & 2) >> 1)
    v = (x & 4) | ((x & 1) << 1) | ((x & 2) >> 1)
    return v ^ ((v & 1) << 2)


def address(x, width, letter):
    require(1 <= width <= 5 and 0 <= x < 8**width, "tensor address")
    return sum(base_map((x >> (3 * j)) & 7, letter) << (3 * j)
               for j in range(width))


def cycles(width):
    size = 8**width
    seen = set()
    result = []
    for x in range(size):
        if x in seen:
            continue
        orbit = []
        y = x
        for _ in range(4):
            orbit.append(y)
            seen.add(y)
            y = address(y, width, "R")
            if y == x:
                break
        require(y == x and len(orbit) in (1, 2, 4), "cycle closure")
        result.append(orbit)
    require(len(seen) == size, "cycle coverage")
    return result


def predicted(width):
    require(1 <= width <= 5, "verification width")
    return {1: 2**width, 2: (4**width - 2**width) // 2,
            4: (8**width - 4**width) // 4}


def cycle_checks():
    rows = []
    for width in range(1, 6):
        counts = dict(Counter(map(len, cycles(width))))
        require(counts == predicted(width), "cycle formula")
        rows.append({"width": width, "cycles": counts})
    return rows


def residue_checks():
    rows = []
    for length in (1, 2, 4):
        divisor = abs(1 - (-2)**length)
        weights = [(-2)**(length - j) for j in range(length)]
        safe = 0
        for values in product(range(15), repeat=length):
            numerators = [sum(c * values[(j - k) % length]
                              for k, c in enumerate((-1, 2, -4, 8)))
                          for j in range(length)]
            exact = all(n % 15 == 0 for n in numerators)
            congruence = sum(w * v for w, v in zip(weights, values)) % divisor == 0
            require(exact == congruence, "cycle membership")
            safe += exact
        require(safe == 15**length // divisor, "cycle index")
        rows.append({"length": length, "residues": 15**length, "safe": safe})
    return rows


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def mul(x, y):
    return (x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def permute(vector, width, letter):
    result = [(0, 0)] * len(vector)
    for x, value in enumerate(vector):
        result[address(x, width, letter)] = value
    return result


def phase(vector, inverse=False):
    units = ((1, 0), (0, 1), (-1, 0), (0, -1))
    sign = -1 if inverse else 1
    return [mul(units[(sign * x.bit_count()) % 4], v)
            for x, v in enumerate(vector)]


def kernel(vector, width, inverse=False):
    require(1 <= width <= 2 and len(vector) == 8**width, "literal width")
    sign = -1 if inverse else 1
    a = (Fraction(1, 2), Fraction(sign, 2))
    b = (Fraction(1, 2), Fraction(-sign, 2))
    result = vector
    for digit in range(width):
        bit = 1 << (3 * digit)
        result = [add(mul(a, v), mul(b, result[x ^ bit]))
                  for x, v in enumerate(result)]
    return result


def forward(vector, width, repaired):
    middle = kernel(vector, width)
    if repaired:
        middle = phase(middle)
    u = permute(middle, width, "U")
    v = permute(middle, width, "V")
    result = [add(a, (2 * b[0], 2 * b[1])) for a, b in zip(u, v)]
    if repaired:
        result = phase(result)
    return kernel(result, width)


def left_inverse(vector, width, repaired):
    result = kernel(vector, width, inverse=True)
    if repaired:
        result = phase(result, inverse=True)
    return permute(result, width, "U")


def dyadic(value):
    denominator = Fraction(value).denominator
    return denominator & (denominator - 1) == 0


def membership(vector, width, repaired):
    transformed = left_inverse(vector, width, repaired)
    for orbit in cycles(width):
        length = len(orbit)
        divisor = abs(1 - (-2)**length)
        for component in (0, 1):
            value = sum((-2)**(length - j) * transformed[x][component]
                        for j, x in enumerate(orbit)) / divisor
            if not dyadic(value):
                return False
    return True


def real_matrix(width, repaired):
    size = 8**width
    result = [[Fraction(0) for _ in range(2 * size)] for _ in range(2 * size)]
    for column in range(2 * size):
        vector = [(0, 0)] * size
        vector[column % size] = (1, 0) if column < size else (0, 1)
        output = forward(vector, width, repaired)
        for row, value in enumerate(output):
            result[row][column] = value[0]
            result[size + row][column] = value[1]
    return result


def rank_mod(matrix, prime):
    rows = [[int(v.numerator % prime) * pow(v.denominator, -1, prime) % prime
             for v in row] for row in matrix]
    rank = 0
    for column in range(len(rows[0])):
        pivot = next((j for j in range(rank, len(rows)) if rows[j][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][column], -1, prime)
        rows[rank] = [x * inv % prime for x in rows[rank]]
        for j in range(rank + 1, len(rows)):
            coefficient = rows[j][column]
            if coefficient:
                rows[j] = [(x - coefficient * y) % prime
                           for x, y in zip(rows[j], rows[rank])]
        rank += 1
    return rank


def rational_inverse(matrix):
    size = len(matrix)
    rows = [row[:] + [Fraction(j == k) for k in range(size)]
            for j, row in enumerate(matrix)]
    for column in range(size):
        pivot = next(j for j in range(column, size) if rows[j][column])
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [x / scale for x in rows[column]]
        for j in range(size):
            if j != column:
                scale = rows[j][column]
                rows[j] = [x - scale * y for x, y in zip(rows[j], rows[column])]
    return [row[size:] for row in rows]


def literal_checks():
    rows = []
    for width, repaired in product((1, 2), (False, True)):
        matrix = real_matrix(width, repaired)
        counts = predicted(width)
        n3 = sum(counts.values())
        n5 = counts[4]
        ranks = [rank_mod(matrix, p) for p in (3, 5)]
        require(ranks == [2 * (8**width - n3), 2 * (8**width - n5)],
                "literal completed-map local ranks")
        rows.append({"width": width, "repaired": repaired, "ranks_mod_3_5": ranks})
        if width == 1:
            inverse = rational_inverse(matrix)
            denominator = lcm(*(x.denominator for row in inverse for x in row))
            odd = denominator
            for _ in range(denominator.bit_length()):
                if odd % 2:
                    break
                odd //= 2
            require(odd == 15, "sharp odd denominator")
            for multiplier in (3, 5):
                require(any(not dyadic(multiplier * x) for row in inverse for x in row),
                        "single-prime denominator replacement rejected")
            for trial in range(64):
                flat = [Fraction(((trial >> (j % 6)) & 1) * (j + 1) - j % 3)
                        for j in range(16)]
                vector = list(zip(flat[:8], flat[8:]))
                output = [sum(x * y for x, y in zip(row, flat)) for row in inverse]
                require(membership(vector, 1, repaired) == all(map(dyadic, output)),
                        "congruence versus independently solved inverse")
            for column in range(16):
                vector = [(matrix[j][column], matrix[8 + j][column]) for j in range(8)]
                require(membership(vector, 1, repaired), "complete forward image fixture")
    return rows


def controls():
    weights = (1, 7, 4, 13)
    require(sum(w * v for w, v in zip(weights, (8, 1, 0, 0))) % 15 == 0,
            "weighted relation positive")
    require(sum((8, 1, 0, 0)) % 15 != 0, "unweighted relation rejected")
    require(not dyadic(Fraction(1, 3)) and not dyadic(Fraction(1, 5)),
            "both odd primes required")
    require(dyadic(Fraction(1, 32)), "dyadic denominator allowed")
    return 3


def main():
    result = {"cycles": cycle_checks(), "residues": residue_checks(),
              "literal": literal_checks(), "controls": controls()}
    package = Path(__file__).resolve().parent
    result["package_sha256"] = {p.name: sha256(p.read_bytes()).hexdigest()
                                for p in sorted(package.iterdir()) if p.is_file()}
    print(json.dumps(result, sort_keys=True))
    print("PASS_TWO_IMAGE_INVERSE_LATTICE widths=1..5 cycle_residues=50865 "
          "literal_maps=4 inverse_membership_probes=128 odd_denominator=15 no_new_kappa")


if __name__ == "__main__":
    main()
