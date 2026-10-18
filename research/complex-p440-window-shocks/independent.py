#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate forward-pulse / integer-rank checker; imports no primary code.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance.
This is implementation diversity, not independent human review.
"""
import argparse
from collections import defaultdict
from fractions import Fraction
import gzip
import hashlib
from itertools import combinations
import json
from math import gcd, lcm
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_HASH = "e8e6e78ff7422275c38324499e1f33fb2ecd30de9503aef2b8f1ee80d8c4df8e"


def check(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def amount(g):
    return Fraction(g[3], g[4]) if g[0] == "add" else Fraction(g[2], g[3])


def run(gates, initial, pulses=None):
    state = dict(initial)
    pulses = pulses or {}
    for index in range(len(gates) + 1):
        for donor, change in pulses.get(index, []):
            state[donor] = state.get(donor, 0) + change
            if not state[donor]:
                del state[donor]
        if index == len(gates) or gates[index] is None:
            continue
        g = gates[index]
        value = state.get(g[1], 0)
        value = value + amount(g) * state.get(g[2], 0) if g[0] == "add" else amount(g) * value
        if value:
            state[g[1]] = value
        else:
            state.pop(g[1], None)
    return state


def difference(a, b):
    return {k: a.get(k, 0) - b.get(k, 0) for k in set(a) | set(b) if a.get(k, 0) != b.get(k, 0)}


def normalize(v):
    denom = 1
    for value in v.values():
        denom = lcm(denom, Fraction(value).denominator)
    out = [(k, int(Fraction(v[k]) * denom)) for k in sorted(v)]
    common = 0
    for _, n in out:
        common = gcd(common, n)
    common *= 1 if out[0][1] > 0 else -1
    return tuple((k, n // common) for k, n in out)


def integer_rank(columns):
    """Fraction-free row elimination with gcd reduction; no rational RREF."""
    coordinates = sorted(set().union(*(set(v) for v in columns)))
    matrix = []
    for k in coordinates:
        row = [Fraction(v.get(k, 0)) for v in columns]
        scale = lcm(*(v.denominator for v in row))
        matrix.append([int(v * scale) for v in row])
    rank = 0
    for j in range(len(columns)):
        p = next((i for i in range(rank, len(matrix)) if matrix[i][j]), None)
        if p is None:
            continue
        matrix[rank], matrix[p] = matrix[p], matrix[rank]
        for i in range(rank + 1, len(matrix)):
            if not matrix[i][j]:
                continue
            a, b = matrix[rank][j], matrix[i][j]
            matrix[i] = [a * x - b * y for x, y in zip(matrix[i], matrix[rank])]
            divisor = gcd(*matrix[i])
            if divisor:
                matrix[i] = [x // divisor for x in matrix[i]]
        rank += 1
    return rank


def direct_windows(word):
    B = word["B"]
    check(all(g[1] != 440 for g in B), "pivot is not constant")
    deleted = [i for i, g in enumerate(B) if g[0] == "add" and g[2] == 440]
    check(deleted == [892, 928, 1192], "deletion mismatch")
    seq = B + [word["cleanup"][i] for i, _ in word["early_cleanup"]]
    reduced = [None if i in deleted else g for i, g in enumerate(seq)]
    delta = difference(run(seq, {440: Fraction(1)}), run(reduced, {440: Fraction(1)}))
    readers, writers = defaultdict(list), defaultdict(list)
    for i, g in enumerate(reduced[:len(B)]):
        if g is None:
            continue
        writers[g[1]].append(i)
        if g[0] == "add" and g[2] != 440:
            readers[g[2]].append(i)
    result = []
    zeros = 0
    for donor in sorted(readers):
        for j, start in enumerate(readers[donor]):
            for width in range(1, min(4, len(readers[donor]) - j) + 1):
                reads = readers[donor][j:j + width]
                stop = reads[-1]
                if any(start <= i <= stop for i in writers[donor]):
                    break
                response = run(reduced, {}, {start: [(donor, Fraction(1))],
                                             stop + 1: [(donor, Fraction(-1))]})
                if not response:
                    zeros += 1
                    continue
                result.append({"donor": donor, "start": start, "end": stop + 1,
                               "reads": reads, "response": [[k, str(response[k])] for k in sorted(response)]})
    return delta, result, zeros


def exhaustive_spans(delta, canonical_directions):
    vectors = [dict(d) for d in canonical_directions]
    hit = [i for i, v in enumerate(vectors) if 588 in v]
    miss = [i for i, v in enumerate(vectors) if 588 not in v]
    masks = [sum(1 << k for k in v) for v in vectors]
    candidates = rejected_by_support = rank_checks = 0
    for i in hit:
        factor = delta[588] / Fraction(vectors[i][588])
        remainder = difference(delta, {k: factor * v for k, v in vectors[i].items()})
        check(bool(remainder), "one-direction repair")
        mask = sum(1 << k for k in remainder)
        # Deliberately enumerate ALL unordered pairs with repetition. The
        # primary checker uses an additional rare-coordinate reduction.
        for position, j in enumerate(miss):
            for k in miss[position:]:
                candidates += 1
                if mask & ~(masks[j] | masks[k]):
                    rejected_by_support += 1
                    continue
                rank_checks += 1
                check(integer_rank([vectors[j], vectors[k], remainder]) > integer_rank([vectors[j], vectors[k]]),
                      "repair with one anchor")
    target_mask = sum(1 << k for k in delta)
    for i, j in combinations(hit, 2):
        for k in miss:
            candidates += 1
            if target_mask & ~(masks[i] | masks[j] | masks[k]):
                rejected_by_support += 1
                continue
            rank_checks += 1
            cols = [vectors[i], vectors[j], vectors[k]]
            check(integer_rank(cols + [delta]) > integer_rank(cols), "repair with two anchors")
    for ids in combinations(hit, 3):
        candidates += 1
        rank_checks += 1
        cols = [vectors[i] for i in ids]
        check(integer_rank(cols + [delta]) > integer_rank(cols), "repair with three anchors")
    return {"classified_combinations": candidates, "support_rejections": rejected_by_support,
            "integer_rank_rejections": rank_checks, "repairs": 0}


def literal_map(word, windows=None, omit_close=False):
    """All 704 arbitrary input columns of B plus early cleanup, including dirt."""
    B = word["B"]
    sequence = B + [word["cleanup"][i] for i, _ in word["early_cleanup"]]
    rows = [{i: Fraction(1)} for i in range(704)]
    edits = defaultdict(list)
    for number, w in enumerate(windows or []):
        c = Fraction(w["coefficient"])
        edits[w["start"]].append(["add", w["donor"], 440, c.numerator, c.denominator])
        if not (omit_close and number == 0):
            edits[w["end"]].append(["add", w["donor"], 440, -c.numerator, c.denominator])
    def apply(g):
        target = g[1]
        c = amount(g)
        if g[0] == "scale":
            rows[target] = {k: c * v for k, v in rows[target].items() if c * v}
        else:
            out = dict(rows[target])
            for k, value in rows[g[2]].items():
                out[k] = out.get(k, 0) + c * value
                if not out[k]:
                    del out[k]
            rows[target] = out
    for i, g in enumerate(sequence):
        for edit in edits[i]:
            apply(edit)
        if windows is None or i not in (892, 928, 1192):
            apply(g)
    return [[[k, str(v)] for k, v in sorted(row.items())] for row in rows]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    ap.add_argument("--receipt", type=Path, default=HERE / "INDEPENDENT.json")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()
    raw = (HERE / "inputs/BASE-WORD.json.gz").read_bytes()
    check(hashlib.sha256(raw).hexdigest() == SOURCE_HASH, "independent source mismatch")
    word = json.loads(gzip.decompress(raw))
    delta, windows, zero = direct_windows(word)
    certificate = json.loads(args.certificate.read_text())
    check(sha(windows) == certificate["windows_sha256"], "direct-window response mismatch")
    check([[k, str(delta[k])] for k in sorted(delta)] == certificate["deletion_error"], "direct deletion mismatch")
    directions = sorted({normalize({k: Fraction(v) for k, v in w["response"]}) for w in windows})
    check(sha(directions) == certificate["directions_sha256"], "direction mismatch")
    check((len(windows), len(directions), zero) ==
          (certificate["nonzero_windows"], certificate["projective_directions"], certificate["zero_windows"]), "coverage mismatch")
    counts = exhaustive_spans(delta, directions)
    positive = [
        {"donor": 518, "start": 41, "end": 42, "coefficient": "-1"},
        {"donor": 641, "start": 160, "end": 161, "coefficient": "4"},
        {"donor": 42, "start": 493, "end": 494, "coefficient": "1"},
        {"donor": 106, "start": 527, "end": 528, "coefficient": "1"},
    ]
    original = literal_map(word)
    check(literal_map(word, positive) == original, "four-window full-column identity fails")
    check(literal_map(word, positive, omit_close=True) != original, "missing restore accepted")
    wrong = [dict(w) for w in positive]
    wrong[1]["coefficient"] = "2"
    check(literal_map(word, wrong) != original, "wrong coefficient accepted")
    check(literal_map(word, positive[:3]) != original, "three-window omission accepted")
    result = {"status": "PASS_INDEPENDENT_P440_FORWARD_INTEGER_RANK", "windows": len(windows),
              "directions": len(directions), "zero_windows": zero, "census": counts,
              "formal_columns": 704, "literal_map_sha256": sha(original),
              "controls": ["missing donor close", "wrong donor coefficient", "missing fourth window"]}
    if args.write_receipt:
        args.receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        check(result == json.loads(args.receipt.read_text()), "independent saved receipt mismatch")
    print("PASS_INDEPENDENT_P440_FORWARD_INTEGER_RANK windows=%s directions=%s columns=704 controls=3"
          % (len(windows), len(directions)))


if __name__ == "__main__":
    main()
