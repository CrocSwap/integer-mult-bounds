#!/usr/bin/env python3
"""Exact bounded census, independent matrix pricing and whole-word replay.

Sagar Thakrar, with substantial OpenAI Codex assistance. Apache-2.0.
Finite checks only; the inherited supplier assumptions remain open.
"""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
S = runpy.run_path(str(HERE / "search.py"))
V, C, need = S["V"], S["C"], S["need"]


def same(actual, expected, message):
    need(C["canonical"](actual) == C["canonical"](expected), message)


def source_pins():
    manifest = C["load"](HERE / "SOURCES.json")
    for path, expected in manifest["files"].items():
        need(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected,
             "source pin: " + path)
    C["pins"](ROOT)
    return len(manifest["files"])


def inverse(matrix):
    rows = [[(matrix[i] >> j) & 1 for j in range(4)] + [int(i == j) for j in range(4)]
            for i in range(4)]
    for j in range(4):
        pivot = next((i for i in range(j, 4) if rows[i][j]), None)
        if pivot is None:
            return None
        rows[j], rows[pivot] = rows[pivot], rows[j]
        for i in range(4):
            if i != j and rows[i][j]:
                rows[i] = [a ^ b for a, b in zip(rows[i], rows[j])]
    return [sum(rows[i][4 + j] << i for i in range(4)) for j in range(4)]


def independent_census(certificate, pairs, columns):
    words = S["group"]()
    inverses = {m: inv for m in itertools.product(range(1, 16), repeat=4)
                if (inv := inverse(m)) is not None}
    need(set(inverses) == set(words) and len(inverses) == 20160, "direct GL(4,2) domain")
    for matrix, word in words.items():
        current = [1, 2, 4, 8]
        for d, s in word:
            current[d] ^= current[s]
        same(current, matrix, "shortest-word endpoint")
        for d, s in itertools.permutations(range(4), 2):
            neighbor = list(matrix)
            neighbor[d] ^= neighbor[s]
            need(len(words[tuple(neighbor)]) <= len(word) + 1, "shortest-distance edge inequality")
    need(words[(1, 2, 4, 8)] == (), "identity distance")
    sets = [{i for i in range(111) if col >> i & 1} for col in columns]
    frozen = [set(col) for col in sets]
    for d, s in pairs:
        frozen[s].symmetric_difference_update(frozen[d])
    candidates = list(itertools.combinations(range(199), 2))
    candidates.sort(key=lambda ij: hashlib.sha256(("7:%d:%d" % ij).encode()).digest())
    same([e["indices"] for e in certificate["census"]], candidates[:64], "quartet selection")
    digest = hashlib.sha256()
    for entry, indices in zip(certificate["census"], candidates[:64]):
        labels = pairs[indices[0]] + pairs[indices[1]]
        weights = []
        for mask in range(16):
            value = set()
            for j in range(4):
                if mask >> j & 1:
                    value.symmetric_difference_update(sets[labels[j]])
            weights.append(len(value))
        constant = 11949 - 4 - sum(len(frozen[j]) for j in labels)
        best = None
        for matrix, masks in sorted(inverses.items()):
            price = constant + 2 * len(words[matrix]) + sum(weights[m] for m in masks)
            digest.update(bytes(indices) + bytes(matrix) + price.to_bytes(4, "big"))
            choice = (price, matrix)
            best = choice if best is None or choice < best else best
        same(best, (entry["bill"]["native_ADDs"], entry["matrix"]), "independent minimum")
    same(digest.hexdigest(), certificate["census_sha256"], "independent complete census")


def controls(original, candidate, reference):
    rejected = []

    def reject(label, action):
        try:
            action()
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError("control accepted: " + label)

    def endpoint(word):
        need(V["boundary_columns"](word) == reference, "D boundary mismatch")

    # These are the three connected quartet operations, not unrelated pairs.
    winner = C["load"](HERE / "CERTIFICATE.json")["winner"]
    helpers = winner["helpers"]
    v = candidate["v"]
    for index, (d, s) in enumerate(winner["word"]):
        operation = [0, 2 * v + helpers[d], [2 * v + helpers[s]]]
        positions = [i for i, op in enumerate(candidate["D"]) if op == operation]
        need(len(positions) == 2, "quartet prepare/restore multiplicity")
        for side, position in enumerate(positions):
            mutant = copy.deepcopy(candidate)
            del mutant["D"][position]
            reject(f"quartet-{index}-pass-{side}-omitted", lambda m=mutant: endpoint(m))
    mutant = copy.deepcopy(candidate)
    first = next(i for i, g in enumerate(mutant["D"])
                 if g == [0, 2 * v + helpers[1], [2 * v + helpers[2]]])
    mutant["D"][first], mutant["D"][first - 1] = mutant["D"][first - 1], mutant["D"][first]
    reject("dependent-preparations-reordered", lambda: endpoint(mutant))
    mutant = copy.deepcopy(candidate)
    mutant["D"][0][0] = 1
    reject("illegal-D-frame", lambda: V["d_atoms"](mutant))
    mutant = copy.deepcopy(candidate)
    mutant["A"][0][1] += 1
    reject("outside-D-change", lambda: V["outside_d"](original, mutant))
    bill = V["bill"](candidate)
    wrong = dict(bill, native_ADDs=bill["native_ADDs"] - 1)
    reject("undercharged-complete-word", lambda: V["check_bill"](candidate, wrong))
    floor = C["load"](S["PRE"] / "floor-word.json.gz")
    endpoint(floor)
    rejected_bill = V["bill"](floor)
    reject("endpoint-valid-nine-stage-overflow",
           lambda: V["guards"](rejected_bill["F"], rejected_bill["B"]))
    neutral = copy.deepcopy(candidate)
    op = [0, 2 * v, [2 * v + 1]]
    neutral["D"] = [op, op] + neutral["D"]
    endpoint(neutral)
    need(V["bill"](neutral)["native_ADDs"] == bill["native_ADDs"] + 2,
         "neutral pair must cost two ADDs")
    return dict(rejected=rejected, neutral_pair_charged=2)


def verify():
    pins = source_pins()
    certificate = C["load"](HERE / "CERTIFICATE.json")
    same(S["search"](), certificate, "complete search regeneration")
    original, parent, previous, target, pairs, columns = S["inputs"]()
    independent_census(certificate, pairs, columns)
    nomination = C["load"](S["PRE"] / "NOMINATION.json")
    column_sets = [{i for i in range(111) if col >> i & 1} for col in columns]
    pair_floor = V["dual_check"](column_sets, nomination["primary_dual"],
                                  nomination["nominations"][0]["pairs"])
    winner = certificate["winner"]
    need(winner is not None, "admitted improvement required")
    operations = S["helper_operations"](pairs, winner["indices"], winner["word"])
    candidate = S["construct"](parent, target, columns, operations)
    V["check_bill"](candidate, winner["bill"])
    V["guards"](winner["bill"]["F"], winner["bill"]["B"])
    reference = V["boundary_columns"](original)
    for word in (previous, candidate):
        V["outside_d"](original, word)
        for reverse in (False, True):
            need(V["boundary_columns"](word, reverse) == reference, "all 661 D columns")
    negative = controls(original, candidate, reference)
    source = V["source_checks"](ROOT, dict(baseline=original, previous=previous, candidate=candidate))
    return dict(status="PASS_R439_HELPER_QUARTETS", source_pins=pins,
                combinations=certificate["combinations"], columns=661,
                native_ADDs=winner["bill"]["native_ADDs"], saved_ADDs=3,
                candidate_sha256=C["digest"](candidate), bill=winner["bill"],
                controls=negative, source_checks=source, pair_floor=pair_floor, no_new_kappa=True)


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
