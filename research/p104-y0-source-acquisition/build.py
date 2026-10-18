#!/usr/bin/env python3
"""Emit the fixed Y0 two-arrival word; verification is in verify.py.

Prepared for commdata2338, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def span(basis):
    values = {0}
    for b in basis:
        values |= {x ^ b for x in tuple(values)}
    return values


def basis_of(values):
    basis, current = [], {0}
    for v in sorted(values):
        if v not in current:
            basis.append(v)
            current |= {x ^ v for x in tuple(current)}
    if current != set(values):
        raise ValueError("not a subspace")
    return basis


def build():
    source = ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
    word = json.loads(source.read_text())
    fixture = json.loads((ROOT / "research/p104-native-channel/inputs/P104-FIXTURE.json").read_text())
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            r = [0] * 8
            r[i], r[j] = 2, 2 * sign
            roots.add(tuple(r))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            roots.add((1, *signs))
    data = fixture["section4_explicit_P104"]
    roots -= {tuple(r) for r in data["F0"] + data["C"]}
    ports = sorted(roots)
    coefficients = {
        s: Fraction(int(s == 0)) - Fraction(sum(x * y for x, y in zip(ports[0], r)), 8)
        for s, r in enumerate(ports)
    }
    coefficients = {s: c for s, c in coefficients.items() if c}
    terminal = span(word["final_frames"]["Y0"])
    endpoint = basis_of(terminal)
    full = list(1 << j for j in range(9))
    normals = [1, 4]
    rooms = [basis_of({v for v in terminal if (v & n).bit_count() % 2 == 0})
             for n in normals]
    groups = [[], []]
    for s in coefficients:
        line = span(word["initial_frames"][f"X{s}"])
        choices = [j for j, room in enumerate(rooms) if line <= span(room)]
        if not choices:
            raise ValueError("uncovered source")
        groups[choices[0]].append(s)
    initial = {f"N{s}": [] for s in coefficients}
    final = {f"N{s}": full for s in coefficients}
    first, last = [], []

    def move(events, register, before, after):
        events.append(["transport", register, before, after, len(after) - len(before)])

    for s in coefficients:
        first.append(["add", "Y0", f"N{s}", -1, []])
    for group, room in zip(groups, rooms):
        for s in group:
            reg, line = f"N{s}", word["initial_frames"][f"X{s}"]
            move(first, reg, [], line)
            first.append(["add", reg, f"X{s}", str(coefficients[s]), line])
            move(first, reg, line, room)
        collector = f"N{group[0]}"
        for s in group[1:]:
            first.append(["add", collector, f"N{s}", 1, room])
        # Keep feeder values intact until after collector delivery/unmerging.
        for s in group[1:]:
            move(first, f"N{s}", room, full)
        move(last, collector, room, endpoint)
        last.append(["add", "Y0", collector, 1, endpoint])
        move(last, collector, endpoint, full)
        for s in group[1:]:
            last.append(["add", collector, f"N{s}", -1, full])
        for s in group:
            last.append(["add", f"N{s}", f"X{s}", str(-coefficients[s]), full])
    return {
        "schema_version": 1,
        "source_witness_sha256": sha256(source.read_bytes()).hexdigest(),
        "target": 0, "cover_normals": normals, "groups": groups,
        "initial_frames": initial, "final_frames": final,
        "insertions": [{"completed_cut": 0, "events": first},
                       {"completed_cut": 3467, "events": last}],
    }


def formatted(value, depth=0):
    """Keep each literal event on one line for review."""
    pad = "  " * (depth + 1)
    if isinstance(value, dict):
        entries = [pad + json.dumps(k) + ": " + formatted(v, depth + 1)
                   for k, v in sorted(value.items())]
        return "{\n" + ",\n".join(entries) + "\n" + "  " * depth + "}"
    if isinstance(value, list) and value and isinstance(value[0], (dict, list)):
        return "[\n" + ",\n".join(pad + formatted(v, depth + 1) for v in value) + "\n" + "  " * depth + "]"
    return json.dumps(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path, help="new output file; never overwritten")
    args = parser.parse_args()
    with args.out.open("x", encoding="utf-8") as out:
        out.write(formatted(build()) + "\n")


if __name__ == "__main__":
    main()
