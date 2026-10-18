#!/usr/bin/env python3
"""Source-bound fresh-fiber audit. Standard library; no predecessor execution.

Prepared for Adam Gall with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import tarfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BIT = "research/e8-bit-p111-tuned/tune/EXPECTED.json"
ASSEMBLY = "research/community-frontier1094-audit/ASSEMBLY.json"
ARCHIVE = "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz"
ARCHIVE_PINS = "research/complex-t16-rare-pattern-exchanges/SOURCE.json"
SELECTED = "certificates/selected-result.json"


class Reject(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Reject(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def reject_control(name, function):
    try:
        function()
    except Reject:
        return name
    raise Reject("negative control accepted: " + name)


def check_digest(data, expected):
    require(digest(data) == expected, "source digest mismatch")


def authenticate():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    inputs = {}
    pins = {}
    for entry in manifest["files"]:
        if entry["usage"] == "input":
            data = (ROOT / entry["path"]).read_bytes()
            check_digest(data, entry["sha256"])
            require(git_blob(data) == entry["git_blob"], "source Git blob mismatch")
            inputs[entry["path"]] = data
            pins[entry["path"]] = entry["sha256"]
    require({BIT, ASSEMBLY, ARCHIVE, ARCHIVE_PINS, SELECTED} <= inputs.keys(),
            "missing selected source")
    # Authenticate the container before opening, and the member before parsing.
    with tarfile.open(ROOT / ARCHIVE, "r:gz") as archive:
        member = archive.extractfile("code/assemble.py")
        require(member is not None, "missing archived assembler")
        assembler = member.read()
    archive_pins = json.loads(inputs[ARCHIVE_PINS])
    check_digest(assembler, archive_pins["files"]["code/assemble.py"])
    constants = {}
    for node in ast.parse(assembler).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id == "BIT_BLOB":
                constants["blob"] = ast.literal_eval(node.value)
            if isinstance(target, ast.Tuple):
                names = [item.id for item in target.elts if isinstance(item, ast.Name)]
                if names == ["BIT_L", "BIT_T"]:
                    constants["stages"], constants["replicas"] = ast.literal_eval(node.value)
    require(constants == {"blob": git_blob(inputs[BIT]), "stages": 9, "replicas": 32},
            "selected assembler bit binding")
    selected = json.loads(inputs[SELECTED])
    require(selected["certificate"] == ASSEMBLY, "selected assembly path")
    check_digest(inputs[ASSEMBLY], selected["certificate_sha256"])
    assembly = json.loads(inputs[ASSEMBLY])
    require(assembly["bit_supplier"]["git_blob_sha1"] == constants["blob"],
            "assembly bit blob")
    check_digest(inputs[BIT], assembly["input_sha256"]["package:inputs/PR589-EXPECTED.json"])
    pins[ARCHIVE + ":code/assemble.py"] = digest(assembler)
    return json.loads(inputs[BIT]), assembly, pins


def selected_facts(bit, assembly):
    word, nine = bit["word"], bit["nine"]
    profile = {int(rank): count for rank, count in nine["profile"].items()}
    require(all(type(count) is int and count > 0 for count in profile.values()), "profile count")
    require(set(profile) == {1, 2, 3, 4, 5, 6, 7, 42}, "selected profile ranks")
    m, stages, replicas = 64, 9, 32
    pairs = (stages - 1) // 2
    live = 2 * pairs * word["v"] * replicas
    mass = sum(rank * count for rank, count in profile.items())
    deficit = replicas * (2 * pairs * word["v"] - stages * word["decoder_constant"])
    require(live == nine["bit"]["live"] == 28416, "selected live stock")
    require(nine["bit"]["physical"] == live + 9 == 28425, "selected physical stock")
    require(mass == nine["bit"]["rank_mass"] == m * live - deficit, "selected rank mass")
    require(deficit == assembly["bit_supplier"]["derived_deficit"], "selected deficit")
    require(max(profile) == nine["bit"]["maxchild"] == 42, "selected maximum child")
    require(m * m > 2 * max(profile) ** 2, "selected halving guard")
    require(len(assembly["bootstrap"]) == len(assembly["conservative_bootstrap"]) == 7,
            "selected bootstrap stages")
    edges = sum(profile.values())
    fallback = 32 * m * m
    # This is the existing complete charge, not a new endpoint calculation.
    coefficient = Fraction(fallback * edges, 10**16 * live)
    zero_moment = Fraction(mass, m * live) + coefficient / m
    require(zero_moment < 1, "orientation: unchanged bill at exponent zero")
    return {
        "m": m, "live_roles": live, "physical_roles": nine["bit"]["physical"],
        "profile": {str(rank): count for rank, count in sorted(profile.items())},
        "edges": edges, "rank_mass": mass, "deficit": deficit,
        "max_child": max(profile), "fallback_per_bad_edge": fallback,
        "bad_fraction_retained": "1/10000000000000000",
        "fallback_coefficient_before_rank_power": str(coefficient),
        "complete_moment_at_a_zero": str(zero_moment),
        "scope": "Existing selected bill only; no new moment root or stock coefficient.",
    }


def split_row(index, width, depth):
    digits = []
    for _ in range(depth):
        index, digit = divmod(index, width)
        digits.append(digit)
    return (index, *reversed(digits))


def join_row(row, width):
    value = row[0]
    for digit in row[1:]:
        value = value * width + digit
    return value


def route(row, width, level, direction=1):
    # Current permutation depends on ancestors only; future stock is untouched.
    ancestor = row[: level + 1]
    shift = 1 + sum((i + 1) * value for i, value in enumerate(ancestor))
    changed = (row[level + 1] + direction * shift) % width
    return row[: level + 1] + (changed,) + row[level + 2 :]


def check_route(rows, width, level, transform):
    laws = {}
    images = defaultdict(set)
    for row in rows:
        new = transform(row)
        require(len(new) == len(row), "route arity")
        require(new[: level + 1] == row[: level + 1], "route changed ancestor")
        require(new[level + 2 :] == row[level + 2 :], "route changed future stock")
        require(0 <= new[level + 1] < width, "route outside current field")
        key = row[: level + 2]
        if key in laws:
            require(laws[key] == new[level + 1], "route reads future stock")
        laws[key] = new[level + 1]
        images[row[: level + 1]].add(new[level + 1])
    require(all(len(image) == width for image in images.values()), "nonbijective current route")


def check_complete_fibers(rows, width, depth, level):
    require(len(rows) == len(set(rows)), "duplicate address")
    fibers = defaultdict(Counter)
    for row in rows:
        require(len(row) == depth + 1, "row arity")
        require(all(0 <= x < width for x in row[1:]), "row digit")
        fibers[row[: level + 1]][row[level + 1]] += 1
    wanted = Counter({digit: width ** (depth - level - 1) for digit in range(width)})
    require(all(fiber == wanted for fiber in fibers.values()), "incomplete current/future fiber")
    return len(fibers)


def address_cases():
    cases = cuts = fibers = rows_checked = 0
    for width in range(2, 7):
        for depth in range(1, 5):
            stock = width**depth
            for genuine in (stock, stock + 1, 2 * stock - 1):
                padded = ((genuine + stock - 1) // stock) * stock
                require(genuine <= padded < 2 * genuine, "one-padding volume")
                rows = [split_row(index, width, depth) for index in range(padded)]
                require(all(join_row(row, width) == i for i, row in enumerate(rows)), "radix round trip")
                # Separate Cartesian oracle, not another repeated-divmod implementation.
                cartesian = list(product(range(padded // stock), *([range(width)] * depth)))
                require(rows == cartesian, "Euclidean/Cartesian disagreement")
                for level in range(depth):
                    check_route(rows, width, level, lambda row: route(row, width, level))
                    moved = [route(row, width, level) for row in rows]
                    # Prefix-dependent stopping and child selection are allowed.
                    active = [row for row in moved if level == 0 or sum(row[: level + 1]) % 3 != 0]
                    fibers += check_complete_fibers(active, width, depth, level)
                    cuts += 1
                for row in rows:
                    moved = row
                    for level in range(depth):
                        moved = route(moved, width, level)
                    for level in reversed(range(depth)):
                        moved = route(moved, width, level, -1)
                    require(moved == row, "completed route restoration")
                rows_checked += len(rows)
                cases += 1
    return {"cases": cases, "cuts": cuts, "conditional_fibers": fibers,
            "padded_rows": rows_checked, "widths": [2, 6], "depths": [1, 4]}


def det2(matrix):
    a, b, c, d = matrix
    return a * d - b * c


def gl2_low_fibers():
    records = []
    for prime, power in ((3, 1), (3, 2), (5, 1), (5, 2)):
        modulus = prime**power
        fibers = Counter()
        route_images = set()
        count = 0
        for matrix in product(range(modulus), repeat=4):
            if det2(matrix) % prime == 0:
                continue
            a, b, c, d = matrix
            fibers[tuple(x % prime for x in matrix)] += 1
            # Right multiply by [[1,1],[0,1]], a genuine GL route.
            routed = (a, (a + b) % modulus, c, (c + d) % modulus)
            require(det2(routed) % prime != 0, "right route left GL")
            route_images.add(routed)
            count += 1
        low_count = (prime**2 - 1) * (prime**2 - prime)
        lifts = prime ** (4 * (power - 1))
        require(len(fibers) == low_count, "GL low class count")
        require(set(fibers.values()) == {lifts}, "GL low fibers unequal")
        require(count == low_count * lifts == len(route_images), "GL right route not bijective")
        records.append({"prime": prime, "power": power, "low_classes": low_count,
                        "lifts_per_low_class": lifts, "matrices": count})
    return records


def projective_predicate_cases():
    records = []
    for prime in (3, 5, 7):
        lines = [(1, slope) for slope in range(prime)] + [(0, 1)]
        fixed_bad = Counter({line: 0 for line in lines})
        selected_bad = total = 0
        for matrix in product(range(prime), repeat=4):
            if det2(matrix) % prime == 0:
                continue
            a, b = matrix[:2]
            kernels = [v for v in lines if (a * v[0] + b * v[1]) % prime == 0]
            require(len(kernels) == 1, "projective kernel is not unique")
            chosen = kernels[0]
            selected_bad += int((a * chosen[0] + b * chosen[1]) % prime == 0)
            for v in lines:
                fixed_bad[v] += int((a * v[0] + b * v[1]) % prime == 0)
            total += 1
        require(set(fixed_bad.values()) == {total // (prime + 1)}, "fixed-edge density")
        require(selected_bad == total, "adaptive witness not always bad")
        # All edge indicators summed at fixed cost still obey linearity exactly.
        require(sum(fixed_bad.values()) == total, "fixed-edge sum")
        records.append({"prime": prime, "matrices": total, "edges": prime + 1,
                        "fixed_bad_fraction": str(Fraction(1, prime + 1)),
                        "adaptive_bad_fraction": "1", "row_map": "identity"})
    return records


def semantic_controls(bit, assembly, predicates):
    controls = []
    rows = list(product(range(2), range(3), range(3)))
    controls.append(reject_control("current_route_reads_future", lambda: check_route(
        rows, 3, 0, lambda row: (row[0], (row[1] + row[2]) % 3, row[2]))))
    controls.append(reject_control("nonbijective_current_route", lambda: check_route(
        rows, 3, 0, lambda row: (row[0], 0, row[2]))))
    equal_rows = list(product(range(3), repeat=3))
    controls.append(reject_control("ancestor_future_alias", lambda: check_route(
        equal_rows, 3, 0, lambda row: (row[2], row[1], row[0]))))
    genuine = [split_row(index, 3, 2) for index in range(10)]
    controls.append(reject_control("pruned_padded_domain", lambda: check_complete_fibers(
        genuine, 3, 2, 1)))
    cell = [row for row in genuine if row[:2] == (1, 0)]
    require(cell == [(1, 0, 0)], "genuine-prefix witness")
    all_padded = [split_row(index, 3, 2) for index in range(18)]
    check_complete_fibers(all_padded, 3, 2, 1)
    selected_bad = Fraction(predicates[0]["adaptive_bad_fraction"])
    fixed_bound = Fraction(predicates[0]["fixed_bad_fraction"])
    controls.append(reject_control("adaptive_edge_at_fixed_edge_charge", lambda: require(
        selected_bad <= fixed_bound, "adaptive edge violates its claimed density")))
    tampered = deepcopy(bit)
    tampered["nine"]["profile"]["42"] -= 1
    controls.append(reject_control("omitted_selected_edge", lambda: selected_facts(tampered, assembly)))
    tampered = deepcopy(bit)
    tampered["nine"]["bit"]["physical"] -= 1
    controls.append(reject_control("live_stock_substituted_for_physical", lambda: selected_facts(tampered, assembly)))
    source_bytes = (ROOT / BIT).read_bytes()
    controls.append(reject_control("source_byte_corruption", lambda: check_digest(
        source_bytes + b" ", digest(source_bytes))))
    # The complete padded domain is sufficient; restoration is a distinct condition.
    controls.append(reject_control("unrestored_row_at_unpadding", lambda: require(
        {join_row(route(row, 3, 0), 3) for row in genuine} == set(range(10)),
        "genuine prefix not invariant at unfinished route")))
    return controls


def build_result():
    bit, assembly, source_pins = authenticate()
    facts = selected_facts(bit, assembly)
    predicates = projective_predicate_cases()
    return {
        "status": "PASS_SELECTED_COVER_FRESH_FIBERS",
        "selected": facts,
        "address_audit": address_cases(),
        "gl2_low_fibers": gl2_low_fibers(),
        "adaptive_minor_counterexamples": predicates,
        "genuine_prefix_counterexample": {
            "W": 3, "D": 2, "stock": 9, "genuine": 10, "padded": 18,
            "ancestor": [1, 0], "genuine_fresh_values": [0],
            "padded_bad_fraction": "1/3", "genuine_bad_fraction": "1",
        },
        "negative_controls_rejected": semantic_controls(bit, assembly, predicates),
        "source_sha256": source_pins,
        "limits": [
            "All-depth theorem uses the written prefix/complete-domain hypotheses.",
            "Selected all-size field dependency graph remains an inherited compiler obligation.",
            "No stock coefficient, improved root, new supplier or multiplication theorem.",
            "Finite matrices are GL2 controls, not enumeration of selected GL64.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path, help="create a new external receipt")
    args = parser.parse_args()
    result = build_result()
    if args.write_result is not None:
        destination = args.write_result.resolve()
        require(not destination.is_relative_to(PACKAGE), "regenerate to an external path")
        with destination.open("x", encoding="utf-8") as output:
            output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        require(canonical(expected) == canonical(result), "saved result differs from reconstruction")
    print(result["status"], "cases=" + str(result["address_audit"]["cases"]),
          "cuts=" + str(result["address_audit"]["cuts"]),
          "GL_rings=" + str(len(result["gl2_low_fibers"])),
          "controls=" + str(len(result["negative_controls_rejected"])))


if __name__ == "__main__":
    try:
        main()
    except (Reject, OSError, KeyError, ValueError, tarfile.TarError) as error:
        raise SystemExit("REJECT_SELECTED_COVER_FRESH_FIBERS: " + str(error)) from error
