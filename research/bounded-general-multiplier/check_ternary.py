"""Check the changed cover on its native inputs and independent full-ring examples."""

from collections import Counter
from fractions import Fraction
from functools import cache
from hashlib import sha256
from itertools import product
from math import lcm
from pathlib import Path
from random import Random
import gzip
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ternary_frames import (
    covered_factors, frame_at_three, identity, inverse, matcher, multiply, native_factors,
    projector, residue, split, transpose,
)
from ternary_leaf import lower_coefficient, lower_slot, ordered_chart, run_leaf, select_pivot
from factored_frames import Frame, apply_row, inverse_word, move_cover

VENDOR = Path(__file__).resolve().parent / "vendor"
sys.path.insert(0, str(VENDOR))
from leaf import good_column
from cover import cold_swap, high_stream, low_action, row_program


def checked_file(path, digest):
    data = (VENDOR / path).read_bytes()
    assert sha256(data).hexdigest() == digest, path
    return data


def determinant(matrix):
    rows = [list(map(Fraction, row)) for row in matrix]
    d = 1
    for j in range(len(rows)):
        p = next(i for i in range(j, len(rows)) if rows[i][j])
        if p != j:
            rows[p], rows[j] = rows[j], rows[p]
            d = -d
        pivot = rows[j][j]
        d *= pivot
        for i in range(j + 1, len(rows)):
            scale = rows[i][j] / pivot
            if scale:
                rows[i][j:] = [a - scale * b for a, b in zip(rows[i][j:], rows[j][j:], strict=True)]
    return d


def height(counter, label, mat):
    entries = [Fraction(x) for row in mat for x in row]
    a, b = counter.get(label, (0, 1))
    counter[label] = max(a, *(abs(x.numerator) for x in entries)), max(b, *(x.denominator for x in entries))


def scaled(matrix):
    denominator = lcm(*(Fraction(x).denominator for row in matrix for x in row))
    return [[int(x * denominator) for x in row] for row in matrix], denominator


def native():
    for name, digest in (
        ("cover.py", "52cfdb73f0289b1d2fd015865104dc66ecb7478eef2dbe3d48325791cea7b786"),
        ("leaf.py", "a91655fd1f1429961ee1db4698b7f3f2ce091e2d94e775dc63f02c9eb8db6c64"),
        ("retained/fallback.py", "c3c516a9b1541608b271acb9a782573d57f3e9a87ae97ca0c224e79b27d0a003"),
    ):
        checked_file(name, digest)
    word = json.loads(gzip.decompress(checked_file(
        "binary.json.gz", "d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9"
    )))
    root = json.loads(gzip.decompress(checked_file(
        "EFREE-CALLER.json.gz", "757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b"
    )))
    frames = word["frames"]
    mats, denominators, ranks = {}, {}, {}
    frame_dets, port_dets, heights = Counter(), Counter(), {}
    raw_route = Counter()

    def raw_factor(matrix):
        program = row_program(matrix, 3)
        raw_route["longest word"] = max(raw_route["longest word"], len(program))
        for op, *args in program:
            if op in ("scale", "add"):
                a = Fraction(args[-1])
                assert abs(a.numerator) <= 20 and a.denominator <= 20
                raw_route[op + " numerator"] = max(raw_route[op + " numerator"], abs(a.numerator))
                raw_route[op + " denominator"] = max(raw_route[op + " denominator"], a.denominator)

    for raw_key, desc in frames.items():
        key = int(raw_key)
        basis = transpose(desc["B"] + desc["A"])
        r = desc["dim"]
        assert len(desc["B"]) == r and len(basis) == 8
        frame_dets[abs(int(determinant(basis)))] += 1
        height(heights, "frame", basis)
        height(heights, "inverse frame", inverse(basis))
        p = projector(basis, r)
        height(heights, "projector", p)
        certified, rank = frame_at_three(p)
        assert r == rank and projector(certified, rank) == p
        raw_factor(basis)
        raw_factor(certified)
        mats[key], denominators[key] = scaled(p)
        ranks[key] = r

    @cache
    def difference(a, b):
        if ranks[a] > ranks[b]:
            return difference(b, a)
        x, y, d, e = mats[a], mats[b], denominators[a], denominators[b]
        assert ranks[a] < ranks[b]
        assert multiply(x, y) == multiply(y, x) == [[e * z for z in row] for row in x]
        diff = [[Fraction(s, e) - Fraction(t, d) for s, t in zip(row, sub, strict=True)]
                for row, sub in zip(y, x, strict=True)]
        height(heights, "native difference", diff)
        frame, rank = frame_at_three(diff)
        assert rank == ranks[b] - ranks[a]
        raw_factor(frame)
        return rank

    legs = [(a, b) for op, _, a, b in (e for e in word["program"] if e[0] == "MOVE")]
    helpers = list(zip(word["start"][222:], word["final"][222:], strict=True))
    for a, b in legs + helpers:
        difference(a, b)
    for i in range(111):
        h, body = word["start"][i], word["final"][i + 111]
        basis = transpose(frames[str(h)]["B"] + frames[str(body)]["B"])
        port_dets[abs(int(determinant(basis)))] += 1
        height(heights, "port", basis)
        height(heights, "inverse port", inverse(basis))
        raw_factor(basis)
        assert ranks[h] == 1 and ranks[body] == 7 and len(basis) == 8
        assert projector(basis, 1) == [[Fraction(x, denominators[h]) for x in row] for row in mats[h]]
    assert frame_dets == {1: 28, 4: 326, 16: 250, 64: 32} and port_dets == {1: 8, 4: 103}
    flags = Counter(e[0] for e in root["events"])
    assert flags == {"SWAP": 364, "ADD": 362, "LOCAL": 36, "IDLE_ONE": 32, "QUERY": 4}
    assert root["ambient_rank"] == 127 and root["body_rank"] == 7 and root["stages"] == 18
    assert sorted(e[1] for e in root["events"] if e[0] == "LOCAL") == sorted(list(range(1, 19)) * 2)
    print("raw frames", sorted(frame_dets.items()), "ports", sorted(port_dets.items()))
    print("raw heights (maximum absolute numerator, maximum denominator)", sorted(heights.items()))
    print("raw eight-axis frame/port factor programs", sorted(raw_route.items()))
    print("native MOVE and helper occurrences", len(legs), len(helpers),
          "distinct unordered pairs", len({tuple(sorted(x)) for x in legs + helpers}))
    print("priced root", root["roles"], "logical axes", root["ambient_rank"], "physical axes", 8 + 7 * 18,
          sorted(flags.items()), "port-stage routes", 111 * 18)
    return word, mats, denominators


def check_frames(rng):
    for n in (2, 3, 4, 6):
        for r in range(1, n):
            f = identity(n)
            for _ in range(4 * n):
                i, j = rng.sample(range(n), 2)
                scale = Fraction(rng.randrange(-6, 7), rng.choice((1, 2, 4, 5, 7)))
                f[i] = [x + scale * y for x, y in zip(f[i], f[j], strict=True)]
            p, t = projector(f, r), projector(identity(n), r)
            m = matcher(p, t)
            assert multiply(p, m) == multiply(m, t)
            assert residue(determinant(m), 3)
            if r > 1:
                left, right = split(p, r - 1)
                assert multiply(left, right) == multiply(right, left) == [[0] * n for _ in range(n)]
                assert multiply(left, left) == left and multiply(right, right) == right
                assert frame_at_three(left)[1] == r - 1 and frame_at_three(right)[1] == 1


def check_cover():
    """Run the retained physical right route with the new frame convention."""
    p = projector([[1, Fraction(1, 2)], [1, 1]], 1)
    target = projector([[0, 1], [1, 0]], 1)
    m = matcher(p, target)
    charts = [frame_at_three(z) for z in (p, target)]
    s = Frame(2, row_program(charts[0][0], 3), (0,)).matcher_to(
        Frame(2, row_program(charts[1][0], 3), (0,))
    )
    assert multiply(p, m) == multiply(m, target)
    groups, records = 0, 0
    for a, b, c, d in product(range(3), repeat=4):
        if (a * d - b * c) % 3:
            low = [[a, b], [c, d]]
            out, carry = low_action(low, m, 3)
            back, back_carry = low_action(out, inverse(m), 3)
            assert back == low
            for w in ((1, 2, 3) if low == [[1, 0], [0, 1]] else (1, 2)):
                side = 3 ** (w - 1)
                data = list(range(side**4))
                moved = high_stream(data, m, 3, w, carry)
                assert high_stream(moved, inverse(m), 3, w, back_carry) == data
                factor_low, factor_data = move_cover(data, low, s, w)
                assert factor_low == out and factor_data == moved
                assert move_cover(factor_data, factor_low, tuple(inverse_word(s)), w) == (low, data)
                for i, xs in enumerate(product(range(side), repeat=4)):
                    g = [[low[j][k] + 3 * xs[2 * j + k] for k in range(2)] for j in range(2)]
                    actual = multiply(g, m)
                    addr = 0
                    for j in range(2):
                        for k in range(2):
                            entry = residue(actual[j][k], 3**w)
                            assert out[j][k] == entry % 3
                            addr = addr * side + entry // 3
                    assert moved[addr] == i
                groups += 1
                records += len(data)
    cold_records = 0
    for w in range(1, 5):
        extent = 3**w
        for prefix, gap, suffix in ((1, 1, 1), (2, 3, 2)):
            total = prefix * extent * gap * extent * suffix
            source = list(range(total))
            moved = cold_swap(source, 3, w, prefix, gap, suffix)
            for i, actual in enumerate(moved):
                q, s = divmod(i, suffix)
                q, x = divmod(q, extent)
                q, g = divmod(q, gap)
                p, y = divmod(q, extent)
                assert actual == (((p * extent + x) * gap + g) * extent + y) * suffix + s
            cold_records += total
    print("complete affine cover cases and records", groups, records, "cold records", cold_records)


def check_factored(rng):
    """Compare source, product, partial block, physical matcher and covered leaf."""
    f = [[1, Fraction(1, 2)], [1, 1]]
    g = [[1, 0, -1], [Fraction(1, 2), 1, 0], [1, 0, 1]]
    a = Frame(2, row_program(f, 3), (0,))
    b = Frame(3, row_program(g, 3), (0, 1))
    ab = a.tensor(b)
    h = [[f[i // 3][j // 3] * g[i % 3][j % 3] for j in range(6)] for i in range(6)]
    axes = (5, 1, 7, 3, 4, 0)
    parts = ab.embed(8, axes).parts(1)
    s = parts[0].matcher_to(parts[1])
    count = 0
    for digits in (1, 2, 3):
        m = 3**digits
        for _ in range(24):
            x = [rng.randrange(m) for _ in range(8)]
            want = [residue(y, m) for y in multiply([x[:6]], h)[0]]
            assert apply_row(ab.word, x[:6], m) == want
            assert apply_row(tuple(inverse_word(ab.word)), want, m) == x[:6]
            p, q = parts
            assert apply_row(s, p.project(x, m), m) == q.project(apply_row(s, x, m), m)
            total = ab.embed(8, axes).project(x, m)
            assert [(l + r) % m for l, r in zip(p.project(x, m), q.project(x, m), strict=True)] == total
            assert [(l + r) % m for l, r in zip(p.project(x, m), p.complement().project(x, m), strict=True)] == x
            low = identity(8)
            for _ in range(20):
                i, j = rng.sample(range(8), 2)
                coeff = rng.randrange(m)
                low[i] = [(v + coeff * w) % m for v, w in zip(low[i], low[j], strict=True)]
            u, v = q.covered_line(low, digits)
            prod = multiply([x], low)[0]
            after = q.project(prod, m)
            lhs = sum(t * z for t, z in zip(x, u, strict=True)) % m
            assert [(lhs * sum(v[i] * low[i][j] for i in range(8))) % m for j in range(8)] == after
            count += 1
    print("factored tensor, mask, route, terminal checks", count)


def reference(u, v, weights, head, tail, modulus):
    n, width = len(u), len(weights)
    h, t = [row.copy() for row in head], [row.copy() for row in tail]
    for j, a in enumerate(weights):
        x = [pow(a[i], -1, modulus) * head[i][j] for i in range(n)]
        y = [tail[n - 1 - i][width - 1 - j] for i in range(n)]
        delta = sum(c * (r - l) for c, r, l in zip(v, y, x, strict=True))
        for i in range(n):
            h[i][j] = (head[i][j] + a[i] * u[i] * delta) % modulus
            t[n - 1 - i][width - 1 - j] = (y[i] - u[i] * delta) % modulus
    return h + t


def check_leaves(rng, word, matrices, denominators):
    counts = Counter()
    dense_checks = 0

    def check(u, v, digits, width, dense=False):
        nonlocal dense_checks
        n, modulus = len(u), 3**digits
        units = [a for a in range(modulus) if a % 3]
        weights = [[rng.choice(units) for _ in range(n)] for _ in range(width)]
        head = [[rng.randrange(modulus) for _ in range(width)] for _ in range(n)]
        tail = [[rng.randrange(modulus) for _ in range(width)] for _ in range(n)]
        got, calls = run_leaf(u, v, weights, head, tail, digits)
        expected = reference(u, v, weights, head, tail, modulus)
        pivot = select_pivot(u, v)
        assert got == expected and calls == (width,) * (0 if not width else 9 if pivot else 1)
        counts[digits, len(calls)] += 1
        if dense and width:
            order, b, c = ordered_chart(u, v, pivot, modulus)
            a = [weights[0][i] for i in order]
            p = [[x * y % modulus for y in c] for x in b]
            prior = good_column(p, a, modulus)
            middle = (len(prior) - 1) // 2
            assert prior[middle] == ["weighted_swap", 0, 2 * n - 1, a[0] * c[0] % modulus]
            reduced = list(prior[:middle])
            assert reduced.pop(3 * (n - 1)) == ["lower", 2 * n - 1, 0, 0]
            for s, op in enumerate(reduced):
                dst, src, i = lower_slot(n, s)
                coeff = lower_coefficient(s // (n - 1), i, b, c, a[0], a[i], pow(c[0], -1, modulus), modulus)
                assert op == ["lower", dst, src, coeff]
            dense_checks += 1

    for digits in (1, 2):
        modulus = 3**digits
        for u in product(range(modulus), repeat=2):
            for v in product(range(modulus), repeat=2):
                if sum(x * y for x, y in zip(u, v, strict=True)) % modulus == 1:
                    check(u, v, digits, 1 + (sum(u) + sum(v)) % 4, True)
    for n in (1, 3, 4, 7):
        for digits in (1, 2, 3, 4):
            modulus = 3**digits
            for k in range(25):
                while True:
                    u, v = ([rng.randrange(modulus) for _ in range(n)] for _ in range(2))
                    d = sum(x * y for x, y in zip(u, v, strict=True))
                    if d % 3:
                        break
                v = [x * pow(d, -1, modulus) % modulus for x in v]
                check(u, v, digits, k % 6, k < 4)
    _, _, a, b = word["program"][12]
    p = [[Fraction(x, denominators[b]) - Fraction(y, denominators[a])
          for x, y in zip(r, s, strict=True)] for r, s in zip(matrices[b], matrices[a], strict=True)]
    assert word["program"][12] == ["MOVE", 683, 2, 125]
    native = native_factors(p)
    histogram = Counter()
    for digits in (1, 2, 3):
        modulus = 3**digits
        for k in range(48):
            g = identity(8)
            for _ in range(40):
                i, j = rng.sample(range(8), 2)
                value = rng.randrange(modulus)
                g[i] = [(x + value * y) % modulus for x, y in zip(g[i], g[j], strict=True)]
            u, v = covered_factors(native, g, digits)
            assert all((sum(v[i] * g[i][j] for i in range(8)) - residue(native[1][j], modulus)) % modulus == 0 for j in range(8))
            assert sum(x * y for x, y in zip(u, v, strict=True)) % modulus == 1
            check(u, v, digits, 1 + k % 5, k % 8 == 0)
            histogram[int(bool(select_pivot(u, v)))] += 1
    assert all(histogram[i] > 0 for i in (0, 1))
    print("full-ring physical cases", sum(counts.values()), "nonleading pivots", sum(v for (_, c), v in counts.items() if c == 9),
          "dense precursor word comparisons", dense_checks)
    print("native covered MOVE by leading/nonleading pivot", sorted(histogram.items()))


if __name__ == "__main__":
    random = Random(784603)
    word, mats, denoms = native()
    check_frames(random)
    check_cover()
    check_factored(Random(85201))
    check_leaves(random, word, mats, denoms)
    print("PASS_TERNARY_NATIVE_COVER")
