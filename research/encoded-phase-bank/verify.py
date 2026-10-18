#!/usr/bin/env python3
"""Finite evidence for the written encoded-bank theorem; no predecessor imports.

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import hashlib
from itertools import combinations, permutations, product
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def crossings(word):
    require(bool(word), "empty schedule")
    counts = Counter(word)
    require(all(type(j) is int and j >= 0 for j in word), "bad column")
    require(set(counts) == set(range(len(counts))), "noncanonical columns")
    require(all(n == 2 for n in counts.values()), "column must occur twice")
    pos = {j: [i for i, k in enumerate(word) if k == j] for j in counts}
    return tuple((i, j) for i, j in combinations(sorted(pos), 2)
                 if (pos[i][0] < pos[j][0] < pos[i][1] < pos[j][1]
                     or pos[j][0] < pos[i][0] < pos[j][1] < pos[i][1]))


def paired_words(n):
    """Every double-occurrence word modulo renaming by first appearance."""
    def visit(word, counts):
        if len(word) == 2 * n:
            yield tuple(word)
            return
        for j, count in enumerate(counts):
            if count == 1:
                counts[j] = 2
                yield from visit(word + [j], counts)
                counts[j] = 1
        if len(counts) < n:
            yield from visit(word + [len(counts)], counts + [1])
    yield from visit([], [])


def symp(a, b):
    return ((a[0] & b[1]).bit_count() + (a[1] & b[0]).bit_count()) % 2


def frames(q):
    vectors = [(x, z) for x in range(1 << q) for z in range(1 << q) if x or z]
    return [(a, b) for a in vectors for b in vectors if symp(a, b)]


def criterion(word, encoding):
    if any(symp(a, b) != 1 for a, b in encoding):
        return False
    return all(not symp(a, b) for i, j in crossings(word)
               for a in encoding[i] for b in encoding[j])


def literal_polynomial(word, encoding, q):
    """Literal i^(x.z) X(x)Z(z) action, accumulated in Z/4.

    Prefix translations, not the crossing graph, produce the phase terms.
    Original bank labels are tracked separately and must all cancel.
    """
    shifts, signs, phase = [0] * q, [0] * q, {}

    def add(key, value):
        phase[key] = (phase.get(key, 0) + value) % 4
        if not phase[key]:
            del phase[key]

    for j in word:
        for side, (x, z) in enumerate(encoding[j]):
            variable = 2 * j + side
            add((variable,), (x & z).bit_count() % 2)
            for bit in range(q):
                if (z >> bit) & 1:
                    signs[bit] ^= 1 << variable
                    mask = shifts[bit]
                    while mask:
                        low = mask & -mask
                        other = low.bit_length() - 1
                        add(tuple(sorted({variable, other})), 2)
                        mask ^= low
                if (x >> bit) & 1:
                    shifts[bit] ^= 1 << variable
    return phase, shifts, signs


def expected_phase(word, encoding):
    terms = {}
    for j, (a, b) in enumerate(encoding):
        if symp(a, b):
            terms[(2 * j, 2 * j + 1)] = 2
    for i, j in crossings(word):
        for a in range(2):
            for b in range(2):
                if symp(encoding[i][a], encoding[j][b]):
                    terms[(2 * i + a, 2 * j + b)] = 2
    return terms


def check_encoding(word, encoding, q):
    phase, shifts, signs = literal_polynomial(word, encoding, q)
    require(not any(shifts + signs), "bank return failed")
    require(phase == expected_phase(word, encoding), "crossing formula mismatch")
    wanted = {(2 * j, 2 * j + 1): 2 for j in range(len(encoding))}
    require((phase == wanted) == criterion(word, encoding), "criterion mismatch")
    return phase == wanted


def weighted_assignment(pi, weights):
    n = len(pi)
    require(sorted(pi) == list(range(n)), "not a permutation")
    require(len(weights) == n and all(type(w) is int and w >= 0 for w in weights),
            "bad weights")
    ends, banks, seen = {}, {}, []
    for j in pi:
        start = max((ends[i] for i in seen if i < j), default=0)
        ends[j] = start + weights[j]
        banks[j] = tuple(range(start, ends[j]))
        seen.append(j)
    return max(ends.values(), default=0), banks


def brute_chain(pi, weights):
    """Independent subset enumeration, without the DP recurrence."""
    best = 0
    for mask in range(1 << len(pi)):
        seq = [j for k, j in enumerate(pi) if (mask >> k) & 1]
        if all(a < b for a, b in zip(seq, seq[1:])):
            best = max(best, sum(weights[j] for j in seq))
    return best


def reference_pins():
    data = json.loads((HERE / "REFERENCES.json").read_text())
    require(len(data) == 2, "reference inventory")
    for ref in data:
        raw = (HERE / ref["local_path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == ref["sha256"], "reference SHA256")
        header = b"blob " + str(len(raw)).encode() + b"\0"
        require(hashlib.sha1(header + raw).hexdigest() == ref["git_blob"], "reference Git blob")
    return len(data)


def run():
    pins = reference_pins()
    exhaustive, successes, words = 0, 0, 0
    one = frames(1)
    require(len(one) == 6, "one-bit frame census")
    for n in range(1, 5):
        for word in paired_words(n):
            words += 1
            for enc in product(one, repeat=n):
                successes += check_encoding(word, enc, 1)
                exhaustive += 1
    rng = random.Random(70)
    two = frames(2)
    require(len(two) == 120, "two-bit frame census")
    sampled = 0
    for n in range(1, 7):
        for word in paired_words(n):
            check_encoding(word, [rng.choice(two) for _ in range(n)], 2)
            sampled += 1

    weighted, max_bits = 0, 0
    for n in range(1, 6):
        for pi in permutations(range(n)):
            edges = crossings(tuple(range(n)) + pi)
            for weights in product(range(3), repeat=n):
                width, banks = weighted_assignment(pi, weights)
                require(width == brute_chain(pi, weights), "weighted chain optimum")
                require(all(len(banks[j]) == weights[j] for j in range(n)), "lost label")
                require(all(set(banks[i]).isdisjoint(banks[j]) for i, j in edges),
                        "overlapping comparable intervals")
                require(all(all(0 <= b < width for b in bs) for bs in banks.values()), "bank extent")
                weighted += 1
                max_bits = max(max_bits, width)

    cycle = (0, 1, 4, 0, 3, 4, 2, 3, 1, 2)
    require(set(crossings(cycle)) == {(0, 1), (0, 4), (1, 2), (2, 3), (3, 4)}, "C5 crossing graph")
    plane_sets = {frozenset((a, b, (a[0] ^ b[0], a[1] ^ b[1]))) for a, b in two}
    planes = sorted(plane_sets, key=lambda s: sorted(s))
    neighbors = [[k for k, t in enumerate(planes)
                  if all(not symp(a, b) for a in s for b in t)] for s in planes]
    require(len(planes) == 20 and all(len(ns) == 1 for ns in neighbors), "two-bit commutant planes")
    require(all(neighbors[neighbors[i][0]][0] == i and neighbors[i][0] != i
                for i in range(20)), "orthogonality is ten disjoint edges")
    colors = (0, 1, 0, 1, 2)
    enc3 = [((0, 1 << c), (1 << c, 0)) for c in colors]
    require(check_encoding(cycle, enc3, 3), "C5 three-bit construction")

    controls = {}
    controls["same_order_shared_bit"] = not check_encoding((0, 1, 0, 1), [one[0]] * 2, 1)
    controls["wrong_diagonal_pairing"] = not check_encoding((0, 0), [((1, 0), (1, 0))], 1)
    controls["three_crossing_one_bit"] = not check_encoding((0, 1, 2, 0, 1, 2), [one[0]] * 3, 1)
    for name, word in [("missing_consumer", (0, 1, 0)), ("extra_consumer", (0, 0, 0)),
                       ("label_gap", (0, 2, 0, 2))]:
        try:
            crossings(word)
        except ValueError:
            controls[name] = True
        else:
            controls[name] = False
    canonical = [((0, 1), (1, 0))] * 2
    formula = expected_phase((0, 1, 0, 1), canonical)
    require(formula[(0, 3)] == formula[(1, 2)] == 2, "cross-term controls")
    for key in [(0, 3), (1, 2), (0, 1)]:
        mutant = dict(formula)
        del mutant[key]
        controls["omit_term_" + str(key)] = mutant != literal_polynomial((0, 1, 0, 1), canonical, 1)[0]
    require(all(controls.values()), "negative control failed")
    return {"status": "PASS_ENCODED_PHASE_BANK", "no_new_kappa": True,
            "references": pins, "q1_canonical_words": words,
            "q1_exhaustive_encodings": exhaustive, "q1_correct_encodings": successes,
            "q2_seed": 70, "q2_one_encoding_per_word": sampled,
            "weighted_permutation_cases": weighted, "max_constructed_bits": max_bits,
            "C5": {"schedule": cycle, "two_bit_symplectic_planes": 20,
                   "orthogonality_edges": 10, "constructed_bits": 3},
            "negative_controls": controls}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    expected = json.loads((HERE / "RESULT.json").read_text())
    require(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True), "receipt mismatch")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
