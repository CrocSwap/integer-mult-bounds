#!/usr/bin/env python3
"""Emit the finite universal-connector certificate (Python standard library)."""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

BASE = "91a2094f2e022930069e8cfdc810a3ea1b81cd09"
SEED = 52
ROOT = Path(__file__).resolve().parent


def double_words(n, word=(), counts=()):
    """Restricted-growth words: quotient by first-occurrence source naming."""
    if len(word) == 2 * n:
        yield word
        return
    for label, count in enumerate(counts):
        if count == 1:
            after = counts[:label] + (2,) + counts[label + 1:]
            yield from double_words(n, word + (label,), after)
    if len(counts) < n:
        yield from double_words(n, word + (len(counts),), counts + (1,))


def prefixes(word):
    values = [0]
    for label in word:
        values.append(values[-1] ^ (1 << label))
    return values


def difference_mask(word):
    values = prefixes(word)
    return sum(1 << d for d in {a ^ b for a in values for b in values})


def census(n):
    entries = sorted((list(w), difference_mask(w)) for w in double_words(n))
    hist = Counter(mask.bit_count() for _, mask in entries)
    payload = json.dumps(entries, separators=(",", ":")).encode()
    return {"sources": n, "pairings": len(entries),
            "histogram": dict(sorted((str(k), v) for k, v in hist.items())),
            "canonical_entries_sha256": sha256(payload).hexdigest(),
            "max_coverage": max(hist)}


def schedule(source_word, n, rows, allow_four=False):
    """Place each readout at two prefix slots, or four if necessary."""
    values = prefixes(source_word)
    slots = [[] for _ in values]
    endpoints = []
    for i, row in enumerate(rows):
        pair = next((list(c) for c in combinations(range(len(values)), 2)
                     if values[c[0]] ^ values[c[1]] == row), None)
        if pair is None and allow_four:
            pair = next((list(c) for c in combinations(range(len(values)), 4)
                         if values[c[0]] ^ values[c[1]] ^ values[c[2]] ^ values[c[3]] == row), None)
        if pair is None:
            raise ValueError(f"unrealized row {row}")
        endpoints.append(pair)
        for slot in pair:
            slots[slot].append(["A", i])
    word = []
    for k, reads in enumerate(slots):
        word.extend(reads)
        if k < len(source_word):
            word.append(["B", source_word[k]])
    return {"sources": n, "rows": rows, "source_word": list(source_word),
            "readout_slots": endpoints, "word": word, "queries": len(word)}


def product_word(factors, source, target, depth=0):
    """Factors are listed in application order; all leaves are XOR shears."""
    if len(factors) == 1:
        return [[factors[0], source, target]]
    cut = len(factors) // 2
    connector = f"scratch{depth}"
    right = product_word(factors[:cut], source, connector, depth + 1)
    left = product_word(factors[cut:], connector, target, depth + 1)
    return right + left + right[::-1] + left[::-1]


def lower(item, lengths):
    words, factors = {}, {}
    for kind in ("B", "A"):
        for i, length in enumerate(lengths[kind]):
            name = f"{kind}{i}"
            factors[name] = [f"{name}.{k}" for k in range(length)]
            src, dst = (f"x{i}", "z") if kind == "B" else ("z", f"y{i}")
            words[name] = product_word(factors[name], src, dst)
    literal = [op for kind, i in item["word"] for op in words[f"{kind}{i}"]]
    return {"factor_lengths": lengths, "factors": factors,
            "query_leaf_prices": {k: len(v) for k, v in words.items()},
            "leaf_word": literal, "leaf_calls": len(literal),
            "borrowed_dirty_arrays": 1 + (max(sum(lengths.values(), [])) - 1).bit_length()}


def main():
    four = (0, 1, 0, 1, 2, 3, 2, 3)
    five_ten = (0, 1, 2, 0, 3, 1, 4, 2, 3, 4)
    five_twelve = (2, 0, 2, 1, 2, 0, 3, 1, 4, 2, 3, 4)
    schedules = {
        "four_all": schedule(four, 4, list(range(1, 16))),
        "five_extra_source": schedule(five_twelve, 5, list(range(1, 32))),
        "five_extra_output": schedule(five_ten, 5, list(range(1, 32)), True),
    }
    lengths = {"B": [1, 2, 3, 4, 5], "A": [1] * 31}
    lowered = {k: lower(v, lengths) for k, v in schedules.items() if k.startswith("five")}
    result = {"schema": "universal-connector-boundary-v1", "base": BASE,
              "assignment_seed": SEED, "censuses": [census(4), census(5)],
              "schedules": schedules, "lowered": lowered,
              "five_source_comparators": {"column_stars": 170, "row_stars": 222},
              "scope": "Exact binary query model; no new kappa or supplier integration"}
    (ROOT / "CERTIFICATE.json").write_text(json.dumps(result, indent=2) + "\n")
    print("GENERATED_UNIVERSAL_CONNECTOR_BOUNDARY")


if __name__ == "__main__":
    main()
