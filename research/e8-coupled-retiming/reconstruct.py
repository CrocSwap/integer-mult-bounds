"""Check the E8 scalar map, frame paths, and recursive cost from one certificate.

This file uses only the Python standard library. It imports no supplier code.
The checks do not prove the all-size tape compiler or the multiplication theorem.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(row, source, coefficient):
    for key, value in source.items():
        result = row.get(key, Q(0)) + coefficient * value
        if result:
            row[key] = result
        else:
            row.pop(key, None)


def elements(basis):
    result = {0}
    for vector in basis:
        require(vector not in result, "Dependent frame basis")
        result |= {x ^ vector for x in result}
    return frozenset(result)


@lru_cache(None)
def logarithm(ratio):
    def small(value):
        t = (value - 1) / (value + 1)
        total = Q(0)
        power = t
        terms = 80
        for j in range(terms):
            total += 2 * power / (2 * j + 1)
            power *= t * t
        tail = 2 * power / ((2 * terms + 1) * (1 - t * t))
        return total, total + tail

    exponent = 0
    while ratio >= 2:
        ratio /= 2
        exponent += 1
    lo, hi = small(ratio)
    a, b = small(Q(2))
    return lo + exponent * a, hi + exponent * b


def exponential(value):
    require(0 <= value < 1, "Exponential bound requires an argument below one")
    total = term = Q(1)
    for j in range(1, 21):
        term *= value / j
        total += term
    tail = term * value / 21 / (1 - value / 22)
    return total, total + tail


def moment(histogram, dimension, stock, saving, fallback=True):
    lo = hi = Q(0)
    terms = {rank: Q(count) for rank, count in histogram.items()}
    if fallback:
        terms[1] = terms.get(1, Q(0)) + Q(
            32 * dimension * dimension * sum(histogram.values()), 10**16
        )
    for rank, count in terms.items():
        a, b = logarithm(Q(dimension, rank))
        lower = exponential(saving * a)[0]
        upper = exponential(saving * b)[1]
        weight = count * rank / (dimension * stock)
        lo += weight * lower
        hi += weight * upper
    return lo, hi


def reconstruct(c):
    h, v, helpers = c["h"], c["v"], c["R"]
    require((h, v) == (9, 120), "This audit is for the E8 label family")
    require(not c["ext"], "Exterior gauges are outside this audit")
    ports = c["ports"]
    require(set(ports) == {p for p in range(512) if p.bit_count() in (3, 7)}, "E8 ports")
    spaces = [elements(f) for f in c["frames"]]
    dimensions = [len(f) for f in c["frames"]]
    require(len(set(spaces)) == len(spaces), "Duplicate frame spaces")
    require(all(all(0 <= x < 512 for x in s) for s in spaces), "Frame outside ambient space")
    total = 2 * v + helpers
    require(len(c["start"]) == len(c["final"]) == total, "Endpoint count")
    current = list(c["start"])
    rows = [{i: Q(1)} if i < v else {} for i in range(total)]
    by_role = {kind: Counter() for kind in "xysc"}
    allowed = {("x", "s"), ("s", "s"), ("s", "y"), ("x", "y"), ("x", "x")}

    def kind(register):
        return "x" if register < v else "y" if register < 2 * v else "s"

    def climb(register, frame):
        previous = current[register]
        require(spaces[previous] <= spaces[frame], "A frame path is not nested")
        if previous != frame:
            by_role[kind(register)][dimensions[frame] - dimensions[previous]] += 1
            current[register] = frame

    for i, port in enumerate(ports):
        require(spaces[current[i]] == {0, port}, "Source start")
        require(spaces[c["final"][i]] == frozenset(range(512)), "Source final")
        require(spaces[current[v + i]] == {0}, "Target start")
        require(spaces[c["final"][v + i]] == {x for x in range(512) if (x & port).bit_count() % 2 == 0}, "Target final")
    for i in range(2 * v, total):
        require(spaces[current[i]] == {0} and len(spaces[c["final"][i]]) == 512, "Helper endpoints")

    def run(gates, phase):
        for gate in gates:
            tag, frame, pivot, terms = gate[:4]
            require(tag in ("in", "out"), "Unsupported gate")
            spectators = gate[4] if tag == "out" else []
            registers = [pivot] + [r for r, _, _ in terms] + spectators
            require(len(set(registers)) == len(registers), "Aliased gate ports")
            require(all(0 <= r < total for r in registers), "Register outside circuit")
            require(phase == "B" or all(kind(r) != "y" for r in registers), "Early target operation")
            for register in registers:
                climb(register, frame)
            for register, numerator, denominator in terms:
                target, source = (pivot, register) if tag == "in" else (register, pivot)
                require((kind(source), kind(target)) in allowed, "Unsupported scalar direction")
                require(denominator > 0, "Coefficient denominator")
                add(rows[target], rows[source], Q(numerator, denominator))

    run(c["A"], "A")
    retained = c["ret"]
    require(sorted(k for k, _, _ in retained) == list(range(len(retained))), "Retained total indices")
    totals = {}
    for k, register, frame in retained:
        require(kind(register) == "s" and current[register] == frame, "Retained total frame")
        totals[k] = dict(rows[register])
        by_role["c"][dimensions[frame]] += 1
    require(all(spaces[current[v + i]] == {0} for i in range(v)), "Target moved before scatter")
    require(len(c["scat"]["table"]) == v, "Scatter size")
    for target, entries in enumerate(c["scat"]["table"]):
        for k, numerator, denominator in entries:
            add(rows[v + target], totals[k], Q(numerator, denominator))
    run(c["B"], "B")
    require(all(rows[i] == {i: Q(1)} and rows[v + i] == {i: Q(1)} for i in range(v)), "Clean-source scalar identity")
    for i, frame in enumerate(c["final"]):
        climb(i, frame)
    recorded = {kind: {int(r): n for r, n in hist.items()} for kind, hist in c["blocks"].items()}
    require(by_role == recorded, "Recorded histogram differs from actual paths")
    invocation = sum(by_role.values(), Counter())
    copy_cost = sum(rank * count for rank, count in by_role["c"].items())
    require(copy_cost == c["cst"], "Copy cost")
    mass = sum(rank * count for rank, count in invocation.items())
    require(mass == c["N"] == helpers * h + 2 * v * (h - 1) + copy_cost, "Telescoping rank identity")
    histogram = Counter({rank: 5 * count for rank, count in invocation.items()})
    for rank in (h - 1, 2 * h - 2, 2 * h + 2, 4):
        histogram[rank] += 2 * v
    dimension, stock = 5 * h, 4 * v + helpers
    deficit = dimension * stock - sum(rank * count for rank, count in histogram.items())
    require(deficit == 4 * v - 5 * copy_cost, "Five-stage deficit")
    return {
        "h": h, "v": v, "helpers": helpers, "frames": len(spaces),
        "source_columns": v, "copy_cost": copy_cost,
        "invocation_histogram": dict(sorted(invocation.items())), "invocation_mass": mass,
        "m": dimension, "W": stock, "histogram": dict(sorted(histogram.items())),
        "rank_mass": dimension * stock - deficit, "deficit": deficit,
        "scope": "Exact scalar source columns and frame paths. The general dirty and frame transfer theorems remain dependencies. No tape compiler or Lean build is checked.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--saving", default="876248285600677/1000000000000000000")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    blob = args.certificate.read_bytes()
    raw = gzip.decompress(blob) if blob[:2] == b"\x1f\x8b" else blob
    result = reconstruct(json.loads(raw))
    result["source_sha256"] = hashlib.sha256(raw).hexdigest()
    saving = Q(args.saving)
    lower, upper = moment(result["histogram"], result["m"], result["W"], saving)
    following = moment(result["histogram"], result["m"], result["W"], saving + Q(1, 10**18))
    require(upper < 1, "Requested saving is not certified")
    result["saving"] = str(saving)
    scale = 2**256
    lo = lower - 1
    hi = upper - 1
    enclosed = [Q(lo.numerator * scale // lo.denominator, scale),
                Q(-((-hi.numerator * scale) // hi.denominator), scale)]
    result["moment_minus_one"] = list(map(str, enclosed))
    result["interval_method"] = "Exact rational log and exp bounds; outward rounding to 256 bits for the saved interval."
    result["adjacent_grid_excluded"] = following[0] > 1
    result["moment_gap_decimal"] = float(1 - upper)
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    print(json.dumps({k: result[k] for k in ("source_sha256", "helpers", "copy_cost", "invocation_mass", "rank_mass", "deficit", "saving", "moment_gap_decimal", "adjacent_grid_excluded")}, indent=2))


if __name__ == "__main__":
    main()
