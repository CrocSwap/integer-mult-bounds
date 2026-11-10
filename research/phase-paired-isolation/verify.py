"""Verify the new isolation theorem's finite corroboration.

Produced by Nick Petalas. Apache-2.0. No predecessor executable is used.
"""

from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import sys

from linear import check_block, identity, inverse, isolate, multiply, need
from oracle import (binary_block, binary_group, binary_matrix, binary_product,
                    similarity_capacity, ternary_block, ternary_group,
                    ternary_product)

HERE = Path(__file__).resolve().parent


def reject(action):
    try:
        action()
    except ValueError:
        return 1
    raise ValueError("Rejecting control accepted")


def exhaustive_binary():
    relatives = similarities = pairs = equivalences = 0
    histogram = {}
    for n in (1, 2, 3):
        group = binary_group(n)
        need(len(group) == (1, 6, 168)[n - 1], "Complete binary group")
        for rows, _ in group:
            found = isolate(identity(n), binary_matrix(rows), 2)
            optimum = similarity_capacity(rows, group)
            need(found["capacity"] == optimum, "Exhaustive similarity optimum")
            relatives += 1
            similarities += len(group)
            key = f"{n}:{found['readable']}:{optimum}"
            histogram[key] = histogram.get(key, 0) + 1
    group = binary_group(2)
    for left, _ in group:
        for right, _ in group:
            best = 0
            for output, _ in group:
                for input_basis, _ in group:
                    a = binary_product(binary_product(output, left), input_basis)
                    b = binary_product(binary_product(output, right), input_basis)
                    best = max(best, min(binary_block(a), binary_block(b)))
                    equivalences += 1
            answer = isolate(binary_matrix(left), binary_matrix(right), 2)
            need(answer["capacity"] == best, "Full two-sided endpoint optimum")
            pairs += 1
    return {"relative_maps": relatives, "similarities": similarities,
            "map_pairs": pairs, "two_sided_basis_pairs": equivalences,
            "readable_capacity_histogram": histogram}


def exhaustive_ternary():
    group = ternary_group()
    need(len(group) == 48, "Complete ternary group")
    comparisons = 0
    for rows, _ in group:
        best = 0
        for basis, back in group:
            changed = ternary_product(ternary_product(back, rows), basis)
            best = max(best, ternary_block(changed))
            comparisons += 1
        need(isolate(identity(2), rows, 3)["capacity"] == best,
             "Complete ternary similarity optimum")
    return {"relative_maps": len(group), "similarities": comparisons}


def jordan(blocks):
    n = sum(size for size, _ in blocks)
    out = [[0] * n for _ in range(n)]
    start = 0
    for size, eigenvalue in blocks:
        for i in range(size):
            out[start + i][start + i] = eigenvalue
            if i + 1 < size:
                out[start + i][start + i + 1] = 1
        start += size
    return tuple(tuple(row) for row in out)


def rational_profiles():
    count = 0
    for single in range(5):
        for double in range(3):
            for triple in range(3):
                for other in range(2):
                    blocks = ([(1, 1)] * single + [(2, 1)] * double
                              + [(3, 1)] * triple + [(1, 2)] * other)
                    n = sum(size for size, _ in blocks)
                    if not 1 <= n <= 8:
                        continue
                    change = tuple(tuple(Fraction(int(i == j) + int(j == i + 1))
                                         for j in range(n)) for i in range(n))
                    core = multiply(multiply(inverse(change, 0), jordan(blocks), 0),
                                    change, 0)
                    left = tuple(tuple(Fraction(int(i == j) + int(i == j + 1))
                                       for j in range(n)) for i in range(n))
                    right = multiply(left, core, 0)
                    answer = isolate(left, right)
                    need(answer["capacity"] == single, "All singleton blocks isolated")
                    need(answer["readable"] == single + double + triple,
                         "Longer chains remain readable but coupled")
                    count += 1
    return count


def phase_fixture(maps):
    # F5 contains all four fourth roots; 2 is its chosen square root of -1.
    branches = (1, 4, 2, 3)
    checks = positive = 0
    for offset in range(4):
        rotated = maps[offset:] + maps[:offset]
        first = isolate(rotated[0], rotated[1], 5)
        second = isolate(rotated[2], rotated[3], 5)
        size = min(first["capacity"], second["capacity"])
        for root, supplied in zip(branches, rotated):
            plus, minus = (1 + root * root) * 3 % 5, (1 - root * root) * 3 % 5
            output = tuple(tuple((plus * first["output"][i][j]
                                  + minus * second["output"][i][j]) % 5
                                 for j in range(3)) for i in range(3))
            input_basis = tuple(tuple((plus * first["input"][i][j]
                                       + minus * second["input"][i][j]) % 5
                                      for j in range(3)) for i in range(3))
            chosen = first if plus else second
            need(output == chosen["output"] and input_basis == chosen["input"],
                 "Both interpolated charts agree on opposite roots")
            for scalar in (1, root):
                scaled = tuple(tuple(scalar * x % 5 for x in row) for row in supplied)
                actual = multiply(multiply(output, scaled, 5), input_basis, 5)
                normalized = tuple(tuple(x * pow(scalar, -1, 5) % 5 for x in row)
                                   for row in actual)
                check_block(normalized, size, 5)
                need(inverse(output, 5) and inverse(input_basis, 5), "Unit charts")
                checks += 1
                positive += int(size > 0)
    return checks, positive


def phase_charts():
    negative = (identity(3), jordan([(1, 1), (2, 1)]),
                identity(3), jordan([(3, 1)]))
    capacities = [isolate(negative[j], negative[j + 1], 5)["capacity"] for j in (0, 2)]
    need(capacities == [1, 0], "Both phase pairs are necessary")
    left = ((1, 1, 0), (0, 1, 1), (0, 0, 1))
    positive = (identity(3), jordan([(1, 1), (2, 1)]), left,
                multiply(left, jordan([(1, 1), (1, 1), (1, 2)]), 5))
    checks = [phase_fixture(maps) for maps in (negative, positive)]
    total = sum(row[0] for row in checks)
    accepted = sum(row[1] for row in checks)
    need(accepted > 0, "Nonzero four-phase attainment exercised")
    return {"branches": total, "positive_capacity_branches": accepted}


def sharp_workspace():
    count = gaussian = 0
    for chains in range(1, 4):
        for workspace in range(4):
            core = jordan([(2, 1)] * chains + [(1, 1)] * workspace)
            answer = isolate(identity(len(core)), core)
            need(answer["capacity"] == workspace, "No net workspace gain")
            need(answer["readable"] == chains + workspace, "Exact readout gap")
            count += 1
            # The desired q^-1 Gaussian scalar changes sign between q=+/-1.
            # Independently restored identity workspace therefore has relative -1.
            relative = jordan([(2, 1)] * chains + [(1, -1)] * workspace)
            normalized = isolate(identity(len(relative)), relative)
            need(normalized["capacity"] == 0 and normalized["readable"] == chains,
                 "Identity workspace cannot isolate an extra q^-1 Gaussian")
            gaussian += 1
    # M(q)=I+((1+q)/2)E12, with literal inverse I-((1+q)/2)E12.
    for root in (Fraction(-1), Fraction(1)):
        coefficient = (1 + root) / 2
        forward = ((1, coefficient), (0, 1))
        backward = ((1, -coefficient), (0, 1))
        need(multiply(forward, backward, 0) == identity(2), "Exact inverse")
        need(forward[1] == (0, 1), "Completed second readout")
        scaled = tuple(tuple(x / root for x in row) for row in forward)
        scaled_inverse = tuple(tuple(root * x for x in row) for row in backward)
        need(multiply(scaled, scaled_inverse, 0) == identity(2), "Gaussian inverse")
        need(scaled[1] == (0, 1 / root), "Completed q^-1 Gaussian readout")
    need(isolate(((1, 1), (0, 1)), identity(2))["capacity"] == 0,
         "No common isolated readout")
    return {"identity_target_profiles": count, "gaussian_target_profiles": gaussian}


def controls():
    actions = [
        lambda: isolate(((0, 0), (0, 0)), identity(2)),
        lambda: isolate(identity(2), ((1, 0), (0, 0))),
        lambda: isolate(((1, 0, 0), (0, 1, 0)), identity(2)),
        lambda: isolate(identity(13), identity(13)),
        lambda: isolate(((1.0,),), ((1,),)),
        lambda: isolate(((1,),), ((1,),), 4),
        lambda: isolate(((Fraction(1, 3),),), ((1,),), 3),
        lambda: check_block(((1, 1), (0, 1)), 1, 0),
        lambda: check_block(((1, 0), (1, 1)), 1, 0),
        lambda: need(isolate(identity(2), ((1, 1), (0, 1)))["capacity"] == 1,
                     "Nullity alone undercounts dirty feedback"),
        lambda: need(isolate(identity(3), jordan([(1, 1), (2, 1)]))["capacity"]
                     <= isolate(identity(3), jordan([(3, 1)]))["capacity"],
                     "The other phase pair has a stricter obstruction"),
    ]
    return sum(reject(action) for action in actions)


def receipt():
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "linear.py", "oracle.py", "verify.py")
    hashes = {}
    for name in names:
        path = HERE / name
        need(path.is_file() and not path.is_symlink(), "Regular package file required")
        need(path.stat().st_size <= 1_000_000, "Package file outside capacity")
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    return hashes


def main():
    need(len(sys.argv) == 1, "No external search parameters supported")
    result = {"status": "PASS_PHASE_PAIRED_ISOLATION", "files": receipt(),
              "binary": exhaustive_binary(), "ternary": exhaustive_ternary(),
              "rational_profiles": rational_profiles(), "phase_branches": phase_charts(),
              "workspace_profiles": sharp_workspace(), "rejections": controls()}
    print(json.dumps(result, sort_keys=True, indent=2))
    print(result["status"])


if __name__ == "__main__":
    main()
