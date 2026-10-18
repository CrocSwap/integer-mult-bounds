#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact scalar/frame counterexample to the P104 arrival-shape premise."""

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PORTS = 104
FULL = tuple(1 << i for i in range(8, -1, -1))
CORE_EVENTS = 4058
CARRIERS = 4992
MAX_EVENTS = CORE_EVENTS + 7 * CARRIERS


def require(ok, message):
    if not ok:
        raise ValueError(message)


def frame(vectors):
    require(isinstance(vectors, (list, tuple)) and len(vectors) <= 9, "frame size")
    pivots = [0] * 9
    for value in vectors:
        require(type(value) is int and 0 < value < 512, "binary label")
        for bit in range(8, -1, -1):
            if value & (1 << bit):
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    for bit in range(9):
        for higher in range(bit + 1, 9):
            if pivots[higher] & (1 << bit):
                pivots[higher] ^= pivots[bit]
    return tuple(value for value in reversed(pivots) if value)


def subset(left, right):
    for value in left:
        for pivot in right:
            value = min(value, value ^ pivot)
        if value:
            return False
    return True


def load_inputs():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for item in sources["files"]:
        if item["usage"] == "input":
            data = (ROOT / item["path"]).read_bytes()
            require(hashlib.sha256(data).hexdigest() == item["sha256"], "source pin")
    for item in sources["external_inputs"]:
        data = (PACKAGE / item["path"]).read_bytes()
        require(
            hashlib.sha256(data).hexdigest() == item["sha256"], "external source pin"
        )
    inputs = ROOT / "research/p104-native-channel/inputs"
    return (
        json.loads((inputs / "LOWRANK-WITNESS.json").read_text()),
        json.loads((inputs / "P104-FIXTURE.json").read_text()),
    )


def correction(fixture):
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.add(tuple(row))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            roots.add((1, *signs))
    puncture = fixture["section4_explicit_P104"]
    removed = {tuple(row) for row in puncture["F0"] + puncture["C"]}
    roots = sorted(roots - removed)
    require(len(roots) == PORTS, "P104 root count")
    matrix = []
    for t, target in enumerate(roots):
        row = []
        for s, source in enumerate(roots):
            dot = sum(a * b for a, b in zip(target, source, strict=True))
            require(dot % 4 == 0, "integral root Gram entry")
            row.append(Q(t == s) - Q(dot, 8))
        matrix.append(row)
    require(
        sum(bool(x) for row in matrix for x in row) == CARRIERS, "correction support"
    )
    return matrix


def make_word(witness, matrix):
    """Batch ZERO/source contacts before the core; hyperplane/FULL contacts after."""
    require(len(witness["program"]) == CORE_EVENTS, "core event bound")
    initial = dict(witness["initial_frames"])
    final = dict(witness["final_frames"])
    before, after = [], []
    for t in range(PORTS):
        for s in range(PORTS):
            coefficient = matrix[t][s]
            if not coefficient:
                continue
            helper, source, target = f"H{t}_{s}", f"X{s}", f"Y{t}"
            line, hyperplane = initial[source], final[target]
            require(
                len(frame(line)) == 1 and len(frame(hyperplane)) == 8,
                "carrier dimensions",
            )
            require(
                subset(frame(line), frame(hyperplane)),
                "source line in target hyperplane",
            )
            require(
                initial[target] == [] and frame(final[source]) == FULL,
                "contact boundaries",
            )
            initial[helper], final[helper] = [], list(FULL)
            before.extend(
                [
                    ["add", target, helper, "-1", []],
                    ["transport", helper, [], line, 1],
                    ["add", helper, source, str(coefficient), line],
                    ["transport", helper, line, hyperplane, 7],
                ]
            )
            after.extend(
                [
                    ["add", target, helper, "1", hyperplane],
                    ["transport", helper, hyperplane, list(FULL), 1],
                    ["add", helper, source, str(-coefficient), list(FULL)],
                ]
            )
    program = before + witness["program"] + after
    require(len(program) == MAX_EVENTS, "complete event count")
    return {"initial_frames": initial, "final_frames": final, "program": program}


def add_row(destination, source, coefficient):
    for name, value in source.items():
        result = destination.get(name, Q(0)) + coefficient * value
        if result:
            destination[name] = result
        else:
            destination.pop(name, None)


def execute(word):
    """Replay every independent input, including arbitrary helper dirt."""
    require(len(word["program"]) <= MAX_EVENTS, "event capacity")
    require(len(word["initial_frames"]) <= 280 + CARRIERS, "register capacity")
    frames = {name: frame(value) for name, value in word["initial_frames"].items()}
    rows = {name: {name: Q(1)} for name in frames}
    profile, scalar = Counter(), Counter()
    for event in word["program"]:
        kind, register = event[:2]
        if kind == "transport":
            _, _, old, new, rank = event
            old, new = frame(old), frame(new)
            require(frames[register] == old, "transport entry")
            require(subset(old, new) or subset(new, old), "nested transport")
            if register.startswith("H"):
                require(subset(old, new) and len(old) < len(new), "monotone carrier")
            require(
                type(rank) is int and rank == abs(len(new) - len(old)) > 0,
                "transport rank",
            )
            frames[register] = new
            profile[rank] += 1
        elif kind == "add":
            _, _, source, coefficient, common = event
            require(
                register != source
                and frames[register] == frames[source] == frame(common),
                "common addition frame",
            )
            coefficient = Q(coefficient)
            require(
                coefficient.denominator <= 8 and abs(coefficient) <= 4,
                "scalar alphabet",
            )
            add_row(rows[register], rows[source], coefficient)
            scalar[kind] += 1
        elif kind == "zero":
            require(
                register == "C" and register not in rows, "owned private initialization"
            )
            frames[register], rows[register] = frame(event[2]), {}
            scalar[kind] += 1
        elif kind == "copy":
            _, _, source, common = event
            require(register == "C" and not rows[register], "owned zero copy target")
            require(frames[register] == frames[source] == frame(common), "copy frame")
            rows[register] = dict(rows[source])
            scalar[kind] += 1
        else:
            require(kind == "erase" and register == "C", "owned private erasure")
            require(frames[register] == frame(event[2]), "private erasure frame")
            del frames[register], rows[register]
            scalar[kind] += 1
    require(set(rows) == set(word["initial_frames"]), "all private lifetimes closed")
    require(
        frames == {name: frame(value) for name, value in word["final_frames"].items()},
        "final frames",
    )
    return rows, dict(sorted(profile.items())), dict(sorted(scalar.items()))


def check_endpoints(rows, matrix=None):
    for name, row in rows.items():
        expected = {name: Q(1)}
        if name.startswith("Y"):
            t = int(name[1:])
            if matrix is None:
                expected[f"X{t}"] = Q(1)
            else:
                expected.update(
                    {
                        f"X{s}": Q(t == s) - matrix[t][s]
                        for s in range(PORTS)
                        if Q(t == s) - matrix[t][s]
                    }
                )
        require(row == expected, "arbitrary-input endpoint " + name)


def export_relay_word(word):
    """Express only the added correction in the predecessor checker's grammar."""
    initial_count = 4 * CARRIERS
    helpers = {}
    for event in word["program"][:initial_count]:
        if event[0] == "add" and event[1].startswith("Y"):
            helpers[event[2]] = len(helpers)
    require(len(helpers) == CARRIERS, "export helper count")
    ops = [["move_zero_all", CARRIERS]]
    for cut, events in (
        (0, word["program"][:initial_count]),
        (CORE_EVENTS, word["program"][initial_count + CORE_EVENTS :]),
    ):
        for event in events:
            kind, destination = event[:2]
            if kind == "transport":
                ops.append(["move", helpers[destination], event[3]])
            elif destination.startswith("Y"):
                ops.append(
                    ["write", int(destination[1:]), helpers[event[2]], event[3], cut]
                )
            else:
                ops.append(
                    ["read", helpers[destination], int(event[2][1:]), event[3], cut]
                )
    return {"lifetimes": CARRIERS, "ops": ops}


def audit():
    witness, fixture = load_inputs()
    matrix = correction(fixture)
    core, native_profile, _ = execute(witness)
    check_endpoints(core, matrix)
    word = make_word(witness, matrix)
    rows, profile, scalar = execute(word)
    check_endpoints(rows)
    added = {
        rank: profile.get(rank, 0) - native_profile.get(rank, 0) for rank in profile
    }
    added = {rank: count for rank, count in added.items() if count}
    require(added == {1: 9984, 7: 4992}, "arrival profile")
    # The coverage template is an explicitly conditional accounting assumption.
    total = Q(72 * 832, 9) + 56
    native_mass = sum(rank * count for rank, count in native_profile.items())
    allowance = total - native_mass
    require(native_mass == 2368 and allowance == 4344, "native coverage allowance")
    require(9 * 482 <= allowance < 9 * 483, "fixed-template lifetime limit")
    return {
        "status": "PASS_P104_ARRIVAL_SHAPE_AUDIT",
        "correction_entries": CARRIERS,
        "registers": len(rows),
        "events": len(word["program"]),
        "added_profile": added,
        "added_rank_mass": sum(rank * count for rank, count in added.items()),
        "scalar_events": scalar,
        "conservative_fixed_template_lifetime_limit": 482,
        "scope": (
            "Logical scalar/frame counterexample; "
            "no feasible <=482 design or new kappa."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write receipt to a new file")
    parser.add_argument(
        "--relay-word", type=Path, help="export correction for the original checker"
    )
    args = parser.parse_args()
    result = audit()
    expected = json.loads((PACKAGE / "EXPECTED.json").read_text())
    # JSON round-trip normalizes integer histogram keys for receipt comparison.
    require(json.loads(json.dumps(result)) == expected, "expected receipt")
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        with args.out.open("x") as handle:
            require(handle.write(output) == len(output), "complete receipt write")
    if args.relay_word:
        witness, fixture = load_inputs()
        word = export_relay_word(make_word(witness, correction(fixture)))
        encoded = json.dumps(word) + "\n"
        with args.relay_word.open("x") as handle:
            require(handle.write(encoded) == len(encoded), "complete word write")
    print(output, end="")


if __name__ == "__main__":
    main()
