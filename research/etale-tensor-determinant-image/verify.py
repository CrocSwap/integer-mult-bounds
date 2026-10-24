"""Exact finite controls for the finite-etale determinant-image theorem.

No dependencies, predecessor-code imports, network access, or file writes.
The all-dimension claim is the written proof, not this bounded enumeration.
"""

import hashlib
import itertools
import json
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def add(a, b, p, scale=1):
    return tuple(tuple((x + scale * y) % p for x, y in zip(ar, br))
                 for ar, br in zip(a, b))


def multiply(a, b, p):
    n = len(a)
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(n)) % p
                       for j in range(n)) for i in range(n))


def power(a, exponent, p):
    result = identity(len(a))
    for bit in range(exponent.bit_length()):
        if (exponent >> bit) & 1:
            result = multiply(result, a, p)
        a = multiply(a, a, p)
    return result


def rref(rows, p):
    rows = [list(row) for row in rows]
    pivots = []
    height, width = len(rows), len(rows[0])
    for column in range(width):
        candidates = [i for i in range(len(pivots), height) if rows[i][column]]
        if not candidates:
            continue
        pivot = len(pivots)
        other = candidates[0]
        rows[pivot], rows[other] = rows[other], rows[pivot]
        inv = pow(rows[pivot][column], -1, p)
        rows[pivot] = [(x * inv) % p for x in rows[pivot]]
        for i in range(height):
            if i != pivot and rows[i][column]:
                factor = rows[i][column]
                rows[i] = [(x - factor * y) % p
                           for x, y in zip(rows[i], rows[pivot])]
        pivots.append(column)
        if len(pivots) == height:
            break
    return rows, pivots


def nullspace(rows, p):
    reduced, pivots = rref(rows, p)
    width = len(rows[0])
    basis = []
    for column in range(width):
        if column in pivots:
            continue
        vector = [0] * width
        vector[column] = 1
        for i, pivot in enumerate(pivots):
            vector[pivot] = -reduced[i][column] % p
        basis.append(tuple(vector))
    return basis


def determinant(a, p):
    rows = [list(row) for row in a]
    value, n = 1, len(a)
    for column in range(n):
        candidates = [i for i in range(column, n) if rows[i][column]]
        if not candidates:
            return 0
        other = candidates[0]
        if other != column:
            rows[column], rows[other] = rows[other], rows[column]
            value = -value
        pivot = rows[column][column]
        value = value * pivot % p
        for i in range(column + 1, n):
            factor = rows[i][column] * pow(pivot, -1, p) % p
            rows[i] = [(x - factor * y) % p
                       for x, y in zip(rows[i], rows[column])]
    return value % p


def linear_combination(matrices, coefficients, p):
    result = tuple(tuple(0 for _ in matrices[0]) for _ in matrices[0])
    for matrix, coefficient in zip(matrices, coefficients):
        result = add(result, matrix, p, coefficient)
    return result


def coordinates(matrices, target, p):
    n, count = len(target), len(matrices)
    rows = [[matrix[i][j] for matrix in matrices] + [target[i][j]]
            for i in range(n) for j in range(n)]
    reduced, pivots = rref(rows, p)
    require(pivots == list(range(count)), "matrix outside the algebra")
    return tuple(reduced[i][-1] for i in range(count))


def bilinear(table, x, y, p):
    n = len(table)
    return tuple(sum(x[i] * y[j] * table[i][j][k]
                     for i in range(n) for j in range(n)) % p
                 for k in range(n))


def apply(a, x, p):
    return tuple(sum(v * w for v, w in zip(row, x)) % p for row in a)


def columns(a):
    return tuple(zip(*a))


def algebra_table(p, polynomials):
    degrees = [len(f) - 1 for f in polynomials]
    n, table, offset = sum(degrees), [], 0
    blocks = []
    for f, degree in zip(polynomials, degrees):
        blocks.append((offset, degree, f))
        offset += degree
    for i in range(n):
        row = []
        for j in range(n):
            vector = [0] * n
            for start, degree, f in blocks:
                if start <= i < start + degree and start <= j < start + degree:
                    monomial = [0] * (2 * degree - 1)
                    monomial[i + j - 2 * start] = 1
                    for k in range(2 * degree - 2, degree - 1, -1):
                        coefficient = monomial[k]
                        for t in range(degree):
                            monomial[k - degree + t] -= coefficient * f[t]
                    vector[start:start + degree] = [x % p for x in monomial[:degree]]
            row.append(tuple(vector))
        table.append(tuple(row))
    return tuple(table)


def change_bases(table, p):
    n = len(table)
    left, right = [list(r) for r in identity(n)], [list(r) for r in identity(n)]
    if n > 1:
        left[0][1], right[1][0] = 1, 1
    output = tuple(tuple((p - 1) * int(j == (i + 1) % n) % p
                         for j in range(n)) for i in range(n))
    lc, rc = columns(left), columns(right)
    require(all(determinant(a, p) for a in (left, right, output)), "singular chart")
    return tuple(tuple(apply(output, bilinear(table, x, y, p), p)
                       for y in rc) for x in lc)


def left_nucleus(table, p):
    n, rows = len(table), []
    for i, j, k in itertools.product(range(n), repeat=3):
        row = [0] * (2 * n * n)
        for ell in range(n):
            row[ell * n + i] += table[ell][j][k]
            row[n * n + k * n + ell] -= table[i][j][ell]
        rows.append([x % p for x in row])
    solutions = nullspace(rows, p)
    matrices = [tuple(tuple(v[n * n + i * n + j] for j in range(n))
                      for i in range(n)) for v in solutions]
    require(len(matrices) == n, "wrong promised nucleus dimension")
    require(len(rref([sum(m, ()) for m in matrices], p)[1]) == n,
            "output projection is not faithful")
    for a, b in itertools.product(matrices, repeat=2):
        require(multiply(a, b, p) == multiply(b, a, p), "noncommutative nucleus")
    return matrices


def extract_degrees(table, p):
    algebra, n = left_nucleus(table, p), len(table)
    frobenius_columns = [coordinates(algebra, power(a, p, p), p) for a in algebra]
    frobenius = tuple(zip(*frobenius_columns))
    fixed_coefficients = nullspace(add(frobenius, identity(n), p, -1), p)
    fixed = [linear_combination(algebra, v, p) for v in fixed_coefficients]
    pieces = [identity(n)]
    for c in fixed:
        refined = []
        for e in pieces:
            for scalar in range(p):
                projector = add(identity(n), power(add(c, identity(n), p, -scalar),
                                                   p - 1, p), p, -1)
                piece = multiply(e, projector, p)
                if any(sum(piece, ())):
                    require(multiply(piece, piece, p) == piece, "not an idempotent")
                    refined.append(piece)
        pieces = refined
        require(len(pieces) <= n, "too many spectral pieces")
    require(len(pieces) == len(fixed), "fixed algebra was not fully split")
    require(linear_combination(pieces, [1] * len(pieces), p) == identity(n),
            "incomplete idempotent partition")
    degrees = sorted(len(rref(e, p)[1]) for e in pieces)
    require(sum(degrees) == n, "wrong total degree")
    return degrees


def predicted_image(p, degrees):
    negative = p != 2 and (any(d % 2 == 0 for d in degrees)
                          or len(set(degrees)) != len(degrees))
    signs = {1, p - 1} if negative else {1}
    return {(a, b, c) for a, b, c in itertools.product(range(1, p), repeat=3)
            if a * b * c % p in signs}


def is_autotopism(table, f, g, h, p):
    basis, n = columns(identity(len(table))), len(table)
    return all(bilinear(table, apply(f, basis[i], p), apply(g, basis[j], p), p)
               == apply(h, table[i][j], p)
               for i in range(n) for j in range(n))


def all_invertible(n, p):
    require(n <= 3 and p ** (n * n) <= 20000, "matrix census exceeds bound")
    result = []
    for entries in itertools.product(range(p), repeat=n * n):
        matrix = tuple(tuple(entries[i * n + j] for j in range(n)) for i in range(n))
        if determinant(matrix, p):
            result.append(matrix)
    return result


def direct_autotopisms(table, p, unit):
    n, image, count = len(table), set(), 0
    matrices = all_invertible(n, p)
    require(len(matrices) ** 2 <= 250000, "autotopism census exceeds bound")
    for f, g in itertools.product(matrices, repeat=2):
        b = apply(g, unit, p)
        h = tuple(zip(*(bilinear(table, apply(f, x, p), b, p)
                        for x in columns(identity(n)))))
        if determinant(h, p) and is_autotopism(table, f, g, h, p):
            count += 1
            image.add((pow(determinant(f, p), -1, p),
                       pow(determinant(g, p), -1, p), determinant(h, p)))
    return image, count, len(matrices) ** 2


def explicit_witnesses(table, p, polynomials):
    n, norm_representatives = len(table), {}
    for vector in itertools.product(range(p), repeat=n):
        matrix = tuple(zip(*(bilinear(table, vector, x, p)
                             for x in columns(identity(n)))))
        norm = determinant(matrix, p)
        if norm and norm not in norm_representatives:
            norm_representatives[norm] = matrix
    require(set(norm_representatives) == set(range(1, p)), "norm is not onto")
    automorphisms, start = [identity(n)], 0
    blocks = []
    for polynomial in polynomials:
        degree = len(polynomial) - 1
        blocks.append((start, degree, polynomial))
        matrix = [list(row) for row in identity(n)]
        for j in range(start, start + degree):
            vector = tuple(int(i == j) for i in range(n))
            value = vector
            for _ in range(p - 1):
                value = bilinear(table, value, vector, p)
            for i in range(n):
                matrix[i][j] = value[i]
        automorphisms.append(tuple(tuple(row) for row in matrix))
        start += degree
    for (a, d, fa), (b, e, fb) in itertools.combinations(blocks, 2):
        if d == e:
            require(fa == fb, "fixture needs an explicit factor isomorphism")
            permutation = list(range(n))
            permutation[a:a + d], permutation[b:b + d] = range(b, b + d), range(a, a + d)
            automorphisms.append(tuple(tuple(int(i == permutation[j]) for j in range(n))
                                       for i in range(n)))
    image = set()
    for sigma in automorphisms:
        require(is_autotopism(table, sigma, sigma, sigma, p), "bad automorphism")
        for ma, mb in itertools.product(norm_representatives.values(), repeat=2):
            f, g = multiply(ma, sigma, p), multiply(mb, sigma, p)
            h = multiply(multiply(ma, mb, p), sigma, p)
            require(is_autotopism(table, f, g, h, p), "bad unit witness")
            image.add((pow(determinant(f, p), -1, p),
                       pow(determinant(g, p), -1, p), determinant(h, p)))
    return image


def check_controls():
    require((1, 1, 2) in predicted_image(3, [1, 1, 1]), "missed odd factor swap")
    require((1, 1, 2) in predicted_image(3, [2]), "missed even-degree Frobenius")
    require((1, 1, 2) not in predicted_image(3, [1, 3]), "spurious negative sign")
    require((1, 1, 2) in predicted_image(3, [3, 3]), "missed repeated odd degree")
    bad = [list(row) for row in identity(2)]
    bad[0][0] = 0
    require(determinant(bad, 3) == 0, "singular matrix control failed")
    try:
        coordinates([identity(2)], ((1, 1), (0, 1)), 3)
    except ValueError:
        pass
    else:
        raise ValueError("outside-algebra control accepted")
    zero_table = tuple(tuple((0, 0) for _ in range(2)) for _ in range(2))
    try:
        left_nucleus(zero_table, 3)
    except ValueError:
        pass
    else:
        raise ValueError("wrong-nucleus-dimension control accepted")
    scalar_table = algebra_table(5, ((0, 1),))
    require(is_autotopism(scalar_table, ((2,),), ((1,),), ((2,),), 5),
            "scalar autotopism control failed")
    scalar_image = predicted_image(5, [1])
    require((3, 1, 2) in scalar_image and (2, 1, 2) not in scalar_image,
            "inverse-input determinant convention lost")


def main():
    # Constant-first monic irreducibles; degrees two and three have no base-field root.
    linear, f2quad, f2cube = (0, 1), (1, 1, 1), (1, 1, 0, 1)
    f3quad, f3cube, f5quad = (1, 0, 1), (1, 2, 0, 1), (2, 0, 1)
    fixtures = [(3, (linear,) * 3), (3, (f3cube,)),
                (3, (linear, f3quad)), (3, (linear, f3cube)),
                (3, (f3cube, f3cube)), (2, (linear,) * 3),
                (2, (f2cube,)), (2, (f2quad,)),
                (3, (linear, linear)), (3, (f3quad,)),
                (5, (linear, linear)), (5, (f5quad,))]
    results, censuses = [], []
    for p, polynomials in fixtures:
        require(p in (2, 3, 5) and sum(len(f) - 1 for f in polynomials) <= 6,
                "fixture outside finite bounds")
        for f in polynomials:
            if len(f) > 2:
                require(all(sum(c * x ** i for i, c in enumerate(f)) % p
                            for x in range(p)), "fixture polynomial has a root")
        table = algebra_table(p, polynomials)
        degrees = sorted(len(f) - 1 for f in polynomials)
        require(extract_degrees(table, p) == degrees, "wrong intrinsic factor degrees")
        require(extract_degrees(change_bases(table, p), p) == degrees,
                "factor degrees depend on tensor charts")
        image = predicted_image(p, degrees)
        require(explicit_witnesses(table, p, polynomials) == image, "image not attained")
        results.append({"p": p, "degrees": degrees, "image_size": len(image)})
        if len(table) <= 2 or (p == 2 and len(table) == 3):
            unit, offset = [0] * len(table), 0
            for polynomial in polynomials:
                unit[offset] = 1
                offset += len(polynomial) - 1
            actual, count, pairs = direct_autotopisms(table, p, tuple(unit))
            require(actual == image, "direct stabilizer image disagrees")
            censuses.append({"p": p, "degrees": degrees, "autotopisms": count,
                             "candidate_input_pairs": pairs})
    check_controls()
    package = Path(__file__).resolve().parent
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
              for name in ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")}
    print(json.dumps({"status": "PASS_ETALE_TENSOR_DETERMINANT_IMAGE",
                      "python": sys.version.split()[0], "fixtures": results,
                      "direct_censuses": censuses, "control_groups": 8,
                      "candidate_input_pairs": sum(c["candidate_input_pairs"] for c in censuses),
                      "accepted_autotopisms": sum(c["autotopisms"] for c in censuses),
                      "source_sha256": hashes}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
