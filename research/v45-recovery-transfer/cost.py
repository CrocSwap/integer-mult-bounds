#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact fixed-bin marginal cost screen for the frozen PR2979 inventory.

The independent basis/dual implementation is new to this package. Rational
logarithm/exponential enclosures are executed from authenticated PR2979 root.py,
credited to Marius-Paul Dumitrean and that package's inherited moment lineage.
This is a finite fractional relaxation at a fixed complex saving parameter;
it supplies neither an extraction nor physical/supplier/outer admission.
"""

import hashlib
import itertools
import json
import types
from fractions import Fraction as Q
from pathlib import Path

SOURCE = "research/rank7-joint-endframes/"
PINS = {
    "CLAIM.json": "436e0d297cbdf195445d3697d496ac675e95210b79e70ce602a6a6667a4c6ce9",
    "certificates/RELAX-CAP.json": (
        "b272680de5842f7fd5f442cd0aeadfd317fe6af266ddee1a1e0738a919ba856e"
    ),
    "tools/root.py": "55f5aca39b5ee2fe4687ac8863e6c24569010f27a332883c069b8e14b8fe09e3",
    "allocation/PROFILE.json": (
        "94a819747f3ced41f1544ada0036c983fc0c92847b9644380f877a06cd7931cf"
    ),
}
CAPS = (8, 16, 32, 48)
WIDTHS = (4, 5, 6, 7, 8, 9)
BINS = (672, 448, 448, 448)
CALLS = 9


def need(condition, message):
    """Keep every acceptance condition live under optimized Python."""
    if not condition:
        raise ValueError(message)


def authenticate(raw, expected):
    need(len(raw) <= 65536, "cost input exceeds fixed byte cap")
    need(hashlib.sha256(raw).hexdigest() == expected, "cost source digest")


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate cost JSON key")
        result[key] = value
    return result


def sources(root):
    """Authenticate every input before parsing or executing the retained kernel."""
    raw = {}
    for name, digest in PINS.items():
        value = (root / SOURCE / name).read_bytes()
        authenticate(value, digest)
        raw[name] = value
    values = {
        name: json.loads(value, object_pairs_hook=unique)
        for name, value in raw.items()
        if name.endswith(".json")
    }
    kernel = types.ModuleType("v45_authenticated_tariff")
    filename = str(root / SOURCE / "tools/root.py")
    exec(compile(raw["tools/root.py"], filename, "exec"), kernel.__dict__)
    return values, kernel


def pattern(capacity, widths):
    need(type(capacity) is int and capacity in CAPS, "cost pattern capacity")
    need(len(widths) <= 12, "cost pattern helper count")
    need(all(type(w) is int and w in WIDTHS for w in widths), "cost width")
    remaining = capacity - sum(widths)
    need(remaining >= 0, "cost pattern exceeds capacity")
    col = [Q(int(capacity == c)) for c in CAPS]
    col += [Q(widths.count(w)) for w in WIDTHS]
    return col, remaining


def inverse(matrix):
    size = len(matrix)
    need(size == 10 and all(len(r) == size for r in matrix), "cost basis size")
    rows = [r[:] + [Q(int(i == j)) for j in range(size)] for i, r in enumerate(matrix)]
    for j in range(size):
        choices = [i for i in range(j, size) if rows[i][j]]
        need(bool(choices), "singular cost basis")
        k = choices[0]
        rows[j], rows[k] = rows[k], rows[j]
        divisor = rows[j][j]
        rows[j] = [v / divisor for v in rows[j]]
        for i in range(size):
            if i != j:
                multiplier = rows[i][j]
                rows[i] = [v - multiplier * w for v, w in zip(rows[i], rows[j])]
    return [r[size:] for r in rows]


def dot(left, right):
    need(len(left) == len(right), "cost vector dimensions")
    return sum((x * y for x, y in zip(left, right)), Q(0))


def setup(cert):
    entries = cert["basis_patterns"]
    need(len(entries) == 10, "ten source basis patterns")
    columns, idle = zip(*(pattern(e["capacity"], e["widths"]) for e in entries))
    matrix = [[col[i] for col in columns] for i in range(10)]
    inv = inverse(matrix)
    inventory = {int(k): Q(v) for k, v in cert["inventory_per_call"].items()}
    need(set(inventory) == set(WIDTHS), "cost inventory support")
    rhs = list(map(Q, BINS)) + [CALLS * inventory[w] for w in WIDTHS]
    counts = [dot(row, rhs) for row in inv]
    need(all(v >= 0 for v in counts), "primal cost feasibility")
    need(counts == [Q(e["count_per_replica"]) for e in entries], "basis count binding")
    return matrix, inv, idle, counts


def enclosure(coefficients, tariffs):
    lower = sum(v * tariffs[r][0 if v > 0 else 1] for r, v in coefficients.items())
    upper = sum(v * tariffs[r][1 if v > 0 else 0] for r, v in coefficients.items())
    need(lower <= upper, "cost interval order")
    return lower, upper


def serialize_interval(interval):
    return {"lower": str(interval[0]), "upper": str(interval[1])}


def dual_census(inv, idle, tariffs):
    dual = [{} for _ in range(10)]
    for j in range(10):
        for k, rank in enumerate(idle):
            if rank:
                dual[j][rank] = dual[j].get(rank, Q(0)) + inv[k][j]
    counts = {"patterns": 0, "tight": 0, "strict": 0}
    minimum = None
    for cap in CAPS:
        domains = [range(cap // width + 1) for width in WIDTHS]
        for numbers in itertools.product(*domains):
            remainder = cap - dot(numbers, WIDTHS)
            if remainder < 0:
                continue
            counts["patterns"] += 1
            col = [Q(int(cap == c)) for c in CAPS] + list(numbers)
            coeff = {int(remainder): Q(1)} if remainder else {}
            for j, value in enumerate(col):
                for rank, multiplier in dual[j].items():
                    coeff[rank] = coeff.get(rank, Q(0)) - value * multiplier
            coeff = {rank: value for rank, value in coeff.items() if value}
            if not coeff:
                counts["tight"] += 1
                continue
            lower, _ = enclosure(coeff, tariffs)
            need(lower > 0, "nonpositive cost reduced-cost lower bound")
            minimum = lower if minimum is None else min(minimum, lower)
            counts["strict"] += 1
    need(counts == {"patterns": 2551, "tight": 12, "strict": 2539}, "cost census")
    counts["minimum_reduced_cost_lower"] = str(minimum)
    return counts


def check_idle_mass(idle_delta, freed):
    need(sum(rank * number for rank, number in idle_delta.items()) == CALLS * freed,
         "unpaid freed helper width")


def marginal(matrix, inv, idle, counts, old, new):
    rhs = [Q(0)] * 10
    rhs[4 + WIDTHS.index(old)] = -CALLS
    rhs[4 + WIDTHS.index(new)] = CALLS
    delta = [dot(row, rhs) for row in inv]
    need([dot(row, delta) for row in matrix] == rhs, "inventory perturbation identity")
    need(all(x + dx >= 0 for x, dx in zip(counts, delta)), "changed basis feasibility")
    idle_delta = {}
    for rank, change in zip(idle, delta):
        if rank and change:
            idle_delta[rank] = idle_delta.get(rank, Q(0)) + change
    freed = old - new
    expected = {3: -Q(9 * freed, 20), 5: -Q(9 * freed, 4), 48: Q(9 * freed, 20)}
    need(idle_delta == expected, "changed optimal idle profile")
    check_idle_mass(idle_delta, freed)
    return {
        "old_width": old,
        "new_width": new,
        "basis_delta_per_replica": list(map(str, delta)),
        "idle_delta_per_replica": {str(r): str(v) for r, v in sorted(idle_delta.items())},
    }


def complete_profiles(claim, cert, literal):
    need(claim["profile"] == literal, "literal complete profile binding")
    need(claim["local_profile"] == cert["local_per_call"], "local profile binding")
    need(claim["width_inventory"] == cert["inventory_per_call"], "inventory binding")
    replicas = claim["replicas"]
    need(type(replicas) is int and replicas == 74, "replica binding")
    need(claim["calls"] == CALLS * replicas == 666, "complete local call multiplicity")
    paid = {int(r): Q(n) for r, n in literal.items()}
    need(sum(r * n for r, n in paid.items()) == 65088 * replicas, "literal rank mass")
    fractional = {int(r): CALLS * Q(n) for r, n in cert["local_per_call"].items()}
    for rank, number in cert["idle_per_replica"].items():
        fractional[int(rank)] = fractional.get(int(rank), Q(0)) + Q(number)
    need(sum(r * n for r, n in fractional.items()) == 65088, "fractional rank mass")
    need(all(paid.get(r, 0) >= replicas * n for r, n in
             {int(r): CALLS * Q(n) for r, n in cert["local_per_call"].items()}.items()),
         "literal profile omits local calls")
    return fractional


def controls():
    trials = {
        "one_of_two_freed_width_units_unpaid": lambda: check_idle_mass(
            {3: -Q(9, 20), 5: -Q(9, 4), 48: Q(9, 20)}, 2),
        "omitted_rank48_idle_charge": lambda: check_idle_mass(
            {3: -Q(9, 10), 5: -Q(9, 2)}, 2),
        "overfilled_basis_pattern": lambda: pattern(8, [8, 4]),
        "source_corruption_before_execution": lambda: authenticate(b"corrupt", PINS["tools/root.py"]),
    }
    rejected = []
    for name, action in trials.items():
        try:
            action()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("cost control accepted: " + name)
    return rejected


def verify_cost(root):
    """Return a deterministic receipt; root is the repository/export directory."""
    values, kernel = sources(Path(root))
    claim = values["CLAIM.json"]
    cert = values["certificates/RELAX-CAP.json"]
    target = Q(claim["complex_lower"])
    need(target == Q("0.001729033982646513517717"), "cost comparator parameter")
    matrix, inv, idle, counts = setup(cert)
    tariffs = {r: kernel.H(r, target) for r in range(1, 49)}
    census = dual_census(inv, idle, tariffs)
    changes = [marginal(matrix, inv, idle, counts, old, new)
               for old, new in ((8, 7), (9, 8), (9, 7))]
    debit = enclosure({48: Q(1, 20), 3: -Q(1, 20), 5: -Q(1, 4)}, tariffs)
    budget = enclosure({1: Q(2), 48: -Q(1, 10), 3: Q(1, 10), 5: Q(1, 2)}, tariffs)
    fractional = complete_profiles(claim, cert, values["allocation/PROFILE.json"])
    moment = kernel.moment(fractional, target, 896)
    slack = (Q(73 * 896, 9) * (1 - moment[1]), Q(73 * 896, 9) * (1 - moment[0]))
    need(0 < debit[0] and 0 < budget[0] and 0 < slack[0], "positive cost boundary")
    ceiling = (budget[0] + slack[0], budget[1] + slack[1])
    return {
        "status": "PASS_FIXED_TARGET_FRACTIONAL_COST_SCREEN",
        "parameter": "complex moment b, not a newly released outer kappa",
        "target": str(target),
        "dual_census": census,
        "marginals": changes,
        "idle_debit_per_freed_width": serialize_interval(debit),
        "two_width_local_overhead_budget": serialize_interval(budget),
        "old_literal_fractional_headroom_per_call": serialize_interval(slack),
        "two_width_overhead_ceiling_for_old_literal_target": serialize_interval(ceiling),
        "rejected_controls": controls(),
        "scope": "Fixed bins, one additional inventory change, fractional owners; no extraction or admission.",
    }


if __name__ == "__main__":
    print(json.dumps(verify_cost(Path(__file__).resolve().parents[2]), sort_keys=True))
