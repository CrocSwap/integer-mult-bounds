#!/usr/bin/env python3
"""Reconstruct the 01021323 false prune and count it on a small domain.

The pinned length-18 census groups prefix states by bit 0 and compares their
collision count with the balanced weight-parity budget. This check walks that
rule independently. It does not run a seven-label census or change kappa.
"""

from math import comb
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
WORD = (0, 1, 0, 2, 1, 3, 2, 3)
DOMAINS = ((3, 6), (3, 8), (4, 8))
MARKER = (
    "PASS_F7_BIT0_FALSE_PRUNE word=01021323 bit0_collisions=8 "
    "balanced_budget=5 simple_false_prunes=0,0,6 no_new_kappa"
)


def fail(message):
    raise SystemExit("FAIL_F7_BIT0_FALSE_PRUNE " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def budget(size, other, dimension):
    """Even-collision allowance for one actual class split."""
    even_nonzero = (1 << (dimension - 1)) - 1
    return comb(size, 2) + comb(other, 2) - even_nonzero


def prefixes(word):
    state = 0
    states = [0]
    for label in word:
        state ^= 1 << label
        states.append(state)
    return states


def universal(points, dimension):
    covered = 0
    ordered = list(points)
    for index, left in enumerate(ordered):
        for right in ordered[index:]:
            covered |= 1 << (left ^ right)
    return covered.bit_count() == (1 << dimension)


def collision_walk(word, odd_class):
    """Count new pair-sums the way the pinned census does, for one grouping."""
    even_points = [0]
    odd_points = []
    even_support = odd_support = collisions = 0
    state = 0
    trace = []
    for index, label in enumerate(word):
        successor = state ^ (1 << label)
        closing = index == len(word) - 1 and successor == 0
        if closing:
            added = 0
        elif odd_class(successor):
            added = 0
            for point in odd_points:
                added |= 1 << (successor ^ point)
            fresh = (added & odd_support).bit_count()
            odd_support |= added
            odd_points.append(successor)
        else:
            added = 0
            for point in even_points:
                added |= 1 << (successor ^ point)
            fresh = (added & even_support).bit_count()
            even_support |= added
            even_points.append(successor)
        if not closing:
            collisions += fresh
        state = successor
        trace.append(collisions)
    return collisions, len(even_points), len(odd_points), trace


def bit0(state):
    return state & 1


def weight(state):
    return state.bit_count() & 1


def even_words(dimension, length):
    """Restricted-growth words in which every used label occurs evenly."""
    found = []
    letters = [0] * length
    counts = [0] * dimension

    def walk(index, used):
        if index == length:
            if all(count % 2 == 0 for count in counts[:used]):
                found.append(tuple(letters))
            return
        for label in range(min(used + 1, dimension)):
            letters[index] = label
            counts[label] += 1
            walk(index + 1, used + 1 if label == used else used)
            counts[label] -= 1

    counts[0] = 1
    walk(1, 1)
    return found


def domain_row(dimension, length):
    allowance = budget(length // 2, length // 2, dimension)
    universal_count = simple_count = false_prunes = weight_exceeded = 0
    for word in even_words(dimension, length):
        states = prefixes(word)
        if states[-1] != 0:
            continue
        points = set(states[:-1])
        if not universal(points, dimension):
            continue
        universal_count += 1
        if len(states[:-1]) != len(points):
            continue
        simple_count += 1
        bit_collisions, _, _, _ = collision_walk(word, bit0)
        weight_collisions, even_size, odd_size, _ = collision_walk(word, weight)
        if bit_collisions > allowance:
            false_prunes += 1
            if weight_collisions > budget(even_size, odd_size, dimension):
                weight_exceeded += 1
    return {
        "n": dimension,
        "length": length,
        "universal": universal_count,
        "simple_universal": simple_count,
        "balanced_budget": allowance,
        "simple_false_prunes": false_prunes,
        "weight_budget_exceeded": weight_exceeded,
    }


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/universal-f7-singleton-seedb859517b/engine.py",
        "research/universal-f7-singleton-seedb859517b/search.py",
        "research/universal-f7-singleton-l20-seed06704c39/engine.py",
    }
    require(set(pinned) == expected, "input inventory changed")
    texts = {}
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)
        texts[path] = (ROOT / path).read_text(encoding="utf-8")
    engine = texts["research/universal-f7-singleton-seedb859517b/engine.py"]
    vendored = texts["research/universal-f7-singleton-l20-seed06704c39/engine.py"]
    search = texts["research/universal-f7-singleton-seedb859517b/search.py"]
    require(engine == vendored, "the length-20 package no longer vendors the same engine")
    require("elif nq & 1:" in engine, "census no longer groups by bit 0")
    require(
        'if budget is not None and st["coll"] + newcoll > budget:' in engine,
        "census no longer prunes on the collision budget",
    )
    require(
        "r = cyclic_census(7, 18, budget=9, simple=True, prefix=pref)" in search,
        "length-18 call changed",
    )
    require(
        "C(9,2) + C(9,2) - 63 = 9 (budget=9)" in search,
        "length-18 budget justification changed",
    )


def evaluate():
    authenticate()
    states = prefixes(WORD)
    points = states[:-1]
    require(states == [0, 1, 3, 2, 6, 4, 12, 8, 0], "prefix states changed")
    require(len(points) == len(set(points)) == 8, "the eight nonclosing states are not distinct")
    require(states[-1] == 0, "the word does not restore")
    require(universal(points, 4), "the word is not universal on four labels")
    require(sorted(WORD.count(label) for label in range(4)) == [2, 2, 2, 2], "label counts changed")
    bit_collisions, bit_even, bit_odd, bit_trace = collision_walk(WORD, bit0)
    weight_collisions, weight_even, weight_odd, weight_trace = collision_walk(WORD, weight)
    balanced = budget(4, 4, 4)
    actual_bit = budget(bit_even, bit_odd, 4)
    require(bit_collisions == 8 and balanced == 5 and actual_bit == 9, "counterexample budgets changed")
    require(weight_collisions == 0 and (weight_even, weight_odd) == (4, 4), "weight walk changed")
    require(all(value <= balanced for value in weight_trace), "weight collisions exceed the balanced budget")
    exceed = next(index for index, value in enumerate(bit_trace) if value > balanced)
    rows = [domain_row(dimension, length) for dimension, length in DOMAINS]
    require(
        [(row["universal"], row["simple_false_prunes"]) for row in rows] == [(10, 0), (182, 0), (26, 6)],
        "small-domain census changed",
    )
    require(all(row["weight_budget_exceeded"] == 0 for row in rows), "a weight-parity budget also rejected a simple word")
    return {
        "word": list(WORD),
        "prefix_states": states,
        "prefix_set": sorted(set(points)),
        "universal": True,
        "weight_split": [weight_even, weight_odd],
        "weight_collisions": weight_collisions,
        "balanced_budget": balanced,
        "bit0_split": [bit_even, bit_odd],
        "bit0_collisions": bit_collisions,
        "bit0_actual_budget": actual_bit,
        "bit0_exceeds_balanced_at_index": exceed,
        "predecessor_call": "cyclic_census(7, 18, budget=9, simple=True)",
        "vendored_engine_same_text": True,
        "domains": rows,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
