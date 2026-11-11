"""Exact first central-key collision; standard library, no output files."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def eye(n: int) -> list[list[int]]:
    return [[int(i == j) for j in range(n)] for i in range(n)]


def add(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    return [[x ^ y for x, y in zip(ar, br, strict=True)]
            for ar, br in zip(a, b, strict=True)]


def mul(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    columns = tuple(zip(*b, strict=True))
    return [[sum(x * y for x, y in zip(row, col, strict=True)) % 2
             for col in columns] for row in a]


def echelon(a: list[list[int]]) -> tuple[list[list[int]], list[int]]:
    rows = [row[:] for row in a]
    pivots: list[int] = []
    for col in range(len(rows[0])):
        pivot = next((i for i in range(len(pivots), len(rows))
                      if rows[i][col]), None)
        if pivot is None:
            continue
        target = len(pivots)
        rows[target], rows[pivot] = rows[pivot], rows[target]
        for i in range(len(rows)):
            if i != target and rows[i][col]:
                rows[i] = [x ^ y for x, y in
                           zip(rows[i], rows[target], strict=True)]
        pivots.append(col)
        if len(pivots) == len(rows):
            break
    return rows, pivots


def rank(a: list[list[int]]) -> int:
    return len(echelon(a)[1])


def inverse(a: list[list[int]]) -> list[list[int]]:
    n = len(a)
    require(all(len(row) == n for row in a), "nonsquare matrix")
    reduced, pivots = echelon([row + unit for row, unit in
                               zip(a, eye(n), strict=True)])
    require(pivots[:n] == list(range(n)), "singular matrix")
    return [row[n:] for row in reduced]


def jordan(partition: tuple[int, ...]) -> tuple[list[list[int]], list[int]]:
    require(bool(partition) and all(k > 0 for k in partition), "bad partition")
    require(sum(partition) <= 8, "fixture dimension bound")
    n = sum(partition)
    h = [[0] * n for _ in range(n)]
    bottoms: list[int] = []
    offset = 0
    for length in partition:
        bottoms.append(offset)
        for i in range(offset, offset + length - 1):
            h[i][i + 1] = 1
        offset += length
    return h, bottoms


def canonical_pair(partition: tuple[int, ...]) -> tuple[list[list[int]], list[list[int]]]:
    h, bottoms = jordan(partition)
    d, a = len(h), len(bottoms)
    n = 3 * d + a
    w = add(eye(d), h)
    tops = [bottom + length - 1 for bottom, length in
            zip(bottoms, partition, strict=True)]
    s, t = [[0] * n for _ in range(n)], [[0] * n for _ in range(n)]
    for i, j in itertools.product(range(d), repeat=2):
        s[i][j] = s[i][2 * d + j] = h[i][j]
        s[2 * d + i][j] = s[2 * d + i][2 * d + j] = w[i][j]
        t[d + i][d + j] = t[d + i][2 * d + j] = h[i][j]
        t[2 * d + i][d + j] = t[2 * d + i][2 * d + j] = w[i][j]
    for i, top in enumerate(tops):
        for matrix, row in ((s, top), (t, d + top),
                            (s, 2 * d + top), (t, 2 * d + top)):
            matrix[row][3 * d + i] = 1
        s[3 * d + i][3 * d + i] = t[3 * d + i][3 * d + i] = 1
    return s, t


def literal_header(partition: tuple[int, ...]) -> tuple[list[list[int]], list[list[int]], dict]:
    h, bottoms = jordan(partition)
    d, a = len(h), len(bottoms)
    n, m = 4 * d + a, 3 * d + a
    w = add(eye(d), h)
    iota = eye(d) * 3 + h + [[int(j == b) for j in range(d)] for b in bottoms]
    pi = [w[i] * 3 + eye(d)[i] + [0] * a for i in range(d)]
    basis = [[int(i == j) for j in range(m)] for i in range(3 * d)]
    basis += [w[i] * 3 + [0] * a for i in range(d)]
    basis += [[0] * (3 * d) + [int(i == j) for j in range(a)] for i in range(a)]
    header = [x + y for x, y in zip(iota, basis, strict=True)]
    inv = inverse(header)
    pdiag = [0] * d + [1] * d + [0] * d + [1] * (d + a)
    qdiag = [0] * (2 * d) + [1] * (2 * d + a)
    p = mul(inv, [[v * x for x in row] for v, row in zip(pdiag, header, strict=True)])
    q = mul(inv, [[v * x for x in row] for v, row in zip(qdiag, header, strict=True)])
    require(mul(pi, iota) == eye(d), "split identity")
    require(mul(p, p) == p and mul(q, q) == q, "full idempotents")
    require(mul(p, q) == mul(q, p), "full commutation")
    require([row[:d] for row in p[:d]] == eye(d), "P pivot")
    require([row[:d] for row in q[:d]] == eye(d), "Q pivot")
    require([row[:d] for row in mul(p, q)[:d]] == h, "compressed product")
    residuals = []
    for matrix in (p, q):
        correction = mul([row[:d] for row in matrix[d:]], [row[d:] for row in matrix[:d]])
        residuals.append(add([row[d:] for row in matrix[d:]], correction))
    return residuals[0], residuals[1], {"ambient": n, "residual": m, "sectors": [d, d, d, d + a]}


def power_ranks(matrix: list[list[int]]) -> list[int]:
    power, result = eye(len(matrix)), []
    for _ in range(8):
        power = mul(power, matrix)
        result.append(rank(power))
    return result


def square_zero_basis(z: list[list[int]]) -> list[list[int]]:
    n = len(z)
    require(mul(z, z) == [[0] * n for _ in range(n)], "not square zero")
    columns = [list(col) for col in zip(*z, strict=True)]
    chosen: list[list[int]] = []
    for j in echelon(z)[1]:
        chosen += [columns[j], eye(n)[j]]
    reduced, pivots = echelon(z)
    for free in range(n):
        if free in pivots:
            continue
        vector = [int(i == free) for i in range(n)]
        for row, pivot in zip(reduced, pivots):
            vector[pivot] = row[free]
        trial = [list(col) for col in zip(*(chosen + [vector]), strict=True)]
        if rank(trial) > len(chosen):
            chosen.append(vector)
    require(len(chosen) == n, "incomplete Jordan basis")
    return [list(row) for row in zip(*chosen, strict=True)]


def partitions(n: int) -> list[tuple[int, ...]]:
    require(1 <= n <= 4, "partition domain")
    result = []
    for length in range(1, n + 1):
        for parts in itertools.combinations_with_replacement(range(1, n + 1), length):
            if sum(parts) == n:
                result.append(tuple(reversed(parts)))
    return sorted(result, reverse=True)


def check_collision() -> dict:
    fixtures = []
    for partition in ((3, 1), (2, 2)):
        s, t, metadata = literal_header(partition)
        require(mul(s, s) == s and mul(t, t) == t, "residual idempotents")
        require(rank(add(mul(s, t), mul(t, s))) == 8, "not sharp")
        k = add(s, t)
        z = mul(k, k)
        kranks, zranks = power_ranks(k), power_ranks(z)
        cs, ct = canonical_pair(partition)
        require(power_ranks(add(cs, ct)) == kranks, "canonical/literal mismatch")
        require(zranks == [4] + [0] * 7, "central partition")
        fixtures.append((s, t, z, kranks, metadata))
    require(fixtures[0][3] == [8, 4, 2] + [0] * 5, "first pair separator")
    require(fixtures[1][3] == [8, 4] + [0] * 6, "second pair separator")
    b0, b1 = [square_zero_basis(f[2]) for f in fixtures]
    g = mul(b0, inverse(b1))
    require(rank(g) == 14 and mul(fixtures[0][2], g) == mul(g, fixtures[1][2]), "central intertwiner")
    return {"fixtures": [{"partition": p, "S": f[0], "T": f[1], "K_ranks": f[3], **f[4]}
                         for p, f in zip(((3, 1), (2, 2)), fixtures, strict=True)], "central_intertwiner": g}


def check_minimality() -> dict:
    collisions, comparisons, total = [], 0, 0
    for d in range(1, 5):
        data = partitions(d)
        total += len(data)
        for left, right in itertools.combinations(data, 2):
            comparisons += 1
            odd = lambda p: tuple(sum(max(k - j, 0) for k in p) for j in (1, 3, 5, 7))
            if odd(left) == odd(right):
                collisions.append([left, right])
    require(collisions == [[(3, 1), (2, 2)]], "unexpected first collision")
    return {"partitions": total, "comparisons": comparisons, "collisions": collisions}


def check_controls() -> int:
    rejected = 0
    for operation in (lambda: jordan(()), lambda: jordan((0,)),
                      lambda: jordan((9,)), lambda: partitions(0),
                      lambda: inverse([[0, 0], [0, 0]]),
                      lambda: square_zero_basis(eye(2))):
        try:
            operation()
        except ValueError:
            rejected += 1
    require(rejected == 6, "missing input/control rejection")
    s, t = canonical_pair((4,))
    require(power_ranks(mul(add(s, t), add(s, t)))[0] == 6, "distinct central control")
    s, t = canonical_pair((3, 1))
    require(power_ranks(add(s, t))[2] != 0, "central-only equivalence control")
    return rejected + 2


def main() -> None:
    scientific = {"collision": check_collision(), "minimality": check_minimality(),
                  "controls": check_controls()}
    payload = json.dumps(scientific, sort_keys=True, separators=(",", ":")).encode()
    package = Path(__file__).resolve().parent
    source_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in sorted(package.iterdir()) if p.is_file()}
    receipt = {"status": "PASS_SCHUR_CENTRAL_ALIAS", "evidence_sha256": hashlib.sha256(payload).hexdigest(),
               "source_sha256": source_hashes, "minimality": scientific["minimality"],
               "controls": scientific["controls"], "K_ranks": [x["K_ranks"] for x in scientific["collision"]["fixtures"]]}
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
