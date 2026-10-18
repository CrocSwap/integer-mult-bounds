"""Seed-3 finite nomination; OpenAI Codex assistance, Apache-2.0.

No global optimality claim. Helper matching followed by shared target donors.
"""
import copy
import gzip
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz"


def weight(x):
    return bin(x).count("1")


def nominate(vectors, rng):
    """Choose disjoint (changed vector, added vector) pairs with positive net gain."""
    scored = []
    for d in range(len(vectors)):
        for s in range(len(vectors)):
            if d != s:
                gain = weight(vectors[d]) - weight(vectors[d] ^ vectors[s]) - 2
                scored.append((-gain, rng.random(), d, s))
    used, chosen = set(), []
    for minus_gain, tie, d, s in sorted(scored):
        if minus_gain < 0 and d not in used and s not in used:
            chosen.append((d, s))
            used.update((d, s))
    return chosen


def source_rows(word):
    rows = [0] * 120
    for f, d, sources in word["D"]:
        for s in sources:
            rows[d - 120] ^= 1 << (s - 240)
    return rows


def search(word):
    rows = source_rows(word)
    columns = [sum(((r >> j) & 1) << i for i, r in enumerate(rows)) for j in range(420)]
    rng = random.Random(3)
    # Right multiplication by H changes column source by column destination.
    column_pairs = nominate(columns, rng)
    helper_pairs = [[s + 240, d + 240] for d, s in column_pairs]
    for d, s in column_pairs:
        columns[d] ^= columns[s]
    after_helpers = [sum(((c >> i) & 1) << j for j, c in enumerate(columns)) for i in range(120)]
    initial_target_local = nominate(after_helpers, rng)
    donors = {s for d, s in initial_target_local}
    gains = [[weight(after_helpers[d]) - weight(after_helpers[d] ^ after_helpers[s]) - 2
              for s in range(120)] for d in range(120)]

    def assign(frozen_donors):
        pairs, score = [], 0
        for d in range(120):
            if d not in frozen_donors:
                gain, s = max((gains[d][s], s) for s in frozen_donors)
                if gain > 0:
                    pairs.append((d, s))
                    score += gain
        return score, pairs

    score, _ = assign(donors)
    trace = [(len(donors), score)]
    evaluations = 0
    # One bounded extension of the disjoint-pair class after overlap discovery.
    for _ in range(30):
        options = [(assign(donors ^ {s})[0], s) for s in range(120)]
        evaluations += 120
        new_score, s = max(options)
        if new_score <= score:
            break
        donors ^= {s}
        score = new_score
        trace.append((len(donors), score))
    score, target_local = assign(donors)
    target_pairs = [[d + 120, s + 120] for d, s in target_local]
    transformed = list(after_helpers)
    for d, s in target_local:
        transformed[d] ^= transformed[s]
    return dict(assignment_seed=3, method="greedy helper matching then shared target donors",
                helper_pairs=helper_pairs, target_pairs=target_pairs,
                transformed_rows=[[j + 240 for j in range(420) if r >> j & 1] for r in transformed],
                helper_only_adds=sum(map(weight, after_helpers)) + 2 * len(helper_pairs),
                searched_orientations=dict(helper=420*419, target=120*119),
                target_search=dict(method="best assignment to donors, at most 30 strictly improving single-donor toggles",
                                   donors=sorted(s+120 for s in donors),
                                   saved_over_helper_only=score, trace=[list(x) for x in trace],
                                   evaluated_toggle_sets=evaluations, maximum_iterations=30))


def build(word, recipe):
    hp = [[0, d, [s]] for d, s in recipe["helper_pairs"]]
    tp = [[0, d, [s]] for d, s in recipe["target_pairs"]]
    feed = [[0, i + 120, row] for i, row in enumerate(recipe["transformed_rows"]) if row]
    out = copy.deepcopy(word)
    out["D"] = hp + tp + feed + list(reversed(tp)) + list(reversed(hp))
    return out


if __name__ == "__main__":
    word = json.load(gzip.open(SOURCE, "rt"))
    recipe = search(word)
    out = build(word, recipe)
    (HERE / "recipe.json").write_text(json.dumps(recipe, indent=2) + "\n")
    (HERE / "output").mkdir(exist_ok=True)
    (HERE / "output/candidate.json").write_text(json.dumps(out, separators=(",", ":")) + "\n")
    print("D", sum(len(g[2]) for g in word["D"]), "->", sum(len(g[2]) for g in out["D"]),
          "helper_pairs", len(recipe["helper_pairs"]), "target_pairs", len(recipe["target_pairs"]),
          "helper_only", recipe["helper_only_adds"])
