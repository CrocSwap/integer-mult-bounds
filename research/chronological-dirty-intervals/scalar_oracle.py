"""Compressed integer-prefix oracle, independently from formal leaf expansion.

@CubeJerry with substantial OpenAI Codex assistance; Apache-2.0.
Only scalar +-1 factors, exact integer matrices and Fraction inversion.
"""
from fractions import Fraction
from functools import lru_cache


def need(ok, message):
    if not ok:
        raise ValueError(message)


def eye(d):
    return [[int(i == j) for j in range(d)] for i in range(d)]


def product(a, b):
    columns = list(zip(*b))
    return [[sum(c*d for c, d in zip(row, col)) for col in columns] for row in a]


def inverse(matrix):
    d = len(matrix)
    rows = [[Fraction(c) for c in row]+unit for row, unit in zip(matrix, eye(d))]
    for j in range(d):
        pivot = next((i for i in range(j, d) if rows[i][j]), None)
        need(pivot is not None, "singular prefix")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        divisor = rows[j][j]
        rows[j] = [c/divisor for c in rows[j]]
        for i in range(d):
            if i != j:
                coefficient = rows[i][j]
                rows[i] = [c-coefficient*v for c, v in zip(rows[i], rows[j])]
    need(all(c.denominator == 1 for row in rows for c in row), "nonintegral inverse")
    return [[int(c) for c in row[d:]] for row in rows]


@lru_cache(maxsize=256)
def leaf_count(n):
    if n == 1:
        return 1
    return 2*(leaf_count(n//2)+leaf_count(n-n//2))


def prefix(n, cut, negative_indices):
    need(isinstance(n, int) and 1 <= n <= 1 << 32, "scalar factor capacity")
    need(0 <= cut <= leaf_count(n), "scalar cut range")
    need(len(set(negative_indices)) == len(negative_indices)
         and all(0 <= i < n for i in negative_indices), "negative factor indices")
    d = (n-1).bit_length()+2
    accumulated = eye(d)
    lo, count, x, y, level = 0, n, 0, 1, 0
    def coefficient(start, size):
        return (-1)**sum(start <= i < start+size for i in negative_indices)
    def shear(source, target, value):
        matrix = eye(d)
        matrix[target][source] = value
        return matrix
    while True:
        if cut == 0:
            return accumulated
        if cut == leaf_count(count):
            return product(shear(x, y, coefficient(lo, count)), accumulated)
        left = count//2
        right = count-left
        lu, lv = leaf_count(left), leaf_count(right)
        z = level+2
        b, a = coefficient(lo, left), coefficient(lo+left, right)
        if cut <= lu:
            count, y = left, z
        elif cut <= lu+lv:
            accumulated = product(shear(x, z, b), accumulated)
            lo, count, x, cut = lo+left, right, z, cut-lu
        elif cut <= 2*lu+lv:
            completed = product(shear(x, z, -b), product(shear(z, y, a), shear(x, z, b)))
            accumulated = product(completed, accumulated)
            count, y, cut = left, z, 2*lu+lv-cut
        else:
            accumulated = product(shear(x, y, a*b), accumulated)
            lo, count, x, cut = lo+left, right, z, 2*(lu+lv)-cut
        level += 1


def verify_witnesses():
    witnesses = []
    for h in range(1, 33):
        n = 1 << h
        negatives = tuple(n-(1 << k)-1 for k in range(h-1))
        a, b = 3*4**(h-1)//5, (4**h+2)//3
        pa, pb = prefix(n, a, negatives), prefix(n, b, negatives)
        q = inverse(pa)
        need(product(pa, q) == eye(h+2), "scalar inverse identity")
        interval = product(pb, q)
        expected = [(-1)**(h-1)*(1+h//2), 1]
        expected += [j*(-1)**(h+j) for j in range(1, h+1)]
        need(interval[1] == expected, "PR1374 exact target row")
        norm = max(sum(abs(c) for c in row) for row in interval)
        need(norm == h*h//2+h+2, "sharp witness norm")
        if h == 2:
            need(norm > h+2 and norm > h*h//2+h+1, "understated-bound controls")
            need(product(q, pb) != interval, "wrong matrix product-order control")
        witnesses.append({"h": h, "n": n, "cuts": [a, b], "norm": norm})
    return {"exact_integer_witnesses": witnesses,
            "method": "compressed four-phase prefixes plus rational Gauss-Jordan inverse",
            "controls": ["false_linear_bound", "sharp_bound_minus_one", "wrong_product_order"]}


if __name__ == "__main__":
    import json
    print(json.dumps(verify_witnesses(), sort_keys=True))
