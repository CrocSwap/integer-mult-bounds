#!/usr/bin/env python3
"""Six-source universal dirty-connector boundary (standard library only).

Checks, for the PR943 query model:
  * two independently implemented censuses of restored source words on six
    labels at lengths 12 and 14, with the PR943 five-source census as a
    positive control;
  * the explicit length-2^k + 2^(n-k) universal construction for n <= 8;
  * a dense F2 replay of the complete 142-query all-63-row schedule, with
    mutation controls;
  * the exact 142-query optimum for the all-63-row batch;
  * the counting lower bound f(7) >= 18.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


# ---------------------------------------------------------------- census A
def restricted_growth_words(n, length):
    """Words over 0..n-1, labels in first-occurrence order, all counts even >= 2."""
    word, count = [0] * length, [0] * n

    def rec(i, used):
        odd = sum(count[j] & 1 for j in range(used))
        if odd + 2 * (n - used) > length - i:
            return
        if i == length:
            yield tuple(word)
            return
        for j in range(min(used + 1, n)):
            word[i] = j
            count[j] += 1
            yield from rec(i + 1, max(used, j + 1))
            count[j] -= 1

    yield from rec(0, 0)


def coverage_pairwise(word):
    """|D(w)| computed as the set of pairwise XORs of boundary prefixes."""
    prefix, values = 0, {0}
    for j in word:
        prefix ^= 1 << j
        values.add(prefix)
    values = list(values)
    return len({a ^ b for a in values for b in values})


def census_a(n, length):
    hist, records = Counter(), []
    for word in restricted_growth_words(n, length):
        size = coverage_pairwise(word)
        hist[size] += 1
        records.append("".join(map(str, word)) + ":" + str(size))
    return hist, sha256("\n".join(sorted(records)).encode()).hexdigest()


# ---------------------------------------------------------------- census B
def perfect_matchings(points):
    """Pair the least unmatched point with every possible partner."""
    if not points:
        yield []
        return
    first, rest = points[0], points[1:]
    for k, partner in enumerate(rest):
        for tail in perfect_matchings(rest[:k] + rest[k + 1:]):
            yield [(first, partner)] + tail


def canonical(word):
    rename, out = {}, []
    for label in word:
        out.append(rename.setdefault(label, len(rename)))
    return tuple(out)


def coverage_membership(word, n):
    """|D(w)| via the dual test: m is covered iff some prefix p has p^m a prefix."""
    present = [False] * (1 << n)
    prefix = 0
    present[0] = True
    for j in word:
        prefix ^= 1 << j
        present[prefix] = True
    prefixes = [p for p in range(1 << n) if present[p]]
    return sum(1 for m in range(1 << n) if any(present[p ^ m] for p in prefixes))


def census_b(n, length):
    """Words with one label four times (length 2n+2) or all twice (2n)."""
    need(length in (2 * n, 2 * n + 2), "census B covers lengths 2n and 2n+2 only")
    pairs_needed = length // 2
    words = set()
    for matching in perfect_matchings(list(range(length))):
        need(len(matching) == pairs_needed, "matching size")
        groupings = [None] if length == 2 * n else list(combinations(range(pairs_needed), 2))
        for merge in groupings:
            word, label = [None] * length, 0
            for index, (a, b) in enumerate(matching):
                if merge is not None and index == merge[1]:
                    continue
                word[a] = word[b] = label
                if merge is not None and index == merge[0]:
                    c, d = matching[merge[1]]
                    word[c] = word[d] = label
                label += 1
            words.add(canonical(word))
    hist, records = Counter(), []
    for word in words:
        size = coverage_membership(word, n)
        hist[size] += 1
        records.append("".join(map(str, word)) + ":" + str(size))
    return hist, sha256("\n".join(sorted(records)).encode()).hexdigest()


# ------------------------------------------------------------ construction
def gray_cycle(coordinates):
    """Closed reflected Gray walk through every point of the given coordinates."""
    if len(coordinates) == 1:
        return [coordinates[0], coordinates[0]]
    flips = []
    for t in range(1, 1 << len(coordinates)):
        flips.append(coordinates[(t & -t).bit_length() - 1])
    return flips + [coordinates[-1]]


def universal_word(n):
    k = (n + 1) // 2
    first = list(range(k))
    second = list(range(k, n))
    return gray_cycle(first) + (gray_cycle(second) if second else [])


def prefixes(word):
    out, p = [0], 0
    for j in word:
        p ^= 1 << j
        out.append(p)
    return out


def schedule_for_all_rows(n, word):
    """Place each nonzero row's two A readouts at boundaries realizing its mask."""
    pre = prefixes(word)
    first_at = {}
    for t, p in enumerate(pre):
        first_at.setdefault(p, t)
    slots = []
    for mask in range(1, 1 << n):
        hit = next(((first_at[p], first_at[p ^ mask]) for p in first_at if p ^ mask in first_at), None)
        need(hit is not None, f"mask {mask} uncovered")
        slots.append(sorted(hit))
    ops = []
    for t in range(len(word) + 1):
        for i, pair in enumerate(slots):
            ops.extend(("A", i) for s in pair if s == t)
        if t < len(word):
            ops.append(("B", word[t]))
    return ops


# ------------------------------------------------------------ dense replay
def apply(matrix, vector):
    return sum(1 << r for r, row in enumerate(matrix) if bin(row & vector).count("1") & 1)


def random_matrix(rng, d):
    return [rng.randrange(1 << d) for _ in range(d)]


def replay(n, ops, rows, d, rng, trials):
    """y_i += sum_j M_ij A_i B_j x_j with x, z restored, on arbitrary dirty data."""
    for _ in range(trials):
        B = [random_matrix(rng, d) for _ in range(n)]
        A = [random_matrix(rng, d) for _ in rows]
        x = [rng.randrange(1 << d) for _ in range(n)]
        y0 = [rng.randrange(1 << d) for _ in rows]
        z0 = rng.randrange(1 << d)
        y, z = y0[:], z0
        for kind, index in ops:
            if kind == "B":
                z ^= apply(B[index], x[index])
            else:
                y[index] ^= apply(A[index], z)
        if z != z0:
            return False
        for i, mask in enumerate(rows):
            want = y0[i]
            for j in range(n):
                if mask >> j & 1:
                    want ^= apply(A[i], apply(B[j], x[j]))
            if y[i] != want:
                return False
    return True


def mutations(ops):
    b_positions = [k for k, op in enumerate(ops) if op[0] == "B"]
    a_positions = [k for k, op in enumerate(ops) if op[0] == "A"]
    yield "omitted_final_source", ops[:b_positions[-1]] + ops[b_positions[-1] + 1:]
    moved = ops[:]
    k = a_positions[len(a_positions) // 2]
    op = moved.pop(k)
    moved.insert(b_positions[0], op) if k > b_positions[0] else moved.insert(len(moved), op)
    yield "moved_readout", moved
    dropped = ops[:a_positions[0]] + ops[a_positions[0] + 1:]
    yield "single_readout", dropped
    retarget = ops[:]
    retarget[a_positions[0]] = ("A", (retarget[a_positions[0]][1] + 1) % (len(a_positions) // 2))
    yield "wrong_output_destination", retarget


# ------------------------------------------------------------------ bounds
def counting_lower_bound(n):
    """Least even L allowing |P| <= L prefixes with |D| = 2^n, by parity counts."""
    L = 2 * n
    while True:
        half = L // 2
        ok = any(
            e * o >= 1 << (n - 1) and e * (e - 1) // 2 + o * (o - 1) // 2 + 1 >= 1 << (n - 1)
            for e in range(1, half + 1) for o in range(1, half + 1)
        )
        if ok:
            return L
        L += 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-expected", action="store_true")
    args = parser.parse_args()
    result = {"censuses": [], "constructions": {}, "batch": {}, "controls": {}}

    # Positive control: PR943's five-source histogram.
    pr943 = {16: 42, 19: 120, 21: 180, 22: 56, 23: 45, 24: 220, 26: 110, 28: 150, 31: 22}
    for n, length in ((5, 10), (6, 12), (6, 14)):
        ha, da = census_a(n, length)
        hb, db = census_b(n, length)
        need(ha == hb and da == db, f"census disagreement n={n} L={length}")
        if (n, length) == (5, 10):
            need(dict(ha) == pr943, "PR943 five-source histogram not reproduced")
        need(max(ha) < 1 << n, f"unexpected full-coverage word n={n} L={length}")
        result["censuses"].append({
            "sources": n, "length": length, "words": sum(ha.values()),
            "max_coverage": max(ha), "masks": 1 << n,
            "histogram": {str(k): ha[k] for k in sorted(ha)}, "records_sha256": da,
        })

    for n in range(1, 9):
        word = universal_word(n)
        need(coverage_pairwise(word) == 1 << n, f"construction fails n={n}")
        need(all(word.count(j) % 2 == 0 and word.count(j) >= 2 for j in range(n)), "restoration")
        k = (n + 1) // 2
        need(len(word) == (1 << k) + ((1 << (n - k)) if n > k else 0), "length formula")
        result["constructions"][str(n)] = {"length": len(word), "lower_bound": counting_lower_bound(n),
                                           "word": word}
    need(result["constructions"]["6"]["length"] == 16, "six-source witness length")
    need(result["constructions"]["7"]["lower_bound"] == 18, "f(7) counting bound")

    # Exact all-63-row batch optimum: |w| + sum of readouts, each row even >= 2.
    n, rows = 6, list(range(1, 64))
    floor = {}
    for c in result["censuses"]:
        if c["sources"] == 6:
            uncovered = (len(rows) + 1) - c["max_coverage"]
            floor[c["length"]] = c["length"] + 2 * len(rows) + 2 * uncovered
    floor[16] = 16 + 2 * len(rows)
    need(floor == {12: 168, 14: 150, 16: 142}, "batch floors")
    ops = schedule_for_all_rows(n, result["constructions"]["6"]["word"])
    need(len(ops) == 142, "witness schedule length")
    rng = random.Random(20261013)
    for d in (1, 2, 3):
        need(replay(n, ops, rows, d, rng, 40), f"dense replay failed d={d}")
        need(replay(n, ops[::-1], rows, d, rng, 20), f"inverse-order replay failed d={d}")
    detected = []
    for name, bad in mutations(ops):
        need(not replay(n, bad, rows, 3, random.Random(7), 40), f"control not detected: {name}")
        detected.append(name)
    result["batch"] = {"sources": 6, "rows": 63, "optimum_queries": 142,
                       "floor_by_source_length": {str(k): v for k, v in sorted(floor.items())},
                       "witness_ops_sha256": sha256(json.dumps(ops).encode()).hexdigest()}
    result["controls"] = {"dense_dimensions": [1, 2, 3], "mutations_detected": detected}

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    path = ROOT / "EXPECTED.json"
    if args.write_expected:
        path.write_text(text)
    else:
        need(path.read_text() == text, "EXPECTED.json mismatch")
    print("PASS_SIX_SOURCE_CONNECTOR f(6)=16 max14=59/64 max12=49/64 batch63=142 f(7) in [18,24]")


if __name__ == "__main__":
    main()
