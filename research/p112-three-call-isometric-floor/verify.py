#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact evidence for PROOF.md; stdlib, read-only default, checks active under -O.

Sricharan Vagvala (@theon199), with substantial OpenAI Codex assistance.
No predecessor executable is imported. --write updates only EXPECTED.json.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import permutations, product
import json
from pathlib import Path
import random
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def object_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(path):
    def invalid_constant(value):
        raise ValueError("nonfinite JSON constant: " + value)
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=object_pairs,
                      parse_constant=invalid_constant)


def source_pins():
    data = read_json(HERE / "SOURCES.json")
    require(data["base_commit"] == BASE, "source base")
    required = {"certificates/selected-result.json", "docs/research/agent-task-catalog.json",
                "research/p112-batch-centre-floor/PROOF.md",
                "research/p112-batch-centre-floor/README.md",
                "research/complex-local-word-ceiling/README.md"}
    require(len(data["files"]) == len(required)
            and {x["path"] for x in data["files"]} == required, "source inventory")
    for entry in data["files"]:
        name = entry["path"]
        if entry["usage"] == "provenance":
            payload = subprocess.run(["git", "-C", str(ROOT), "show", BASE + ":" + name],
                                     check=True, capture_output=True).stdout
        else:
            require(entry["usage"] == "input", "source usage")
            payload = (ROOT / name).read_bytes()
        require(hashlib.sha256(payload).hexdigest() == entry["sha256"], "source sha256: " + name)
        blob = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
        require(blob == entry["git_blob"], "source Git blob: " + name)
    return {"base_commit": BASE, "bound_files": len(required)}


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def binary_basis(rows):
    pivots, indices = {}, []
    for index, value in enumerate(rows):
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                indices.append(index)
                break
    return indices


def binary_rank(rows):
    return len(binary_basis(rows))


def rational_rank(rows):
    pivots = {}
    for row in rows:
        v = list(map(Fraction, row))
        for column, basis in sorted(pivots.items()):
            coefficient = v[column]
            if coefficient:
                v = [x - coefficient * y for x, y in zip(v, basis)]
        column = next((j for j, value in enumerate(v) if value), None)
        if column is not None:
            pivot = v[column]
            pivots[column] = [x / pivot for x in v]
    return len(pivots)


def modular_rank(rows, prime=65537):
    """A nonzero mod-prime minor certifies a rational rank lower bound."""
    pivots = {}
    for row in rows:
        v = [x % prime for x in row]
        for column, basis in sorted(pivots.items()):
            coefficient = v[column]
            if coefficient:
                v = [(x - coefficient * y) % prime for x, y in zip(v, basis)]
        column = next((j for j, value in enumerate(v) if value), None)
        if column is not None:
            inverse = pow(v[column], -1, prime)
            pivots[column] = [(x * inverse) % prime for x in v]
    return len(pivots)


def invert_binary(rows):
    size = len(rows)
    a = [row | (1 << (size + i)) for i, row in enumerate(rows)]
    for column in range(size):
        pivot = next((i for i in range(column, size) if (a[i] >> column) & 1), None)
        require(pivot is not None, "singular binary form")
        a[column], a[pivot] = a[pivot], a[column]
        for i in range(size):
            if i != column and ((a[i] >> column) & 1):
                a[i] ^= a[column]
    require([x & ((1 << size) - 1) for x in a] == [1 << i for i in range(size)],
            "binary inverse identity")
    return [x >> size for x in a]


def geometry():
    # Four-point affine planes of F2^3, with all sign lines; no imported data.
    live = []
    for normal in range(1, 8):
        for offset in (0, 1):
            support = [x for x in range(8) if ((normal & x).bit_count() & 1) == offset]
            require(len(support) == 4, "affine plane size")
            for signs in product((-1, 1), repeat=3):
                root = [0] * 8
                for coordinate, sign in zip(support, (1,) + signs):
                    root[coordinate] = sign
                live.append(root)
    axes = [[2 * (i == j) for i in range(8)] for j in range(8)]
    roots = axes + live
    require(len(live) == 112 and len({tuple(x) for x in roots}) == 120, "root count")
    require(all(dot(x, x) == 4 for x in roots), "root norm")
    require(all(dot(x, y) % 2 == 0 for x in roots for y in roots), "Gram integrality")
    require(all(sum(x[i] * x[j] for x in live) == 56 * (i == j)
                for i in range(8) for j in range(8)), "X transpose X")
    gram = [sum(((1 + dot(x, y) // 2) & 1) << j for j, y in enumerate(roots)) for x in roots]
    chosen = binary_basis(gram)
    require(len(chosen) == 9, "Gram rank nine")
    labels = [sum(((row >> index) & 1) << j for j, index in enumerate(chosen)) for row in gram]
    form = invert_binary([labels[index] for index in chosen])

    def pair(x, y):
        return sum(((x >> i) & 1) * ((form[i] & y).bit_count() & 1) for i in range(9)) & 1

    require(all(pair(labels[i], labels[j]) == ((gram[i] >> j) & 1)
                for i in range(120) for j in range(120)), "label/form reconstruction")
    require(binary_rank(labels[8:]) == 9, "live label rank")
    live_labels = labels[8:]
    census, deficient = Counter(), []
    for functional in range(1, 512):
        complement = [root for root, label in zip(live, live_labels)
                      if (functional & label).bit_count() & 1]
        rank = modular_rank(complement)
        census[rank] += 1
        if rank != 8:
            kernels = [j for j in range(8) if all(row[j] == 0 for row in complement)]
            require(rank == 7 and len(kernels) == 1, "deficient complement kernel")
            require(rational_rank(complement) == 7, "independent deficient rational rank")
            deficient.append([functional, kernels[0]])
    require(census == {8: 503, 7: 8}, "support census")
    require(sorted(j for _, j in deficient) == list(range(8)), "eight coordinate kernels")
    exceptional = [[label for root, label in zip(live, live_labels) if root[j]] for j in range(8)]
    require(all(len(s) == 56 and binary_rank(s) == 8 for s in exceptional), "exceptional dimensions")
    pairs = [[binary_rank([sum(pair(x, y) << k for k, y in enumerate(w)) for x in u])
              for w in exceptional] for u in exceptional]
    require(pairs == [[8] * 8 for _ in range(8)], "within-call pair lemma")
    normals = []
    for support in exceptional:
        candidates = [x for x in range(1, 512) if all(pair(x, y) == 0 for y in support)]
        require(len(candidates) == 1, "exceptional hyperplane normal")
        normals.append(candidates[0])
    receipt = {"live_roots": 112, "ambient_labels": 9, "modular_prime": 65537,
               "complement_ranks": dict(sorted(census.items())), "deficient": deficient,
               "support_pair_ranks": pairs, "geometry_sha256": sha([roots, labels, form])}
    return live, live_labels, pair, exceptional, normals, receipt


def xor_sum(values):
    result = 0
    for value in values:
        result ^= value
    return result


def check_chart(chart, pair):
    require(len(chart) == 512 and set(chart) == set(range(512)), "chart bijection")
    basis = [chart[1 << j] for j in range(9)]
    require(all(chart[x] == xor_sum(basis[j] for j in range(9) if (x >> j) & 1)
                for x in range(512)), "chart linearity")
    require(all(pair(basis[i], basis[j]) == pair(1 << i, 1 << j)
                for i in range(9) for j in range(9)), "chart isometry")


def rank_of_pairing(u, w, pair):
    ub, wb = [u[i] for i in binary_basis(u)], [w[i] for i in binary_basis(w)]
    return binary_rank([sum(pair(x, y) << k for k, y in enumerate(wb)) for x in ub])


def lower_term(a, c, order, width):
    position = {block: i for i, block in enumerate(order)}
    return [[a[i] * c[j] if position[i // width] > position[j // width] else 0
             for j in range(len(c))] for i in range(len(a))]


def ordering_certificate():
    patterns = []
    for left in range(1, 8):
        for right in range(1, 8):
            if left & right:
                continue
            a, c = [[(mask >> i) & 1 for i in range(3)] for mask in (left, right)]
            ranks = [rational_rank(lower_term(a, c, order, 1)) for order in permutations(range(3))]
            expected_sum = 3 if sum(a) == sum(c) == 1 else 4
            require(set(ranks) <= {0, 1} and sum(ranks) == expected_sum, "three-call deletion counts")
            patterns.append({"reader_mask": left, "source_mask": right, "six_ranks": ranks})
    require(len(patterns) == 12, "complete disjoint support domain")
    a, c = [1, 0, 1, 0], [0, 1, 0, 1]
    four_ranks = [rational_rank(lower_term(a, c, order, 1)) for order in permutations(range(4))]
    require(max(four_ranks) == 2 and sum(four_ranks) == 24, "four-call scope control")
    return {"three_call_patterns": patterns, "three_call_order_checks": 72,
            "four_call_control": {"rank_histogram": dict(sorted(Counter(four_ranks).items())),
                                  "rank_sum": sum(four_ranks), "orders": 24}}


def unit(index, size=24):
    return [int(i == index) for i in range(size)]


def coefficient_endpoint(terms):
    return [[sum(a[i] * c[j] for a, c in terms) for j in range(24)] for i in range(24)]


def check_endpoint(terms):
    require(coefficient_endpoint(terms) == [[int(i == j) for j in range(24)] for i in range(24)],
            "all-pairs coefficient endpoint")


def root_values(coefficient, live):
    return [dot(root, coefficient[8 * s:8 * s + 8]) for s in range(3) for root in live]


def term_price(a, c, live, labels, charts, pair):
    spans = []
    for coefficient in (a, c):
        spans.append(sorted({charts[s][label] for s in range(3)
                             for root, label in zip(live, labels)
                             if dot(root, coefficient[8 * s:8 * s + 8])}))
    return rank_of_pairing(*spans, pair)


def fixture(name, terms, live, labels, charts, pair):
    check_endpoint(terms)
    actual = [[0] * 336 for _ in range(336)]
    prices, pure_terms = [], []
    for a, c in terms:
        av, cv = root_values(a, live), root_values(c, live)
        for i, value in enumerate(av):
            if value:
                for j, other in enumerate(cv):
                    if other:
                        actual[i][j] += value * other
        reader = {s for s in range(3) if any(a[s * 8:(s + 1) * 8])}
        source = {s for s in range(3) if any(c[s * 8:(s + 1) * 8])}
        require(reader and source, "inactive fixture term")
        pure = not reader.intersection(source)
        rank = term_price(a, c, live, labels, charts, pair)
        require(rank >= (7 if pure else 8), "term rank floor")
        prices.append(rank)
        if pure:
            pure_terms.append((a, c))
    for i in range(336):
        for j in range(336):
            expected = dot(live[i % 112], live[j % 112]) if i // 112 == j // 112 else 0
            require(actual[i][j] == expected, "live all-pairs endpoint")
    p, n = len(pure_terms), len(terms) - len(pure_terms)
    require(3 * n + 2 * p >= 72, "averaged triangular count")
    require(3 * sum(prices) >= 576 + 5 * p, "copy floor")
    lower_ranks = []
    for order in permutations(range(3)):
        ranks = [rational_rank(lower_term(a, c, order, 8)) for a, c in pure_terms]
        require(24 <= n + sum(ranks), "triangular order rank inequality")
        lower_ranks.append(sum(ranks))
    return {"name": name, "terms": len(terms), "pure": p, "non_pure": n,
            "price_histogram": dict(sorted(Counter(prices).items())), "cost": sum(prices),
            "lower_ranks_by_order": lower_ranks, "all_pairs_checked": 336 ** 2,
            "terms_sha256": sha(terms)}


def rejected(action, diagnostic):
    try:
        action()
    except ValueError as error:
        require(diagnostic in str(error), "wrong control rejection: " + str(error))
        return
    raise ValueError("control was accepted: " + diagnostic)


def run():
    sources = source_pins()
    live, labels, pair, exceptional, normals, geom_receipt = geometry()
    orders = ordering_certificate()
    isotropic = [x for x in range(1, 512) if pair(x, x) == 0]
    require(len(isotropic) == 255, "isotropic vector count")
    targets = [u for u in isotropic if all(pair(v, u) for v in normals)]
    require(len(targets) == 16, "targeted transvection count")
    chosen = random.Random(47).sample(targets, 2)
    charts = [list(range(512))] + [[x ^ (u if pair(x, u) else 0) for x in range(512)] for u in chosen]
    for chart in charts:
        check_chart(chart, pair)
    cross_ranks = [[rank_of_pairing(exceptional[i], [charts[1][x] for x in exceptional[j]], pair)
                    for j in range(8)] for i in range(8)]
    require(cross_ranks == [[7] * 8 for _ in range(8)], "real rank-seven cross terms")
    for i in range(8):
        for j in range(8):
            direct = binary_rank([sum(pair(x, charts[1][y]) << k
                                     for k, y in enumerate(exceptional[j])) for x in exceptional[i]])
            require(direct == cross_ranks[i][j], "direct cross-pair rank")
    standard = [(unit(i), unit(i)) for i in range(24)]
    one_cross = [(a[:], c[:]) for a, c in standard]
    one_cross[0][1][8] = 1
    one_cross.append((unit(0), [-x for x in unit(8)]))
    wide_cross = [(a[:], c[:]) for a, c in standard]
    wide_cross[0][1][8] = wide_cross[0][1][16] = 1
    wide_cross.append((unit(0), [-int(i in (8, 16)) for i in range(24)]))
    coupled = [(unit(i), unit(i)) for i in range(24) if i not in (0, 8, 16)]
    common = [int(i in (0, 8, 16)) for i in range(24)]
    coupled.append((common, common[:]))
    for s in range(3):
        correction = [-int(i in (0, 8, 16) and i != 8 * s) for i in range(24)]
        coupled.append((unit(8 * s), correction))
    fixtures = [fixture(name, terms, live, labels, charts, pair) for name, terms in
                (("standard", standard), ("one_rank7_cross", one_cross),
                 ("one_three_call_pure", wide_cross), ("sharp_deletion_coupled", coupled))]
    require(fixtures[0]["cost"] == 192 and fixtures[1]["cost"] == 199, "attainment / rank-seven fixture")
    require(fixtures[3]["non_pure"] == 22 and fixtures[3]["pure"] == 3
            and fixtures[3]["lower_ranks_by_order"] == [2] * 6, "sharp triangular count fixture")
    controls = []
    shear = [x ^ (((x >> 1) & 1) << 0) for x in range(512)]
    rejected(lambda: check_chart(shear, pair), "chart isometry")
    controls.append("invertible nonisometric chart rejected")
    rejected(lambda: require(min(map(min, cross_ranks)) >= 8, "false common-chart floor"),
             "false common-chart floor")
    controls.append("false per-term rank-eight floor rejected")
    wrong_sign = [(a[:], c[:]) for a, c in one_cross]
    wrong_sign[-1] = (unit(0), unit(8))
    rejected(lambda: check_endpoint(wrong_sign), "all-pairs coefficient endpoint")
    controls.append("wrong cross cancellation sign rejected")
    rejected(lambda: check_endpoint(standard[:-1]), "all-pairs coefficient endpoint")
    controls.append("missing coordinate term rejected")
    correlated = coupled[:22]
    diagonal = coefficient_endpoint(correlated)
    require(all(diagonal[i][j] == int(i == j) for i in range(24) for j in range(24)
                if i // 8 == j // 8), "diagonal-only control positive side")
    rejected(lambda: check_endpoint(correlated), "all-pairs coefficient endpoint")
    controls.append("diagonal-only crosstalk rejected by all-pairs check")
    four = orders["four_call_control"]
    rejected(lambda: require(3 * four["rank_sum"] <= 2 * four["orders"], "four-call mean exceeds 2/3"),
             "four-call mean exceeds 2/3")
    controls.append("invalid four-call extension rejected")
    rejected(lambda: require(max(four["rank_histogram"]) <= 1, "four-call truncation rank two"),
             "four-call truncation rank two")
    controls.append("rank-one truncation assumption at four calls rejected")
    require(Fraction(7) > Fraction(4, 9) * 8 and Fraction(7, 8) > Fraction(2, 3),
            "power-price positivity endpoints")
    return {"schema_version": 1, "sources": sources, "geometry": geom_receipt,
            "ordering": orders, "chart_seed": 47, "transvection_vectors": chosen,
            "cross_pair_ranks": cross_ranks, "fixtures": fixtures, "negative_controls": controls,
            "proof_status": "written quantified proof; finite evidence only, no formal theorem"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="replace only this package's EXPECTED.json")
    args = parser.parse_args()
    result = run()
    path = HERE / "EXPECTED.json"
    if args.write:
        path.write_text(canonical(result), encoding="utf-8")
    else:
        require(read_json(path) == json.loads(canonical(result)), "receipt mismatch")
    print(canonical(result), end="")
    print("receipt_sha256", sha(result))
    print("PASS_P112_THREE_CALL_ISOMETRIC_FLOOR")


if __name__ == "__main__":
    main()
