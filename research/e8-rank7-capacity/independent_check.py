"""Independent dot-kernel census and norm reconstruction. Apache-2.0."""

import ast
import json
import runpy
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
helpers = runpy.run_path(str(PACKAGE / "verify.py"))
require = helpers["require"]


def invert(matrix):
    require(
        len(matrix) == 8 and all(len(row) == 8 for row in matrix), "eight-square matrix"
    )
    rows = [
        [Fraction(x) for x in row] + [Fraction(i == j) for j in range(8)]
        for i, row in enumerate(matrix)
    ]
    for j in range(8):
        pivot = next(i for i in range(j, 8) if rows[i][j])
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = rows[j][j]
        rows[j] = [x / scale for x in rows[j]]
        for i in range(8):
            if i != j:
                scale = rows[i][j]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[j], strict=True)]
    return [row[8:] for row in rows]


def norm_model():
    raw = helpers["authenticate"]()
    tree = ast.parse(raw)
    simple = ast.literal_eval(
        next(
            node.value
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "SIMPLE" for t in node.targets)
        )
    )
    require(type(simple) is tuple and len(simple) == 8, "simple-root literal")
    inverse = invert(list(zip(*simple, strict=True)))
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-2, 2):
            row = [0] * 8
            row[i], row[j] = 2, sign
            roots.append(tuple(row))
    roots.extend(
        row
        for row in product((-1, 1), repeat=8)
        if row[0] == 1 and sum(x < 0 for x in row) % 2 == 0
    )
    require(len(roots) == 120, "independent root-line inventory")
    frame = {
        tuple(2 if j == i else sign if j == i + 1 else 0 for j in range(8))
        for i in range(0, 8, 2)
        for sign in (-2, 2)
    }
    residues, live = set(), set()
    for root in roots:
        c = [sum(a * b for a, b in zip(row, root, strict=True)) for row in inverse]
        require(all(x.denominator == 1 for x in c), "integral root coordinates")
        residue = sum((int(x) % 2) << i for i, x in enumerate(c))
        residues.add(residue)
        if root not in frame:
            live.add(residue)
    q = []
    for x in range(256):
        vector = [sum(simple[i][j] for i in range(8) if x >> i & 1) for j in range(8)]
        norm = sum(a * a for a in vector)
        require(norm % 8 == 0, "even-lattice norm")
        q.append(norm // 8 % 2)
    require(
        residues == {i for i, value in enumerate(q) if value} and len(live) == 112,
        "independent quadratic/root/frame binding",
    )
    return q, live


def dual_vector(normal, polar):
    candidates = [
        x
        for x in range(256)
        if all(
            ((normal >> j) & 1)
            == (sum((polar[i] >> j) & 1 for i in range(8) if x >> i & 1) % 2)
            for j in range(8)
        )
    ]
    require(len(candidates) == 1, "nondegenerate dual identification")
    return candidates[0]


def compute():
    q, live = norm_model()
    polar = [
        [q[(1 << i) ^ (1 << j)] ^ q[1 << i] ^ q[1 << j] for j in range(8)]
        for i in range(8)
    ]
    packed = [sum(v << j for j, v in enumerate(row)) for row in polar]
    dual = [dual_vector(n, packed) for n in range(256)]
    histogram, equalities = Counter(), []
    # RREF normals: leading low pivots; this enumerates each ordinary-dot
    # annihilator once, independently of the primary unordered polar planes.
    for i, j in combinations(range(8), 2):
        free_a = [k for k in range(i + 1, 8) if k != j]
        free_b = list(range(j + 1, 8))
        for code_a in range(1 << len(free_a)):
            a = (1 << i) | sum(((code_a >> k) & 1) << v for k, v in enumerate(free_a))
            for code_b in range(1 << len(free_b)):
                b = (1 << j) | sum(
                    ((code_b >> k) & 1) << v for k, v in enumerate(free_b)
                )
                sections = [[] for _ in range(4)]
                for x in range(256):
                    if q[x]:
                        sections[
                            (a & x).bit_count() % 2 + 2 * ((b & x).bit_count() % 2)
                        ].append(x)
                polar_type = q[dual[a] ^ dual[b]] ^ q[dual[a]] ^ q[dual[b]]
                for support in sections:
                    surviving = [x for x in support if x in live]
                    histogram[(polar_type, len(support), len(surviving))] += 1
                    if len(support) == 36:
                        equalities.append(tuple(1 | x << 1 for x in support))
    serial = json.dumps(sorted(equalities), separators=(",", ":")).encode()
    return histogram, sha256(serial).hexdigest()


def main():
    histogram, digest = compute()
    expected = json.loads((PACKAGE / "RESULT.json").read_text())
    rows = [[*key, count] for key, count in sorted(histogram.items())]
    require(rows == expected["histogram"], "independent full section histogram")
    require(
        digest == expected["full_equality_supports_sha256"],
        "independent equality supports",
    )
    require(
        sum(histogram.values()) == 43180
        and max(k[1] for k in histogram) == 36
        and sum(n for k, n in histogram.items() if k[2] == 36) == 448,
        "independent capacity and equality",
    )
    print("PASS_INDEPENDENT_E8_RANK7 affine_sections=43180 fixed_frame_equality=448")


if __name__ == "__main__":
    main()
