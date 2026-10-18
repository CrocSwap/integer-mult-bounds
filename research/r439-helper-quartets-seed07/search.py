#!/usr/bin/env python3
"""One bounded GL(4,2) fusion search around the frozen PR941 R439 word.

Sagar Thakrar, with substantial OpenAI Codex assistance. Apache-2.0.
Uses Gareth Davidson's PR915/926/941 target basis, matching and exact bills.
The group-search mechanism follows Ross Richardson's PR965 GL(3,2) work.
"""
from collections import Counter, deque
import copy
import hashlib
import itertools
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRE = ROOT / "research/r439-helper-matching"
V = runpy.run_path(str(PRE / "verify.py"))
C = V["C"]
need = C["need"]


def inputs():
    original = C["load"](ROOT / C["WORD"])
    parent = C["load"](PRE / "vendor/pr915/candidate.json.gz")
    previous = C["load"](PRE / "candidate.json.gz")
    rows, _, target = V["frozen_parent"](original, parent)
    pairs = C["load"](PRE / "NOMINATION.json")["selected_pairs"]
    V["validate_pairs"](pairs, parent["R"])
    need(len(pairs) == 199 and len(target) == 306, "frozen dimensions")
    need(V["reconstruct"](parent, rows, target, pairs)[0] == previous,
         "PR941 reconstruction")
    columns = [sum(1 << i for i, row in enumerate(rows) if j in row)
               for j in range(parent["R"])]
    return original, parent, previous, target, pairs, columns


def group():
    generators = [(d, s) for d in range(4) for s in range(4) if d != s]
    words = {(1, 2, 4, 8): ()}
    queue = deque(words)
    while queue:
        matrix = queue.popleft()
        for d, s in generators:
            nxt = list(matrix)
            nxt[d] ^= nxt[s]
            nxt = tuple(nxt)
            if nxt not in words:
                words[nxt] = words[matrix] + ((d, s),)
                queue.append(nxt)
    need(len(words) == 20160, "GL(4,2) order")
    return words


def inverse_columns(word):
    masks = [1, 2, 4, 8]
    for d, s in word:
        masks[s] ^= masks[d]
    return masks


def quartets(pairs):
    return sorted(itertools.combinations(range(len(pairs)), 2), key=lambda ij:
                  hashlib.sha256(f"7:{ij[0]}:{ij[1]}".encode()).digest())[:64]


def helper_operations(pairs, indices, word):
    first, second = indices
    labels = pairs[first] + pairs[second]
    operations = []
    for i, pair in enumerate(pairs):
        if i == first:
            operations.extend((labels[d], labels[s]) for d, s in word)
        elif i != second:
            operations.append(tuple(pair))
    return operations


def construct(parent, target, columns, operations):
    transformed = list(columns)
    for d, s in operations:
        transformed[s] ^= transformed[d]
    v = parent["v"]
    helpers = [[0, 2 * v + d, [2 * v + s]] for d, s in operations]
    middle = [[0, v + i, [2 * v + j for j, col in enumerate(transformed)
                          if col >> i & 1]] for i in range(v)]
    need(all(g[2] for g in middle), "empty middle row")
    result = copy.deepcopy(parent)
    result["D"] = helpers + target + middle + target[::-1] + helpers[::-1]
    return result


def admitted(bill):
    return (64 * bill["F"] ** 3 * bill["B"] ** 2 < 1 << 104 and
            (1 << 18) * bill["F"] ** 5 * bill["B"] ** 4 < 1 << 192)


def search():
    original, parent, previous, target, pairs, columns = inputs()
    words = group()
    basis = [(matrix, word, inverse_columns(word))
             for matrix, word in sorted(words.items())]
    baseline = V["bill"](previous)
    need(baseline["native_ADDs"] == 11949 and admitted(baseline), "baseline bill")
    frozen = list(columns)
    for d, s in pairs:
        frozen[s] ^= frozen[d]
    census, accepted, scan_hash = [], [], hashlib.sha256()
    for indices in quartets(pairs):
        labels = pairs[indices[0]] + pairs[indices[1]]
        combinations = [0] * 16
        for mask in range(1, 16):
            low = mask & -mask
            combinations[mask] = combinations[mask ^ low] ^ columns[labels[low.bit_length() - 1]]
        weights = [x.bit_count() for x in combinations]
        frozen_weight = sum(frozen[j].bit_count() for j in labels)
        constant = baseline["native_ADDs"] - 4 - frozen_weight
        best = None
        for matrix, word, masks in basis:
            price = constant + 2 * len(word) + sum(weights[m] for m in masks)
            scan_hash.update(bytes(indices) + bytes(matrix) + price.to_bytes(4, "big"))
            item = (price, matrix, word)
            if best is None or item < best:
                best = item
        price, matrix, word = best
        candidate = construct(parent, target, columns, helper_operations(pairs, indices, word))
        bill = V["bill"](candidate)
        need(price == bill["native_ADDs"], "optimistic and complete price agree")
        entry = dict(indices=list(indices), helpers=labels, matrix=list(matrix),
                     word=[list(op) for op in word], bill=bill, admitted=admitted(bill))
        census.append(entry)
        if admitted(bill) and price < baseline["native_ADDs"]:
            accepted.append(entry)
    winner = min(accepted, key=lambda x: (x["bill"]["native_ADDs"], x["bill"]["F"],
                                         x["bill"]["B"], x["indices"])) if accepted else None
    return dict(format="r439-helper-quartets/1", seed=7, quartet_count=64,
                group_order=len(words), combinations=64 * len(words),
                distance_histogram=dict(sorted(Counter(map(len, words.values())).items())),
                census_sha256=scan_hash.hexdigest(), baseline=baseline,
                census=census, admitted_improvements=len(accepted), winner=winner)


if __name__ == "__main__":
    print(json.dumps(search(), indent=2, sort_keys=True))
