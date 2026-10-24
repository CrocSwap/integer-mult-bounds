#!/usr/bin/env python3
"""Exact bounded replay of the rank-two classification; standard library only."""

from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def binary_rank(rows, width):
    pivots = [0] * width
    rank = 0
    for value in rows:
        for bit in range(width - 1, -1, -1):
            if not (value >> bit) & 1:
                continue
            if pivots[bit]:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                rank += 1
                break
    return rank


def rank_table(width):
    require(width in (3, 6), "rank table domain")
    mask = (1 << width) - 1
    return bytes(binary_rank((v & mask, (v >> width) & mask,
                              v >> (2 * width)), width)
                 for v in range(1 << (3 * width)))


def binary_product(left, right, width):
    result = []
    for row in left:
        value = 0
        for j in range(width):
            if (row >> j) & 1:
                value ^= right[j]
        result.append(value)
    return tuple(result)


def literal_two_factor_criterion(rows, rank6, rank3):
    """Apply the cited criterion to full 6x6 targets, without rank factors."""
    for phi in (1, 2, 3):
        r = rows[:3] if phi == 1 else rows[3:]
        if phi == 3:
            r = tuple(rows[i] ^ rows[i + 3] for i in range(3))
        whole_rank = rank6[r[0] | (r[1] << 6) | (r[2] << 12)]
        for v in (1, 2, 3):
            c = tuple((x & 7) if v == 1 else (x >> 3) if v == 2
                      else ((x & 7) ^ (x >> 3)) for x in r)
            if rank3[c[0] | (c[1] << 3) | (c[2] << 6)] == whole_rank:
                return True
    return False


def full_a_pencil(a, b):
    for phi in (1, 2, 3):
        x = (a & 7) if phi == 1 else (a >> 3) if phi == 2 else ((a & 7) ^ (a >> 3))
        y = (b & 7) if phi == 1 else (b >> 3) if phi == 2 else ((b & 7) ^ (b >> 3))
        if not x or not y or x == y:
            return False
    return True


def common_b_row(b1, b2):
    parts = (b1 & 7, b2 & 7, b1 >> 3, b2 >> 3)
    return len({x for x in parts if x}) == 1


def binary_coordinate_factor(rows, column):
    other = 7 << (3 * (1 - column))
    return all((row & other) == ((1 << i) & other)
               for i, row in enumerate(rows))


def binary_exception_word(a, b, b1, b2, target):
    parts = (b1 & 7, b2 & 7, b1 >> 3, b2 >> 3)
    base = next(x for x in parts if x)
    c1 = int(parts[0] == base) | (int(parts[1] == base) << 1)
    ac = (a if c1 & 1 else 0) ^ (b if c1 & 2 else 0)
    first, second = ac & 7, ac >> 3
    require(first != 0, "exceptional A_1 c_1 must be nonzero")
    h = (first & -first).bit_length() - 1
    ell = tuple((1 << h) if (second >> i) & 1 else 0 for i in range(3))
    m11 = tuple(row & 7 for row in target[:3])
    m12 = tuple(row >> 3 for row in target[:3])
    m22 = tuple(row >> 3 for row in target[3:])
    correction = binary_product(ell, m12, 3)
    d = tuple(x ^ y for x, y in zip(m22, correction))
    ident = (1, 2, 4)
    f1 = ident + tuple(ell[i] | (ident[i] << 3) for i in range(3))
    f2 = tuple(ident[i] | (m12[i] << 3) for i in range(3)) + tuple(x << 3 for x in d)
    f3 = m11 + tuple(x << 3 for x in ident)
    factors = (f1, f2, f3)
    require(all(binary_coordinate_factor(f, j) for f, j in zip(factors, (0, 1, 0))),
            "illegal right-vector factor")
    require(binary_product(f1, binary_product(f2, f3, 6), 6) == target,
            "three-factor word differs from target")
    return factors


def binary_census():
    rank6, rank3 = rank_table(6), rank_table(3)
    bases = [(a, b) for a in range(1, 64) for b in range(a + 1, 64) if b < (a ^ b)]
    right = [(a, b, common_b_row(a, b)) for a in range(1, 64)
             for b in range(1, 64) if a != b]
    require(len(bases) == 651 and len(right) == 3906, "rank-factor coverage")
    histogram = [0, 0, 0, 0]
    digest = sha256()
    samples = {}
    full_pencils = 0
    for a, b in bases:
        full = full_a_pencil(a, b)
        full_pencils += full
        selectors = tuple(((a >> i) & 1) | (((b >> i) & 1) << 1) for i in range(6))
        for b1, b2, common in right:
            options = (0, b1, b2, b1 ^ b2)
            rows = tuple(options[i] for i in selectors)
            exception = full and common
            passing = literal_two_factor_criterion(rows, rank6, rank3)
            require(passing != exception, "classification disagrees with full-matrix criterion")
            cost = 3 if exception else 2
            if exception:
                binary_exception_word(a, b, b1, b2, rows)
            histogram[cost] += 1
            digest.update(bytes(rows + (cost,)))
            samples.setdefault((full, common), rows)
    require(histogram == [0, 0, 2535162, 7644], "complete cost histogram")
    require(full_pencils == 182 and len(samples) == 4, "pencil-class coverage")
    return {"targets": sum(histogram), "histogram": histogram,
            "column_spaces": len(bases), "right_factors": len(right),
            "exceptional_column_spaces": full_pencils,
            "table_sha256": digest.hexdigest()}, samples


def add(a, b, q):
    return a ^ b if q == 4 else (a + b) % q


def multiply(a, b, q):
    if q == 4:
        return ((0, 0, 0, 0), (0, 1, 2, 3),
                (0, 2, 3, 1), (0, 3, 1, 2))[a][b]
    return a * b % q


def negative(a, q):
    return a if q == 4 else -a % q


def inverse(a, q):
    require(a != 0, "division by zero")
    return next(b for b in range(1, q) if multiply(a, b, q) == 1)


def matrix_product(a, b, q):
    out = [[0] * len(b[0]) for _ in a]
    for i in range(len(a)):
        for j in range(len(b[0])):
            value = 0
            for k in range(len(b)):
                value = add(value, multiply(a[i][k], b[k][j], q), q)
            out[i][j] = value
    return out


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def solve(a, b, q):
    """Solve A X=B, with zero free variables; reject inconsistent systems."""
    n, rhs = len(a[0]), len(b[0])
    rows = [list(x) + list(y) for x, y in zip(a, b)]
    pivots = []
    for col in range(n):
        candidates = [i for i in range(len(pivots), len(rows)) if rows[i][col]]
        if not candidates:
            continue
        k, source = len(pivots), candidates[0]
        rows[k], rows[source] = rows[source], rows[k]
        factor = inverse(rows[k][col], q)
        rows[k] = [multiply(x, factor, q) for x in rows[k]]
        for i in range(len(rows)):
            if i != k and rows[i][col]:
                factor = negative(rows[i][col], q)
                rows[i] = [add(x, multiply(factor, y, q), q)
                           for x, y in zip(rows[i], rows[k])]
        pivots.append(col)
    if any(any(row[n:]) for row in rows[len(pivots):]):
        return None
    out = [[0] * rhs for _ in range(n)]
    for i, col in enumerate(pivots):
        out[col] = rows[i][n:]
    require(matrix_product(a, out, q) == b, "linear solve postcondition")
    return out


def dense_rank(a, q):
    basis = []
    for column in zip(*a):
        rhs = [[x] for x in column]
        if not basis or solve([list(row) for row in zip(*basis)], rhs, q) is None:
            if any(column):
                basis.append(column)
    return len(basis)


def free_matrix(s, m):
    return [[s[i // m][j // m] if i % m == j % m else 0
             for j in range(2 * m)] for i in range(2 * m)]


def coordinate_factor(f, column, m):
    return all(f[i][j] == int(i == j) for i in range(2 * m)
               for j in range(2 * m) if j // m != column)


def projective(q):
    return [(1, x) for x in range(q)] + [(0, 1)]


def chart(first, q, columns=False):
    second = next(v for v in projective(q)
                  if add(multiply(first[0], v[1], q),
                         negative(multiply(first[1], v[0], q), q), q))
    rows = [list(first), list(second)]
    return [list(x) for x in zip(*rows)] if columns else rows


def two_factor_word(target, q):
    m = len(target) // 2
    for phi in projective(q):
        g = free_matrix(chart(phi, q), m)
        for v in projective(q):
            h = free_matrix(chart(v, q, columns=True), m)
            n = matrix_product(matrix_product(g, target, q), h, q)
            a = [row[:m] for row in n[:m]]
            b = [row[:m] for row in n[m:]]
            c = solve(a, [row[m:] for row in n[:m]], q)
            if c is None:
                continue
            bc = matrix_product(b, c, q)
            d = [[add(n[i + m][j + m], negative(bc[i][j], q), q)
                  for j in range(m)] for i in range(m)]
            f1, f2 = identity(2 * m), identity(2 * m)
            for i in range(m):
                f1[i][:m], f1[i + m][:m] = a[i], b[i]
                f2[i][m:], f2[i + m][m:] = c[i], d[i]
            require(coordinate_factor(f1, 0, m) and coordinate_factor(f2, 1, m),
                    "two-factor alphabet")
            require(matrix_product(f1, f2, q) == n, "two-factor chart endpoint")
            gi, hi = solve(g, identity(2 * m), q), solve(h, identity(2 * m), q)
            require(gi is not None and hi is not None, "free chart inverse")
            endpoint = matrix_product(matrix_product(gi, f1, q),
                                      matrix_product(f2, hi, q), q)
            require(endpoint == target, "two-factor actual endpoint")
            return g, h, f1, f2
    return None


def explicit_example(m):
    target = [[0] * (2 * m) for _ in range(2 * m)]
    target[0][0] = target[1][m] = target[m + 1][0] = target[m + 2][m] = 1
    f1, f2, f3 = identity(2 * m), identity(2 * m), identity(2 * m)
    f1[m + 1][0] = f2[1][m] = 1
    for i in range(m):
        for j in range(m):
            f2[m + i][m + j] = int((i, j) == (2, 0))
            f3[i][j] = int((i, j) == (0, 0))
    return target, (f1, f2, f3)


def finite_field_examples(samples):
    cases = []
    for q, m in product((2, 3, 4, 5, 7), (3, 4)):
        target, factors = explicit_example(m)
        require(dense_rank(target, q) == 2, "explicit ordinary rank")
        require(two_factor_word(target, q) is None, "explicit shorter word")
        endpoint = matrix_product(factors[0], matrix_product(factors[1], factors[2], q), q)
        require(endpoint == target, "all-field explicit three-factor word")
        require(all(coordinate_factor(f, j, m) for f, j in zip(factors, (0, 1, 0))),
                "all-field legal factor")
        require(matrix_product(factors[2], matrix_product(factors[1], factors[0], q), q)
                != target, "reversed chronology control")
        require(matrix_product(factors[0], factors[2], q) != target, "omitted factor control")
        cases.append({"q": q, "m": m, "cost": 3})
    for (full, common), rows in sorted(samples.items()):
        target = [[(row >> j) & 1 for j in range(6)] for row in rows]
        require((two_factor_word(target, 2) is None) == (full and common),
                "independent dense chart witnesses")
    return cases


def controls():
    target, factors = explicit_example(3)
    for data in product(range(2), repeat=6):
        value = [[x] for x in data]
        for factor in reversed(factors):
            value = matrix_product(factor, value, 2)
        require(value == matrix_product(target, [[x] for x in data], 2), "dirty input")
    boundary = [[0] * 4 for _ in range(4)]
    boundary[2][2] = boundary[3][3] = 1
    require(dense_rank(boundary, 2) == 2 and coordinate_factor(boundary, 0, 2),
            "m=2 one-factor boundary")
    require(not full_a_pencil(9, 18), "dependent sum pencil control")
    require(not common_b_row(1, 16), "rank-one blocks need a common row")
    require(multiply(2, 2, 4) == 3 and add(2, 2, 4) == 0,
            "F4 differs from integers modulo four")
    require(solve([[0]], [[1]], 2) is None, "inconsistent solve must reject")
    require(solve([[0]], [[0]], 2) == [[0]], "singular consistent solve")
    changed = [row[:] for row in factors[0]]
    changed[0][3] = 1
    require(not coordinate_factor(changed, 0, 3), "changed fixed block column")
    return {"dirty_inputs": 64, "boundary_and_mutation_controls": 7}


def source_receipt():
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    manifest = json.loads(bounded_read(package / "SOURCES.json"))
    require(len(manifest["files"]) <= 8, "source manifest capacity")
    hashes = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            digest = sha256(bounded_read(root / row["path"])).hexdigest()
            require(digest == row["sha256"], "predecessor source drift: " + row["path"])
            hashes[row["path"]] = digest
    for name in ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py"):
        path = package / name
        hashes[path.relative_to(root).as_posix()] = sha256(bounded_read(path)).hexdigest()
    return hashes


def bounded_read(path):
    with path.open("rb") as stream:
        data = stream.read(1048577)
    require(len(data) <= 1048576, "source file exceeds one MiB")
    return data


def main():
    hashes = source_receipt()
    census, samples = binary_census()
    fields = finite_field_examples(samples)
    checks = controls()
    receipt = {"schema": "rank-two-right-vector/v1", "census": census,
               "field_examples": fields, "controls": checks, "file_sha256": hashes}
    encoded = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    print(encoded)
    print("PASS_RIGHT_VECTOR_RANK_TWO targets=2542806 cost2=2535162 cost3=7644 "
          "three_factor_words=7644 no_new_kappa receipt_sha256=" + sha256(encoded.encode()).hexdigest())


if __name__ == "__main__":
    main()
