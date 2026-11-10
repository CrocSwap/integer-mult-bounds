"""Replay the finite six-piece rank-chain limitation; write only to stdout."""

import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

from model import cut_tables, integer_rank


def require(predicate, message):
    if not predicate:
        raise ValueError(message)


def dynamic_program(length, subsets, cost, demand):
    require(length in (5, 6, 7), "unsupported certificate length")
    best = None
    minimum_costs = []
    for start in range(64):
        # Every finite cost is at most 7*35, so 1000 is an exact infinity sentinel.
        previous = {end: (0 if end == start else 1000) for end in subsets[start]}
        for _ in range(length):
            previous = {
                end: min(previous[middle] + cost[middle][end]
                         for middle in subsets[start] if end & middle == end)
                for end in subsets[start]
            }
        row = []
        for end in subsets[start]:
            value = previous[end]
            row.append(value)
            if demand[start][end]:
                candidate = (Fraction(value, demand[start][end]), start, end, value,
                             demand[start][end])
                best = candidate if best is None or candidate < best else best
        minimum_costs.append(row)
    require(best is not None, "no positive demand")
    ratio, start, end, numerator, denominator = best
    return {"length": length, "capacity": str(ratio), "start": start, "end": end,
            "cost": numerator, "demand": denominator, "minimum_costs": minimum_costs}


def literal_chains(length, cost, demand):
    # A bit is absent, or leaves at one of length+1 boundaries: (length+2)^6 chains.
    best = None
    count = 0
    positive = 0
    witness = None
    for exits in product(range(length + 2), repeat=6):
        chain = tuple(sum(1 << bit for bit, leave in enumerate(exits) if leave > t)
                      for t in range(length + 1))
        count += 1
        denominator = demand[chain[0]][chain[-1]]
        if not denominator:
            continue
        positive += 1
        numerator = sum(cost[chain[t]][chain[t + 1]] for t in range(length))
        ratio = Fraction(numerator, denominator)
        if best is None or ratio < best:
            best, witness = ratio, chain
    require(count == (length + 2) ** 6, "chain coverage mismatch")
    return {"chains": count, "positive_demand_chains": positive,
            "capacity": str(best), "attaining_chain": witness}


def compute():
    planes, orbits, subsets, cost, demand = cut_tables()
    programs = [dynamic_program(n, subsets, cost, demand) for n in (5, 6, 7)]
    for row, expected in zip(programs, ("19/10", "23/10", "27/10")):
        require(row["capacity"] == expected, "unexpected exact chain capacity")
    literal = {str(n): literal_chains(n, cost, demand) for n in (6, 7)}
    for row in programs[1:]:
        require(row["capacity"] == literal[str(row["length"])]["capacity"],
                "direct chain enumeration disagrees with dynamic programming")
    return {"schema_version": 1, "planes": planes, "orbits": orbits,
            "call_cut_ranks": cost, "target_cut_ranks": demand,
            "dynamic_programs": programs, "literal": literal}


def rejection_controls(result):
    rejected = 0
    for false_predicate, name in (
        (Fraction(result["dynamic_programs"][1]["capacity"]) < 2, "six calls fail for two"),
        (Fraction(result["dynamic_programs"][2]["capacity"]) >= 3, "seven calls pass for three"),
        (result["literal"]["7"]["chains"] == 8 ** 6, "seven-call chain undercount"),
    ):
        try:
            require(false_predicate, name)
        except ValueError:
            rejected += 1
    # A rank-one matrix with dependent rows detects counting nonzero rows as rank.
    require(integer_rank([[1, 2], [2, 4]], range(2), range(2)) == 1,
            "rank dependence control failed")
    require(rejected == 3, "a false mathematical assertion was accepted")
    return rejected


def certificate_text(result):
    lines = []
    for key, value in sorted(result.items()):
        if key.endswith("cut_ranks"):
            encoded = "[\n" + ",\n".join("    " + json.dumps(row) for row in value) + "\n  ]"
        else:
            encoded = json.dumps(value, sort_keys=True)
        lines.append("  " + json.dumps(key) + ": " + encoded)
    return "{\n" + ",\n".join(lines) + "\n}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit regenerated certificate")
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(certificate_text(result))
        return
    package = Path(__file__).resolve().parent
    expected = json.loads((package / "CERTIFICATE.json").read_text())
    require(json.loads(json.dumps(result)) == expected, "committed certificate differs")
    controls = rejection_controls(result)
    files = sorted(path for path in package.iterdir() if path.is_file())
    require(len(files) <= 10, "unexpected package inventory")
    require(all(path.stat().st_size <= 2_000_000 for path in files), "oversize package file")
    hashes = {path.name: sha256(path.read_bytes()).hexdigest() for path in files}
    print(json.dumps({"status": "PASS_BIT_PERMUTATION_CHAIN_LIMIT",
                      "chain_capacities": [r["capacity"] for r in result["dynamic_programs"]],
                      "literal_chains": sum(r["chains"] for r in result["literal"].values()),
                      "rejecting_controls": controls, "sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
