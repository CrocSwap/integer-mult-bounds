#!/usr/bin/env python3
"""Lost-free size bound from one fractional cover of the selected ports.

The checker prices the retained frames. It does not census frames.
"""

import hashlib
import json
import tarfile
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_LOST_FREE_COVER frames=112 bound=56 no_new_kappa"
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
BUDGETS = "research/plane-port-copy-budgets/RESULT.json"
MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
COVER_SHA = "67986250ea6d7ae5a71c20a0c1e0365cca142aaa7fbead20c47c959a535f2c2b"
WITNESS_SHA = "a98a88ebacc2b8fa3548387c1004cbfcc583ed5a3417b681c08eff68abe75dd6"


def fail(message):
    raise SystemExit("FAIL_LOST_FREE_COVER " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bits(value):
    return [(value // (2 ** index)) % 2 for index in range(9)]


def dot(left, right):
    return sum(x * y for x, y in zip(left, right)) % 2


def rank(rows):
    matrix = [list(row) for row in rows]
    pivot = 0
    for column in range(9):
        selected = next((index for index in range(pivot, len(matrix)) if matrix[index][column]), None)
        if selected is None:
            continue
        matrix[pivot], matrix[selected] = matrix[selected], matrix[pivot]
        for index in range(len(matrix)):
            if index != pivot and matrix[index][column]:
                matrix[index] = [(x + y) % 2 for x, y in zip(matrix[index], matrix[pivot])]
        pivot += 1
    return pivot


def labels():
    with tarfile.open(ROOT / ARCHIVE, "r:gz") as archive:
        member = archive.extractfile(MEMBER)
        require(member is not None, "the selected phase member is missing")
        raw = json.loads(member.read())
    recipes = raw["recipes"]
    require(len(recipes) == 112, "the selected port count moved")
    found = [None] * 112
    for record in recipes:
        port = record["port"]
        require(found[port] is None, "a selected port is repeated")
        found[port] = bits(record["q"])
    require(all(row is not None for row in found), "a selected port is missing")
    require(len({tuple(row) for row in found}) == 112, "two ports share a label")
    require(all(dot(row, row) == 1 for row in found), "a selected label is isotropic")
    require(rank(found) == 9, "the selected labels lost rank")
    return found


def cover(rows):
    data = json.loads((PACKAGE / "cover.json").read_text(encoding="utf-8"))
    frames = data["frames"]
    require(len(frames) == 112, "the frame count moved")
    coverage = [Fraction(0)] * 112
    total = Fraction(0)
    seen = set()
    for frame in frames:
        ports = frame["ports"]
        require(len(set(ports)) == 8, "a frame repeated a port")
        key = tuple(sorted(ports))
        require(key not in seen, "a frame was repeated")
        seen.add(key)
        chosen = [rows[port] for port in ports]
        for left_index, left in enumerate(chosen):
            for right_index, right in enumerate(chosen):
                require(dot(left, right) == int(left_index == right_index), "a frame left the identity Gram matrix")
        require(rank(chosen) == 8, "a frame lost rank")
        weight = Fraction(frame["weight"])
        require(weight > 0, "a frame weight is not positive")
        total += weight
        for port in ports:
            coverage[port] += weight
    require(all(value == 1 for value in coverage), "a port missed weight one")
    require(total == 14, "the total weight moved")
    return total


def witness(rows):
    data = json.loads((PACKAGE / "witness.json").read_text(encoding="utf-8"))
    planes = {int(port): bits(value) for port, value in data.items()}
    require(len(planes) == 32, "the witness plane count moved")
    for port, partner in planes.items():
        label = rows[port]
        require(dot(label, label) == dot(partner, partner) == 1 and dot(label, partner) == 0, "a witness plane is degenerate")
    for left, left_partner in planes.items():
        for right, right_partner in planes.items():
            if left != right and dot(rows[left], rows[right]) == 0:
                require(
                    dot(rows[left], right_partner) == dot(left_partner, rows[right]) == dot(left_partner, right_partner) == 0,
                    "a witness pair is not lost-free",
                )
    return len(planes)


def cost(size):
    return 72 + 2 * (112 - size)


def evaluate():
    require(sha256(ROOT / ARCHIVE) == "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6", "archive drift")
    require(sha256(ROOT / BUDGETS) == "253deb61a0c90674726fa77d143e140a8f46012b1bdddc37e6f127ba8a56d464", "budget drift")
    require(sha256(PACKAGE / "cover.json") == COVER_SHA, "cover drift")
    require(sha256(PACKAGE / "witness.json") == WITNESS_SHA, "witness drift")
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    budgets = json.loads((ROOT / BUDGETS).read_text(encoding="utf-8"))["complex"]["shrink"]
    require(budgets["rank2/incumbent_ceiling"]["charge"] == 164, "the rank-2 ceiling moved")
    require(budgets["rank8/incumbent_ceiling"]["charge"] == 160, "the rank-8 ceiling moved")
    rows = labels()
    total = cover(rows)
    require(witness(rows) == 32, "the witness size moved")
    require(4 * total == 56 and cost(56) == 184, "the size bound moved")
    require([cost(size) for size in range(32, 37)] == [232, 230, 228, 226, 224], "the size-32 tariff moved")
    require(cost(37) == 222 and cost(66) == 164 and cost(68) == 160, "the comparison sizes moved")
    require(all(cost(size) >= Fraction(1792, 9) for size in range(49)) and cost(49) < Fraction(1792, 9), "the saving threshold moved")
    require(52 + 2 * (112 - 56) == 164 and 48 + 2 * (112 - 56) == 160, "the tie block costs moved")
    return {
        "frames": 112,
        "total_weight": "14",
        "lost_free_bound": 56,
        "witness_planes": 32,
        "bound_cost": 184,
        "size_32_cost": 232,
        "below_224_at": 37,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
