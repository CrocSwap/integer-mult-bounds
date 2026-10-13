#!/usr/bin/env python3
"""Bounded restored-helper-star search on the frozen PR915 target basis.

Generalizes Gareth Davidson's PR926 disjoint-pair builder. Apache-2.0.
Prepared for @theon199 with substantial OpenAI Codex assistance.
"""
import argparse
import copy
import gzip
from pathlib import Path
import random
import runpy

C = runpy.run_path(str(Path(__file__).with_name("common.py")))
PARENT = "research/r439-target-compensation/candidate.json.gz"


def assemble(parent, columns, edges):
    word = copy.deepcopy(parent)
    v = word["v"]
    helper = [[0, 2 * v + a, [2 * v + b]] for a, b in edges]
    middle = [[0, v + i, [2 * v + j for j, col in enumerate(columns) if col >> i & 1]]
              for i in range(v)]
    word["D"] = helper + parent["D"][:306] + middle + parent["D"][306 + v:] + helper[::-1]
    return word


def bound(word, reverse=False):
    """Macro positive interpreter; verifier independently lowers COPY/ERASE."""
    v = word["v"]
    values = [1] * (2 * v + word["R"])
    peak = 1
    sections = ("C", "B", "scatter", "A", "D") if reverse else ("D", "A", "scatter", "B", "C")
    for section in sections:
        if section == "scatter":
            centers = reversed(range(len(word["ret"]))) if reverse else range(len(word["ret"]))
            for j in centers:
                copied = values[word["ret"][j]]
                for i, row in enumerate(word["scatter"]):
                    if j in row:
                        values[v + i] += copied
                        peak = max(peak, values[v + i])
        else:
            for _, d, sources in reversed(word[section]) if reverse else word[section]:
                values[d] += sum(values[s] for s in sources)
                peak = max(peak, values[d])
    return peak


def admitted(forward, backward):
    return (64 * forward**3 * backward**2 < 1 << 104
            and (1 << 18) * forward**5 * backward**4 < 1 << 192)


def search(parent, degree):
    C["need"](degree in (1, 2), "degree must be one or two")
    C["need"]((parent["v"], parent["R"]) == (111, 439), "parent dimensions")
    columns = [0] * 439
    for _, d, sources in parent["D"][306:417]:
        for s in sources:
            columns[s - 222] ^= 1 << (d - 111)
    census, positive = [], []
    rng = random.Random(19)
    for a in range(439):
        for b in range(439):
            if a == b:
                continue
            gain = columns[b].bit_count() - (columns[b] ^ columns[a]).bit_count() - 2
            tie = rng.getrandbits(64)
            census.append([a, b, gain, tie])
            if gain > 0:
                positive.append((-gain, tie, a, b))
    positive.sort()
    centers, leaves, edges, steps, rejected = {}, set(), [], [], []
    skips = 0
    for negative_gain, tie, a, b in positive:
        if a in leaves or b in leaves or b in centers or len(centers.get(a, [])) >= degree:
            skips += 1
            continue
        trial_cols = list(columns)
        trial_cols[b] ^= trial_cols[a]
        trial = assemble(parent, trial_cols, edges + [(a, b)])
        forward, backward = bound(trial), bound(trial, True)
        row = dict(a=a, b=b, gain=-negative_gain, F=forward, B=backward)
        if not admitted(forward, backward):
            rejected.append(row)
            continue
        columns = trial_cols
        edges.append((a, b))
        centers.setdefault(a, []).append(b)
        leaves.add(b)
        steps.append(row)
    word = assemble(parent, columns, edges)
    forward, backward = bound(word), bound(word, True)
    d_adds = sum(len(g[2]) for g in word["D"])
    total = sum(len(g[2]) for sec in "DABC" for g in word[sec]) + sum(map(len, word["scatter"]))
    certificate = dict(
        format="r439-helper-stars/1", seed=19, max_leaves=degree,
        parent_sha256=C["digest"](parent), candidate_sha256=C["digest"](word),
        census_sha256=C["digest"](census), ordered_pairs=len(census), positive_pairs=len(positive),
        overlap_skips=skips, guard_rejections=rejected, steps=steps,
        helper_edges=len(edges), helper_components=len(centers),
        two_leaf_stars=sum(len(x) == 2 for x in centers.values()),
        target_shears=306, middle_weight=sum(x.bit_count() for x in columns),
        D_adds=d_adds, native_ADDs=total, saved_beyond_PR915=13208 - total,
        F=forward, B=backward,
        local_bound=str(64 * forward**3 * backward**2),
        nine_stage_bound=str((1 << 18) * forward**5 * backward**4),
        stopping_rule="one complete gain-ordered pass; no retargeting, restart, or neutral move")
    return word, certificate


def run(root, output):
    C["pins"](root)
    parent = C["load"](Path(root) / PARENT)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    for degree, name in ((1, "pair-control"), (2, "candidate")):
        word, certificate = search(parent, degree)
        C["write"](output / (name + "-certificate.json"), certificate)
        with (output / (name + ".json.gz")).open("xb") as stream:
            stream.write(gzip.compress(C["canonical"](word), mtime=0))
        print(name, certificate["native_ADDs"], "ADDs;", certificate["two_leaf_stars"], "two-leaf stars", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=C["ROOT"])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.source_root, args.output)
