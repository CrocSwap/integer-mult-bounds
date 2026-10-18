#!/usr/bin/env python3
"""Source-bound exact S4 two-premium finite certificate. Apache-2.0."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRICES = (2, 1, 2)


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def unique_object(items):
    result = {}
    for key, value in items:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def source_check():
    sources = read_json(HERE / "SOURCES.json")
    result = {}
    for item in sources["files"]:
        if item["usage"] != "input":
            continue
        digest = hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest()
        need(digest == item["sha256"], "source drift: " + item["path"])
        result[item["path"]] = digest
    return result


def permutations():
    return tuple(itertools.permutations(range(4)))


def compose(p, q):
    return tuple(p[q[i]] for i in range(4))


def generator(label):
    need(type(label) is int and 0 <= label < 3, "adjacent label boundary")
    p = list(range(4))
    p[label], p[label + 1] = p[label + 1], p[label]
    return tuple(p)


def scalar_product(a, b):
    return tuple(sum(a[2 * i + k] * b[2 * k + j] for k in range(2)) % 2
                 for i in range(2) for j in range(2))


def projectors():
    result = []
    for bits in itertools.product((0, 1), repeat=4):
        nonzero = any(bits)
        determinant = bits[0] * bits[3] ^ bits[1] * bits[2]
        if nonzero and determinant == 0 and scalar_product(bits, bits) == bits:
            result.append(bits)
    need(len(result) == 6, "six rank-one idempotents")
    return result


def formal_product(a, b):
    result = {}
    for p, x in a.items():
        for q, y in b.items():
            g = compose(p, q)
            z = scalar_product(x, y)
            old = result.get(g, (0, 0, 0, 0))
            result[g] = tuple(s ^ t for s, t in zip(old, z))
    return {g: x for g, x in result.items() if any(x)}


def paid(label, projector):
    need(projector in projectors(), "rank-one idempotent boundary")
    e = (0, 1, 2, 3)
    eye = (1, 0, 0, 1)
    return {e: tuple(x ^ y for x, y in zip(eye, projector)),
            generator(label): projector}


def replay(word):
    result = {(0, 1, 2, 3): (1, 0, 0, 1)}
    for label, projector in word:
        result = formal_product(paid(label, projector), result)
    return result


def target(a, b):
    result = {a: (1, 0, 0, 0)}
    old = result.get(b, (0, 0, 0, 0))
    result[b] = (old[0], old[1], old[2], old[3] ^ 1)
    return result


def direct_words():
    e = (0, 1, 2, 3)
    words, distances = {e: []}, {e: 0}
    for cost in range(1, 10):
        for label, weight in enumerate(PRICES):
            if weight > cost:
                continue
            previous = [p for p in words if distances[p] == cost - weight]
            for p in previous:
                q = compose(generator(label), p)
                if q not in words:
                    words[q] = words[p] + [label]
                    distances[q] = cost
    need(len(words) == 24 and max(distances.values()) == 9, "direct weighted coverage")
    for p in words:
        need(sum(PRICES[label] for label in words[p]) == distances[p], "complete word invoice")
        need(distances[p] >= lower(p), "direct word violates inherited cut bound")
        for label, weight in enumerate(PRICES):
            q = compose(generator(label), p)
            need(distances[q] <= distances[p] + weight, "shortest-path dual inequality")
    return words, distances


def lower(p):
    inversions = sum(p[i] > p[j] for i in range(4) for j in range(i + 1, 4))
    return inversions + int(p[0] != 0) + int(p[3] != 3)


def cut_rank(formal, points, inside):
    outside = [p for p in points if p not in inside]
    rows = [0] * (2 * len(outside))
    for permutation, matrix in formal.items():
        for column, point in enumerate(inside):
            image = tuple(permutation[i] for i in point)
            if image not in outside:
                continue
            row = outside.index(image)
            for i in range(2):
                for j in range(2):
                    if matrix[2 * i + j]:
                        rows[i * len(outside) + row] ^= 1 << (j * len(inside) + column)
    rank = 0
    for column in range(2 * len(inside)):
        pivot = next((i for i in range(rank, len(rows)) if rows[i] >> column & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(rank + 1, len(rows)):
            if rows[i] >> column & 1:
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def cut_checks():
    natural = [(i,) for i in range(4)]
    ordered = list(itertools.permutations(range(4), 2))
    cuts = [(ordered, [(i, j) for i in range(4) for j in range(i + 1, 4)]),
            (natural, [(0,)]), (natural, [(0,), (1,), (2,)])]
    for label, price in enumerate(PRICES):
        for projector in projectors():
            bill = sum(cut_rank(paid(label, projector), points, inside)
                       for points, inside in cuts)
            need(bill == price, "explicit paid cut invoice")
    for p in permutations():
        bill = sum(cut_rank(target(p, (0, 1, 2, 3)), points, inside)
                   for points, inside in cuts)
        need(bill == lower(p), "explicit target cut rank")
    scalar_count = 0
    for scalar in itertools.product((0, 1), repeat=4):
        if scalar[0] * scalar[3] ^ scalar[1] * scalar[2] != 1:
            continue
        formal = {(0, 1, 2, 3): scalar}
        need(all(cut_rank(formal, points, inside) == 0 for points, inside in cuts),
             "free scalar cut charge")
        scalar_count += 1
    need(scalar_count == 6, "complete free GL2 inventory")
    return {"paid_factor_cut_ranks": 54, "target_cut_ranks": 72, "free_scalar_cut_ranks": 18}


def formal_checks(words):
    count = omissions = 0
    for a in permutations():
        for b in permutations():
            word = ([(i, (1, 0, 0, 0)) for i in words[a]]
                    + [(i, (0, 0, 0, 1)) for i in words[b]])
            expected = target(a, b)
            need(replay(word) == expected, "full arbitrary-dirty formal endpoint")
            inverse_word = list(reversed(word))
            need(formal_product(replay(inverse_word), expected)
                 == {(0, 1, 2, 3): (1, 0, 0, 1)}, "complete inverse restoration")
            for position in range(len(word)):
                need(replay(word[:position] + word[position + 1:]) != expected,
                     "omitted call accepted")
                omissions += 1
            count += 1
    # Free scalar normalization uses conjugation plus augmentation, see README.
    for n in projectors():
        for label in range(3):
            gate = paid(label, n)
            need(formal_product(gate, gate) == {(0, 1, 2, 3): (1, 0, 0, 1)},
                 "paid involution")
    return {"ordered_endpoints": count, "single_call_omissions_rejected": omissions,
            "paid_involutions": 18}


def compile_engine(directory, source=None):
    compiler = shutil.which("g++") or shutil.which("clang++")
    need(compiler is not None, "C++17 compiler required")
    executable = Path(directory) / "engine"
    args = [compiler, "-std=c++17", "-O3", "-Wall", "-Wextra", "-Werror",
            "-Wpedantic", "-Wconversion", "-Wshadow", "-D_GLIBCXX_ASSERTIONS",
            str(source or HERE / "engine.cpp"), "-o", str(executable)]
    subprocess.run(args, check=True, capture_output=True, text=True, timeout=120)
    return executable


def run_engine(executable, argument="9"):
    run = subprocess.run([str(executable), argument], check=True, capture_output=True,
                         text=True, timeout=120)
    return json.loads(run.stdout, object_pairs_hook=unique_object)


def validate_census(census, distances):
    need(census["radius"] == 9, "insufficient weighted radius")
    ps = permutations()
    required = [(a, b) for a in range(24) for b in range(a, 24)
                if distances[ps[a]] + distances[ps[b]] != lower(ps[a]) + lower(ps[b])]
    need(len(required) == 47, "cut-gap domain")
    need([(q[0], q[1]) for q in census["queries"]] == required,
         "missing, repeated or reordered query")
    for a, b, direct, bound, best, hits in census["queries"]:
        need(direct == distances[ps[a]] + distances[ps[b]], "direct invoice")
        need(bound == lower(ps[a]) + lower(ps[b]), "cut invoice")
        need(best == direct and hits > 0, "shorter word or absent attaining meet")
    need(sum(census["layers"]) == census["states"], "layer accounting")


def compute():
    sources = source_check()
    words, distances = direct_words()
    with tempfile.TemporaryDirectory(prefix="s4-two-premium-") as directory:
        census = run_engine(compile_engine(directory))
    validate_census(census, distances)
    return {"schema_version": 1, "status": "PASS_S4_TWO_PREMIUM_REGISTERS",
            "source_sha256": sources, "prices": list(PRICES),
            "permutation_order": [list(p) for p in permutations()],
            "direct_distances": [distances[p] for p in permutations()],
            "direct_chronological_words": [words[p] for p in permutations()],
            "formal_controls": formal_checks(words), "cut_controls": cut_checks(), "census": census}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="explicitly regenerate EXPECTED.json")
    args = parser.parse_args()
    result = compute()
    if args.write:
        (HERE / "EXPECTED.json").write_text(json.dumps(result, indent=2) + "\n")
    need(result == read_json(HERE / "EXPECTED.json"), "complete fixed receipt mismatch")
    print("PASS_S4_TWO_PREMIUM_REGISTERS ordered_pairs=576 states=971369 "
          "unordered_gaps=47 no_new_kappa")


if __name__ == "__main__":
    main()
