#!/usr/bin/env python3
"""Exact dirty-shear minima by complete radius-four shear-coset pairing.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
The meet-in-the-middle setup follows @commdata2338, PR1306. This implementation
adds simultaneous all-shear coset pairing; no predecessor code is imported.
"""
import argparse
from collections import Counter
from itertools import permutations
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
H, T, RADIUS = 3, 4, 4


class Reject(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Reject(message)


def identity(n):
    return sum(1 << (i * n + i) for i in range(n))


def step(matrix, gate, n):
    destination, source = gate
    return matrix ^ (((matrix >> (source * n)) & ((1 << n) - 1))
                     << (destination * n))


def target(k, h, t):
    n = h + t
    return identity(n) ^ sum(((k >> (r * h)) & ((1 << h) - 1))
                             << ((h + r) * n) for r in range(t))


def ball(h, t, feedback, radius):
    """All complete matrices at distances <= radius, retaining first parents."""
    n = h + t
    gates = [(d, s) for d in range(n) for s in range(n)
             if d != s and (feedback or not (d < h <= s))]
    seen = {identity(n): (0, -1)}
    layer, spheres = [identity(n)], [1]
    for depth in range(1, radius + 1):
        following = []
        for matrix in layer:
            for index, gate in enumerate(gates):
                reached = step(matrix, gate, n)
                if reached not in seen:
                    seen[reached] = (depth, index)
                    following.append(reached)
        spheres.append(len(following))
        layer = following
    return seen, gates, spheres


def coset(matrix, h, t):
    """Return (representative of M*S, Q), where M*T_Q = representative.

    S consists of all shears T_K. Reduce helper columns modulo the ordered
    target-column span, retaining exact coefficients. Invertibility makes
    the target columns independent. The key is packed by columns.
    """
    n = h + t
    columns = [sum(((matrix >> (r * n + c)) & 1) << r for r in range(n))
               for c in range(n)]
    basis = {}
    for j, column in enumerate(columns[h:]):
        coefficient = 1 << j
        while column:
            pivot = (column & -column).bit_length() - 1
            if pivot not in basis:
                basis[pivot] = column, coefficient
                break
            vector, combination = basis[pivot]
            column ^= vector
            coefficient ^= combination
        else:
            raise Reject("dependent target columns")
    key, label = 0, 0
    for c in range(h):
        column, coefficient = columns[c], 0
        for pivot in sorted(basis):
            if column & (1 << pivot):
                vector, combination = basis[pivot]
                column ^= vector
                coefficient ^= combination
        key |= column << (n * c)
        for r in range(t):
            label |= ((coefficient >> r) & 1) << (r * h + c)
    for c in range(h, n):
        key |= columns[c] << (n * c)
    return key, label


def word_for(matrix, seen, gates, n):
    backwards = []
    while matrix != identity(n):
        depth, index = seen[matrix]
        gate = gates[index]
        backwards.append(list(gate))
        matrix = step(matrix, gate, n)
        need(seen[matrix][0] == depth - 1, "BFS parent depth")
    return backwards[::-1]


def check_word(word, k, h, t, feedback=False):
    n, matrix = h + t, identity(h + t)
    need(type(word) is list, "word must be a list")
    for gate in word:
        need(type(gate) is list and len(gate) == 2
             and all(type(index) is int and 0 <= index < n for index in gate),
             "typed gate indices")
        d, s = gate
        need(d != s, "self XOR is not reversible")
        need(feedback or not (d < h <= s), "target feedback forbidden")
        matrix = step(matrix, gate, n)
    need(matrix == target(k, h, t), "complete dirty boundary mismatch")
    return len(word)


def census(h, t, feedback, radius=RADIUS):
    seen, gates, spheres = ball(h, t, feedback, radius)
    groups = {}
    for matrix, (depth, _) in seen.items():
        key, label = coset(matrix, h, t)
        groups.setdefault(key, []).append((label, depth, matrix))
    best = [None] * (1 << (h * t))
    first = identity(h + t)
    best[0] = (0, first, first)
    pairs = 0
    for group in groups.values():
        for i, (ka, da, a) in enumerate(group):
            for kb, db, b in group[i + 1:]:
                pairs += 1
                k, cost = ka ^ kb, da + db
                if best[k] is None or cost < best[k][0]:
                    best[k] = cost, a, b
    lengths, words, outside = [], [], []
    for k, hit in enumerate(best):
        if hit is None:
            # Exclusion through 2*radius plus an explicit 2*radius+1 word
            # closes the gap. A miss alone never establishes a minimum.
            witness = [[h + r, c] for r in range(t) for c in range(h)
                       if k & (1 << (r * h + c))]
            need(len(witness) == 2 * radius + 1,
                 "insufficient radius: direct witness does not close the gap")
            length = len(witness)
            outside.append(k)
        else:
            length, a, b = hit
            witness = (word_for(b, seen, gates, h + t)
                       + word_for(a, seen, gates, h + t)[::-1])
        need(check_word(witness, k, h, t, feedback) == length, "witness length")
        lengths.append(length)
        words.append(witness)
    return {"spheres": spheres, "cosets": len(groups),
            "unordered_distinct_pairs": pairs, "outside_double_radius": outside,
            "lengths": lengths, "words": words}


def orbit(k, h, t):
    return {sum(((k >> (r * h + c)) & 1) << (rr * h + cc)
                for rr, r in enumerate(rows) for cc, c in enumerate(columns))
            for rows in permutations(range(t)) for columns in permutations(range(h))}


def controls():
    rejected = []

    def reject(name, action):
        try:
            action()
        except Reject:
            rejected.append(name)
        else:
            raise Reject("negative control accepted: " + name)

    star = [[0, 1], [2, 0], [0, 1]]
    check_word(star, 3, 2, 1)
    feedback = [[0, 1], [1, 0], [0, 1], [1, 0], [0, 1]]
    check_word(feedback, 1, 1, 1, True)
    reject("unrestored_helper", lambda: check_word(star[:-1], 3, 2, 1))
    reject("dirty_target_mixing", lambda: check_word([[1, 0], [2, 1]], 3, 1, 2))
    reject("wrong_helper_input", lambda: check_word([[2, 0]], 3, 2, 1))
    reject("feedback_in_restricted_alphabet", lambda: check_word(feedback, 1, 1, 1))
    reject("noninvertible_self_xor", lambda: check_word([[0, 0]], 0, 1, 1))
    reject("boolean_gate_index", lambda: check_word([[True, 0]], 1, 1, 1))
    reject("insufficient_radius", lambda: census(2, 2, True, 1))
    small, _, _ = ball(1, 2, True, 6)
    need(len(small) == 168, "GL3 positive control incomplete")
    fibers = Counter()
    for matrix in small:
        key, label = coset(matrix, 1, 2)
        fibers[key] += 1
        for k in range(4):
            product, right = 0, target(k, 1, 2)
            for row in range(3):
                value = 0
                for col in range(3):
                    if matrix & (1 << (row * 3 + col)):
                        value ^= (right >> (col * 3)) & 7
                product |= value << (row * 3)
            need(coset(product, 1, 2) == (key, label ^ k), "coset product control")
    need(len(fibers) == 42 and set(fibers.values()) == {4}, "complete coset fibers")
    return {"positive_star_cost": 3, "positive_feedback_cost": 5,
            "gl3_matrices": 168, "exact_coset_products": 672,
            "negative_controls": rejected}


def build():
    restricted = census(H, T, False)
    unrestricted = census(H, T, True)
    need(restricted["lengths"] == unrestricted["lengths"],
         "feedback saving found; do not issue a no-gain certificate")
    missing = restricted["outside_double_radius"]
    need(missing == unrestricted["outside_double_radius"], "different radius misses")
    expected_missing = [k for k in range(1 << (H * T))
                        if sorted((k >> (r * H)) & 7 for r in range(T)) == [3, 5, 6, 7]]
    need(missing == expected_missing and len(missing) == 24, "nine-gate class")
    remaining, representatives = set(range(1 << (H * T))), []
    while remaining:
        k = min(remaining)
        members = orbit(k, H, T)
        need(members <= remaining, "orbit partition")
        length = restricted["lengths"][k]
        need(all(restricted["lengths"][other] == length for other in members),
             "orbit costs differ")
        representatives.append({"k": k, "orbit_size": len(members), "minimum": length,
                                "restricted_witness": restricted["words"][k]})
        remaining -= members
    def stats(result):
        return {key: value for key, value in result.items() if key not in ("lengths", "words")}
    histogram = Counter(restricted["lengths"])
    return {"schema_version": 1, "helpers": H, "targets": T,
            "maps": 1 << (H * T), "gate_cost": 1, "ancillas": 0,
            "all_inputs_arbitrary": True, "radius": RADIUS, "feedback_gains": 0,
            "minimum_histogram": [histogram[i] for i in range(10)],
            "restricted": stats(restricted), "unrestricted": stats(unrestricted),
            "orbits": representatives, "controls": controls()}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def load(path):
    def unique(pairs):
        data = {}
        for key, value in pairs:
            need(key not in data, "duplicate JSON key")
            data[key] = value
        return data
    return json.loads(path.read_text(), object_pairs_hook=unique)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--certificate", type=Path, default=PACKAGE / "CERTIFICATE.json")
    args = parser.parse_args()
    result = build()
    if args.write:
        args.certificate.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(canonical(load(args.certificate)) == canonical(result),
             "certificate differs from complete exact regeneration")
    print("PASS_SHEAR_3X4_COSETS maps=4096 orbits=" + str(len(result["orbits"]))
          + " max_minimum=9 feedback_gains=0 no_new_kappa")


if __name__ == "__main__":
    main()
