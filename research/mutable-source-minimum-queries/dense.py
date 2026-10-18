#!/usr/bin/env python3
"""Second oracle: bit-matrix execution, with no imports from the symbolic engine."""
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def apply(matrix, value):
    return sum(((row & value).bit_count() % 2) << k for k, row in enumerate(matrix))


def run_root(word, values, matrices):
    state = values.copy()
    for event in word:
        kind = event[0]
        if kind == "Q":
            state["z"] ^= apply(matrices["B"], state[f"x{event[1]}"])
        elif kind == "R":
            state[f"y{event[1]}"] ^= apply(matrices[f"A{event[1]}"], state["z"])
        elif kind == "X":
            state[f"x{event[2]}"] ^= state[f"x{event[1]}"]
        else:
            raise ValueError("unknown root operation")
    return state


def run_leaves(word, values, matrices):
    state = values.copy()
    for op, source, target in word:
        need(source != target, "aliased port")
        state[target] ^= state[source] if op == "" else apply(matrices[op], state[source])
    return state


def target(values, matrices):
    out = values.copy()
    for m in range(1, 32):
        source = 0
        for j in range(5):
            if m >> j & 1:
                source ^= values[f"x{j}"]
        out[f"y{m}"] ^= apply(matrices[f"A{m}"], apply(matrices["B"], source))
    return out


def bank(length, identity=False):
    rng = random.Random(9017 + length)
    unit = [1 << j for j in range(length)]
    matrices = {}
    for name in [f"B{k}" for k in range(5)] + [f"A{m}" for m in range(1, 32)]:
        matrices[name] = unit[:] if identity else [rng.randrange(1 << length) for _ in range(length)]
    if length >= 2 and not identity:
        # Two explicit noncommuting factors, without a probabilistic premise.
        matrices["B0"] = unit[:]
        matrices["B1"] = unit[:]
        matrices["B0"][0] ^= 2
        matrices["B1"][1] ^= 1
        # Keep the complete B nondegenerate as well: random singular suffixes
        # could otherwise erase the noncommuting-factor test's observable map.
        for k in range(2, 5):
            matrices[f"B{k}"] = unit[:]
            donor, target_row = rng.sample(range(length), 2)
            matrices[f"B{k}"][target_row] ^= 1 << donor
        matrices["A21"] = unit[:]
        need(any(apply(matrices["B0"], apply(matrices["B1"], 1 << k)) !=
                 apply(matrices["B1"], apply(matrices["B0"], 1 << k)) for k in range(length)),
             "noncommuting fixture failed")
    # Compute common B independently by multiplying the factor matrices on columns.
    columns = []
    for j in range(length):
        value = 1 << j
        for k in range(5):
            value = apply(matrices[f"B{k}"], value)
        columns.append(value)
    matrices["B"] = [sum(((column >> k) & 1) << j for j, column in enumerate(columns))
                     for k in range(length)]
    if length >= 2:
        need(len({apply(matrices["B"], value) for value in range(1 << length)}) == 1 << length,
             "nondegenerate B fixture failed")
    return matrices


def main():
    cert = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    names = [f"x{j}" for j in range(5)] + [f"y{m}" for m in range(1, 32)] + ["z", "w0", "w1", "w2"]
    executions = 0
    fixtures = [(1, True)] + [(length, False) for length in range(1, 5)]
    for length, identity in fixtures:
        matrices = bank(length, identity)
        initial = []
        for name in names:
            for bit in range(length):
                values = dict.fromkeys(names, 0)
                values[name] = 1 << bit
                initial.append(values)
        rng = random.Random(2301 + length)
        initial += [{name: rng.randrange(1 << length) for name in names} for _ in range(4)]
        for item in cert["schedules"].values():
            word, leaves = item["word"], item["leaf_word"]
            for values in initial:
                wanted = target(values, matrices)
                actual = run_root(word, values, matrices)
                need(actual == wanted, "dense root forward failed")
                need(run_root(word[::-1], actual, matrices) == values, "dense root inverse failed")
                actual = run_leaves(leaves, values, matrices)
                need(actual == wanted, "dense expanded forward failed")
                need(run_leaves(leaves[::-1], actual, matrices) == values, "dense expanded inverse failed")
                executions += 4
    # Independent concrete failure witnesses on scalar identity maps.
    item = cert["schedules"]["minimum_queries"]
    matrices = bank(1, True)
    values = dict.fromkeys(names, 0)
    values["x1"] = 1
    bad = item["word"][:-1]
    actual = run_root(bad, values, matrices)
    wanted = target(values, matrices)
    # Last XOR donor is x1: outputs remain correct, x0 fails restoration.
    need(all(actual[f"y{m}"] == wanted[f"y{m}"] for m in range(1, 32)) and actual["x0"] != 0,
         "concrete source-only restoration control failed")
    values = dict.fromkeys(names, 0)
    values["z"] = 1
    bad = [e[:] for e in item["word"]]
    bad.pop(next(i for i, e in enumerate(bad) if e[0] == "R"))
    need(run_root(bad, values, matrices) != target(values, matrices), "concrete dirty-z control failed")
    report = {"fixtures": len(fixtures), "lengths": [1, 2, 3, 4], "all_basis_and_mixed_executions": executions,
              "directions": ["root_forward", "root_inverse", "expanded_forward", "expanded_inverse"],
              "schedules": 4, "concrete_failure_controls": 2}
    need(report == json.loads((HERE / "DENSE.json").read_text(encoding="utf-8")), "dense receipt drift")
    print(f"PASS_MINIMUM_QUERY_DENSE fixtures=5 executions={executions} controls=2")


if __name__ == "__main__":
    main()
