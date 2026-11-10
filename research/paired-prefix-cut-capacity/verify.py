"""Exact paired-prefix cut checks. Nick Petalas. Apache-2.0."""
from fractions import Fraction as Q
from itertools import combinations, permutations, product
from math import gcd, lcm
from pathlib import Path
import hashlib
import json


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def mm(a, b):
    return [[sum(x * y for x, y in zip(row, col))
             for col in zip(*b)] for row in a]


def add_matrix(n, dst, src, coefficient):
    need(type(n) is int and 2 <= n <= 8, "matrix dimension")
    need(type(dst) is int and type(src) is int and
         0 <= dst < n and 0 <= src < n and dst != src, "distinct roles")
    c = Q(coefficient)
    need(c and c.denominator & (c.denominator - 1) == 0 and
         max(abs(c.numerator).bit_length(), c.denominator.bit_length()) <= 16,
         "bounded nonzero dyadic coefficient")
    a = eye(n)
    a[dst][src] = c
    return a


def rref(a, width):
    need(0 <= width <= 3 and len(a) <= 3, "kernel dimension")
    need(all(len(row) == width for row in a), "constraint shape")
    a = [[Q(x) for x in row] for row in a]
    pivots = []
    for col in range(width):
        row = next((i for i in range(len(pivots), len(a)) if a[i][col]), None)
        if row is None:
            continue
        k = len(pivots)
        a[k], a[row] = a[row], a[k]
        scale = a[k][col]
        a[k] = [x / scale for x in a[k]]
        for i in range(len(a)):
            if i != k:
                scale = a[i][col]
                a[i] = [x - scale * y for x, y in zip(a[i], a[k])]
        pivots.append(col)
    return a, pivots


def primitive(row):
    scale = lcm(*(Q(x).denominator for x in row))
    values = [int(scale * x) for x in row]
    divisor = gcd(*values)
    need(divisor != 0, "nonzero primitive row")
    return [x // divisor for x in values]


def bezout(a, b):
    need(max(abs(a).bit_length(), abs(b).bit_length()) <= 64, "Bezout size")
    old_r, r, old_s, s, old_t, t = abs(a), abs(b), 1, 0, 0, 1
    for _ in range(192):
        if not r:
            u = old_s if a >= 0 else -old_s
            v = old_t if b >= 0 else -old_t
            need(u * a + v * b == old_r, "Bezout identity")
            return old_r, u, v
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    raise ValueError("Bezout iteration budget exhausted")


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]]


def kernel(a, width):
    """Rows forming the full integer kernel, hence its full dyadic localization."""
    reduced, pivots = rref(a, width)
    rank = len(pivots)
    if not rank:
        return eye(width)
    if rank == width:
        return []
    first = primitive(reduced[0])
    if width == 2:
        result = [[-first[1], first[0]]]
    elif rank == 2:
        result = [primitive(cross(first, primitive(reduced[1])))]
    else:
        a0, b0, c0 = first
        g, s, t = bezout(a0, b0)
        if not g:
            result = [[1, 0, 0], [0, 1, 0]]
        else:
            h = gcd(g, c0)
            result = [[b0 // g, -a0 // g, 0],
                      [-s * (c0 // h), -t * (c0 // h), g // h]]
    need(all(not any(sum(x * y for x, y in zip(row, v)) for row in a)
             for v in result), "kernel equations")
    need(len(rref(result, width)[1]) == width - rank, "kernel rank")
    return result


def determinant(a):
    n = len(a)
    need(n <= 3 and all(len(row) == n for row in a), "minor dimension")
    total = Q(0)
    for p in permutations(range(n)):
        inversions = sum(p[i] > p[j] for i in range(n) for j in range(i + 1, n))
        term = Q((-1) ** inversions)
        for i in range(n):
            term *= a[i][p[i]]
        total += term
    return total


def capacity(a):
    """Determinantal-divisor oracle, without predecessor executable imports."""
    m, n = len(a), len(a[0]) if a else 0
    need(m <= 3 and n <= 3 and all(len(row) == n for row in a), "pairing size")
    scale = max((Q(x).denominator for row in a for x in row), default=1)
    need(all(Q(x).denominator & (Q(x).denominator - 1) == 0
             for row in a for x in row), "dyadic pairing")
    integer = [[int(scale * x) for x in row] for row in a]
    count = 0
    for k in range(1, min(m, n) + 1):
        divisor = 0
        for rows in combinations(range(m), k):
            for cols in combinations(range(n), k):
                value = determinant([[integer[i][j] for j in cols] for i in rows])
                need(value.denominator == 1, "integer minor")
                divisor = gcd(divisor, int(value))
        if not divisor or divisor & (divisor - 1):
            break
        count = k
    return count


def cut_data(a, b, f, g):
    n = len(a)
    outside = [j for j in range(n) if j not in g]
    left = kernel([[a[i][j] for i in f] for j in outside], len(f))
    right = kernel([[b[j][i] for i in f] for j in outside], len(f))
    pairing = [[sum(x * y for x, y in zip(v, u)) for u in right] for v in left]
    return capacity(pairing)


def word(n, operations):
    a = b = eye(n)
    for dst, src, c in operations:
        a = mm(add_matrix(n, dst, src, c), a)
        b = mm(b, add_matrix(n, dst, src, -c))
    need(mm(a, b) == mm(b, a) == eye(n), "complete dirty endpoint")
    return a, b


def prefixes(n):
    if n == 2:
        result = []
        for values in product(range(-2, 3), repeat=4):
            a, b, c, d = values
            if a * d - b * c == 1:
                result.append(([[a, b], [c, d]], [[d, -b], [-c, a]]))
        return result
    operations = [(i, j, c) for i in range(3) for j in range(3)
                  if i != j for c in (-1, 1)]
    result = [word(3, [])]
    result.extend(word(3, [op]) for op in operations)
    result.extend(word(3, [op, operations[(i + 3) % 12]])
                  for i, op in enumerate(operations))
    for c in (2, 3, 5):
        result.append(word(3, [(0, 2, 1), (1, 2, c), (2, 0, 1), (2, 1, c)]))
    return result


def screen():
    counts = {"prefix_instances": 0, "edits": 0, "same_side": 0,
              "crossing": 0, "delta_minus_one": 0, "delta_zero": 0,
              "delta_plus_one": 0}
    delta_keys = {-1: "delta_minus_one", 0: "delta_zero", 1: "delta_plus_one"}
    for n in (2, 3):
        cases = prefixes(n)
        counts["prefix_instances"] += len(cases)
        for a, b in cases:
            need(mm(a, b) == mm(b, a) == eye(n), "prefix inverse")
            for fm in range(1, (1 << n) - 1):
                f = [i for i in range(n) if fm >> i & 1]
                for gm in range(1, (1 << n) - 1):
                    g = [i for i in range(n) if gm >> i & 1]
                    old = cut_data(a, b, f, g)
                    for dst in range(n):
                        for src in range(n):
                            if dst == src:
                                continue
                            for c in (Q(-1, 2), Q(1, 2)):
                                aa = mm(add_matrix(n, dst, src, c), a)
                                bb = mm(b, add_matrix(n, dst, src, -c))
                                need(mm(bb, aa) == eye(n), "paired edit endpoint")
                                delta = cut_data(aa, bb, f, g) - old
                                crossing = (dst in f) != (src in f)
                                need(abs(delta) <= int(crossing), "paired ADD bound")
                                counts["edits"] += 1
                                counts["crossing" if crossing else "same_side"] += 1
                                counts[delta_keys[delta]] += 1
    need(counts["edits"] == counts["crossing"] + counts["same_side"], "coverage")
    return counts


def sharpness():
    cases = 0
    for d in range(1, 5):
        n = 2 * d
        operations = [(2 * i, 2 * i + 1, 1) for i in range(d)]
        a, b = word(n, operations)
        f = list(range(0, n, 2))
        z = list(range(1, n, 2))
        # Old left constraints are I_d, so L=0. New constraints vanish.
        need([[a[i][j] for i in f] for j in z] == eye(d), "old zero module")
        need(all(not b[j][i] for j in z for i in f), "old full right module")
        t, ti = word(n, [(dst, src, -c) for dst, src, c in operations])
        aa, bb = mm(t, a), mm(b, ti)
        need(aa == bb == eye(n), "attaining paired edits")
        need([[sum(aa[i][k] * bb[k][j] for k in range(n))
               for j in f] for i in f] == eye(d), "attaining full unit block")
        for values in product((-1, 0, 1), repeat=n):
            state = list(values)
            inverse = [(dst, src, -c) for dst, src, c in reversed(operations)]
            for dst, src, c in operations + inverse:
                state[dst] += c * state[src]
            need(state == list(values), "attaining cut value")
            for dst, src, c in operations + inverse:
                state[dst] += c * state[src]
            need(state == list(values), "four-pass dirty restoration")
            cases += 1
    return cases


def controls():
    bad = [(1, 0, 0, 1), (2, 0, 0, 1), (2, -1, 1, 1),
           (2, 0, 1, 0), (2, 0, 1, Q(1, 3)), (9, 0, 1, 1)]
    for args in bad:
        try:
            add_matrix(*args)
        except ValueError:
            continue
        raise ValueError("invalid ADD accepted")
    need(capacity([[21]]) == 0 and capacity([[Q(1, 4)]]) == 1, "unit status")
    need(capacity([[3, 0], [0, 5]]) == 1, "joint unit without unit entry")
    need(kernel([[6, 10, 15]], 3) == [[5, -3, 0], [-30, 15, 2]],
         "full rank-two integer kernel")
    a, b = word(2, [(0, 1, 1)])
    need(cut_data(a, b, [0], [0]) == 0, "old sharpness capacity")
    need(cut_data(eye(2), eye(2), [0], [0]) == 1, "zero-change mutant rejects")
    t = add_matrix(2, 0, 1, -1)
    need(mm(mm(b, t), mm(t, a)) != eye(2), "wrong inverse sign rejects")
    return len(bad) + 6


def source_hashes():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    hashes = {}
    for row in pins["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            need(path.stat().st_size <= 1024 * 1024, "source size")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            need(digest == row["sha256"], "source hash: " + row["path"])
            hashes[row["path"]] = digest
    for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"):
        path = HERE / name
        need(path.stat().st_size <= 1024 * 1024, "package file size")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def main():
    hashes = source_hashes()
    result = screen()
    result["dirty_states"] = sharpness()
    result["controls"] = controls()
    result["status"] = "PASS_PAIRED_PREFIX_CUT_CAPACITY"
    result["file_sha256"] = hashes
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
