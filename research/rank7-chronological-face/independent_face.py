#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact arithmetic for PR2979's saturated pattern direction.

No allocation producer, owner checker, LP solver or root routine is imported.
This checks finite bin-pattern arithmetic, not chronological realizability.
All gates remain active with Python -O.
"""

from collections import Counter
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path


CAPS = (8, 16, 32, 48)
WIDTHS = (4, 5, 6, 7, 8, 9)
T = 37
LOCAL = {1: 2445, 2: 706, 3: 232, 4: 108, 5: 18, 8: 8}
INVENTORY = {4: 26, 5: 2, 6: 16, 7: 52, 8: 99, 9: 213}
BINS = {8: 24864, 16: 16576, 32: 16576, 48: 16576}
IDLE = {1: 8655, 3: 2478, 5: 864, 48: 14095}
PROFILE = {1: 822840, 2: 235098, 3: 79734, 4: 35964,
           5: 6858, 8: 2664, 48: 14095}
A = (32, (7, 8, 8, 9))
B = (16, (7, 9))
C = (16, (8, 8))
D = (32, (7, 7, 9, 9))
SWAP_LEFT = Counter({A: 1, B: 1})
SWAP_RIGHT = Counter({C: 1, D: 1})


def need(condition, message):
    if not condition:
        raise ValueError(message)


def plain(counter):
    return {k: v for k, v in sorted(counter.items()) if v}


def load_json(path):
    return json.loads(path.read_text())


def decode(target, widths):
    need(tuple(widths) == WIDTHS, "source width order")
    result = Counter()
    for row in target:
        need(type(row) is list and len(row) == 3, "source pattern row")
        cap, counts, multiplicity = row
        need(type(cap) is int and cap in CAPS, "source capacity")
        need(type(counts) is list and len(counts) == len(widths), "source count vector")
        need(all(type(n) is int and n >= 0 for n in counts), "source width counts")
        need(type(multiplicity) is int and multiplicity > 0, "source multiplicity")
        pattern = tuple(w for w, n in zip(widths, counts) for _ in range(n))
        key = (cap, pattern)
        need(key not in result, "duplicate source pattern")
        result[key] = multiplicity
    return result


def measure(patterns):
    bins, inventory, residual, by_cap = Counter(), Counter(), Counter(), Counter()
    for (cap, widths), count in patterns.items():
        need(type(count) is int and count >= 0, "nonnegative integral pattern counts")
        need(cap in CAPS and all(w in WIDTHS for w in widths), "allowed pattern")
        remainder = cap - sum(widths)
        need(remainder >= 0, "pattern over capacity")
        bins[cap] += count
        for width in widths:
            inventory[width] += count
        residual[remainder] += count
        by_cap[cap, remainder] += count
    return tuple(plain(c) for c in (bins, inventory, residual, by_cap))


def family(k):
    need(type(k) is int and 0 <= k <= 1063, "family parameter outside 0..1063")
    return Counter({
        (8, (8,)): 24864,
        B: 16253 - k, C: 323 + k,
        (32, (9, 9, 9)): 864,
        A: 1063 - k, D: k,
        (32, (6, 8, 9, 9)): 5328,
        (32, (5, 9, 9, 9)): 666,
        (32, (4, 9, 9, 9)): 8655,
        (48, ()): 14095,
        (48, (9, 9, 9, 9, 9)): 2478,
        (48, (4, 8, 9, 9, 9, 9)): 3,
    })


def validate_mix(mix):
    need(mix["T"] == T, "source T37")
    patterns = decode(mix["target"], mix["widths"])
    bins, inventory, residual, by_cap = measure(patterns)
    need(bins == BINS, "bins by capacity")
    need(inventory == {w: 9 * T * n for w, n in INVENTORY.items()}, "width inventory")
    idle = {r: n for r, n in residual.items() if r}
    need(idle == IDLE, "residual histogram")
    profile = Counter({r: 9 * T * n for r, n in LOCAL.items()})
    profile.update(idle)
    need(plain(profile) == PROFILE, "complete paid profile")
    need({int(r): n for r, n in mix["profile"].items()} == PROFILE, "claimed profile")
    need({int(r): n for r, n in mix["idle"].items()} == IDLE, "claimed idle histogram")
    need(plain(patterns) == plain(family(1063)), "source family endpoint")
    return bins, inventory, residual, by_cap


def symbolic_target_reduced_cost(cap_receipt):
    """Compute the basis dual symbolically in independent formal tariff values.

    H(0)=0 is the source convention here. No positivity or optimality is inferred.
    The target's zero result also follows directly from the column relation.
    """
    basis = cap_receipt["basis_patterns"]
    columns = [[Fraction(cap == p["capacity"]) for cap in CAPS] +
               [Fraction(p["widths"].count(w)) for w in WIDTHS] for p in basis]
    size = len(CAPS) + len(WIDTHS)
    need(len(columns) == size, "ten-column relaxation basis")
    matrix = [[columns[j][i] for j in range(size)] +
              [Fraction(i == j) for j in range(size)] for i in range(size)]
    for col in range(size):
        pivot = next((i for i in range(col, size) if matrix[i][col]), None)
        need(pivot is not None, "nonsingular source basis")
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        value = matrix[col][col]
        matrix[col] = [v / value for v in matrix[col]]
        for row in range(size):
            if row != col:
                value = matrix[row][col]
                matrix[row] = [v - value * p for v, p in zip(matrix[row], matrix[col])]
    inverse = [row[size:] for row in matrix]
    target = [Fraction(cap == D[0]) for cap in CAPS] + [Fraction(D[1].count(w)) for w in WIDTHS]
    coefficients = Counter()
    for i, p in enumerate(basis):
        remainder = p["capacity"] - sum(p["widths"])
        if remainder:
            coefficients[remainder] -= sum(inverse[i][j] * target[j] for j in range(size))
    need(not plain(coefficients), "symbolic target reduced cost")
    return {}


def verify_face(package_root=None):
    root = Path(package_root) if package_root is not None else Path(__file__).resolve().parent
    source = root / "sources"
    mix = load_json(source / "construction/allocation/T37-FACE-MIX.json")
    receipt = load_json(source / "certificates/RELAX-CAP.json")
    measured = validate_mix(mix)
    need(measure(SWAP_LEFT) == measure(SWAP_RIGHT), "all-tariff swap identity")
    need(all(sum(widths) == cap for cap, widths in SWAP_LEFT | SWAP_RIGHT), "saturated swap bins")
    for k in range(1064):
        patterns = family(k)
        need(measure(patterns) == measured, "complete family invariants")
        outside = sum(count * widths.count(7) for (cap, widths), count in patterns.items() if cap != 16)
        need(outside == 1063 + k, "width-7 outside count")
    need({int(r): n for r, n in receipt["local_per_call"].items()} == LOCAL, "source local profile")
    need({int(w): n for w, n in receipt["inventory_per_call"].items()} == INVENTORY, "source per-call inventory")
    cap_idle = {int(r): Fraction(n) * T for r, n in receipt["idle_per_replica"].items()}
    delta = plain({r: Fraction(IDLE.get(r, 0)) - cap_idle.get(r, 0) for r in set(IDLE) | set(cap_idle)})
    need(delta == {1: Fraction(-3), 3: Fraction(-57, 20), 5: Fraction(15, 4), 48: Fraction(-3, 20)}, "integral versus cap histogram")
    need(sum(r * n for r, n in delta.items()) == 0 and delta, "equal mass is not equal tariff")
    need(symbolic_target_reduced_cost(receipt) == {}, "zero symbolic reduced cost")
    t74 = {int(r): n for r, n in load_json(source / "allocation/PROFILE.json").items()}
    need(t74 == {r: 2 * n for r, n in PROFILE.items()}, "T74 doubled profile")
    need(sum(INVENTORY.values()) == 408, "408 helpers per call")
    need(sum(r * n for r, n in PROFILE.items()) == 65088 * T, "complete rank mass")
    rejected = []

    def reject(name, operation, reason):
        try:
            operation()
        except ValueError as error:
            need(str(error) == reason, "wrong rejection reason: " + name)
            rejected.append({"name": name, "reason": reason})
        else:
            raise ValueError("accepted corruption: " + name)

    reject("negative_family_endpoint", lambda: family(-1), "family parameter outside 0..1063")
    reject("upper_family_endpoint", lambda: family(1064), "family parameter outside 0..1063")
    bad = deepcopy(mix)
    bad["target"][0][2] += 1
    reject("source_count_increment", lambda: validate_mix(bad), "bins by capacity")
    bad_inventory = deepcopy(mix)
    bad_inventory["target"][1][2] -= 1
    bad_inventory["target"][2][2] += 1
    reject("capacity_preserving_source_count_change", lambda: validate_mix(bad_inventory), "width inventory")
    bad_profile = deepcopy(mix)
    bad_profile["profile"]["1"] += 1
    bad_profile["profile"]["2"] -= 2
    bad_profile["profile"]["3"] += 1
    reject("rank_mass_preserving_claimed_profile", lambda: validate_mix(bad_profile), "claimed profile")
    wrong = Counter({C: 1, A: 1})
    need(measure(wrong)[0] == measure(SWAP_LEFT)[0] and measure(wrong)[2] == measure(SWAP_LEFT)[2], "wrong swap preserves capacities and residuals")
    reject("saturated_wrong_swap_inventory", lambda: need(measure(wrong)[1] == measure(SWAP_LEFT)[1], "width inventory changed"), "width inventory changed")
    tie_left = Counter({(16, (4, 5)): 1, (16, (6, 7)): 1})
    tie_right = Counter({(16, (4, 6)): 1, (16, (5, 7)): 1})
    left, right = measure(tie_left), measure(tie_right)
    need(left[:2] == right[:2] and sum(r*n for r,n in left[2].items()) == sum(r*n for r,n in right[2].items()), "rank-mass tie control premises")
    need(sum(n for r,n in left[2].items() if r) == sum(n for r,n in right[2].items() if r) == 2, "rank-mass tie child count")
    need(sum(r*r*n for r,n in left[2].items()) == 58 and sum(r*r*n for r,n in right[2].items()) == 52, "explicit tariff distinction")
    reject("inventory_and_mass_tie_wrong_histogram", lambda: need(left[2] == right[2], "residual histogram changed"), "residual histogram changed")
    return {
        "status": "PASS_INDEPENDENT_RANK7_FACE_ARITHMETIC",
        "source_commit": "be191346391661f4d35fc0d1508d0a6029572576",
        "integer_family": {"first": 0, "last": 1063, "verified_points": 1064,
                           "source_parameter": 1063, "width7_outside_cap16": "1063+k"},
        "T37": {"replicas": T, "calls": 9*T, "helper_roles": 9*T*408,
                "bins": BINS, "inventory": measured[1], "idle": IDLE,
                "zero_residual_bins": measured[2][0], "profile": PROFILE,
                "rank_mass": 65088*T},
        "T74_profile": t74,
        "integral_minus_fractional_cap_idle": {str(r): str(v) for r, v in delta.items()},
        "target_symbolic_reduced_cost": {},
        "controls": rejected,
        "scope": "finite bin-pattern arithmetic and written all-tariff identity; no chronology for all k, cap optimality/root replay, supplier admission or new kappa",
    }


if __name__ == "__main__":
    print(json.dumps(verify_face(), sort_keys=True, indent=2))
