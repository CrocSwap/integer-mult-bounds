#!/usr/bin/env python3
"""Sharp source-shear invoice; Arham Tahir / OpenAI Codex, Apache-2.0."""
import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
POINTS = [0, 4, 5, 1, 3, 7, 6, 14, 28, 16, 0]
HEAD = "f1dcab36fa63f8226f70dd07e26f44afb9d39b51"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def pins():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    live = [r for r in manifest["files"] if r["usage"] == "input"]
    need(sorted(r["path"] for r in live) == ["research/universal-connector-boundary/" + n
         for n in ("CERTIFICATE.json", "NOTICE.md", "README.md")], "live source inventory")
    for row in live:
        data = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"], "live source drift")
    predecessor = json.loads((HERE / "PREDECESSOR.json").read_text())
    need(predecessor["pr"] == 1340 and predecessor["head"] == HEAD, "predecessor identity")
    need(sorted(r["local_path"] for r in predecessor["files"]) ==
         ["sources/CERTIFICATE.json", "sources/PROOF.md", "sources/README.md"], "predecessor inventory")
    for row in predecessor["files"]:
        data = (HERE / row["local_path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"], "predecessor drift")
        need(hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
             == row["git_blob"], "predecessor Git blob")
    return json.loads((HERE / "sources/CERTIFICATE.json").read_text())


def pair_words(prefix=(), counts=()):
    if len(prefix) == 10:
        yield prefix
        return
    for label in range(len(counts) + (len(counts) < 5)):
        if label == len(counts):
            yield from pair_words(prefix + (label,), counts + (1,))
        elif counts[label] < 2:
            newer = list(counts)
            newer[label] += 1
            yield from pair_words(prefix + (label,), tuple(newer))


def pairing_census():
    histogram = Counter()
    records = []
    for word in pair_words():
        q = [0]
        for label in word:
            q.append(q[-1] ^ (1 << label))
        coverage = sorted({a ^ b for a in q for b in q})
        histogram[len(coverage)] += 1
        records.append([list(word), coverage])
    need(len(records) == 945 and max(histogram) == 31, "paired-path exclusion")
    return dict(sorted(histogram.items())), digest(sorted(records))


def short_shears():
    gates = [(s, t) for s in range(5) for t in range(5) if s != t]
    identity = tuple(1 << j for j in range(5))
    restored_counts = []
    for length in range(4):
        restored = 0
        for word in product(gates, repeat=length):
            rows = list(identity)
            for source, target in word:
                rows[target] ^= rows[source]
            if tuple(rows) == identity:
                restored += 1
                need(length == 0 or (length == 2 and word[0] == word[1]), "unexpected short identity")
        restored_counts.append(restored)
    need(restored_counts == [1, 0, 20, 0], "short source-restoration counts")
    # With a repeated shear 0->1, ten queries and connector restoration
    # force all query-label counts and the number of middle 1 queries even.
    # Exhaust the resulting multiplicity reductions; full span leaves
    # five effective independent directions, each used exactly twice.
    cases = Counter()
    for counts in product(range(0, 11, 2), repeat=5):
        if sum(counts) != 10:
            continue
        for middle in range(0, counts[1] + 1, 2):
            directions = [1 << j for j, n in enumerate(counts) if n and j != 1]
            if counts[1] > middle:
                directions.append(2)
            if middle:
                directions.append(3)
            basis = {}
            for value in directions:
                while value:
                    bit = value.bit_length() - 1
                    if bit in basis:
                        value ^= basis[bit]
                    else:
                        basis[bit] = value
                        break
            if len(basis) < 5:
                continue
            multiplicities = [n for j, n in enumerate(counts) if n and j != 1]
            multiplicities += [n for n in (counts[1] - middle, middle) if n]
            need(sorted(multiplicities) == [2] * 5, "two-shear normal form")
            cases["all_labels_twice" if all(counts) else "absent_donor"] += 1
    return {"restored_words_by_length": restored_counts,
            "full_span_even_multiplicity_cases": dict(sorted(cases.items()))}


def make_word(points):
    need(len(points) == 11 and points[0] == points[-1] == 0, "ten-query closed path")
    need(len(set(points)) == 10 and all(type(q) is int and 0 <= q < 32 for q in points), "boundary points")
    pairs, readouts = [], [[] for _ in points]
    for mask in range(1, 32):
        pair = next(((s, t) for s in range(11) for t in range(s + 1, 11)
                     if points[s] ^ points[t] == mask), None)
        need(pair is not None, "missing output mask")
        pairs.append(list(pair))
        for boundary in pair:
            readouts[boundary].append(mask)
    word = []
    for boundary in range(11):
        word += [("A" + str(m), 36, 4 + m) for m in readouts[boundary]]
        if boundary == 10:
            continue
        bits = [j for j in range(5) if (points[boundary] ^ points[boundary + 1]) >> j & 1]
        pivot, *others = bits
        word += [("X", j, pivot) for j in others]
        word.append(("B", pivot, 36))
        word += [("X", j, pivot) for j in reversed(others)]
    return word, pairs


def lower(tokens, source, target, scratch):
    need(source != target and source not in scratch and target not in scratch, "scratch/port alias")
    if len(tokens) == 1:
        return [(tokens[0], source, target)]
    need(bool(scratch), "insufficient dirty scratch")
    mid = len(tokens) // 2
    r = lower(tokens[:mid], source, scratch[0], scratch[1:])
    l = lower(tokens[mid:], scratch[0], target, scratch[1:])
    return r + l + r[::-1] + l[::-1]


def expand(word):
    result = []
    for op, source, target in word:
        if op == "X":
            need(0 <= source < 5 and 0 <= target < 5 and source != target, "illegal source shear")
            result.append((op, source, target))
        else:
            result += lower([op + ":" + str(j) for j in range(5)], source, target, [37, 38, 39])
    return result


def free_map(word):
    # All incoming dirty rows are distinct free module basis elements.
    rows = [{(j, ())} for j in range(40)]
    for op, source, target in word:
        need(source != target and 0 <= source < 40 and 0 <= target < 40, "gate ports")
        image = {(j, tokens + (() if op == "X" else (op,))) for j, tokens in rows[source]}
        rows[target].symmetric_difference_update(image)
    return rows


def desired(expanded=False):
    rows = [{(j, ())} for j in range(40)]
    for mask in range(1, 32):
        tokens = (("B", "A" + str(mask)) if not expanded else
                  tuple("B:" + str(j) for j in range(5)) +
                  tuple("A" + str(mask) + ":" + str(j) for j in range(5)))
        rows[4 + mask] |= {(j, tokens) for j in range(5) if mask >> j & 1}
    return rows


def rejected(action):
    try:
        action()
    except (ValueError, KeyError, IndexError):
        return
    raise ValueError("failure control unexpectedly accepted")


def controls(word, expanded):
    def unequal(candidate, expected):
        need(free_map(candidate) == expected, "deliberate semantic mismatch")
    first_x = next(i for i, g in enumerate(word) if g[0] == "X")
    first_b = next(i for i, g in enumerate(word) if g[0] == "B")
    rejected(lambda: unequal([g for i, g in enumerate(word) if i != first_x], desired()))
    rejected(lambda: unequal([g for i, g in enumerate(word) if i != first_b], desired()))
    changed = list(word)
    i = next(i for i, g in enumerate(changed) if g[0] == "A1")
    changed[i] = ("A2", 36, 5)
    rejected(lambda: unequal(changed, desired()))
    rejected(lambda: unequal([(op + str(s) if op == "B" else op, s, t) for op, s, t in word], desired()))
    rejected(lambda: lower(["B:0", "B:1"], 0, 36, [0]))
    rejected(lambda: unequal([(op.replace("B:0", "TEMP").replace("B:4", "B:0").replace("TEMP", "B:4"), s, t)
                             for op, s, t in expanded], desired(True)))
    rejected(lambda: make_word(POINTS[:-2] + [POINTS[-3], 0]))
    return 7


def compute():
    predecessor = pins()
    word, pairs = make_word(POINTS)
    expanded = expand(word)
    for candidate, target in ((word, desired()), (word[::-1], desired()),
                              (expanded, desired(True)), (expanded[::-1], desired(True))):
        need(free_map(candidate) == target, "complete free noncommutative map")
    old_word, _ = make_word(predecessor["points"])
    need(free_map(old_word) == desired(), "predecessor map")
    counts = Counter(op if op in ("B", "X") else "A" for op, _, _ in word)
    need(dict(counts) == {"A": 62, "B": 10, "X": 4}, "candidate invoice")
    need(Counter(op if op in ("B", "X") else "A" for op, _, _ in old_word)
         == predecessor["root_counts"], "predecessor invoice")
    histogram, pairing_hash = pairing_census()
    shear_receipt = short_shears()
    leaves = sum(op != "X" for op, _, _ in expanded)
    xors = len(expanded) - leaves
    nodes = 72 * 9
    # Explicitly pay each complete leaf/XOR, internal node and root dispatch.
    unit_tariff = {"candidate": leaves + xors + nodes + len(word),
                   "predecessor": 72 * 28 + 12 + 72 * 9 + len(old_word),
                   "read_only_repair": 74 * 28 + 74 * 9 + 74}
    need(unit_tariff["predecessor"] == predecessor["unit_complete_tariff"]["candidate"],
         "source-bound predecessor tariff")
    return {"schema_version": 1, "points": POINTS, "readout_pairs": pairs,
            "root_counts": dict(sorted(counts.items())), "minimum_shears_at_ten_queries": 4,
            "pairing_histogram": {str(k): v for k, v in histogram.items()},
            "pairing_records_sha256": pairing_hash, "short_shear_exclusion": shear_receipt,
            "word_sha256": digest(word), "expanded_sha256": digest(expanded),
            "map_leaf_calls": leaves, "identity_row_xors": xors,
            "internal_nodes": nodes, "root_instructions": len(word), "borrowed_dirty_rows": 4,
            "unit_tariff": unit_tariff,
            "formal_incoming_rows": 40, "semantic_controls": controls(word, expanded)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path, help="export a receipt without replacing existing files")
    args = parser.parse_args()
    receipt = compute()
    if args.write:
        with args.write.open("x") as out:
            out.write(json.dumps(receipt, indent=2) + "\n")
    else:
        need(receipt == json.loads((HERE / "CERTIFICATE.json").read_text()), "certificate drift")
    print("PASS_MUTABLE_SOURCE_SHEAR_COST minimum_X=4 B=10 A=62 tariff=2744 predecessor=2760 pairings=945")


if __name__ == "__main__":
    main()
