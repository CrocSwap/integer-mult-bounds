#!/usr/bin/env python3
"""Exact corroboration of the five-label proof; no predecessor code is used.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
MASKS = (15, 23, 27, 29, 30, 31)
SOURCE_FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
WITNESS = (0, 1, 2, 3, 4, 3, 2, 3, 4, 0, 3, 1)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def differences(points):
    return {x ^ y for x, y in combinations(points, 2)}


def excess(points, mask):
    classes = tuple(tuple(x for x in points if (x & mask).bit_count() % 2 == bit)
                    for bit in (0, 1))
    supports = tuple(differences(c) for c in classes)
    value = sum(len(c) * (len(c) - 1) // 2 - len(d)
                for c, d in zip(classes, supports))
    return value, classes, supports


def prefix_points(word):
    require(len(word) == 12, "length must be twelve")
    require(all(type(c) is int and 0 <= c < 5 for c in word), "invalid label")
    require(set(word) == set(range(5)), "all five labels must occur")
    points = [0]
    state = 0
    for label in word:
        state ^= 1 << label
        points.append(state)
    require(state == 0, "word is not restored")
    require(len(set(points[:-1])) == 12, "word is not simple")
    return tuple(points[:-1])


def check_word(word, mask, cap=15):
    require(type(mask) is int and mask in MASKS, "functional must have weight >=4")
    points = prefix_points(word)
    require(len(differences(points)) == 31, "word is not universal")
    value, classes, _ = excess(points, mask)
    require(value <= cap, "excess exceeds claimed cap")
    # A separate ordered-pair multiplicity calculation checks the definition.
    ordered = sum(sum(count // 2 - 1 for count in Counter(
        x ^ y for x in c for y in c if x != y).values()) for c in classes)
    require(value == ordered, "unordered and ordered excess disagree")
    return value, classes


def canonical_cycles():
    """Every length-12 simple closed word up to first-occurrence relabeling.

    Only simplicity and the forced final singleton edge filter the traversal.
    No excess, universality, parity-budget or rotation prune is used.
    """
    stack = [((), (0,), 1, -1)]
    while stack:
        word, points, seen, highest = stack.pop()
        if len(word) == 11:
            last = points[-1]
            if last and last & (last - 1) == 0:
                yield word + (last.bit_length() - 1,), points
            continue
        for label in range(min(highest + 1, 4) + 1):
            state = points[-1] ^ (1 << label)
            if not (seen >> state) & 1:
                stack.append((word + (label,), points + (state,),
                              seen | (1 << state), max(highest, label)))


def matching_identities(word, points, mask):
    _, classes, _ = excess(points, mask)
    sizes = tuple(map(len, classes))
    stays = [0, 0]
    crossing = 0
    for index, label in enumerate(word):
        bit = (points[index] & mask).bit_count() % 2
        if mask & (1 << label):
            crossing += 1
        else:
            stays[bit] += 1
    require(all(2 * sizes[b] == 2 * stays[b] + crossing for b in (0, 1)),
            "cycle degree identity failed")
    if mask != 31:
        require(all(2 * stays[b] <= sizes[b] for b in (0, 1)), "not a matching")
        require(max(sizes) <= 2 * min(sizes), "matching balance failed")
    else:
        require(sizes == (6, 6), "all-ones functional must alternate")


def walk_checks():
    closed = full_alphabet = universal = checks = 0
    histogram = Counter()
    maxima = {mask: -1 for mask in MASKS}
    for word, points in canonical_cycles():
        closed += 1
        full_alphabet += len(set(word)) == 5
        for mask in MASKS:
            matching_identities(word, points, mask)
        if len(differences(points)) != 31:
            continue
        universal += 1
        require(prefix_points(word) == points, "enumeration prefix mismatch")
        for mask in MASKS:
            value, classes = check_word(word, mask)
            split = tuple(sorted(map(len, classes), reverse=True))
            histogram[(mask.bit_count(), split, value)] += 1
            maxima[mask] = max(maxima[mask], value)
            checks += 1
    require((closed, full_alphabet, universal, checks) == (3695, 3381, 828, 4968),
            "bounded walk census changed")
    require(set(maxima.values()) == {11}, "measured high-weight maximum changed")
    return {"canonical_closed": closed, "all_five_labels": full_alphabet,
            "universal": universal, "functional_checks": checks,
            "matching_checks": closed * 6, "maxima_by_mask": maxima,
            "histogram": [{"weight": key[0], "split": key[1], "excess": key[2],
                           "count": count} for key, count in sorted(histogram.items())]}


def projected_plane_obstruction(majority, minority):
    """Check the finite ingredients of the proof's planar-minority contradiction."""
    v = 16
    require({x ^ v for x in majority} == set(majority), "majority not v-invariant")
    require(len(differences(majority)) == 13, "wrong majority support")
    require(len(differences(minority)) == 3, "minority is not an affine plane")
    require({x ^ v for x in minority} == set(minority), "minority not v-invariant")
    projected = {x & 15 for x in majority}
    endpoints = sorted({x & 15 for x in minority})
    require(len(endpoints) == 2, "expected two projected minority vertices")
    z = endpoints[0] ^ endpoints[1]
    require(z not in differences(projected), "missing direction is already present")
    common = {x for x in projected if all((x ^ u).bit_count() == 1 for u in endpoints)}
    require(len(common) < 2, "two cross-fiber transitions would be possible")
    return len(common)


def cube_neighbor_checks():
    pairs = 0
    for u, w in combinations(range(16), 2):
        common = [x for x in range(16)
                  if (x ^ u).bit_count() == 1 and (x ^ w).bit_count() == 1]
        require(len(common) == (2 if (u ^ w).bit_count() == 2 else 0),
                "cube common-neighbor count")
        if common:
            require(common[0] ^ common[1] == u ^ w, "common-neighbor difference")
        pairs += 1
    return pairs


def set_checks():
    """All v-invariant (8,4) pairs at f=01111; coordinate symmetry covers the rest."""
    even = [x for x in range(16) if x.bit_count() % 2 == 0]
    odd = [x for x in range(32) if (x & 15).bit_count() % 2 == 1]
    cases = universal = planes = 0
    common_counts = Counter()
    for projected in combinations(even, 4):
        majority = projected + tuple(x ^ 16 for x in projected)
        da = differences(majority)
        require(len(differences(projected)) in (3, 6), "four-point support lemma")
        require(len(da) == 1 + 2 * len(differences(projected)), "lift support lemma")
        for minority in combinations(odd, 4):
            cases += 1
            db = differences(minority)
            require(len(db) in (3, 6), "four-point support dichotomy failed")
            if len(da | db) != 15 or len({a ^ b for a in majority for b in minority}) != 16:
                continue
            universal += 1
            require(len(da) == 13, "planar majority cannot be universal")
            if len(db) == 3:
                planes += 1
                common_counts[projected_plane_obstruction(majority, minority)] += 1
            else:
                require(34 - len(da) - len(db) == 15, "nonplanar split cap")
    require((cases, universal, planes) == (127400, 13664, 224), "set envelope changed")
    require(common_counts == {0: 32, 1: 192}, "planar obstruction counts changed")
    return {"pairs": cases, "universal_sets": universal,
            "universal_planar_minority": planes, "common_neighbors": common_counts}


def must_reject(action, reason):
    try:
        action()
    except ValueError as error:
        require(reason in str(error), "rejected for the wrong reason: " + str(error))
        return
    raise ValueError("negative control was accepted: " + reason)


def controls():
    for mask in (0, 1, 32, True):
        must_reject(lambda: check_word(WITNESS, mask), "functional")
    for word, reason in (
        (WITNESS[:-1], "length"), ((True,) + WITNESS[1:], "label"),
        ((5,) + WITNESS[1:], "label"), (WITNESS[:-1] + (0,), "restored"),
        ((0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 0, 0), "simple"),
    ):
        must_reject(lambda: check_word(word, 23), reason)
    must_reject(lambda: check_word(WITNESS, 23, cap=10), "cap")
    points = prefix_points(WITNESS)
    require(check_word(WITNESS, 23)[0] == 11, "positive fixture")
    require(excess(points, 1)[0] == 21, "low-weight boundary control")
    majority = (0, 3, 5, 9, 16, 19, 21, 25)
    minority = (1, 14, 17, 30)
    require(len(differences(majority + minority)) == 31, "set control not universal")
    value = excess(majority + minority, 15)[0]
    require(value == 18, "set-only counterexample changed")
    must_reject(lambda: require(value <= 15, "set-only cap"), "set-only cap")
    require(projected_plane_obstruction(majority, minority) == 0, "set obstruction")
    return {"input_and_cap_rejections": 10, "low_weight_excess": 21,
            "set_only_excess": 18, "positive_word": WITNESS, "positive_mask": 23}


def payload():
    return {"schema": "f7-five-label-pruning-proof/v1", "proved_budget": 15,
            "walks": walk_checks(), "set_envelope": set_checks(), "controls": controls(),
            "cube_neighbor_pairs": cube_neighbor_checks(),
            "source_sha256": {name: sha256((PACKAGE / name).read_bytes()).hexdigest()
                              for name in SOURCE_FILES}}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def check_receipt(actual, expected):
    # Canonical JSON comparison also distinguishes bool from int and int from float.
    require(canonical(actual) == canonical(expected), "receipt differs from fresh evidence")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-receipt", action="store_true")
    args = parser.parse_args()
    actual = payload()
    if args.emit_receipt:
        print(json.dumps(actual, indent=2, sort_keys=True))
        return
    receipt = (PACKAGE / "RESULT.json").read_bytes()
    require(len(receipt) < 65536, "receipt too large")
    check_receipt(actual, json.loads(receipt))
    for key, value in (("proved_budget", 14), ("proved_budget", True)):
        mutant = dict(actual)
        mutant[key] = value
        must_reject(lambda: check_receipt(actual, mutant), "receipt")
    print("PASS_F7_FIVE_LABEL_PRUNING_PROOF universal=828 functionals=4968 "
          "set_pairs=127400 planar_obstructions=224 proved_budget=15 measured_max=11")


if __name__ == "__main__":
    main()
