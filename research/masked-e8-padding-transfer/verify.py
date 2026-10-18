#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact masked E8 decoder transfers. Standard library; no predecessor imports."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
from fractions import Fraction as Q
from math import lcm
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LIMIT = 120
MAX_TERMS = 256
MAX_BYTES = 16 * 1024 * 1024


def need(ok, message):
    if not ok:
        raise ValueError(message)


def geometry():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for a, b in itertools.product((2, -2), repeat=2):
            r = [0] * 8
            r[i], r[j] = a, b
            roots.append(tuple(r))
    roots.extend(s for s in itertools.product((1, -1), repeat=8) if sum(s) % 4 == 0)
    lines, seen = [], set()
    for r in roots:
        key = max(r, tuple(-v for v in r))
        if key not in seen:
            seen.add(key)
            lines.append(r)
    need(len(roots) == 240 and len(lines) == LIMIT, "E8 line count")
    dots = [[sum(a * b for a, b in zip(r, s, strict=True)) for s in lines] for r in lines]
    need(all(v % 4 == 0 for row in dots for v in row), "integral E8 pairing")
    pairing = [sum(((v // 4 + 1) % 2) << j for j, v in enumerate(row)) for row in dots]
    return tuple(lines), tuple(pairing)


LINES, PAIRING = geometry()


def rank2(rows):
    """At most 120 rows, each with at most 120 bits."""
    basis = [0] * LIMIT
    rank = 0
    for original in rows:
        value = original
        for bit in range(LIMIT - 1, -1, -1):
            if value >> bit & 1:
                if basis[bit]:
                    value ^= basis[bit]
                else:
                    basis[bit] = value
                    rank += 1
                    break
    return rank


def span_rank(rows):
    """Independent oracle: enumerate the row span, at most 2^9 elements."""
    span = {0}
    for row in rows:
        extension = {v ^ row for v in span}
        span.update(extension)
        need(len(span) <= 512, "E8 row-span capacity")
    size = len(span)
    need(size == 1 << (size.bit_length() - 1), "binary span cardinality")
    return size.bit_length() - 1


def costs(terms):
    result = []
    for left, right in terms:
        columns = sum(1 << j for j, v in enumerate(right) if v)
        rows = [PAIRING[i] & columns for i, v in enumerate(left) if v]
        rank = rank2(rows)
        need(rank == span_rank(rows), "independent binary rank disagreement")
        result.append(rank)
    return result


def checked_denominator(live, terms):
    need(len(live) <= LIMIT and len(set(live)) == len(live), "duplicate/too many lines")
    need(all(type(i) is int and 0 <= i < LIMIT for i in live), "line ID")
    need(len(terms) <= MAX_TERMS, "term capacity")
    allowed, denominator = set(live), 1
    for left, right in terms:
        need(len(left) == len(right) == LIMIT, "factor width")
        for vector in (left, right):
            for i, v in enumerate(vector):
                need(type(v) is Q and v.numerator.bit_length() <= 256
                     and v.denominator.bit_length() <= 256, "coefficient domain")
                need(not v or i in allowed, "support outside live set")
                denominator = lcm(denominator, v.denominator)
                need(denominator.bit_length() <= 256, "common denominator capacity")
    return denominator


def validate(live, terms):
    denominator = checked_denominator(live, terms)
    matrix = [[0] * LIMIT for _ in range(LIMIT)]
    for left, right in terms:
        rows = [(i, v.numerator * (denominator // v.denominator))
                for i, v in enumerate(left) if v]
        cols = [(j, v.numerator * (denominator // v.denominator))
                for j, v in enumerate(right) if v]
        for i, a in rows:
            for j, b in cols:
                matrix[i][j] += a * b
    for i in live:
        need(matrix[i][i] == denominator ** 2, "diagonal is not one")
        for j in live:
            if i != j and PAIRING[i] >> j & 1:
                need(matrix[i][j] == 0, "forbidden off-diagonal")
    mismatches = sum(8 * matrix[i][j] != denominator ** 2
                     * sum(a * b for a, b in zip(LINES[i], LINES[j], strict=True))
                     for i in live for j in live)
    ranks = costs(terms)
    return {"lines": len(live), "terms": len(terms), "ranks": ranks,
            "cost": sum(ranks), "all_pairs_mismatches": mismatches}


def restrict(terms, live):
    allowed = set(live)
    return tuple((tuple(v if i in allowed else Q(0) for i, v in enumerate(left)),
                  tuple(v if i in allowed else Q(0) for i, v in enumerate(right)))
                 for left, right in terms)


def identity_terms(live):
    return tuple((tuple(Q(i == a) for i in range(LIMIT)),) * 2 for a in live)


def frame_indices():
    frame = []
    for a in range(4):
        for sign in (2, -2):
            r = [0] * 8
            r[2 * a], r[2 * a + 1] = 2, sign
            frame.append(LINES.index(tuple(r)))
    return tuple(frame)


def frame_terms():
    terms = []
    for f in frame_indices():
        v = tuple(Q(sum(a * b for a, b in zip(r, LINES[f], strict=True)), 8) for r in LINES)
        terms.append((v, v))
    return tuple(terms)


def check_pins(root=ROOT):
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            payload = (root / row["path"]).read_bytes()
            need(hashlib.sha256(payload).hexdigest() == row["sha256"], "source hash: " + row["path"])


def load_hit(name, live):
    path = ROOT / "research/complex-frame-pair-decoders/inputs/pr717" / name
    rows = path.read_text(encoding="utf-8").splitlines()
    left = [line.split(":", 1)[1].split() for line in rows if line.strip().startswith("d:")]
    right = [line.split(":", 1)[1].split() for line in rows if line.strip().startswith("t:")]
    need(len(left) == len(right) == 8, "fixture term count")
    terms = []
    for a, b in zip(left, right, strict=True):
        need(len(a) == len(b) == len(live), "fixture port count")
        u, v = [Q(0)] * LIMIT, [Q(0)] * LIMIT
        for i, x, y in zip(live, a, b, strict=True):
            u[i], v[i] = Q(int(x), 2), Q(int(y), 2)
        terms.append((tuple(u), tuple(v)))
    return tuple(terms)


def fixtures():
    full = tuple(range(LIMIT))
    f = frame_indices()
    p112 = tuple(i for i in full if i not in f)
    cases = [("P120", full, frame_terms(), 72),
             ("P112", p112, restrict(frame_terms(), p112), 64)]
    for name, extra, expected in (
        ("P104_HIT_flip_3a.txt", (9, 15, 24, 46, 52, 66, 94, 104), 56),
        ("P111_HIT_g0.txt", (0,), 63), ("P111_HIT_g111.txt", (111,), 63),
    ):
        live = tuple(i for i in p112 if i not in {p112[j] for j in extra})
        cases.append((name, live, load_hit(name, live), expected))
    receipt = {}
    for name, live, terms, expected in cases:
        before = validate(live, terms)
        need(before["cost"] == expected, "fixture cost: " + name)
        need(before["all_pairs_mismatches"] == 0, "original all-pairs fixture: " + name)
        missing = tuple(i for i in full if i not in live)
        padded = validate(full, terms + identity_terms(missing))
        need(padded["cost"] == expected + len(missing) == 72, "padding invoice")
        need(bool(padded["all_pairs_mismatches"]) == bool(missing), "all-pairs scope control")
        receipt[name] = {"original": before, "padded": padded}
    return receipt


def transfers():
    full = tuple(range(LIMIT))
    terms = frame_terms()
    # Exhaust every restriction of a fixed six-line domain. This is a finite
    # transfer check, not an enumeration of optimal decoders on those sets.
    tiny = tuple(range(6))
    base = restrict(terms, tiny)
    original = validate(tiny, base)["ranks"]
    for mask in range(1 << len(tiny)):
        live = tuple(i for i in tiny if mask >> i & 1)
        reduced = restrict(base, live)
        record = validate(live, reduced)
        need(all(a <= b for a, b in zip(record["ranks"], original, strict=True)),
             "restriction rank increased")
        missing = tuple(i for i in tiny if i not in live)
        padded = validate(tiny, reduced + identity_terms(missing))
        need(padded["cost"] == record["cost"] + len(missing), "restriction/padding identity")
    even = tuple(i for i in full if i % 2 == 0)
    odd = tuple(i for i in full if i % 2)
    glued = restrict(terms, even) + restrict(terms, odd)
    result = validate(full, glued)
    need(result["cost"] == validate(even, restrict(terms, even))["cost"]
         + validate(odd, restrict(terms, odd))["cost"], "disjoint gluing cost")
    return {"six_line_subsets": 64, "disjoint_gluing": result}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_candidate(path):
    need(path.is_file(), "candidate must be a regular file")
    with path.open("rb") as stream:
        payload = stream.read(MAX_BYTES + 1)
    need(len(payload) <= MAX_BYTES, "candidate byte capacity")
    data = json.loads(payload.decode("utf-8"), object_pairs_hook=unique_object)
    need(type(data) is dict and set(data) == {"live", "terms"}, "candidate fields")
    live, raw = data["live"], data["terms"]
    need(type(live) is list and len(live) <= LIMIT, "live capacity")
    need(all(type(i) is int and 0 <= i < LIMIT for i in live), "line ID")
    need(len(set(live)) == len(live), "duplicate line ID")
    need(type(raw) is list and len(raw) <= MAX_TERMS, "term capacity")
    terms = []
    for row in raw:
        need(type(row) is dict and set(row) == {"left", "right"}, "term fields")
        factors = []
        for side in ("left", "right"):
            values = row[side]
            need(type(values) is list and len(values) == len(live), "factor width")
            vector = [Q(0)] * LIMIT
            for i, value in zip(live, values, strict=True):
                need(type(value) in (str, int) and len(str(value)) <= 128, "rational coefficient")
                need(re.fullmatch(r"-?[0-9]+(?:/[0-9]+)?", str(value)) is not None,
                     "rational coefficient syntax")
                vector[i] = Q(value)
            factors.append(tuple(vector))
        terms.append(tuple(factors))
    return tuple(live), tuple(terms)


def encode(live, terms):
    return {"live": list(live), "terms": [
        {"left": [str(a[i]) for i in live], "right": [str(b[i]) for i in live]}
        for a, b in terms]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, help="validate a rational masked decoder JSON")
    parser.add_argument("--pad-output", type=Path, help="exclusively create its padded P120 decoder")
    args = parser.parse_args()
    try:
        check_pins()
        need(args.candidate is not None or args.pad_output is None, "padding needs --candidate")
        if args.candidate is not None:
            live, terms = read_candidate(args.candidate)
            record = validate(live, terms)
            if args.pad_output is not None:
                missing = tuple(i for i in range(LIMIT) if i not in live)
                padded = terms + identity_terms(missing)
                padded_record = validate(tuple(range(LIMIT)), padded)
                need(padded_record["cost"] == record["cost"] + len(missing), "padded cost")
                with args.pad_output.open("x", encoding="utf-8") as stream:
                    stream.write(json.dumps(encode(tuple(range(LIMIT)), padded), indent=2) + "\n")
                record = {"original": record, "padded": padded_record}
        else:
            need(rank2(PAIRING) == 9, "binary E8 pairing rank")
            record = {"fixtures": fixtures(), "transfers": transfers()}
        print(json.dumps(record, sort_keys=True, indent=2))
        print("PASS_MASKED_E8_PADDING_TRANSFER")
    except (ValueError, KeyError, TypeError, OSError, ZeroDivisionError, RecursionError) as exc:
        parser.exit(1, "REJECT: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
