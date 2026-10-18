"""Generate exact early-prefix contact candidates using source projections.

This optional search does not import the acceptance checker. It tracks only
the eight coordinates x R^T; verify.py separately validates all 280 boundary
columns, availability, dirty cancellation, and the resulting rank claims.

Rohan Arun / PR1972 supplies the frozen scalar/frame channel, retained by
Chafik Boukhalfa / PR1991. Adam Gall / PR1940 supplies the schedule and Josie
Elliston / PR1071 supplies the P104 fixture and retained decoder lineage.
The pooled-space model follows Gonzalo Mier / PR2173 and Gareth Davidson /
PR2251. New early-prefix generation was prepared for AAAmirinu with
substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
import hashlib
import json
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path


HERE = Path(__file__).resolve().parent
UPPER_CUTS = (2526, 2556, 2572, 2618, 2646)
SOURCE_NAMES = ("LOWRANK-WITNESS.json", "P104-FIXTURE.json")


def load_sources(source_dir):
    """Bind both inputs to this package's source manifest before calculation."""
    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    pins = {}
    for entry in manifest["files"]:
        if entry.get("usage") != "input":
            continue
        name = Path(entry["path"]).name
        if name in SOURCE_NAMES:
            if name in pins:
                raise ValueError("duplicate input source pin: " + name)
            pins[name] = entry["sha256"]
    if set(pins) != set(SOURCE_NAMES):
        raise ValueError("missing channel or fixture source pin")

    inputs = {}
    for name in SOURCE_NAMES:
        raw = (source_dir / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != pins[name]:
            raise ValueError("input source hash mismatch: " + name)
        inputs[name] = json.loads(raw)
    return inputs["LOWRANK-WITNESS.json"], inputs["P104-FIXTURE.json"]


def root_ports(fixture):
    """Reconstruct the 104 doubled E8 roots without predecessor code."""
    lines = set()
    for first, second in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[first], row[second] = 2, 2 * sign
            lines.add(tuple(row))
    for tail in product((-1, 1), repeat=7):
        if tail.count(-1) % 2 == 0:
            lines.add((1, *tail))
    removed = {tuple(row) for row in fixture["F0"] + fixture["C"]}
    if len(lines) != 120 or len(removed) != 16 or not removed <= lines:
        raise ValueError("invalid P104 root fixture")
    return sorted(lines - removed)


@lru_cache(maxsize=None)
def subspace(vectors):
    values = {0}
    for vector in vectors:
        values |= {old ^ vector for old in tuple(values)}
    return tuple(sorted(values))


def insert_basis(basis, row):
    """Insert one rational row while retaining deterministic pivot order."""
    row = list(row)
    for pivot, previous in sorted(basis.items()):
        coefficient = row[pivot]
        if coefficient:
            row = [x - coefficient * y for x, y in zip(row, previous)]
    pivot = next((i for i, value in enumerate(row) if value), None)
    if pivot is None:
        return False
    divisor = row[pivot]
    basis[pivot] = [value / divisor for value in row]
    return True


def solve(matrix, rhs):
    """Return an exact solution with free variables zero, or None."""
    basis = {}
    for row, target in zip(matrix, rhs):
        augmented = list(row) + [target]
        for pivot, previous in sorted(basis.items()):
            coefficient = augmented[pivot]
            if coefficient:
                augmented = [x - coefficient * y
                             for x, y in zip(augmented, previous)]
        pivot = next((i for i, value in enumerate(augmented[:-1]) if value), None)
        if pivot is None:
            if augmented[-1]:
                return None
        else:
            divisor = augmented[pivot]
            basis[pivot] = [value / divisor for value in augmented]

    answer = [Fraction(0)] * (len(matrix[0]) if matrix else 0)
    for pivot, row in sorted(basis.items(), reverse=True):
        answer[pivot] = row[-1] - sum(
            x * y for x, y in zip(row[pivot + 1:-1], answer[pivot + 1:])
        )
    return answer


def projector_contacts(cut, roots, contacts, union_basis):
    """Solve U M = U in the space spanned by captured rank-one operators."""
    operators = [
        [Fraction(value) * component for value in roots[target]
         for component in projection]
        for target, _, _, projection in contacts
    ]
    equations, rhs = [], []
    for row in union_basis.values():
        for column in range(8):
            equations.append([
                sum(row[i] * operator[8 * i + column] for i in range(8))
                for operator in operators
            ])
            rhs.append(row[column])
    solution = solve(equations, rhs)
    if solution is None:
        raise ValueError("no required projector solution at cut " + str(cut))

    # Projections above are x R^T. Actual code coefficients are x R^T / 104,
    # so these contact weights satisfy M = R A and K = C + 12 A R.
    terms = [
        [target, contact_cut, register, str(104 * weight)]
        for (target, contact_cut, register, _), weight in zip(contacts, solution)
        if weight
    ]
    return {"cut": cut, "terms": terms}


def generate(channel, fixture):
    roots = root_ports(fixture)
    projections = {
        name: ([Fraction(value) for value in roots[int(name[1:])]]
               if name.startswith("X") else [Fraction(0)] * 8)
        for name in channel["initial_frames"]
    }
    frames = {name: subspace(tuple(vectors))
              for name, vectors in channel["initial_frames"].items()}
    pools = [set() for _ in roots]
    operator_basis, union_basis = {}, {}
    contacts, witnesses = [], []

    def capture(cut):
        groups = {}
        for name, frame in frames.items():
            groups.setdefault(frame, []).append(name)
        for names in groups.values():
            targets = [int(name[1:]) for name in names if name.startswith("Y")]
            if not targets:
                continue
            nonzero = [(name, tuple(projections[name]))
                       for name in names if any(projections[name])]
            for target in targets:
                for name, projection in nonzero:
                    if name == "Y" + str(target) or projection in pools[target]:
                        continue
                    pools[target].add(projection)
                    insert_basis(union_basis, projection)
                    operator = [Fraction(value) * component
                                for value in roots[target]
                                for component in projection]
                    if insert_basis(operator_basis, operator):
                        contacts.append((target, cut, name, projection))
        if cut in UPPER_CUTS:
            witnesses.append(projector_contacts(cut, roots, contacts, union_basis))

    capture(0)
    for index, event in enumerate(channel["program"][:max(UPPER_CUTS)]):
        operation, name = event[:2]
        if operation == "transport":
            frames[name] = subspace(tuple(event[3]))
        elif operation == "zero":
            projections[name] = [Fraction(0)] * 8
            frames[name] = subspace(tuple(event[2]))
        elif operation == "copy":
            projections[name] = projections[event[2]][:]
        elif operation == "erase":
            del projections[name]
            del frames[name]
        elif operation == "add":
            projections[name] = [
                x + Fraction(event[3]) * y
                for x, y in zip(projections[name], projections[event[2]])
            ]
        else:
            raise ValueError("unknown channel operation: " + str(operation))
        capture(index + 1)
    if tuple(witness["cut"] for witness in witnesses) != UPPER_CUTS:
        raise ValueError("channel ended before every requested witness cut")
    return {"schema": "p104-prefix-minrank/1", "witnesses": witnesses}


def main():
    parser = argparse.ArgumentParser(
        description="Generate P104 prefix contacts; validate separately with verify.py."
    )
    parser.add_argument("--source-dir", type=Path,
                        default=HERE.parent / "p104-native-channel" / "inputs")
    parser.add_argument("--out", type=Path, required=True,
                        help="new output path; existing files are never overwritten")
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError("output already exists: " + str(args.out))
    channel, fixture = load_sources(args.source_dir)
    output = generate(channel, fixture["section4_explicit_P104"])
    with args.out.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(output, indent=2) + "\n")
    print("PASS_P104_EARLY_CONTACT_GENERATION", len(output["witnesses"]), "witnesses")


if __name__ == "__main__":
    main()
