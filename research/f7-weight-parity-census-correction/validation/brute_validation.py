#!/usr/bin/env python3
"""Independent raw-product ground truth and explicit bit-0 counterexamples.

No census implementation is imported.  Every word is enumerated, reduced to
restricted-growth form only for counting, then checked directly by P XOR P.
Run: python3 session2/review/validation/brute_validation.py
"""
from collections import Counter
from itertools import product
from pathlib import Path
import argparse
import json
import tempfile

HERE = Path(__file__).resolve().parent


def canonical(word):
    seen = {}
    out = []
    for label in word:
        if label not in seen:
            seen[label] = len(seen)
        out.append(seen[label])
    return tuple(out)


def describe(word, n):
    counts = [word.count(label) for label in range(n)]
    q = 0
    path = []
    for label in word:
        path.append(q)
        q ^= 1 << label
    states = sorted(set(path))
    coverage = sorted({a ^ b for a in states for b in states})
    stats = {}
    for mode in ("weight", "bit0"):
        groups = [[x for x in states if
                   (x.bit_count() & 1 if mode == "weight" else x & 1) == p]
                  for p in (0, 1)]
        supports = [sorted({a ^ b for i, a in enumerate(g) for b in g[i+1:]})
                    for g in groups]
        pairs = [len(g) * (len(g)-1) // 2 for g in groups]
        stats[mode] = {"groups": groups, "split": [len(g) for g in groups],
                       "pairs": pairs, "supports": supports,
                       "collisions": sum(pairs) - sum(map(len, supports))}
    s, t = stats["weight"]["split"]
    budget = s * (s-1) // 2 + t * (t-1) // 2 - ((1 << (n-1))-1)
    return {"word": "".join(map(str, word)), "n": n, "L": len(word),
            "counts": counts, "prefix_path": path, "states": states,
            "restored": q == 0 and all(c > 0 and c % 2 == 0 for c in counts),
            "coverage": coverage, "universal": len(coverage) == (1 << n),
            "groups": stats, "weight_budget": budget,
            "old_bit0_rule_rejects": stats["bit0"]["collisions"] > budget}


def brute(n, length):
    restored = Counter()
    universal = Counter()
    old_rule_rejects_universal = Counter()
    raw_restored = raw_universal = 0
    words_scanned = 0
    for word in product(range(n), repeat=length):
        words_scanned += 1
        counts = [word.count(label) for label in range(n)]
        if not all(c > 0 and c % 2 == 0 for c in counts):
            continue
        raw_restored += 1
        if canonical(word) != word:
            # Raw universality count does not rely on the canonical test.
            q = 0
            states = set()
            for label in word:
                states.add(q)
                q ^= 1 << label
            if len({a ^ b for a in states for b in states}) == 1 << n:
                raw_universal += 1
            continue
        details = describe(word, n)
        split = ",".join(map(str, details["groups"]["weight"]["split"]))
        restored[split] += 1
        if details["universal"]:
            universal[split] += 1
            raw_universal += 1
            if details["old_bit0_rule_rejects"]:
                old_rule_rejects_universal[split] += 1
    # Include zero-hit feasible target splits, as well as all observed splits.
    splits = {f"{s},{t}": {"restored": restored[f"{s},{t}"],
                           "universal": universal[f"{s},{t}"],
                           "old_bit0_rule_rejects_universal":
                           old_rule_rejects_universal[f"{s},{t}"]}
              for s in range(1, length // 2 + 1)
              for t in range(1, length // 2 + 1)}
    return {"n": n, "L": length, "words_scanned": words_scanned,
            "raw_restored": raw_restored, "raw_universal": raw_universal,
            "canonical_restored": sum(restored.values()),
            "canonical_universal": sum(universal.values()), "splits": splits}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    output_dir = args.output_dir or Path(tempfile.mkdtemp(prefix="f7-brute-validation-"))
    output_dir.mkdir(parents=True, exist_ok=True)
    results = {
        "method": "raw itertools.product, no pruning; direct XOR-set coverage",
        "witnesses": [describe(tuple(map(int, "001212")), 3),
                      describe(tuple(map(int, "01021323")), 4)],
        "cases": [brute(3, 6), brute(3, 8), brute(4, 8)],
        "scope": "Counterexamples disprove the generic bit0 pruning rule; they do not exhibit an n7 L20 universal word."
    }
    for witness in results["witnesses"]:
        if not (witness["restored"] and witness["universal"] and witness["old_bit0_rule_rejects"]):
            raise RuntimeError(witness)
    target = output_dir / "brute_results.json"
    target.write_text(json.dumps(results, indent=2) + "\n")
    print(target)
    for case in results["cases"]:
        print(f"n={case['n']} L={case['L']} canonical restored={case['canonical_restored']} universal={case['canonical_universal']}")


if __name__ == "__main__":
    main()
