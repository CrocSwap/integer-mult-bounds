#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact corroboration; uniform proof in PROOF.md. See README for predecessors.

Gareth Davidson, with substantial OpenAI Codex assistance.
"""
import argparse
from collections import Counter, deque
from itertools import product
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import digest, finish, require

BASIS = ("", "a", "b", "c", "ab", "ac", "ba", "bc", "cb",
         "aba", "abc", "acb", "bab", "bac", "bcb", "cba", "cbc")
INDEX = {name: i for i, name in enumerate(BASIS)}
LETTERS = {"a": 1, "b": 2, "c": 4}
# Group coordinates:12,23,34,13,24,14. Target s+2t+4h maps to bits3,4,5.
DIRECT = {0: "", 1: "abab", 2: "bcbc", 3: "abacbc", 4: "abcbabcb",
          5: "acbabc", 6: "abcbac", 7: "acbacb"}
ADMITTED = (0, 1, 2, 3, 5, 6, 7)
COLS = {"a": ("a", "ab", "abc"), "b": ("b", "ba", "bc", "bac"),
        "c": ("c", "cb", "cba")}
ROWS = {"a": ("a", "ba", "cba"), "b": ("b", "ab", "cb", "acb"),
        "c": ("c", "bc", "abc")}


def gm(x, y):
    a, b, c, d, e, f = ((x >> k) & 1 for k in range(6))
    A, B, C, D, E, F = ((y >> k) & 1 for k in range(6))
    return ((a ^ A) | ((b ^ B) << 1) | ((c ^ C) << 2) |
            ((d ^ D ^ (a & B)) << 3) | ((e ^ E ^ (b & C)) << 4) |
            ((f ^ F ^ (a & E) ^ (d & C)) << 5))


def reduce_word(word):
    if len(word) > 3:
        return None
    while "ca" in word:
        word = word.replace("ca", "ac")
    if any(x * 2 in word for x in "abc"):
        return None
    require(word in INDEX, "quotient basis incomplete")
    return INDEX[word]


TABLE = tuple(tuple(reduce_word(a + b) for b in BASIS) for a in BASIS)


def bits(value):
    while value:
        bit = value & -value
        yield bit.bit_length() - 1
        value ^= bit


def qm(x, y):
    ans = 0
    for a in bits(x):
        for b in bits(y):
            c = TABLE[a][b]
            if c is not None:
                ans ^= 1 << c
    return ans


def qword(word):
    ans = 1
    for letter in word:
        ans = qm(ans, 1 | (1 << INDEX[letter]))
    return ans


def gword(word):
    ans = 0
    for letter in word:
        ans = gm(ans, LETTERS[letter])
    return ans


def image(code):
    a, b, c, d, e, f = ((code >> k) & 1 for k in range(6))
    powers = (a, b, c, d ^ (a & b), e ^ (b & c), f ^ (a & e))
    words = ("a", "b", "c", "abab", "bcbc", "abcbabcb")
    out = 1
    for power, word in zip(powers, words):
        if power:
            out = qm(out, qword(word))
    return out


def rank(vectors):
    pivots = {}
    for v in vectors:
        while v:
            p = v.bit_length() - 1
            if p not in pivots:
                pivots[p] = v
                break
            v ^= pivots[p]
    return len(pivots)


def columns(matrix, r):
    return [sum(((matrix[i] >> j) & 1) << i for i in range(r)) for j in range(r)]


def outer(x, y, r):
    return tuple(y if (x >> i) & 1 else 0 for i in range(r))


def mn(matrix, x, y):
    return tuple(y if (row & x).bit_count() & 1 else 0 for row in matrix)


def valid(word, r):
    require(type(r) is int and r > 0, "positive role count")
    for label, x, y in word:
        require(label in LETTERS and type(x) is int and type(y) is int
                and 0 < x < 1 << r and 0 < y < 1 << r, "illegal paid factor")


def formal(word, r):
    valid(word, r)
    out = {0: tuple(1 << i for i in range(r))}
    zero = (0,) * r
    for label, x, y in word:
        nxt = dict(out)
        for code, mat in out.items():
            increment = mn(mat, x, y)
            for dest in (code, gm(code, LETTERS[label])):
                nxt[dest] = tuple(a ^ b for a, b in zip(nxt.get(dest, zero), increment))
        out = {code: mat for code, mat in nxt.items() if any(mat)}
    return out


def coefficients(word, r):
    out = {"": tuple(1 << i for i in range(r))}
    zero = (0,) * r
    for label, x, y in word:
        nxt = dict(out)
        for name, mat in out.items():
            dest = reduce_word(name + label)
            if dest is not None:
                key = BASIS[dest]
                nxt[key] = tuple(a ^ b for a, b in zip(nxt.get(key, zero), mn(mat, x, y)))
        out = {key: mat for key, mat in nxt.items() if any(mat)}
    return {name: out.get(name, zero) for name in BASIS}


def formal_image(value, r):
    ans = {name: [0] * r for name in BASIS}
    for code, mat in value.items():
        for b in bits(image(code)):
            ans[BASIS[b]] = [a ^ c for a, c in zip(ans[BASIS[b]], mat)]
    return {name: tuple(mat) for name, mat in ans.items()}


def floor(targets):
    return [2 * sum(bool((t & 1) or (t & 4)) for t in targets),
            2 * sum(bool(t) for t in targets),
            2 * sum(bool((t & 2) or (t & 4)) for t in targets)]


def fixture(targets, r, conjugate=False):
    require(all(t in ADMITTED for t in targets) and len(targets) <= r, "outside sharp family")
    mat = [1 << i for i in range(r)]
    if conjugate:
        mat[-1] ^= (1 << (r - 1)) - 1
    cols = columns(mat, r)
    word = [(letter, cols[i], mat[i]) for i, t in enumerate(targets) for letter in DIRECT[t]]
    endpoint = {}
    for i in range(r):
        code = (targets[i] << 3) if i < len(targets) else 0
        term = outer(cols[i], mat[i], r)
        endpoint[code] = tuple(a ^ b for a, b in zip(endpoint.get(code, (0,) * r), term))
    return word, {code: rows for code, rows in endpoint.items() if any(rows)}


def span_check(word, coeff, r):
    counts = Counter(x[0] for x in word)
    bounds = []
    for label in "abc":
        xs = [x for g, x, y in word if g == label]
        ys = [y for g, x, y in word if g == label]
        cs = [v for name in COLS[label] for v in columns(coeff[name], r)]
        rs = [v for name in ROWS[label] for v in coeff[name]]
        require(rank(xs + cs) == rank(xs), "column span implication")
        require(rank(ys + rs) == rank(ys), "row span implication")
        bound = rank(cs) + rank(rs) - rank(coeff[label])
        require(counts[label] >= bound, "coefficient tariff implication")
        bounds.append(bound)
    return bounds


def build():
    images = [image(g) for g in range(64)]
    products = [gm(x, y) for x in range(64) for y in range(64)]
    for x, y in product(range(64), repeat=2):
        require(qm(images[x], images[y]) == images[gm(x, y)], "quotient homomorphism")
    for i, j, k in product(range(17), repeat=3):
        require(qm(qm(1 << i, 1 << j), 1 << k) == qm(1 << i, qm(1 << j, 1 << k)), "associativity")
    distances = {0: 0}
    queue = deque([0])
    while queue:
        g = queue.popleft()
        for a in LETTERS.values():
            h = gm(g, a)
            if h not in distances:
                distances[h] = distances[g] + 1
                queue.append(h)
    table = []
    omitted = 0
    for t in range(8):
        word = [(letter, 1, 1) for letter in DIRECT[t]]
        require(gword(DIRECT[t]) == t << 3, "direct target")
        require(len(word) == distances[t << 3], "direct address length")
        coeff = coefficients(word, 1)
        require(span_check(word, coeff, 1) == floor([t]), "target union formula")
        if t != 4:
            require([DIRECT[t].count(a) for a in "abc"] == floor([t]), "simultaneous attainment")
        for j in range(len(word)):
            require(formal(word[:j] + word[j + 1:], 1) != {t << 3: (1,)}, "omitted call accepted")
            omitted += 1
        table.append({"target": t, "word": DIRECT[t], "counts": [DIRECT[t].count(a) for a in "abc"],
                      "lower_counts": floor([t]), "quotient": images[t << 3], "sharp_family": t != 4})
    alphabet = tuple(product("abc", range(1, 4), range(1, 4)))
    transcript = []
    for length in range(4):
        for word in product(alphabet, repeat=length):
            c = coefficients(word, 2)
            require(c == formal_image(formal(word, 2), 2), "formal/quotient mismatch")
            span_check(word, c, 2)
            transcript.append([list(c[name]) for name in BASIS])
    witnesses = []
    for width in (1, 2, 3):
        for targets in product(ADMITTED, repeat=width):
            r = width + 1
            word, expected = fixture(targets, r)
            require(formal(word, r) == expected, "full formal endpoint")
            require(span_check(word, coefficients(word, r), r) == floor(targets), "mixed tariff")
            counts = [sum(g == a for g, x, y in word) for a in "abc"]
            require(counts == floor(targets), "mixed count attainment")
            witnesses.append([list(targets), r, False, sorted(expected.items()), counts])
    for targets, r in [((1, 2, 3, 5, 6, 7), 8), ((5, 6, 7), 6), ((7,), 4)]:
        word, expected = fixture(targets, r, True)
        require(formal(word, r) == expected, "scalar-conjugated full endpoint")
        require(span_check(word, coefficients(word, r), r) == floor(targets), "conjugated tariff")
        witnesses.append([list(targets), r, True, sorted(expected.items()), floor(targets)])
    kernel = (0, 1, 32, 33)
    require(len(set(kernel)) == 4, "formal kernel nonzero")
    value = 0
    for g in kernel:
        value ^= images[g]
    require(value == 0, "cubic kernel fixture")
    xs, ys = [1, 2, 3], [1, 1, 1]
    summed = [0, 0]
    for x, y in zip(xs, ys):
        summed = [a ^ b for a, b in zip(summed, outer(x, y, 2))]
    require(summed == [0, 0] and rank(xs) == 2 and rank(ys) == 1, "one-span control")
    return {"schema_version": 1, "group_products": 4096, "quotient_dimension": 17,
            "associativity_triples": 4913, "group_map_sha256": digest([list(BASIS), images, products]),
            "address_distance_histogram": {str(k): v for k, v in sorted(Counter(distances.values()).items())},
            "target_table": table, "coefficient_words": len(transcript),
            "coefficient_sha256": digest(transcript), "formal_witnesses": len(witnesses),
            "witness_sha256": digest(witnesses), "omitted_call_controls": omitted,
            "kernel_formal_support": list(kernel), "one_span_ranks": [2, 1, 3],
            "scope": "Uniform written tariff; sharp seven-label mixtures. Pure central labels have necessary bounds only."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    result = build()
    finish(result, "EXPECTED.json", args.write)
    print("PASS_UT4_MIXED_ROOT_TARIFFS witnesses=" + str(result["formal_witnesses"]))


if __name__ == "__main__":
    main()
