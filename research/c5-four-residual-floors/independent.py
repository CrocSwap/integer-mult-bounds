#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent finite checks for four physical C5s and their floor certificate.

The program checks the supplied DATA-PHASES, MATCHING, and CERTIFICATE inputs.
It makes no proof claim beyond these finite fixtures.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from collections import deque
from fractions import Fraction
from pathlib import Path
from typing import Mapping, Sequence

EXPECTED_INPUT_SHA256 = {
    "DATA-PHASES.json.gz": "682092a4c656e0be4bdaa419783440772a80ae875cca4845aea2067927b560f6",
    "MATCHING.json": "4fd648f7b5178bff5441bf364d58234b7bc1a43b924bc6da03013c948f1473b1",
}
CORES = (
    (3, 10, 4, 6, 13),
    (3, 10, 12, 23, 13),
    (6, 13, 23, 54, 26),
    (14, 24, 47, 18, 55),
)
BLOCKS = (1, 2, 4, 8, 16, 5, 9, 10, 18, 20)
R = (2, 2, 2, 2, 2, 4, 4, 4, 4, 4)


class FixtureError(RuntimeError):
    """Raised when an input or finite fixture check fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FixtureError(message)


def dot9(left: int, right: int) -> int:
    """Standard F2 dot product for the nine-bit source labels."""
    require(0 <= left < (1 << 9), f"left label is outside F2^9: {left}")
    require(0 <= right < (1 << 9), f"right label is outside F2^9: {right}")
    parity = 0
    for bit in range(9):
        parity ^= ((left >> bit) & 1) & ((right >> bit) & 1)
    return parity


def gf2_rank(matrix: Sequence[Sequence[int]]) -> int:
    """Dense Gaussian elimination over F2, with rows stored as dense lists."""
    if not matrix:
        return 0
    width = len(matrix[0])
    rows = [list(row) for row in matrix]
    for row in rows:
        require(len(row) == width, "GF(2) matrix has ragged rows")
        require(all(value in (0, 1) for value in row), "GF(2) matrix has a non-bit entry")
    pivot_row = 0
    for column in range(width):
        candidate = next((row for row in range(pivot_row, len(rows)) if rows[row][column]), None)
        if candidate is None:
            continue
        rows[pivot_row], rows[candidate] = rows[candidate], rows[pivot_row]
        for row in range(len(rows)):
            if row != pivot_row and rows[row][column]:
                rows[row] = [a ^ b for a, b in zip(rows[row], rows[pivot_row])]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def pairing_matrix(source_vectors: Sequence[int], target_vectors: Sequence[int]) -> list[list[int]]:
    return [[dot9(left, right) for right in target_vectors] for left in source_vectors]


def table(core: Sequence[int], planes: Mapping[int, Sequence[int]]) -> list[int]:
    """1024 costs, ordered by source mask A outermost and target mask B next."""
    require(len(core) == 5, "table requires a five-plane core")
    require(len(set(core)) == 5, "table core repeats a plane")
    vectors = []
    for plane_id in core:
        require(plane_id in planes, f"missing plane {plane_id}")
        pair = tuple(planes[plane_id])
        require(len(pair) == 2, f"plane {plane_id} does not have two labels")
        vectors.append(pair)

    costs: list[int] = []
    for source_mask in range(32):
        source = [q for i, pair in enumerate(vectors) if source_mask & (1 << i) for q in pair]
        for target_mask in range(32):
            target = [q for i, pair in enumerate(vectors) if target_mask & (1 << i) for q in pair]
            costs.append(gf2_rank(pairing_matrix(source, target)))
    require(len(costs) == 1024, "table did not contain 1024 entries")
    return costs


def plane_block(left: Sequence[int], right: Sequence[int]) -> list[list[int]]:
    return pairing_matrix(left, right)


def validate_core(core: Sequence[int], planes: Mapping[int, Sequence[int]]) -> None:
    require(len(core) == 5, "physical core must contain five planes")
    require(len(set(core)) == 5, "physical core must contain five distinct planes")
    for plane_id in core:
        require(plane_id in planes, f"core refers to missing plane {plane_id}")
        pair = planes[plane_id]
        require(len(pair) == 2, f"plane {plane_id} must have two labels")
        require(plane_block(pair, pair) == [[1, 0], [0, 1]], f"plane {plane_id} does not have Gram matrix I2")

    for i in range(5):
        for j in range(i + 1, 5):
            adjacent = (j == (i + 1) % 5) or (i == (j + 1) % 5)
            block = plane_block(planes[core[i]], planes[core[j]])
            if adjacent:
                require(all(value == 0 for row in block for value in row),
                        f"adjacent planes {core[i]} and {core[j]} pair nonzero")
            else:
                require(any(value == 1 for row in block for value in row),
                        f"nonadjacent planes {core[i]} and {core[j]} pair to zero")


def outer_product(vector: Sequence[int]) -> list[list[int]]:
    """Ordinary integer outer product of a column vector with its transpose."""
    return [[left * right for right in vector] for left in vector]


def fit_terms() -> list[list[list[int]]]:
    terms = []
    for i in range(5):
        vector = [0] * 10
        vector[2 * i + 1] = 1
        vector[2 * ((i + 1) % 5)] = 1
        terms.append(outer_product(vector))
    return terms


def fit_matrix(terms: Sequence[Sequence[Sequence[int]]]) -> list[list[int]]:
    require(len(terms) == 5, "positive fit must have five outer-product terms")
    return [[sum(term[row][column] for term in terms) for column in range(10)] for row in range(10)]


def validate_strict_fit(matrix: Sequence[Sequence[int]]) -> None:
    require(len(matrix) == 10 and all(len(row) == 10 for row in matrix), "positive fit must be 10x10")
    require(all(value in (0, 1) for row in matrix for value in row), "fit has a non-bit coefficient")
    for coordinate in range(10):
        require(matrix[coordinate][coordinate] == 1, f"fit diagonal is zero at {coordinate}")
    for left_plane in range(5):
        for right_plane in range(5):
            if left_plane == right_plane:
                for left_axis in range(2):
                    for right_axis in range(2):
                        if left_axis != right_axis:
                            require(matrix[2 * left_plane + left_axis][2 * right_plane + right_axis] == 0,
                                    f"within-plane off-diagonal is nonzero at {left_plane}")
            else:
                adjacent = (right_plane == (left_plane + 1) % 5) or (left_plane == (right_plane + 1) % 5)
                if not adjacent:
                    for left_axis in range(2):
                        for right_axis in range(2):
                            require(matrix[2 * left_plane + left_axis][2 * right_plane + right_axis] == 0,
                                    "nonadjacent cross-plane strict-mask entry is nonzero")


def validate_fit_attainment(core: Sequence[int], costs: Sequence[int]) -> dict[str, object]:
    """Charge five adjacent full-support pairings separately, each at rank four."""
    term_ranks = []
    for i in range(5):
        edge_support = (1 << i) | (1 << ((i + 1) % 5))
        rank = costs[edge_support * 32 + edge_support]
        require(rank == 4, f"core {list(core)} adjacent term {i} has full pairing rank {rank}, expected 4")
        term_ranks.append(rank)
    total = sum(term_ranks)
    require(total == 20, f"core {list(core)} attainment charge is {total}, expected 20")
    return {"core": list(core), "term_full_pairing_ranks": term_ranks, "total_charge": total}


def expect_rejection(label: str, action) -> None:
    rejected = False
    try:
        action()
    except FixtureError:
        rejected = True
    require(rejected, f"negative fixture was not rejected: {label}")


def run_negative_fixtures(planes: Mapping[int, Sequence[int]], matrix: Sequence[Sequence[int]]) -> list[str]:
    wrong_order = list(CORES[0])
    wrong_order[1], wrong_order[2] = wrong_order[2], wrong_order[1]
    expect_rejection("incorrect plane order", lambda: validate_core(wrong_order, planes))

    broken_fit = [list(row) for row in matrix]
    broken_fit[0][0] ^= 1
    expect_rejection("one broken fit coefficient", lambda: validate_strict_fit(broken_fit))

    broken_planes = {plane_id: tuple(pair) for plane_id, pair in planes.items()}
    first = CORES[0][0]
    broken_pair = list(broken_planes[first])
    broken_pair[0] ^= 1 << 8
    broken_planes[first] = tuple(broken_pair)
    expect_rejection("damaged plane Gram coefficient", lambda: validate_core(CORES[0], broken_planes))
    return ["incorrect plane order", "one broken fit coefficient", "damaged plane Gram coefficient"]


def locate_input_pair(root: Path) -> tuple[Path, Path]:
    candidates = (
        (root / "research/c5-dyadic-decoder-gate/inputs/DATA-PHASES.json.gz",
         root / "research/c5-dyadic-decoder-gate/inputs/MATCHING.json"),
        (root / "inputs/DATA-PHASES.json.gz", root / "inputs/MATCHING.json"),
        (root / "DATA-PHASES.json.gz", root / "MATCHING.json"),
    )
    for data_path, matching_path in candidates:
        if data_path.is_file() and matching_path.is_file():
            return data_path, matching_path
    raise FixtureError("could not locate the permitted DATA-PHASES and MATCHING inputs beneath --root")


def locate_certificate(root: Path) -> Path:
    candidates = (
        root / "research/c5-four-residual-floors/CERTIFICATE.json",
        root / "CERTIFICATE.json",
    )
    for path in candidates:
        if path.is_file():
            return path
    raise FixtureError("could not locate research/c5-four-residual-floors/CERTIFICATE.json beneath --root")


def load_geometry(root: Path) -> tuple[dict[int, int], dict[int, tuple[int, int]], dict[str, str]]:
    data_path, matching_path = locate_input_pair(root)
    hashes = {
        data_path.name: hashlib.sha256(data_path.read_bytes()).hexdigest(),
        matching_path.name: hashlib.sha256(matching_path.read_bytes()).hexdigest(),
    }
    for name, expected in EXPECTED_INPUT_SHA256.items():
        require(hashes[name] == expected, f"pinned source SHA-256 mismatch for {name}")

    with gzip.open(data_path, "rt", encoding="utf-8") as stream:
        data = json.load(stream)
    with matching_path.open("rt", encoding="utf-8") as stream:
        matching_data = json.load(stream)

    recipes = data.get("recipes")
    require(isinstance(recipes, list) and len(recipes) == 112, "expected 112 source recipes")
    labels: dict[int, int] = {}
    for recipe in recipes:
        require(isinstance(recipe, dict), "source recipe must be an object")
        port, q = recipe.get("port"), recipe.get("q")
        require(isinstance(port, int) and 0 <= port < 112, f"invalid recipe port: {port!r}")
        require(port not in labels, f"duplicate recipe port: {port}")
        require(isinstance(q, int) and 0 <= q < (1 << 9), f"invalid F2^9 label at port {port}")
        labels[port] = q
    require(set(labels) == set(range(112)), "recipes do not cover ports 0 through 111")

    matching = matching_data.get("matching")
    require(isinstance(matching, list) and len(matching) == 56, "expected 56 matching planes")
    planes: dict[int, tuple[int, int]] = {}
    used_ports: set[int] = set()
    for plane_id, pair in enumerate(matching):
        require(isinstance(pair, list) and len(pair) == 2, f"matching plane {plane_id} must have two ports")
        left, right = pair
        require(isinstance(left, int) and isinstance(right, int), f"matching plane {plane_id} has noninteger port")
        require(left in labels and right in labels and left != right,
                f"matching plane {plane_id} refers to invalid ports")
        require(left not in used_ports and right not in used_ports, f"matching is not disjoint at plane {plane_id}")
        used_ports.update((left, right))
        planes[plane_id] = (labels[left], labels[right])
    require(len(used_ports) == 112, "matching does not cover all 112 ports")
    return labels, planes, hashes


def load_certificate(root: Path) -> dict[str, object]:
    path = locate_certificate(root)
    with path.open("rt", encoding="utf-8") as stream:
        certificate = json.load(stream)
    require(isinstance(certificate, dict) and certificate.get("schema_version") == 1,
            "unsupported certificate schema")
    require(tuple(certificate.get("blocks", ())) == BLOCKS, "certificate block order differs from fixed blocks")
    require(isinstance(certificate.get("cores"), list) and len(certificate["cores"]) == 4,
            "certificate must contain four cores")
    return certificate


def tariff_sha256(costs: Sequence[int]) -> str:
    """Digest the tariff's compact canonical JSON integer array."""
    payload = json.dumps(list(costs), separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def int_vector(value: object, length: int, label: str) -> tuple[int, ...]:
    require(isinstance(value, list) and len(value) == length, f"{label} must have length {length}")
    require(all(isinstance(item, int) for item in value), f"{label} entries must be integers")
    return tuple(value)


def weighted_sum(weights: Sequence[int], values: Sequence[int]) -> int:
    return sum(weight * value for weight, value in zip(weights, values))


def enumerate_excesses(weights: Sequence[int], cap: int) -> set[tuple[int, ...]]:
    """Enumerate e>=0, e_j=0 for zero weights, and w.e<=cap."""
    if cap < 0:
        return set()
    positive = [i for i, weight in enumerate(weights) if weight > 0]
    current = [0] * len(weights)
    result: set[tuple[int, ...]] = set()

    def visit(position: int, remaining: int) -> None:
        if position == len(positive):
            result.add(tuple(current))
            return
        index = positive[position]
        weight = weights[index]
        for amount in range(remaining // weight + 1):
            current[index] = amount
            visit(position + 1, remaining - weight * amount)
        current[index] = 0

    visit(0, cap)
    return result


def hit_vector(source_mask: int, target_mask: int) -> tuple[int, ...]:
    return tuple(int(bool(source_mask & block) and bool(target_mask & block)) for block in BLOCKS)


def trace_consistent(source_mask: int, target_mask: int, tight: Sequence[int]) -> bool:
    """Solve tight singleton/pair equations by affine graph propagation over Fractions."""
    allowed = source_mask & target_mask
    anchors: list[tuple[int, Fraction]] = [
        (i, Fraction(0)) for i in range(5) if not (allowed & (1 << i))
    ]
    edges: list[tuple[int, int, Fraction]] = []
    for block_index in tight:
        block = BLOCKS[block_index]
        vertices = [i for i in range(5) if block & (1 << i)]
        require(len(vertices) in (1, 2), f"tight block {block} is not singleton or pair")
        hit = Fraction(int(bool(source_mask & block) and bool(target_mask & block)))
        if len(vertices) == 1:
            anchors.append((vertices[0], hit))
        else:
            edges.append((vertices[0], vertices[1], hit))

    adjacency: list[list[tuple[int, Fraction]]] = [[] for _ in range(5)]
    for left, right, value in edges:
        adjacency[left].append((right, value))
        adjacency[right].append((left, value))

    affine: dict[int, tuple[int, Fraction]] = {}
    components: list[list[int]] = []
    for seed in range(5):
        if seed in affine:
            continue
        affine[seed] = (1, Fraction(0))
        component = []
        queue = deque([seed])
        while queue:
            node = queue.popleft()
            component.append(node)
            sign, offset = affine[node]
            for neighbor, edge_value in adjacency[node]:
                if neighbor not in affine:
                    affine[neighbor] = (-sign, edge_value - offset)
                    queue.append(neighbor)
        components.append(component)

    anchors_by_node: dict[int, list[Fraction]] = {}
    for node, value in anchors:
        anchors_by_node.setdefault(node, []).append(value)

    for component in components:
        component_set = set(component)
        forced_roots: list[Fraction] = []
        for node in component:
            sign, offset = affine[node]
            for anchor in anchors_by_node.get(node, []):
                forced_roots.append((anchor - offset) / sign)
        for left, right, value in edges:
            if left not in component_set:
                continue
            left_sign, left_offset = affine[left]
            right_sign, right_offset = affine[right]
            coefficient = left_sign + right_sign
            constant = left_offset + right_offset
            if coefficient:
                forced_roots.append((value - constant) / coefficient)
            elif constant != value:
                return False

        chosen_root = forced_roots[0] if forced_roots else Fraction(0)
        if any(root_value != chosen_root for root_value in forced_roots):
            return False
        for left, right, value in edges:
            if left in component_set:
                left_sign, left_offset = affine[left]
                right_sign, right_offset = affine[right]
                if left_sign * chosen_root + left_offset + right_sign * chosen_root + right_offset != value:
                    return False
        for node in component:
            sign, offset = affine[node]
            node_value = sign * chosen_root + offset
            if any(node_value != anchor for anchor in anchors_by_node.get(node, [])):
                return False
    return True


def run_trace_consistency_fixtures() -> list[str]:
    # The five pair blocks form an odd cycle. With every h=1, z_i=1/2 solves it.
    require(trace_consistent(31, 31, (5, 6, 7, 8, 9)),
            "odd-cycle trace fixture should admit its half-integer solution")
    # Adding the tight singleton z_0=1 conflicts with the forced z_i=1/2 values.
    require(not trace_consistent(31, 31, (0, 5, 6, 7, 8, 9)),
            "anchored odd-cycle trace fixture should be inconsistent")
    return ["odd cycle admits half-integer trace", "anchored odd cycle rejected"]


def verify_cover_and_cases(core_record: dict[str, object], core: Sequence[int], costs: Sequence[int]) -> dict[str, object]:
    scale = core_record.get("cover_scale")
    require(isinstance(scale, int) and scale > 0, f"core {list(core)} cover scale must be positive")
    weights = int_vector(core_record.get("cover_weights"), len(BLOCKS), "cover_weights")
    require(all(weight >= 0 for weight in weights), f"core {list(core)} cover weights must be nonnegative")
    require(len(costs) == 1024, f"core {list(core)} tariff must contain all 1024 costs")
    digest = tariff_sha256(costs)
    require(core_record.get("tariff_sha256") == digest,
            f"core {list(core)} tariff SHA-256 mismatch: computed {digest}")

    minimum_slack = None
    for source_mask in range(32):
        for target_mask in range(32):
            cost = costs[source_mask * 32 + target_mask]
            hits = hit_vector(source_mask, target_mask)
            slack = scale * cost - weighted_sum(weights, hits)
            require(slack >= 0,
                    f"core {list(core)} cover fails at A={source_mask}, B={target_mask}: slack {slack}")
            minimum_slack = slack if minimum_slack is None else min(minimum_slack, slack)

    cap = scale * 19 - weighted_sum(weights, R)
    expected_excesses = enumerate_excesses(weights, cap)
    case_rows = core_record.get("cases")
    require(isinstance(case_rows, list), f"core {list(core)} cases must be a list")
    actual_excesses = []
    parsed_cases = []
    for case_index, case in enumerate(case_rows):
        require(isinstance(case, dict), f"core {list(core)} case {case_index} must be an object")
        excess = int_vector(case.get("excess"), len(BLOCKS), "case excess")
        require(all(value >= 0 for value in excess), "case excess entries must be nonnegative")
        require(all(weight > 0 or excess[j] == 0 for j, weight in enumerate(weights)),
                "zero-weight block excess must be fixed to zero")
        require(weighted_sum(weights, excess) <= cap, "case excess is outside the enumerated budget")
        actual_excesses.append(excess)
        parsed_cases.append((case, excess))
    require(len(actual_excesses) == len(set(actual_excesses)), "certificate repeats an excess case")
    require(set(actual_excesses) == expected_excesses,
            f"core {list(core)} excess cases do not exactly cover enumeration "
            f"(certificate={len(actual_excesses)}, enumerated={len(expected_excesses)})")

    case_summaries = []
    for case_index, (case, excess) in enumerate(parsed_cases):
        target = tuple(R[j] + excess[j] for j in range(len(BLOCKS)))
        budget = scale * 19 - weighted_sum(weights, target)
        tight = [j for j, weight in enumerate(weights) if weight > 0 and excess[j] == 0]
        dual_scale = case.get("dual_scale")
        require(isinstance(dual_scale, int) and dual_scale > 0,
                f"core {list(core)} case {case_index} dual_scale must be positive")
        dual = int_vector(case.get("dual_weights"), len(BLOCKS), "dual_weights")
        require(all(dual[j] >= 0 for j, weight in enumerate(weights) if weight == 0),
                f"core {list(core)} case {case_index} dual is negative on a zero-weight block")
        require(weighted_sum(dual, target) >= 20 * dual_scale,
                f"core {list(core)} case {case_index} dual objective is below 20q")

        retained = 0
        for source_mask in range(32):
            for target_mask in range(32):
                cost = costs[source_mask * 32 + target_mask]
                hits = hit_vector(source_mask, target_mask)
                slack = scale * cost - weighted_sum(weights, hits)
                if slack > budget:
                    continue
                if not trace_consistent(source_mask, target_mask, tight):
                    continue
                retained += 1
                require(weighted_sum(dual, hits) <= dual_scale * cost,
                        f"core {list(core)} case {case_index} dual fails at "
                        f"A={source_mask}, B={target_mask}")
        declared = case.get("admissible_support_pairs")
        require(isinstance(declared, int) and declared == retained,
                f"core {list(core)} case {case_index} admits {retained}, certificate says {declared}")
        case_summaries.append({
            "excess": list(excess),
            "target": list(target),
            "budget": budget,
            "tight_blocks": [BLOCKS[j] for j in tight],
            "admissible_support_pairs": retained,
            "dual_objective": weighted_sum(dual, target),
            "dual_threshold": 20 * dual_scale,
        })

    return {
        "core": list(core),
        "cover_scale": scale,
        "cover_weights": list(weights),
        "tariff_sha256": digest,
        "tariff_entries_checked": len(costs),
        "cover_rows_checked": 1024,
        "minimum_cover_slack": minimum_slack,
        "enumerated_excess_cases": len(expected_excesses),
        "verified_cases": len(case_summaries),
        "admissible_support_pairs_total": sum(row["admissible_support_pairs"] for row in case_summaries),
        "cases": case_summaries,
    }


def build_report(root: Path) -> dict[str, object]:
    labels, planes, hashes = load_geometry(root)
    certificate = load_certificate(root)
    core_records = certificate["cores"]
    require(len(core_records) == len(CORES), "certificate core count differs from fixed geometry")

    core_reports = []
    tariffs = {}
    attainment = []
    certificate_reports = []
    total_cases = 0
    for position, core in enumerate(CORES):
        validate_core(core, planes)
        costs = table(core, planes)
        core_key = ",".join(str(plane) for plane in core)
        tariffs[core_key] = costs
        full_source_cost = costs[31 * 32 + 31]
        core_reports.append({
            "core": list(core),
            "plane_gram_I2": True,
            "adjacent_blocks_zero": True,
            "nonadjacent_blocks_nonzero": True,
            "table_entries": len(costs),
            "full_source_target_rank": full_source_cost,
        })

        attainment.append(validate_fit_attainment(core, costs))
        record = core_records[position]
        require(isinstance(record, dict), f"certificate core record {position} must be an object")
        require(tuple(record.get("core", ())) == core,
                f"certificate core order mismatch at position {position}")
        cert_report = verify_cover_and_cases(record, core, costs)
        total_cases += cert_report["verified_cases"]
        certificate_reports.append(cert_report)

    require(total_cases == 57, f"certificate has {total_cases} verified cases, expected 57")
    terms = fit_terms()
    positive = fit_matrix(terms)
    validate_strict_fit(positive)
    negatives = run_negative_fixtures(planes, positive)
    trace_fixtures = run_trace_consistency_fixtures()
    require(len(labels) == 112, "source label count changed unexpectedly")
    return {
        "scope": "finite geometry and certificate checks only; no proof claim beyond these inputs",
        "input_sha256": hashes,
        "source_label_count": len(labels),
        "source_label_dimension": 9,
        "cores": core_reports,
        "attainment": {
            "positive_fit_shape": [10, 10],
            "outer_product_terms": len(terms),
            "strict_mask_passed": True,
            "per_core": attainment,
            "total_charge_per_core": 20,
        },
        "certificate": {
            "blocks": list(BLOCKS),
            "r": list(R),
            "total_cases": total_cases,
            "cores": certificate_reports,
        },
        "negative_fixtures_rejected": negatives,
        "trace_consistency_fixtures": trace_fixtures,
        "tables": tariffs,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path,
                        help="repository root, inputs directory, or export directory")
    parser.add_argument("--output-json", nargs="?", const="-", metavar="PATH",
                        help="print machine-readable tables and summary; PATH writes JSON to a file")
    args = parser.parse_args(argv)

    try:
        report = build_report(args.root)
    except (FixtureError, OSError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    if args.output_json is not None:
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.output_json == "-":
            sys.stdout.write(rendered)
        else:
            Path(args.output_json).write_text(rendered, encoding="utf-8")
    else:
        ranks = ", ".join(
            f"{','.join(str(p) for p in core['core'])}:{core['full_source_target_rank']}"
            for core in report["cores"]
        )
        counts = ", ".join(
            f"{','.join(str(p) for p in core['core'])}:{core['verified_cases']}"
            for core in report["certificate"]["cores"]
        )
        print("PASS: four physical C5 geometries; 1024 costs per core")
        print(f"Source full-support ranks: {ranks}")
        print("Attainment: five adjacent full-support pairings of rank 4 = 20 per core")
        print(f"Certificate: 57 cases verified ({counts}); all tariff hashes match")
        print(f"Negative fixtures rejected: {len(report['negative_fixtures_rejected'])}")
        print("Trace consistency: half-integer odd cycle accepted; anchored inconsistency rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
