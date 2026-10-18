#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact corroboration of the written UT4 one-slack workspace reduction.

Prepared for @ToikY with substantial OpenAI Codex assistance.
Finite fixtures do not establish 14/15-call existence or kernel formalization.
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LETTERS = {"a": 1, "b": 2, "c": 4}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sibling(name):
    spec = importlib.util.spec_from_file_location("ut4_workspace_" + name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rank(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            p = vector.bit_length() - 1
            if p not in pivots:
                pivots[p] = vector
                break
            vector ^= pivots[p]
    return len(pivots)


def identity(r):
    return [1 << i for i in range(r)]


def mul(a, b):
    out = []
    for row in a:
        value = 0
        while row:
            bit = row & -row
            value ^= b[bit.bit_length() - 1]
            row ^= bit
        out.append(value)
    return out


def outer(x, y, r):
    return [y if (x >> i) & 1 else 0 for i in range(r)]


@lru_cache(maxsize=4096)
def group_product(g, h):
    a, b, c, d, e, f = [(g >> i) & 1 for i in range(6)]
    A, B, C, D, E, F = [(h >> i) & 1 for i in range(6)]
    values = (a ^ A, b ^ B, c ^ C, d ^ D ^ (a & B),
              e ^ E ^ (b & C), f ^ F ^ (a & E) ^ (d & C))
    return sum(v << i for i, v in enumerate(values))


def factors(word, r):
    require(type(r) is int and r >= 1, "invalid role count")
    checked = []
    for label, x, y in word:
        require(label in LETTERS and type(x) is int and type(y) is int
                and 0 < x < (1 << r) and 0 < y < (1 << r), "invalid paid alphabet")
        checked.append((label, x, y))
    return checked


def formal_product(word, r):
    result = {0: identity(r)}
    for label, x, y in factors(word, r):
        updated = {g: rows[:] for g, rows in result.items()}
        for g, rows in result.items():
            increment = mul(rows, outer(x, y, r))
            for h in (g, group_product(g, LETTERS[label])):
                updated[h] = [a ^ b for a, b in zip(updated.get(h, [0] * r), increment)]
        result = {g: rows for g, rows in updated.items() if any(rows)}
    return result


def active_corner(formal, w):
    mask = (1 << w) - 1
    projected = {g: [row & mask for row in rows[:w]] for g, rows in formal.items()}
    return {g: rows for g, rows in projected.items() if any(rows)}


def regular_columns(formal, r):
    columns = []
    for role in range(r):
        for h in range(64):
            column = 0
            for g, rows in formal.items():
                for i, row in enumerate(rows):
                    if (row >> role) & 1:
                        column ^= 1 << (64 * i + group_product(g, h))
            columns.append(column)
    return columns


def compress(word, r, w):
    require(type(w) is int and 1 <= w <= r, "invalid active width")
    word = factors(word, r)
    columns = all(x >> w == 0 for _, x, _ in word)
    rows = all(y >> w == 0 for _, _, y in word)
    require(columns or rows, "no common triangular orientation")
    mask = (1 << w) - 1
    return [(g, x & mask, y & mask) for g, x, y in word if x & mask and y & mask]


def one_slack_orientation(w, counts, spans):
    """Check the integer rank-budget implication, assuming the stated containments.

    The full word's coefficient equations supply those containments in PROOF.md;
    this function never accepts an endpoint from ranks alone.
    """
    require(type(w) is int and w >= 2, "one-slack theorem requires w>=2")
    require(len(counts) == 3 and len(spans) == 6
            and all(type(n) is int and n >= 0 for n in counts + spans), "invalid rank profile")
    require(all(n >= w for n in spans), "missing target span rank")
    require(counts[0] >= spans[0] + spans[1]
            and counts[1] >= w + spans[2] + spans[3]
            and counts[2] >= spans[4] + spans[5], "rank budget violation")
    require(sum(counts) <= 7 * w + 1, "outside one-slack length threshold")
    require(all(spans[i] == w for i in (0, 2, 4))
            or all(spans[i] == w for i in (1, 3, 5)), "no shared orientation")
    return {"columns": all(spans[i] == w for i in (0, 2, 4)),
            "rows": all(spans[i] == w for i in (1, 3, 5))}


def target(r, w):
    P = [1 << i if i < w else 0 for i in range(r)]
    return {g: rows for g, rows in {0: [a ^ b for a, b in zip(identity(r), P)], 32: P}.items()
            if any(rows)}


def source_checks():
    for source in json.loads((HERE / "SOURCES.json").read_text())["files"]:
        if source["usage"] == "input":
            require(hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["sha256"],
                    "pinned model source changed")
    vendor = json.loads((HERE / "VENDOR.json").read_text())
    require(hashlib.sha256((HERE / "quotient.py").read_bytes()).hexdigest() == vendor["sha256"],
            "pinned quotient source changed")


def build_receipt():
    source_checks()
    independent, quotient = sibling("independent"), sibling("quotient")
    require(all(group_product(g, h) == independent.multiply_addresses(g, h)
                for g in range(64) for h in range(64)), "literal group mismatch")
    profiles = []
    for w in range(2, 17):
        for exception in range(-1, 6):
            spans = [w] * 6
            if exception >= 0:
                spans[exception] += 1
            counts = [spans[0] + spans[1], w + spans[2] + spans[3], spans[4] + spans[5]]
            profiles.append([w, counts, spans, one_slack_orientation(w, counts, spans)])
    transcript, pairs, dropped = hashlib.sha256(), 0, 0
    for orientation in ("columns", "rows"):
        alphabet = [(g, x, y) for g in LETTERS
                    for x in range(1, 4 if orientation == "columns" else 8)
                    for y in range(1, 8 if orientation == "columns" else 4)]
        for word in itertools.product(alphabet, repeat=2):
            compressed = compress(word, 3, 2)
            full = formal_product(word, 3)
            small = formal_product(compressed, 2)
            require(active_corner(full, 2) == small, "formal compression mismatch")
            faithful = independent.regular_columns(word, 3)
            require(regular_columns(full, 3) == faithful, "independent full operator mismatch")
            require([c & ((1 << 128) - 1) for c in faithful[:128]]
                    == independent.regular_columns(compressed, 2), "faithful compression mismatch")
            pairs += 1
            dropped += len(word) - len(compressed)
            transcript.update(json.dumps([orientation, word, compressed, small], sort_keys=True).encode())
    witnesses, witness_columns = 0, 0
    for r in range(2, 6):
        for w in range(2, r + 1):
            word = [(g, 1 << i, 1 << i) for i in range(w) for g in "abcbabcb"]
            formal = formal_product(word, r)
            require(formal == target(r, w), "known upper word endpoint")
            require(regular_columns(formal, r) == independent.regular_columns(word, r), "upper faithful mismatch")
            data = quotient.word_coefficients(word, r)
            P = [1 << i if i < w else 0 for i in range(r)]
            require(all(data[k] == P for k in ("abc", "cba", "bac", "acb")), "retained target coefficients")
            require(all(not any(data[k]) for k in ("a", "b", "c", "ab", "bc")), "retained lower coefficients")
            require(formal_product(compress(word, r, w), w) == target(w, w), "known upper word compression")
            witnesses += 1
            witness_columns += 64 * r
    mixed = [("a", 1, 4), ("b", 4, 1)]
    require(active_corner(formal_product(mixed, 3), 2) != formal_product([], 2), "mixed feedback control")
    try:
        compress(mixed, 3, 2)
    except ValueError as error:
        require(str(error) == "no common triangular orientation", "wrong mixed rejection")
    else:
        raise ValueError("mixed orientation accepted")
    require(rank([1, 4]) == 2 and rank([1, 4, 2]) == 3, "rank alone misses active containment")
    return {"schema_version": 1, "uniform_scope": "w>=2,L<=7w+1,r>=w; written proof, not finite extrapolation",
            "two_target_minimum": "C_r=C_2 in {14,15,16}; exact value unresolved",
            "quotient": quotient.self_checks(), "independent": independent.self_checks(),
            "rank_profiles": len(profiles), "rank_profile_sha256": hashlib.sha256(json.dumps(profiles, sort_keys=True).encode()).hexdigest(),
            "ordered_triangular_pairs": pairs, "pair_roles": 3, "active_width": 2,
            "dropped_factor_occurrences": dropped, "pair_transcript_sha256": transcript.hexdigest(),
            "known_upper_witnesses": witnesses, "full_witness_basis_columns": witness_columns,
            "mixed_feedback_rejected": True,
            "equal_rank_wrong_target_plane_control": {"candidate_basis": [1, 4], "active_basis": [1, 2],
                                                        "candidate_rank": 2, "union_rank": 3},
            "new_14_or_15_word": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    if args.write_receipt:
        require(not args.write_receipt.exists(), "output already exists")
    receipt = build_receipt()
    raw = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    if args.write_receipt:
        with args.write_receipt.open("x") as stream:
            stream.write(raw)
    else:
        require(json.dumps(json.loads((HERE / "CERTIFICATE.json").read_text()), sort_keys=True)
                == json.dumps(receipt, sort_keys=True), "certificate differs")
    print("PASS_UT4_ONE_SLACK_WORKSPACE pairs=" + str(receipt["ordered_triangular_pairs"])
          + " unit_two_target_minimum=workspace_independent exact_value_unresolved")


if __name__ == "__main__":
    main()
