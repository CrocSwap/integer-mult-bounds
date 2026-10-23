#!/usr/bin/env python3
"""Trace one arbitrary-input coefficient through the pinned P104 word."""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
INPUTS = {
    "research/p104-endpoint-geometric-budget/geometry.py",
    "research/p104-joint-unit-flags/CERTIFICATE.json",
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
    "research/p104-native-channel/inputs/P104-FIXTURE.json",
}


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL_P104_FLAG0_COEFFICIENT_TRANSPORT " + message)


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def authenticate():
    sources = read("research/p104-flag0-coefficient-transport/SOURCES.json")
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    need(set(pinned) == INPUTS, "input inventory changed")
    for path, row in pinned.items():
        actual = sha256((ROOT / path).read_bytes()).hexdigest()
        need(actual == row["sha256"], "input digest changed: " + path)


def ports(fixture):
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.append(tuple(row))
    roots += [
        (1, *signs)
        for signs in product((-1, 1), repeat=7)
        if signs.count(-1) % 2 == 0
    ]
    section = fixture["section4_explicit_P104"]
    excluded = {tuple(row) for row in section["F0"] + section["C"]}
    return sorted(set(roots) - excluded)


def chronology(program, source, target):
    source_events = [i for i, event in enumerate(program) if source in event]
    target_events = [i for i, event in enumerate(program) if target in event]
    pair_joint = sum(source in event and target in event for event in program)
    need(source_events and target_events, "a named register has no event")
    return source_events[0], source_events[-1], target_events[0], target_events[-1], pair_joint


def trace_one_hot(program, source, target):
    # Coefficients of the formal input z in each logical register row.
    rows = {source: Fraction(1)}
    target_adds = []
    for index, event in enumerate(program):
        kind = event[0]
        if kind == "add":
            _, dst, src, scalar, *_ = event
            scalar = Fraction(scalar)
            source_coefficient = rows.get(src, Fraction(0))
            delta = scalar * source_coefficient
            before = rows.get(dst, Fraction(0))
            rows[dst] = before + delta
            if dst == target and delta:
                target_adds.append(
                    {
                        "event": index,
                        "source": src,
                        "scale": str(scalar),
                        "source_coefficient": str(source_coefficient),
                        "delta": str(delta),
                        "after": str(rows[dst]),
                    }
                )
        elif kind == "transport":
            # The pinned native-channel proof says a transport changes only the
            # frame and retains the logical coefficient row.
            continue
        elif kind == "zero":
            rows[event[1]] = Fraction(0)
        elif kind == "copy":
            rows[event[1]] = rows.get(event[2], Fraction(0))
        elif kind == "erase":
            rows[event[1]] = Fraction(0)
        else:
            need(False, f"unknown event {index}: {kind}")
    return rows.get(target, Fraction(0)), target_adds


def evaluate():
    authenticate()
    certificate = read("research/p104-joint-unit-flags/CERTIFICATE.json")
    witness = read("research/p104-native-channel/inputs/LOWRANK-WITNESS.json")
    fixture = read("research/p104-native-channel/inputs/P104-FIXTURE.json")
    geometry = (ROOT / "research/p104-endpoint-geometric-budget/geometry.py").read_text(
        encoding="utf-8"
    )
    need("ports = sorted(roots -" in geometry, "P104 port ordering source changed")
    need("paths[f'X{s}']" in geometry and "paths[f'Y{t}']" in geometry,
         "source/target path naming changed")
    helpers = certificate["helpers"]
    need(len(helpers) == 208, "joint flag collection size changed")
    flag = helpers[0]
    need(
        (flag["source"], flag["target"], flag["basis"][0]) == (0, 34, 232),
        "selected flag 0 changed",
    )

    vectors = ports(fixture)
    need(len(vectors) == 104, "P104 port count changed")
    src_vec, dst_vec = vectors[0], vectors[34]
    raw_dot = sum(x * y for x, y in zip(src_vec, dst_vec, strict=True))
    need(sum(x * x for x in src_vec) == 8, "source root scale changed")
    need(sum(y * y for y in dst_vec) == 8, "target root scale changed")
    need(raw_dot == 4, "flag 0 Gram pairing changed")
    native_expected = Fraction(raw_dot, 8)
    side_required = -native_expected  # off-diagonal entry of I - G/2

    program = witness["program"]
    need(len(program) == 4058, "native word length changed")
    source, target = "X0", "Y34"
    source_first, source_last, target_first, target_last, pair_joint = chronology(
        program, source, target
    )
    need(target_first == 129 and source_first == 591, "flag 0 event cut changed")
    need(target_last == 3500 and source_last == 3954, "flag 0 last event changed")
    need(pair_joint == 0, "X0 and Y34 now share an event")
    need(target_first < source_first < target_last, "event ordering changed")

    native_coefficient, target_adds = trace_one_hot(program, source, target)
    need(native_coefficient == native_expected, "one-hot native coefficient mismatch")
    expected_adds = [
        {
            "event": 2815,
            "source": "D17",
            "scale": "-1/4",
            "source_coefficient": "-2",
            "delta": "1/2",
            "after": "1/2",
        },
        {
            "event": 2998,
            "source": "D13",
            "scale": "1/4",
            "source_coefficient": "-2",
            "delta": "-1/2",
            "after": "0",
        },
        {
            "event": 3369,
            "source": "D23",
            "scale": "1/4",
            "source_coefficient": "2",
            "delta": "1/2",
            "after": "1/2",
        },
    ]
    need(target_adds == expected_adds, "flag 0 relay additions changed")

    controls = []
    for value in (Fraction(1), Fraction(7, 11), Fraction(-3, 5)):
        native = native_coefficient * value
        correction = side_required * value
        need(native + correction == 0, "side coefficient sign control failed")
        need(native != correction, "native and correction signs collapsed")
        controls.append(
            {
                "z": str(value),
                "native_y34": str(native),
                "required_side_addition": str(correction),
            }
        )

    return {
        "status": "PASS_P104_FLAG0_COEFFICIENT_TRANSPORT",
        "flag0": {"source": source, "target": target, "basis_head": 232},
        "events": {
            "target_first": target_first,
            "source_first": source_first,
            "target_last": target_last,
            "source_last": source_last,
            "X0_Y34_joint_events": pair_joint,
        },
        "raw_doubled_root_dot": raw_dot,
        "native_G_over_2_coefficient": str(native_coefficient),
        "required_I_minus_G_over_2_coefficient": str(side_required),
        "target_additions": target_adds,
        "one_hot_fixture": "x0=z; other x and dirty coefficients zero; y34=0",
        "controls": controls,
        "no_correction_program_or_cost_claim": True,
    }


def main():
    observed = evaluate()
    expected = read("research/p104-flag0-coefficient-transport/RESULT.json")
    need(observed == expected, "RESULT.json differs from exact replay")
    print(
        "PASS_P104_FLAG0_COEFFICIENT_TRANSPORT "
        "flag0=X0->Y34 events=591:2815,2998,3369,3500 "
        "native=+1/2 side=-1/2 arbitrary_z no_correction_claim"
    )


if __name__ == "__main__":
    main()
