#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent finite premises for the bounded block-repair theorem.

OpenAI Codex assistance; source and mathematical scope are in INDEPENDENT.md.
This checker imports no primary or predecessor verification code.  It pulls
canonical query covectors backwards and constructs each route by swapping two
orthonormal coordinate charts, rather than using the predecessor's transvection
formula.  No native supplier, recursive cost or formal kernel is evaluated.
"""

from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import gzip
import hashlib
import json
import tarfile


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
WORD = "candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz"
PHASES = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
MEMBER_SHA256 = {
    WORD: "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    PHASES: "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def sources():
    require(hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() == ARCHIVE_SHA256,
            "archive SHA-256")
    decoded = {}
    with tarfile.open(ARCHIVE) as archive:
        for name, expected in MEMBER_SHA256.items():
            members = [m for m in archive.getmembers() if m.name == name]
            require(len(members) == 1 and members[0].isfile(),
                    "one regular archive member: " + name)
            raw = archive.extractfile(members[0]).read()
            require(hashlib.sha256(raw).hexdigest() == expected,
                    "member SHA-256: " + name)
            decoded[name] = json.loads(gzip.decompress(raw)
                                       if name.endswith(".gz") else raw)
    return decoded[WORD], decoded[PHASES]


def pull_covector(covector, events, backward):
    """Compute f M from elementary row operations by reverse adjoints.

    The canonical backward prefix replaces each generator by its inverse
    transpose, without reversing the chronological generator list.
    """
    result = list(covector)
    for event in reversed(events):
        kind = event[0]
        if kind == "scale":
            target, coefficient = event[1], Q(event[2], event[3])
            require(coefficient != 0, "invertible canonical scale")
            result[target] *= 1 / coefficient if backward else coefficient
        else:
            require(kind == "add", "supported canonical operation")
            target, source = event[1:3]
            coefficient = Q(event[3], event[4])
            require(target != source, "elementary off-diagonal addition")
            if backward:
                target, source, coefficient = source, target, -coefficient
            result[source] += coefficient * result[target]
    return result


def query_rows(word):
    prefix = word["precondition"] + word["compensation"] + word["A"]
    dimension = 1 + max(max(e[1:3]) if e[0] == "add" else e[1]
                        for e in prefix + word["cut"])
    # Only 667 of the 704 local registers are addressed by this prefix.  The
    # remaining zero covector entries do not affect either source restriction.
    require(224 <= dimension <= 704 and len(word["centers"]) == 8,
            "canonical prefix register and query dimensions")
    old, later = [], []
    for centre in word["centers"]:
        row = [Q(0)] * dimension
        row[centre] = Q(1)
        old.append(pull_covector(row, prefix, False)[:112])

        row = [Q(0)] * dimension
        for event in word["cut"]:
            require(event[0] == "add", "canonical cut addition")
            if event[2] == centre:
                row[event[1]] += Q(event[3], event[4])
        row = pull_covector(row, prefix, True)
        # The inherited first-call constant-source endpoint identifies initial
        # D_p and T_p differences.  This is an explicit source-model premise.
        later.append([row[p] + row[112 + p] for p in range(112)])
    return old, later


def pivot_columns(rows):
    work = [list(row) for row in rows]
    pivots = []
    for column in range(len(work[0])):
        next_row = next((i for i in range(len(pivots), len(work))
                         if work[i][column]), None)
        if next_row is None:
            continue
        row = len(pivots)
        work[row], work[next_row] = work[next_row], work[row]
        scale = work[row][column]
        work[row] = [v / scale for v in work[row]]
        for i in range(row + 1, len(work)):
            scale = work[i][column]
            work[i] = [a - scale * b for a, b in zip(work[i], work[row])]
        pivots.append(column)
        if len(pivots) == len(work):
            break
    return pivots


def pair_certificates(rows):
    columns = list(zip(*rows))
    require(all(any(column) for column in columns), "all columns nonzero")
    certificates = []
    for p, q in combinations(range(len(columns)), 2):
        witness = next(((i, j, columns[p][i] * columns[q][j]
                         - columns[q][i] * columns[p][j])
                        for i, j in combinations(range(len(rows)), 2)
                        if columns[p][i] * columns[q][j]
                        != columns[q][i] * columns[p][j]), None)
        require(witness is not None, "column pair is independent")
        i, j, determinant = witness
        certificates.append([p, q, i, j, str(determinant)])
    return certificates


def dot2(left, right):
    return (left & right).bit_count() % 2


def chart_action(record, vector):
    """Swap b_j with e_(9+j), fixing q and all remaining coordinates."""
    q = record["q"]
    basis = record["idle_children"][0]["orthogonal_axes"][:8]
    u, v = vector & 511, (vector >> 9) & 255
    result = q if dot2(q, u) else 0
    for j, axis in enumerate(basis):
        if (v >> j) & 1:
            result ^= axis
        if dot2(axis, u):
            result ^= 1 << (9 + j)
    return result ^ (vector & ~((1 << 17) - 1))


def route_certificates(word, phases):
    records = phases["recipes"]
    require(len(records) == 112 and phases["m"] == 73,
            "selected port count and cover dimension")
    require([r["q"] for r in records] == word["ports"],
            "canonical route/column ordering")
    routes = []
    for record in records:
        basis = record["idle_children"][0]["orthogonal_axes"][:8]
        chart = [record["q"]] + basis
        require(len(chart) == 9 and all(0 < x < 512 for x in chart),
                "local nine-dimensional chart")
        require(all(dot2(a, b) == int(i == j)
                    for i, a in enumerate(chart) for j, b in enumerate(chart)),
                "orthonormal chart")
        columns = tuple(chart_action(record, 1 << k) for k in range(73))
        require(all(chart_action(record, column) == 1 << k
                    for k, column in enumerate(columns)), "involutory route")
        require(all(dot2(a, b) == int(i == j)
                    for i, a in enumerate(columns)
                    for j, b in enumerate(columns)), "orthogonal route")
        require(all(columns[k] == 1 << k for k in range(17, 73)),
                "all spectator columns fixed")
        routes.append(columns)
    require(len(set(routes)) == 112, "all routes distinct")

    products = Counter()
    pair_witness = {}
    for p, record in enumerate(records):
        for q, columns in enumerate(routes):
            if p == q:
                continue
            product = tuple(chart_action(record, column) for column in columns)
            products[product] += 1
            pair_witness.setdefault(product, []).append([p, q])
    require(sum(products.values()) == 112 * 111, "all ordered pairs covered")
    require(max(products.values()) == 1, "relative-route multiplicity M=1")
    # The sorted representation binds every port pair and all 73 columns.
    certificate = sorted((pairs[0], list(product))
                         for product, pairs in pair_witness.items())
    return routes, products, certificate


def rejected(operation):
    try:
        operation()
    except ValueError:
        return True
    return False


def main():
    word, phases = sources()
    old, later = query_rows(word)
    predecessor_path = ROOT / "research/centre-owner-observation-floor/RESULT.json"
    predecessor = json.loads(predecessor_path.read_bytes())
    require([[str(x) for x in row] for row in old] == predecessor["R"],
            "reverse-adjoint old rows equal source receipt")
    require([[str(x) for x in row] for row in later] == predecessor["H"],
            "reverse-adjoint later rows equal source receipt")
    require(all(4 * b == a for r, s in zip(old, later) for a, b in zip(r, s)),
            "H=R/4 on the declared source slice")
    pivots = pivot_columns(old)
    require(len(pivots) == 8, "exact rational rank eight")
    pairs = pair_certificates(old)
    routes, products, product_certificate = route_certificates(word, phases)

    parallel = [list(row) for row in old]
    for row in parallel:
        row[1] = row[0]
    require(rejected(lambda: pair_certificates(parallel)),
            "parallel-column negative control")
    malformed = dict(phases["recipes"][0])
    malformed["q"] ^= 1
    malformed_phases = dict(phases)
    malformed_phases["recipes"] = [malformed] + phases["recipes"][1:]
    require(rejected(lambda: route_certificates(word, malformed_phases)),
            "changed-route source/order negative control")
    duplicate_phases = dict(phases)
    duplicate_phases["recipes"] = [phases["recipes"][0]] * 112
    require(rejected(lambda: route_certificates(word, duplicate_phases)),
            "collapsed-route negative control")

    receipt = {
        "status": "PASS_INDEPENDENT_BOUNDED_BLOCK_REPAIR",
        "proof_level": "finite exact premises plus written all-block implication",
        "archive_sha256": ARCHIVE_SHA256,
        "member_sha256": MEMBER_SHA256,
        "predecessor_result_sha256": hashlib.sha256(predecessor_path.read_bytes()).hexdigest(),
        "row_reconstruction": "canonical reverse adjoints; constant endpoint is inherited",
        "old_rank": 8,
        "source_dimension_per_owner": 112,
        "later_scale": "1/4",
        "pivot_columns": pivots,
        "column_pair_minor_count": len(pairs),
        "column_pair_minor_sha256": digest(pairs),
        "relative_route_ordered_pair_count": sum(products.values()),
        "relative_route_distinct_product_count": len(products),
        "relative_route_multiplicity_histogram": dict(Counter(products.values())),
        "relative_route_certificate_sha256": digest(product_certificate),
        "route_matrix_sha256": digest([list(route) for route in routes]),
        "maximum_relative_route_multiplicity": 1,
        "nonzero_joint_kernel_owner_count_lower_bound": 7,
        "every_block_size_covered": [1, 2, 3, 4, 5, 6],
        "sharp_extra_linear_coordinates_for_covered_block": "104*block_size",
        "controls_rejected": ["parallel_columns", "changed_route", "collapsed_routes"],
        "no_existence_claim_at_seven": True,
        "no_recursive_cost_or_kappa_claim": True,
        "native_and_formal_kernel_replay": False,
    }
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
