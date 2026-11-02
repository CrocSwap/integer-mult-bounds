"""Exact finite corroboration of the vector-cocycle register-word theorem."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path


P = 3
D = 2
IDENTITY = ((1, 0), (0, 1))
ZERO = (0, 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    require(1 <= n <= 21, "matrix capacity")
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def multiply(a, b):
    require(1 <= len(a) <= 21 and len(a[0]) == len(b), "product shape")
    require(1 <= len(b[0]) <= 21, "product capacity")
    return tuple(tuple(sum(x * y for x, y in zip(row, col)) % P
                       for col in zip(*b)) for row in a)


def rank(a):
    require(1 <= len(a) <= 21 and 1 <= len(a[0]) <= 21, "rank capacity")
    rows = [list(row) for row in a]
    pivot = 0
    for col in range(len(rows[0])):
        chosen = next((i for i in range(pivot, len(rows)) if rows[i][col]), None)
        if chosen is None:
            continue
        rows[pivot], rows[chosen] = rows[chosen], rows[pivot]
        scale = pow(rows[pivot][col], -1, P)
        rows[pivot] = [(scale * x) % P for x in rows[pivot]]
        for i in range(pivot + 1, len(rows)):
            scale = rows[i][col]
            rows[i] = [(x - scale * y) % P
                       for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def action(h, v):
    return tuple(sum(h[i][j] * v[j] for j in range(D)) % P for i in range(D))


def group_product(g, k):
    v, h = g
    w, j = k
    hw = action(h, w)
    return tuple((v[i] + hw[i]) % P for i in range(D)), multiply(h, j)


def group_inverse(g):
    v, h = g
    a, b = h[0]
    c, d = h[1]
    inverse = ((d % P, -b % P), (-c % P, a % P))
    hv = action(inverse, v)
    return tuple(-x % P for x in hv), inverse


def affine(g):
    v, h = g
    return tuple(tuple(h[i][j] for j in range(D)) + (v[i],)
                 for i in range(D)) + ((0, 0, 1),)


def groups():
    matrices = []
    for a, b, c, d in itertools.product(range(P), repeat=4):
        if (a * d - b * c) % P == 1:
            matrices.append(((a, b), (c, d)))
    vectors = tuple(itertools.product(range(P), repeat=D))
    return tuple((v, h) for v in vectors for h in matrices)


def projectors(r):
    require(1 <= r <= 3, "projector enumeration capacity")
    vectors = tuple(itertools.product(range(P), repeat=r))
    output = set()
    for x in vectors:
        for y in vectors:
            if sum(a * b for a, b in zip(x, y)) % P == 1:
                output.add(tuple(tuple(a * b % P for b in y) for a in x))
    return tuple(sorted(output))


def call_matrix(n, g):
    r = len(n)
    require(1 <= r <= 7, "call role capacity")
    require(multiply(n, n) == n and rank(n) == 1, "not a rank-one idempotent")
    rho = affine(g)
    size = r * (D + 1)
    return tuple(tuple((int(i == j) + n[i // 3][j // 3]
                        * (rho[i % 3][j % 3] - int(i % 3 == j % 3))) % P
                       for j in range(size)) for i in range(size))


def defect(a, r):
    require(len(a) == 3 * r, "defect shape")
    return tuple(tuple(a[3 * i + k][3 * j + 2] for j in range(r))
                 for i in range(r) for k in range(D))


def group_checks(group):
    cases = 0
    elements = set(group)
    for g in group:
        require(group_product(g, group_inverse(g)) == (ZERO, IDENTITY), "inverse")
        for k in group:
            result = group_product(g, k)
            require(result in elements, "group closure")
            require(affine(result) == multiply(affine(g), affine(k)), "affine law")
            v, h = g
            w, _ = k
            expected = tuple((v[i] + action(h, w)[i]) % P for i in range(D))
            require(result[0] == expected, "crossed homomorphism")
            cases += 1
    return cases


def call_checks(group):
    counts = []
    cases = 0
    for r in range(1, 4):
        alphabet = projectors(r)
        counts.append(len(alphabet))
        for n in alphabet:
            for g in group:
                matrix = call_matrix(n, g)
                require(rank(defect(matrix, r)) == int(g[0] != ZERO), "call rank")
                inverse = call_matrix(n, group_inverse(g))
                require(multiply(matrix, inverse) == eye(3 * r), "call inverse")
                cases += 1
    return counts, cases


def formal_identity(r):
    return {(i, i, (ZERO, IDENTITY)): 1 for i in range(r)}


def formal_right_call(word, n, g):
    r = len(n)
    require(len(word) <= 7 * 7 * 216, "formal support capacity")
    result = dict(word)
    for (i, j, label), value in word.items():
        for k in range(r):
            for term, sign in ((group_product(label, g), 1), (label, -1)):
                key = i, k, term
                result[key] = (result.get(key, 0) + sign * value * n[j][k]) % P
    return {key: value for key, value in result.items() if value}


def formal_image(word, r):
    matrix = [[0] * (3 * r) for _ in range(3 * r)]
    for (i, j, g), value in word.items():
        rho = affine(g)
        for u in range(3):
            for v in range(3):
                matrix[3 * i + u][3 * j + v] += value * rho[u][v]
    return tuple(tuple(x % P for x in row) for row in matrix)


def scalar_matrix(s):
    r = len(s)
    return tuple(tuple(s[i // 3][j // 3] * int(i % 3 == j % 3)
                       for j in range(3 * r)) for i in range(3 * r))


def formal_right_scalar(word, s):
    result = {}
    for (i, j, label), value in word.items():
        for k in range(len(s)):
            key = i, k, label
            result[key] = (result.get(key, 0) + value * s[j][k]) % P
    return {key: value for key, value in result.items() if value}


def word_checks(group):
    cases = 0
    words = 0
    strict_cases = 0
    for r in range(2, 6):
        for trial in range(18):
            image = eye(3 * r)
            word = formal_identity(r)
            charged = 0
            for step in range(1 + trial % 6):
                x = tuple(int(i == (step + trial) % r) for i in range(r))
                y = tuple((1 if x[i] else (trial + i + step) % P) for i in range(r))
                n = tuple(tuple(a * b % P for b in y) for a in x)
                g = group[(31 * trial + 17 * step + 7 * r) % len(group)]
                word = formal_right_call(word, n, g)
                image = multiply(image, call_matrix(n, g))
                charged += int(g[0] != ZERO)
                s = tuple(tuple((int(i == j) + int(i == step % r and
                                                  j == (step + 1) % r)) % P
                                for j in range(r)) for i in range(r))
                word = formal_right_scalar(word, s)
                image = multiply(image, scalar_matrix(s))
                require(formal_image(word, r) == image, "formal/image mismatch")
                require(rank(defect(image, r)) <= charged, "word rank bound")
                cases += 1
            s = tuple(tuple((int(i == j) + int(i == 0 and j == 1)) % P
                            for j in range(r)) for i in range(r))
            mixed = multiply(multiply(scalar_matrix(s), image), scalar_matrix(s))
            observed = rank(defect(mixed, r))
            require(observed == rank(defect(image, r)), "scalar mixing rank")
            strict_cases += int(observed < charged)
            words += 1
    return cases, strict_cases, words


def sharp_checks():
    vectors = tuple(v for v in itertools.product(range(P), repeat=D) if v != ZERO)
    cases = 0
    for w in range(1, 4):
        r = w + 2
        for targets in itertools.product(vectors, repeat=w):
            word = formal_identity(r)
            expected = {(i, i, (targets[i] if i < w else ZERO, IDENTITY)): 1
                        for i in range(r)}
            for i, v in enumerate(targets):
                n = tuple(tuple(int(j == i and k == i) for k in range(r))
                          for j in range(r))
                word = formal_right_call(word, n, (v, IDENTITY))
            require(word == expected, "sharp full formal endpoint")
            require(rank(defect(formal_image(word, r), r)) == w, "sharp rank")
            cases += 1
    return cases


def expect_rejection(callback, message):
    try:
        callback()
    except ValueError:
        return
    raise ValueError(message)


def controls():
    e = (ZERO, IDENTITY)
    translation = ((0, 1), IDENTITY)
    shear = (ZERO, ((1, 1), (0, 1)))
    require(group_product(shear, translation)[0] != (0, 1), "wrong-action control")
    other_shear = (ZERO, ((1, 0), (1, 1)))
    require(group_product(shear, other_shear) != group_product(other_shear, shear),
            "complement must be nonabelian")
    commutators = []
    for i in range(2):
        h = ((1, 1), (0, 1)) if i == 0 else ((1, 0), (1, 1))
        v = (0, 1) if i == 0 else (1, 0)
        a, b = (ZERO, h), (v, IDENTITY)
        c = group_product(group_product(group_product(a, b), group_inverse(a)),
                          group_inverse(b))
        require(c == (tuple(int(i == j) for j in range(2)), IDENTITY), "commutator")
        commutators.append(c[0])
    expect_rejection(lambda: call_matrix(((0, 1), (0, 0)), e), "nilpotent accepted")
    expect_rejection(lambda: call_matrix(((1, 0), (0, 1)), e), "rank-two accepted")
    invisible = call_matrix(((1,),), shear)
    require(rank(defect(invisible, 1)) == 0 and invisible != eye(3), "kernel control")
    nonzero = call_matrix(((1,),), translation)
    require(rank(defect(nonzero, 1)) == 1, "zero-cocycle mutation")
    require(affine(group_product(shear, translation)) !=
            multiply(affine(translation), affine(shear)), "order mutation")
    word = formal_right_call(formal_identity(2), ((1, 0), (0, 0)), translation)
    require(word != formal_identity(2), "omitted target accepted")
    return {"commutator_basis": commutators, "semantic_controls": 7}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path, help="write a fresh source-bound receipt")
    args = parser.parse_args()
    group = groups()
    require(len(group) == 216 and len(set(group)) == 216, "group enumeration")
    pair_count = group_checks(group)
    counts, call_count = call_checks(group)
    prefixes, strict, words = word_checks(group)
    sharp = sharp_checks()
    control_report = controls()
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
              for name in names}
    report = {"status": "PASS_VECTOR_COCYCLE_RANK_FLOOR", "field": P,
              "module_dimension": D, "group_order": len(group),
              "complement_order": len({h for _, h in group}),
              "group_pairs": pair_count, "projectors_by_roles": counts,
              "calls": call_count, "sampled_word_prefixes": prefixes,
              "sampled_words": words, "strict_word_examples": strict,
              "sharp_formal_targets": sharp, "controls": control_report,
              "source_sha256": hashes}
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.emit is not None:
        with args.emit.open("x") as stream:
            stream.write(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
