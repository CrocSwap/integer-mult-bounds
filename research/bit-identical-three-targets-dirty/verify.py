"""Exact finite corroboration of IDENTICAL-TARGET-LEMMA's new scalar step.

This checks every effective four-dimensional extra rank-one idempotent,
every rank-one element in each resulting scalar span, and every rank-three
projector decomposition in the fixed P chart. It is not a finite proof of
the arbitrary-register or unrestricted-rational theorem by itself.
Standard library only. Prepared with substantial OpenAI Codex assistance.
"""

import argparse
import hashlib
import itertools
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def outer(u, v, n):
    return tuple(v if u >> i & 1 else 0 for i in range(n))


def add(*matrices):
    return tuple(__import__("functools").reduce(int.__xor__, row, 0)
                 for row in zip(*matrices))


def mul(a, b):
    return tuple(__import__("functools").reduce(
        int.__xor__, (b[j] for j in range(len(b)) if row >> j & 1), 0)
        for row in a)


def rank(rows):
    basis = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p in basis:
                row ^= basis[p]
            else:
                basis[p] = row
                break
    return len(basis)


def apply(matrix, vector):
    return sum(((row & vector).bit_count() & 1) << i
               for i, row in enumerate(matrix))


def projector(matrix):
    return rank(matrix) == 1 and mul(matrix, matrix) == matrix


def span(matrices):
    result = {tuple(0 for _ in matrices[0])}
    for matrix in matrices:
        result |= {add(current, matrix) for current in tuple(result)}
    return sorted(result)


def block(matrix, coordinates):
    return tuple(sum(((matrix[i] >> j) & 1) << k
                     for k, j in enumerate(coordinates))
                 for i in coordinates)


def invariant_coordinate_set(matrix, coordinates):
    allowed = set(coordinates)
    return all(not (matrix[i] >> j & 1)
               for j in coordinates for i in range(len(matrix))
               if i not in allowed)


def check():
    n = 4
    zero = (0,) * n
    active = (1, 2, 4, 0)
    axes = [outer(1 << i, 1 << i, n) for i in range(3)]
    factors = [(u, v, outer(u, v, n)) for u in range(1, 16)
               for v in range(1, 16) if (u & v).bit_count() & 1]
    require(len(factors) == 120, "Wrong complete idempotent alphabet")
    require(len({m for _, _, m in factors}) == 120, "Duplicate factorization")
    require(all(projector(m) for _, _, m in factors), "Invalid alphabet")

    decompositions = []
    matrices = [m for _, _, m in factors]
    for ids in itertools.combinations(range(120), 3):
        triple = [matrices[i] for i in ids]
        if add(*triple) != active:
            continue
        for i, a in enumerate(triple):
            require(mul(active, a) == a and mul(a, active) == a,
                    "Rank-three decomposition escaped active support")
            for j, b in enumerate(triple):
                require(mul(a, b) == (a if i == j else zero),
                        "Rank-three decomposition is not orthogonal")
        decompositions.append(ids)
    require(len(decompositions) == 28, "Unexpected decomposition count")

    counts = {"active_image": 0, "dirty_common_kernel": 0,
              "active_line": 0, "active_hyperplane": 0}
    cases = []
    checked_members = 0
    partitioned_members = 0
    for u, v, extra in factors:
        pool = [m for m in span(axes + [extra]) if projector(m)]
        checked_members += len(pool)
        if not (u & 8):
            case = "active_image"
            for m in pool:
                require(m[3] == 0, "Image leaves active subspace")
                require(projector(block(m, [0, 1, 2])),
                        "Active restriction lost rank-one idempotence")
            witness = None
        elif not (v & 8):
            case = "dirty_common_kernel"
            for m in pool:
                require(apply(m, 8) == 0, "Dirty line is not common kernel")
                require(projector(block(m, [0, 1, 2])),
                        "Common-kernel quotient lost idempotence")
            witness = None
        else:
            require(((u & v) & 7).bit_count() % 2 == 0,
                    "Active overlap must have even parity")
            i = next(j for j in range(3) if not (u & v & (1 << j)))
            if not (v & (1 << i)):
                case = "active_line"
                coords = [i]
            else:
                case = "active_hyperplane"
                coords = [j for j in range(4) if j != i]
            rest = [j for j in range(4) if j not in coords]
            require(sorted([rank(block(active, coords)),
                            rank(block(active, rest))]) == [1, 2],
                    "Target split is not one plus two")
            for m in pool:
                require(invariant_coordinate_set(m, coords),
                        "Selected flag is not invariant for whole scalar span")
                left, right = block(m, coords), block(m, rest)
                require(mul(left, left) == left and mul(right, right) == right,
                        "Diagonal block idempotence failed")
                require(sorted([rank(left), rank(right)]) == [0, 1],
                        "Paid factor does not partition between blocks")
                partitioned_members += 1
            witness = coords
        counts[case] += 1
        cases.append({"u": u, "v": v, "case": case,
                      "rank_one_members": len(pool), "invariant_coordinates": witness})

    # This one forbidden nilpotent would destroy the parity inference:
    # J4 has all three active overlaps equal to one, but has trace zero.
    nilpotent = outer(15, 15, 4)
    require(rank(nilpotent) == 1 and mul(nilpotent, nilpotent) == zero,
            "Nilpotent mutation fixture is wrong")
    require(not projector(nilpotent), "Nilpotent mutation accepted")
    # A rank-two paid projector cannot use the one-call partition rule.
    rank_two = add(axes[0], axes[1])
    require(rank(rank_two) == 2 and not projector(rank_two),
            "Rank-two paid-call mutation accepted")

    receipt = {
        "status": "FINITE_CORROBORATION_OF_WRITTEN_SCALAR_REDUCTION",
        "idempotents": len(factors),
        "rank_three_projector_decompositions": len(decompositions),
        "effective_extra_projector_cases": counts,
        "rank_one_span_members_checked_with_multiplicity": checked_members,
        "call_partitions_checked_with_multiplicity": partitioned_members,
        "forbidden_controls_rejected": ["rank_one_nilpotent", "rank_two_projector"],
        "cases": cases,
    }
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    receipt["canonical_payload_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Regenerate the explicit finite receipt")
    args = parser.parse_args()
    result = check()
    output = Path(__file__).with_name("CERTIFICATE.json")
    if args.write:
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    else:
        require(json.loads(output.read_text(encoding="utf-8")) == result, "Finite receipt differs from exact recomputation")
    print("PASS_IDENTICAL_THREE_DIRTY_FINITE_CHECK " + json.dumps({k: v for k, v in result.items() if k != "cases"}, sort_keys=True))
