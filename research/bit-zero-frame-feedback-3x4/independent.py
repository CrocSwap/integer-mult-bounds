#!/usr/bin/env python3
"""Literal Boolean-map lower bounds and dirty-input witness verification.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
No primary/predecessor checker imports, matrix packing, or coset calculation.
Shared mathematics: invertible XORs, meet-in-the-middle and permutation symmetry.
This is independent code/representation, not independent human review.
"""
import argparse
from collections import Counter
from itertools import permutations
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


class Invalid(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Invalid(reason)


def xor_table(destination, source):
    return bytes(x ^ (((x >> source) & 1) << destination) for x in range(256))


def expected(k, helpers, targets):
    values = []
    for x in range(1 << (helpers + targets)):
        y = x
        for r in range(targets):
            row = (k >> (r * helpers)) & ((1 << helpers) - 1)
            if (row & x).bit_count() % 2:
                y ^= 1 << (helpers + r)
        values.append(y)
    return bytes(values)


def replay(word, helpers, targets, restricted=True):
    n = helpers + targets
    table = bytes(range(1 << n))
    require(type(word) is list, "word type")
    for gate in word:
        require(type(gate) is list and len(gate) == 2
                and all(type(x) is int and 0 <= x < n for x in gate), "gate type")
        d, s = gate
        require(d != s, "noninvertible gate")
        require(not restricted or not (d < helpers <= s), "forbidden feedback")
        table = table.translate(xor_table(d, s))
    return table


def truth_ball(n, radius):
    gates = [xor_table(d, s) for d in range(n) for s in range(n) if d != s]
    first = bytes(range(1 << n))
    distances, layers = {first: 0}, [[first]]
    for depth in range(1, radius + 1):
        following = []
        for table in layers[-1]:
            for gate in gates:
                reached = table.translate(gate)
                if reached not in distances:
                    distances[reached] = depth
                    following.append(reached)
        layers.append(following)
    return distances, layers


def exclude_shorter(shear, claimed, distances, layers):
    # Balance every word of length L < claimed into halves of length at most
    # floor(L/2) and ceil(L/2); both are in B4 when claimed <=9.
    require(0 <= claimed <= 9, "lower-bound radius insufficient")
    for depth in range(min(4, (claimed - 1) // 2) + 1):
        for left in layers[depth]:
            # A o T: T(x) is the input to A. Do not compose in reverse order.
            right = shear.translate(left + bytes(256 - len(left)))
            other = distances.get(right)
            require(other is None or depth + other >= claimed,
                    "shorter unrestricted word exists")


def transport(k, word, helpers, targets):
    for hp in permutations(range(helpers)):
        for tp in permutations(range(targets)):
            mapping = hp + tuple(helpers + x for x in tp)
            moved = 0
            for r in range(targets):
                for c in range(helpers):
                    if k & (1 << (r * helpers + c)):
                        moved |= 1 << (tp[r] * helpers + hp[c])
            yield moved, [[mapping[d], mapping[s]] for d, s in word]


def verify(data):
    for key, value in {"schema_version": 1, "helpers": 3, "targets": 4,
                       "maps": 4096, "gate_cost": 1, "ancillas": 0,
                       "radius": 4, "feedback_gains": 0}.items():
        require(type(data.get(key)) is int and data[key] == value, "header " + key)
    require(data.get("all_inputs_arbitrary") is True, "arbitrary input contract")
    distances, layers = truth_ball(7, 4)
    require([len(layer) for layer in layers] == data["unrestricted"]["spheres"],
            "unrestricted sphere counts differ")
    covered, histogram = set(), Counter()
    for item in data["orbits"]:
        k, cost, word = item["k"], item["minimum"], item["restricted_witness"]
        require(type(k) is int and 0 <= k < 4096, "representative range")
        require(type(cost) is int and cost == len(word), "cost/witness length")
        require(replay(word, 3, 4) == expected(k, 3, 4), "representative dirty endpoint")
        exclude_shorter(expected(k, 3, 4), cost, distances, layers)
        members = {}
        for moved, witness in transport(k, word, 3, 4):
            members.setdefault(moved, witness)
        require(k == min(members), "noncanonical representative")
        require(type(item["orbit_size"]) is int and len(members) == item["orbit_size"],
                "orbit cardinality")
        require(covered.isdisjoint(members), "overlapping orbits")
        for moved, witness in members.items():
            require(replay(witness, 3, 4) == expected(moved, 3, 4),
                    "transported dirty endpoint")
        covered.update(members)
        histogram[cost] += len(members)
    require(covered == set(range(4096)), "missing labeled shear")
    require([histogram[i] for i in range(10)] == data["minimum_histogram"], "histogram")
    return len(data["orbits"])


def controls():
    failures = []

    def reject(name, action):
        try:
            action()
        except Invalid:
            failures.append(name)
        else:
            raise Invalid("failure control accepted: " + name)

    distances, layers = truth_ball(4, 10)
    require(len(distances) == 20160 and not layers[-1], "complete GL4 control")
    for k in range(16):
        shear = expected(k, 2, 2)
        actual = distances[shear]
        exclude_shorter(shear, actual, distances, layers)
        reject("overstated_minimum_" + str(k),
               lambda: exclude_shorter(shear, actual + 1, distances, layers))
    feedback = [[0, 1], [1, 0], [0, 1], [1, 0], [0, 1]]
    require(replay(feedback, 1, 1, False) == expected(1, 1, 1), "feedback positive")
    reject("feedback_alphabet", lambda: replay(feedback, 1, 1))
    star = [[0, 1], [2, 0], [0, 1]]
    require(replay(star, 2, 1) == expected(3, 2, 1), "star positive")
    require(replay(star[:-1], 2, 1) != expected(3, 2, 1), "missing restoration control")
    dirty_fault = replay([[1, 0], [2, 1]], 1, 2)
    require(dirty_fault[:2] == expected(3, 1, 2)[:2], "zero-target positive trap")
    require(dirty_fault != expected(3, 1, 2), "dirty-target fault undetected")
    reject("radius_guard", lambda: exclude_shorter(expected(1, 1, 1), 10, {}, []))
    return len(failures)


def load(path):
    def unique(pairs):
        data = {}
        for key, value in pairs:
            require(key not in data, "duplicate JSON key")
            data[key] = value
        return data
    return json.loads(path.read_text(), object_pairs_hook=unique)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=PACKAGE / "CERTIFICATE.json")
    args = parser.parse_args()
    orbits = verify(load(args.certificate))
    negatives = controls()
    print("PASS_SHEAR_3X4_TRUTH_TABLES labeled_maps=4096 dirty_inputs_per_map=128 orbits="
          + str(orbits) + " full_GL4=20160 negative_controls=" + str(negatives))


if __name__ == "__main__":
    main()
