#!/usr/bin/env python3
"""Test whether fixed helper trajectories can feed an identity output row."""
from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
NATIVE = REPO / "research/p104-native-channel"
WITNESS = NATIVE / "inputs/LOWRANK-WITNESS.json"
FIXTURE = NATIVE / "inputs/P104-FIXTURE.json"
PROOF = NATIVE / "PROOF.md"
CHANNEL = NATIVE / "inputs/LOWRANK-RESULT.json"
WITNESS_SHA256 = "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e"
FIXTURE_SHA256 = "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4"
PROOF_SHA256 = "5d743145d389ffdfaffc66096fa7e32c7155b18f73d74755403151d0435bb94c"
CHANNEL_SHA256 = "7143ec7780f6f38a8c294df8009c3621936b281d05ae79946ce22f581b73d1b1"
Q = Fraction


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def roots() -> list[tuple[int, ...]]:
    lines: set[tuple[int, ...]] = set()
    for i, j in itertools.combinations(range(8), 2):
        for a, b in itertools.product((-2, 2), repeat=2):
            v = [0] * 8
            v[i], v[j] = a, b
            if next(x for x in v if x) < 0:
                v = [-x for x in v]
            lines.add(tuple(v))
    for signs in itertools.product((-1, 1), repeat=8):
        if signs.count(-1) % 2 == 0:
            v = signs if signs[0] > 0 else tuple(-x for x in signs)
            lines.add(tuple(v))
    need(len(lines) == 120, "wrong E8 root-line count")
    return sorted(lines)


def row_echelon(rows: list[dict[str, Q]], names: list[str]) -> dict[int, dict[int, Q]]:
    pivots: dict[int, dict[int, Q]] = {}
    columns = {name: index for index, name in enumerate(names)}
    for sparse in rows:
        row = {columns[name]: value for name, value in sparse.items() if value}
        while row:
            col = min(row)
            value = row[col]
            pivot = pivots.get(col)
            if pivot is None:
                inverse = 1 / value
                pivots[col] = {index: coefficient * inverse
                               for index, coefficient in row.items()}
                break
            for index, coefficient in pivot.items():
                updated = row.get(index, Q()) - value * coefficient
                if updated:
                    row[index] = updated
                else:
                    row.pop(index, None)
    return pivots


def row_in_span(pivots: dict[int, dict[int, Q]],
                sparse: dict[str, Q], names: list[str]) -> bool:
    columns = {name: index for index, name in enumerate(names)}
    row = {columns[name]: value for name, value in sparse.items() if value}
    while row:
        col = min(row)
        value = row[col]
        pivot = pivots.get(col)
        if pivot is None:
            return False
        for index, coefficient in pivot.items():
            updated = row.get(index, Q()) - value * coefficient
            if updated:
                row[index] = updated
            else:
                row.pop(index, None)
    return True


def nullspace_basis(pivots: dict[int, dict[int, Q]],
                    names: list[str]) -> list[dict[int, Q]]:
    free = [column for column in range(len(names)) if column not in pivots]
    basis = []
    for free_column in free:
        vector = {free_column: Q(1)}
        for pivot_column in sorted(pivots, reverse=True):
            value = -sum((coefficient * vector.get(column, Q())
                          for column, coefficient in pivots[pivot_column].items()
                          if column != pivot_column), Q())
            if value:
                vector[pivot_column] = value
        basis.append(vector)
    return basis


def common_carrier_direction(
        pivots_by_target: list[dict[int, dict[int, Q]]],
        augmented_pivots_by_target: list[dict[int, dict[int, Q]]],
        names: list[str]
        ) -> tuple[int, int, list[int], dict[str, Q]]:
    """Find the common extension space and targets it cannot supply alone."""
    constraints = []
    for pivots in augmented_pivots_by_target:
        for annihilator in nullspace_basis(pivots, names):
            constraints.append({names[column]: value
                                for column, value in annihilator.items()})
    intersection_pivots = row_echelon(constraints, names)
    directions = nullspace_basis(intersection_pivots, names)
    dimension = len(directions)
    if not directions:
        return 0, len(intersection_pivots), list(range(104)), {}

    for augmented_pivots in augmented_pivots_by_target:
        need(all(row_in_span(
            augmented_pivots,
            {names[column]: value for column, value in vector.items()},
            names) for vector in directions),
             "common-direction nullspace is not in every correction extension")

    # A target is blocked when the entire common extension space is already
    # in its fixed span. All other targets can be served by one generic vector
    # in the intersection, since a finite union of proper subspaces cannot
    # cover a vector space over Q.
    blocked = [target for target, pivots in enumerate(pivots_by_target)
               if all(row_in_span(
                   pivots,
                   {names[column]: value for column, value in vector.items()},
                   names) for vector in directions)]
    if len(blocked) == len(pivots_by_target):
        return dimension, len(intersection_pivots), blocked, {}

    # Construct a concrete direction outside every S_t by avoiding the
    # finitely many roots of the associated vector-valued polynomials.
    limit = 104 * max(1, dimension - 1) + 1
    for parameter in range(limit + 1):
        candidate: dict[str, Q] = {}
        power = 1
        for vector in directions:
            for column, value in vector.items():
                name = names[column]
                candidate[name] = candidate.get(name, Q()) + power * value
            power *= parameter
        if all(not row_in_span(pivots_by_target[target], candidate, names)
               for target in range(104) if target not in blocked):
            return dimension, len(intersection_pivots), blocked, {
                name: value for name, value in candidate.items() if value
            }
    if not blocked:
        raise ValueError("failed to construct a common carrier direction")


def coordinate_intersection_basis(
        pivots: dict[int, dict[int, Q]], names: list[str],
        selected_names: set[str]) -> list[dict[str, Q]]:
    """Return a basis for rowspan(pivots) intersect span(selected units)."""
    basis = [pivots[column] for column in sorted(pivots)]
    basis_names = [f"b{index}" for index in range(len(basis))]
    outside_columns = [column for column, name in enumerate(names)
                       if name not in selected_names]
    constraints = []
    for column in outside_columns:
        constraint = {basis_names[index]: row[column]
                      for index, row in enumerate(basis) if row.get(column)}
        if constraint:
            constraints.append(constraint)
    constraint_pivots = row_echelon(constraints, basis_names)
    coefficients = nullspace_basis(constraint_pivots, basis_names)
    intersection = []
    for combination in coefficients:
        row: dict[str, Q] = {}
        for index, coefficient in combination.items():
            for column, value in basis[index].items():
                name = names[column]
                if name in selected_names:
                    row[name] = row.get(name, Q()) + coefficient * value
                    if not row[name]:
                        row.pop(name)
        need(bool(row), "coordinate intersection produced a zero basis row")
        intersection.append(row)
    return intersection


def residual_mod_span(pivots: dict[int, dict[int, Q]],
                      sparse: dict[str, Q], names: list[str]) -> dict[int, Q]:
    columns = {name: index for index, name in enumerate(names)}
    row = {columns[name]: value for name, value in sparse.items() if value}
    residual = {}
    while row:
        col = min(row)
        value = row[col]
        pivot = pivots.get(col)
        if pivot is None:
            residual[col] = value
            row.pop(col)
            continue
        for index, coefficient in pivot.items():
            updated = row.get(index, Q()) - value * coefficient
            if updated:
                row[index] = updated
            else:
                row.pop(index, None)
    return residual


def proportional(left: dict[int, Q], right: dict[int, Q]) -> bool:
    if not left or not right:
        return False
    column = next(iter(right))
    if not left.get(column):
        return False
    scale = left[column] / right[column]
    return all(left.get(index, Q()) == scale * value
               for index, value in right.items()) and all(
                   right.get(index, Q()) == left[index] / scale
                   for index in left)


def in_span_of_two(rows: list[dict[str, Q]], target: dict[str, Q],
                   names: list[str]) -> bool:
    return row_in_span(row_echelon(rows, names), target, names)


def row_echelon_mod(rows: list[dict[int, int]], prime: int
                    ) -> dict[int, dict[int, int]]:
    pivots: dict[int, dict[int, int]] = {}
    for sparse in rows:
        row = {column: value % prime for column, value in sparse.items()
               if value % prime}
        while row:
            column = min(row)
            value = row[column]
            pivot = pivots.get(column)
            if pivot is None:
                inverse = pow(value, -1, prime)
                pivots[column] = {
                    index: coefficient * inverse % prime
                    for index, coefficient in row.items()
                }
                break
            for index, coefficient in pivot.items():
                updated = (row.get(index, 0) - value * coefficient) % prime
                if updated:
                    row[index] = updated
                else:
                    row.pop(index, None)
    return pivots


def row_in_span_mod(pivots: dict[int, dict[int, int]],
                    sparse: dict[int, int], prime: int) -> bool:
    row = {column: value % prime for column, value in sparse.items()
           if value % prime}
    while row:
        column = min(row)
        value = row[column]
        pivot = pivots.get(column)
        if pivot is None:
            return False
        for index, coefficient in pivot.items():
            updated = (row.get(index, 0) - value * coefficient) % prime
            if updated:
                row[index] = updated
            else:
                row.pop(index, None)
    return True


def reduce_mod_prime(row: dict[int, Q], prime: int) -> dict[int, int]:
    return {column: value.numerator % prime *
            pow(value.denominator, -1, prime) % prime
            for column, value in row.items() if value}


def row_coordinate_transform(
        rows: list[dict[str, Q]], names: list[str]
        ) -> tuple[dict[str, int], dict[int, dict[int, Q]],
                   dict[int, dict[int, Q]]]:
    """Build one reusable exact map from rows to their input coefficients."""
    columns = {name: index for index, name in enumerate(names)}
    pivots: dict[int, dict[int, Q]] = {}
    pivot_sources: dict[int, dict[int, Q]] = {}
    for source_index, sparse in enumerate(rows):
        row = {columns[name]: value for name, value in sparse.items() if value}
        source = {source_index: Q(1)}
        while row:
            pivot_column = min(row)
            value = row[pivot_column]
            pivot = pivots.get(pivot_column)
            if pivot is None:
                inverse = 1 / value
                pivots[pivot_column] = {
                    column: coefficient * inverse
                    for column, coefficient in row.items()
                }
                pivot_sources[pivot_column] = {
                    index: coefficient * inverse
                    for index, coefficient in source.items() if coefficient
                }
                break
            for column, coefficient in pivot.items():
                updated = row.get(column, Q()) - value * coefficient
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
            for index, coefficient in pivot_sources[pivot_column].items():
                updated = source.get(index, Q()) - value * coefficient
                if updated:
                    source[index] = updated
                else:
                    source.pop(index, None)
    return columns, pivots, pivot_sources


def representation_from_transform(
        transform: tuple[dict[str, int], dict[int, dict[int, Q]],
                         dict[int, dict[int, Q]]],
        target: dict[str, Q]) -> dict[int, Q]:
    columns, pivots, pivot_sources = transform
    row = {columns[name]: value for name, value in target.items() if value}
    representation: dict[int, Q] = {}
    while row:
        pivot_column = min(row)
        value = row[pivot_column]
        pivot = pivots.get(pivot_column)
        need(pivot is not None,
             "target row is outside the proposed source-row span")
        for column, coefficient in pivot.items():
            updated = row.get(column, Q()) - value * coefficient
            if updated:
                row[column] = updated
            else:
                row.pop(column, None)
        for index, coefficient in pivot_sources[pivot_column].items():
            updated = representation.get(index, Q()) + value * coefficient
            if updated:
                representation[index] = updated
            else:
                representation.pop(index, None)
    return representation


def row_representation(rows: list[dict[str, Q]], target: dict[str, Q],
                       names: list[str]) -> dict[int, Q]:
    """Express target using rows, returning coefficients by input row index."""
    return representation_from_transform(row_coordinate_transform(rows, names),
                                         target)
    return dimension, len(intersection_pivots), blocked, {}


def main() -> None:
    witness_raw, fixture_raw, proof_raw, channel_raw = (
        WITNESS.read_bytes(), FIXTURE.read_bytes(), PROOF.read_bytes(),
        CHANNEL.read_bytes())
    need(hashlib.sha256(witness_raw).hexdigest() == WITNESS_SHA256,
         "pinned low-rank witness changed")
    need(hashlib.sha256(fixture_raw).hexdigest() == FIXTURE_SHA256,
         "pinned P104 fixture changed")
    need(hashlib.sha256(proof_raw).hexdigest() == PROOF_SHA256 and
         b"y_t + sum_s <r_t,r_s> x_s/2" in proof_raw,
         "pinned native channel identity changed")
    need(hashlib.sha256(channel_raw).hexdigest() == CHANNEL_SHA256,
         "pinned native channel result changed")
    witness = json.loads(witness_raw)
    fixture = json.loads(fixture_raw)["section4_explicit_P104"]
    channel = json.loads(channel_raw)
    names = list(witness["initial_frames"])
    need(len(names) == 280 and len(set(names)) == 280,
         "wrong independent boundary column inventory")
    state: dict[str, dict[str, Q]] = {name: {name: Q(1)} for name in names}
    frames = {name: tuple(frame)
              for name, frame in witness["initial_frames"].items()}
    current_index = -1
    last_y_write: dict[int, int] = {}
    for index, event in enumerate(witness["program"]):
        if event[0] in ("add", "transport") and event[1].startswith("Y"):
            last_y_write[int(event[1][1:])] = index
    need(set(last_y_write) == set(range(104)), "missing target terminal writes")
    terminal_source_frames: dict[int, tuple[int, ...]] = {}
    available: dict[str, dict[tuple[tuple[str, str], ...], dict[str, Q]]] = {
        f"Y{i}": {} for i in range(104)
    }
    available_exact: dict[str, dict[tuple[tuple[str, str], ...], dict[str, Q]]] = {
        f"Y{i}": {} for i in range(104)
    }
    available_exact_meta: dict[str, dict[tuple[tuple[str, str], ...], tuple[str, int, tuple[int, ...]]]] = {
        f"Y{i}": {} for i in range(104)
    }
    target_available: dict[str, dict[tuple[tuple[str, str], ...], dict[str, Q]]] = {
        f"Y{i}": {} for i in range(104)
    }
    reads_from_y: list[tuple[int, str, str]] = []

    span_cache: dict[tuple[int, ...], tuple[int, ...]] = {}

    def frame_span(frame: tuple[int, ...]) -> tuple[int, ...]:
        if frame not in span_cache:
            generated = {0}
            for vector in frame:
                generated |= {value ^ vector for value in tuple(generated)}
            span_cache[frame] = tuple(sorted(generated))
        return span_cache[frame]

    def signature(row: dict[str, Q]) -> tuple[tuple[str, str], ...]:
        return tuple(sorted((name, str(value))
                            for name, value in row.items()))

    def capture_available_rows() -> None:
        by_span: dict[tuple[int, ...], list[str]] = defaultdict(list)
        for target in available:
            if target in frames:
                by_span[frame_span(frames[target])].append(target)
        for source, row in state.items():
            if source.startswith("Y"):
                continue
            matching = by_span.get(frame_span(frames[source]), ())
            if not matching:
                continue
            for target in matching:
                row_signature = signature(row)
                available[target].setdefault(row_signature, dict(row))
                if frames[source] == frames[target]:
                    available_exact[target].setdefault(row_signature, dict(row))
                    available_exact_meta[target].setdefault(
                        row_signature, (source, current_index, tuple(frames[source])))

    def capture_target_source(source: str) -> None:
        if source not in state or source not in frames:
            return
        source_span = frame_span(frames[source])
        source_row = state[source]
        for target in target_available:
            if target != source and target in frames and \
                    frame_span(frames[target]) == source_span:
                target_available[target].setdefault(
                    signature(source_row), dict(source_row))

    def capture_targets_matching(source: str) -> None:
        if source not in frames:
            return
        source_span = frame_span(frames[source])
        matching = [target for target in target_available
                    if target in frames and frame_span(frames[target]) == source_span]
        for target in matching:
            if target not in state:
                continue
            for other in matching:
                if other != target:
                    target_available[target].setdefault(
                        signature(state[other]), dict(state[other]))

    capture_available_rows()
    for target in target_available:
        capture_target_source(target)

    for index, event in enumerate(witness["program"]):
        current_index = index
        op = event[0]
        if op == "transport":
            _, reg, _, new, _ = event
            if reg.startswith("Y") and index == last_y_write[int(reg[1:])]:
                target = int(reg[1:])
                terminal_source_frames[target] = tuple(frames[f"X{target}"])
            frames[reg] = tuple(new)
            if reg.startswith("Y"):
                capture_available_rows()
                capture_targets_matching(reg)
            else:
                capture_available_rows()
            continue
        if op == "zero":
            _, reg, frame = event
            state[reg] = {}
            frames[reg] = tuple(frame)
            if reg.startswith("Y"):
                capture_available_rows()
                capture_targets_matching(reg)
            else:
                capture_available_rows()
        elif op == "erase":
            _, reg, frame = event
            state.pop(reg)
            frames.pop(reg)
            if reg.startswith("Y"):
                capture_available_rows()
                capture_targets_matching(reg)
            else:
                capture_available_rows()
        elif op == "copy":
            _, reg, src, frame = event
            if src.startswith("Y"):
                reads_from_y.append((index, reg, src))
            state[reg] = dict(state[src])
            frames[reg] = tuple(frame)
            if reg.startswith("Y"):
                capture_available_rows()
                capture_targets_matching(reg)
            else:
                capture_available_rows()
        else:
            need(op == "add", "unknown source witness operation")
            _, dst, src, coefficient, _ = event
            coefficient = Q(coefficient)
            if src.startswith("Y"):
                reads_from_y.append((index, dst, src))
            if dst.startswith("Y"):
                need(src.startswith(("Q", "D")),
                     "literal target delivery source is outside Q/D")
            for name, value in state[src].items():
                state[dst][name] = state[dst].get(name, Q()) + coefficient*value
                if not state[dst][name]:
                    state[dst].pop(name)
            if dst.startswith("Y"):
                capture_target_source(dst)
            else:
                capture_available_rows()

    need(not reads_from_y, "a target row feeds another register")
    need(set(state) == set(names), "private state is not closed at the endpoint")

    all_roots = roots()
    removed = {tuple(v) for v in fixture["F0"] + fixture["C"]}
    ports = [root for root in all_roots if root not in removed]
    need(len(ports) == 104, "wrong P104 port order/size")
    gram = []
    for x in ports:
        row = []
        for y in ports:
            product = sum(a*b for a, b in zip(x, y))
            need(product % 4 == 0, "root pairing is not integral")
            row.append(product // 4)
        gram.append(row)
    for name in names:
        expected = {name: Q(1)}
        if name.startswith("Y"):
            t = int(name[1:])
            expected.update({f"X{s}": Q(value, 2)
                             for s, value in enumerate(gram[t]) if value})
        need(state[name] == expected,
             f"baseline row replay differs at {name}")

    rank_hist = Counter()
    expanded_rank_hist = Counter()
    row_count_hist = Counter()
    target_failures = 0
    correction_in_helper_span = 0
    correction_in_pooled_span = 0
    correction_outside_pooled_span = 0
    correction_in_helper_plus_target_unit = 0
    correction_in_exact_helper_plus_target_unit = 0
    correction_rows = []
    correction_representations = []
    exact_correction_representations = []
    exact_snapshot_rows_by_target = []
    exact_snapshot_meta_by_target = []
    representation_support_hist = Counter()
    exact_representation_support_hist = Counter()
    pooled_pivots_by_target = []
    augmented_pivots_by_target = []
    x_coordinate_names = {name for name in names if name.startswith("X")}
    x_coordinate_units = [{name: Q(1)} for name in sorted(x_coordinate_names)]
    x_intersection_rows_by_target = []
    x_intersection_dimension_hist = Counter()
    projected_span_rows_by_target = []
    projected_span_rank_hist = Counter()
    for target in range(104):
        reg = f"Y{target}"
        rows = list(available[reg].values())
        exact_rows = list(available_exact[reg].values())
        exact_meta = list(available_exact_meta[reg].values())
        carrier_rows = list(target_available[reg].values())
        unit = {f"X{target}": Q(1)}
        correction = {
            f"X{source}": value for source in range(104)
            if (value := Q(int(source == target)) - Q(gram[target][source], 2))
        }
        correction_rows.append(correction)
        representation = row_representation(rows + [unit], correction, names)
        need(len(rows) in representation and representation[len(rows)],
             f"C_{target} does not need the missing X_t direction")
        correction_representations.append(representation)
        representation_support_hist[len(representation)] += 1
        exact_representation = row_representation(
            exact_rows + [unit], correction, names)
        need(len(exact_rows) in exact_representation and
             exact_representation[len(exact_rows)],
             f"C_{target} does not have an exact-chart X_t representation")
        exact_correction_representations.append(exact_representation)
        exact_snapshot_rows_by_target.append(exact_rows)
        exact_snapshot_meta_by_target.append(exact_meta)
        exact_representation_support_hist[len(exact_representation)] += 1
        base_pivots = row_echelon(rows, names)
        base_rank = len(base_pivots)
        expanded_pivots = row_echelon(rows + carrier_rows, names)
        expanded_rank = len(expanded_pivots)
        pooled_pivots_by_target.append(expanded_pivots)
        x_intersection_rows = coordinate_intersection_basis(
            expanded_pivots, names, x_coordinate_names)
        union_rank = len(row_echelon(
            rows + carrier_rows + x_coordinate_units, names))
        expected_x_intersection_dimension = expanded_rank + 104 - union_rank
        need(len(x_intersection_rows) == expected_x_intersection_dimension,
             f"X-coordinate intersection dimension mismatch at {reg}")
        need(all(set(row) <= x_coordinate_names and row_in_span(
            expanded_pivots, row, names) for row in x_intersection_rows),
             f"invalid X-coordinate intersection basis at {reg}")
        x_intersection_rows_by_target.append(x_intersection_rows)
        x_intersection_dimension_hist[len(x_intersection_rows)] += 1
        projected_rows = [
            {names[column]: value for column, value in row.items()
             if names[column] in x_coordinate_names}
            for row in expanded_pivots.values()
        ]
        projected_pivots = row_echelon(projected_rows, names)
        projected_span_rows_by_target.append(
            [{names[column]: value for column, value in row.items()}
             for row in projected_pivots.values()])
        projected_span_rank_hist[len(projected_pivots)] += 1
        augmented_pivots_by_target.append(
            row_echelon(rows + carrier_rows + [correction], names))
        rank_hist[base_rank] += 1
        row_count_hist[len(rows)] += 1
        expanded_rank_hist[expanded_rank] += 1
        need(not row_in_span(base_pivots, unit, names),
             f"{reg} identity row lies in the existing delivery-source span")
        need(not row_in_span(expanded_pivots, unit, names),
             f"{reg} identity row lies in the fixed target-carrier source span")
        correction_in_helper_span += int(row_in_span(base_pivots, correction, names))
        correction_in_helper_plus_target_unit += int(row_in_span(
            row_echelon(rows + [unit], names), correction, names))
        correction_in_exact_helper_plus_target_unit += int(row_in_span(
            row_echelon(exact_rows + [unit], names), correction, names))
        in_pooled_span = row_in_span(expanded_pivots, correction, names)
        correction_in_pooled_span += int(in_pooled_span)
        correction_outside_pooled_span += int(not in_pooled_span)
        target_failures += 1

    common_direction_dimension, common_constraint_rank, \
        common_blocking_targets, common_direction = common_carrier_direction(
            pooled_pivots_by_target, augmented_pivots_by_target, names)
    need(common_direction_dimension == 72 and common_constraint_rank == 208 and
         common_blocking_targets == list(range(104)) and not common_direction,
         f"one-shared-direction obstruction changed: "
         f"dim={common_direction_dimension}, rank={common_constraint_rank}, "
         f"blocked={common_blocking_targets}, support={len(common_direction)}")

    need(target_failures == 104,
         "some target unit source row entered its fixed-trajectory span")

    x_intersection_pivots_by_target = [
        row_echelon(rows, names) for rows in x_intersection_rows_by_target
    ]
    x_intersection_correction_outside = sum(
        not row_in_span(x_intersection_pivots_by_target[target],
                        correction_rows[target], names)
        for target in range(104))
    x_intersection_augmented_pivots_by_target = [
        row_echelon(x_intersection_rows_by_target[target] +
                    [correction_rows[target]], names)
        for target in range(104)
    ]
    x_common_direction_dimension, x_common_constraint_rank, \
        x_common_blocking_targets, x_common_direction = common_carrier_direction(
            x_intersection_pivots_by_target,
            x_intersection_augmented_pivots_by_target, names)
    need(x_intersection_correction_outside == 104,
         "an actual correction entered S_t intersect X")

    # Project any putative shared H to the X coordinates. Since every C_t is
    # X-supported, C_t must lie in pi_X(S_t) + pi_X(H). A subset of correction
    # cosets independent modulo the sum of their projected fixed spans gives
    # an unconditional lower bound on dim(H).
    projected_order = sorted(
        range(104),
        key=lambda target: (len(projected_span_rows_by_target[target]), target))
    projected_lower_bound_targets: list[int] = []
    projected_lower_bound_span_rank = 0
    projected_lower_bound_joint_rank = 0
    for candidate in projected_order:
        trial_targets = projected_lower_bound_targets + [candidate]
        fixed_rows = [row for target in trial_targets
                      for row in projected_span_rows_by_target[target]]
        fixed_rank = len(row_echelon(fixed_rows, names))
        joint_rows = fixed_rows + [correction_rows[target]
                                   for target in trial_targets]
        joint_rank = len(row_echelon(joint_rows, names))
        if joint_rank - fixed_rank == len(trial_targets):
            projected_lower_bound_targets.append(candidate)
            projected_lower_bound_span_rank = fixed_rank
            projected_lower_bound_joint_rank = joint_rank
    projected_basis_H_rows = [
        correction_rows[target] for target in projected_lower_bound_targets
    ]
    projected_basis_H_rank = len(row_echelon(projected_basis_H_rows, names))
    projected_basis_H_coverage = 0
    full_basis_H_coverage = 0
    full_basis_H_uncovered = []
    for target in range(104):
        projected_augmented_pivots = row_echelon(
            projected_span_rows_by_target[target] + projected_basis_H_rows,
            names)
        projected_covered = row_in_span(
            projected_augmented_pivots, correction_rows[target], names)
        projected_basis_H_coverage += int(projected_covered)

        full_basis_rows = [
            {names[column]: value for column, value in row.items()}
            for row in pooled_pivots_by_target[target].values()
        ]
        full_augmented_pivots = row_echelon(
            full_basis_rows + projected_basis_H_rows, names)
        full_covered = row_in_span(
            full_augmented_pivots, correction_rows[target], names)
        full_basis_H_coverage += int(full_covered)
        if not full_covered:
            full_basis_H_uncovered.append(target)
    initial_full_basis_H_coverage = full_basis_H_coverage

    correction_basis_rank = len(row_echelon(correction_rows, names))
    need(correction_basis_rank == 104,
         "the actual correction rows are not a basis of X")
    correction_coordinate_transform = row_coordinate_transform(
        correction_rows, names)
    x_intersection_correction_coordinates = [
        [representation_from_transform(correction_coordinate_transform, row)
         for row in target_rows]
        for target_rows in x_intersection_rows_by_target
    ]

    def correction_basis_omission_coverage(omissions: set[int]) -> set[int]:
        omission_names = [f"C{index}" for index in sorted(omissions)]
        covered = set(range(104)) - omissions
        for target in omissions:
            projected_rows = [
                {f"C{index}": value for index, value in row.items()
                 if index in omissions}
                for row in x_intersection_correction_coordinates[target]
            ]
            pivots = row_echelon(projected_rows, omission_names)
            if row_in_span(pivots, {f"C{target}": Q(1)},
                           omission_names):
                covered.add(target)
        return covered

    optimized_omissions = set(range(104)) - set(projected_lower_bound_targets)
    initial_coordinate_coverage = correction_basis_omission_coverage(
        optimized_omissions)
    need(len(initial_coordinate_coverage) == initial_full_basis_H_coverage,
         "correction-coordinate coverage differs from full-span coverage")
    while True:
        current_coverage = correction_basis_omission_coverage(
            optimized_omissions)
        best_swap = None
        best_swap_coverage = current_coverage
        selected_indices = set(range(104)) - optimized_omissions
        for removed in sorted(optimized_omissions):
            for added in sorted(selected_indices):
                trial = (optimized_omissions - {removed}) | {added}
                trial_coverage = correction_basis_omission_coverage(trial)
                if len(trial_coverage) > len(best_swap_coverage):
                    best_swap = trial
                    best_swap_coverage = trial_coverage
        if best_swap is None:
            break
        optimized_omissions = best_swap
    optimized_correction_basis_indices = sorted(
        set(range(104)) - optimized_omissions)
    optimized_correction_basis_rows = [
        correction_rows[index] for index in optimized_correction_basis_indices
    ]
    optimized_coverage_targets = sorted(
        correction_basis_omission_coverage(optimized_omissions))
    full_basis_H_coverage = len(optimized_coverage_targets)
    full_basis_H_uncovered = sorted(
        set(range(104)) - set(optimized_coverage_targets))
    full_basis_H_rank = len(row_echelon(
        optimized_correction_basis_rows, names))
    best_constructive_omissions = None
    best_constructive_coverage = set()
    for omission_count in range(len(optimized_omissions), -1, -1):
        for candidate_omissions_tuple in itertools.combinations(
                sorted(optimized_omissions), omission_count):
            candidate_omissions = set(candidate_omissions_tuple)
            candidate_coverage = correction_basis_omission_coverage(
                candidate_omissions)
            if len(candidate_coverage) == 104:
                best_constructive_omissions = candidate_omissions
                best_constructive_coverage = candidate_coverage
                break
        if best_constructive_omissions is not None:
            break
    need(best_constructive_omissions is not None,
         "could not augment the correction-row basis to cover all targets")
    constructive_H_indices = sorted(
        set(range(104)) - best_constructive_omissions)
    constructive_H_rows = [correction_rows[index]
                           for index in constructive_H_indices]
    constructive_H_rank = len(row_echelon(constructive_H_rows, names))
    need(constructive_H_rank == len(constructive_H_indices),
         "constructed correction-row shared space is not independent")
    direct_constructive_H_coverage = 0
    for target in range(104):
        full_basis_rows = [
            {names[column]: value for column, value in row.items()}
            for row in pooled_pivots_by_target[target].values()
        ]
        full_augmented_pivots = row_echelon(
            full_basis_rows + constructive_H_rows, names)
        direct_constructive_H_coverage += int(row_in_span(
            full_augmented_pivots, correction_rows[target], names))
    need(direct_constructive_H_coverage == 104,
         "constructed shared space misses an exact pooled-span correction")

    # Search every 97-row correction-basis space one deletion or one exchange
    # away from the 98-row witness. This is a local construction search only;
    # it is not a minimum-dimension proof for arbitrary 97-dimensional H.
    omitted_from_constructive = set(range(104)) - set(constructive_H_indices)
    selected_from_constructive = set(constructive_H_indices)
    nearby_97_candidates = []
    for removed in sorted(selected_from_constructive):
        candidate_omissions = omitted_from_constructive | {removed}
        nearby_97_candidates.append((
            candidate_omissions,
            correction_basis_omission_coverage(candidate_omissions)))
    for removed in sorted(selected_from_constructive):
        for added in sorted(omitted_from_constructive):
            candidate_omissions = (omitted_from_constructive | {removed}) - {added}
            nearby_97_candidates.append((
                candidate_omissions,
                correction_basis_omission_coverage(candidate_omissions)))
    nearby_97_best_coverage = max(
        len(covered) for _, covered in nearby_97_candidates)
    nearby_97_witness_count = sum(
        len(covered) == 104 for _, covered in nearby_97_candidates)
    nearby_97_witness_omissions = next(
        omissions for omissions, covered in nearby_97_candidates
        if len(covered) == 104)
    nearby_97_witness_indices = sorted(
        set(range(104)) - nearby_97_witness_omissions)
    nearby_97_witness_rows = [correction_rows[index]
                              for index in nearby_97_witness_indices]
    need(len(row_echelon(nearby_97_witness_rows, names)) == 97,
         "nearby 97-row correction witness is not independent")
    nearby_97_direct_coverage = 0
    for target in range(104):
        full_basis_rows = [
            {names[column]: value for column, value in row.items()}
            for row in pooled_pivots_by_target[target].values()
        ]
        full_augmented_pivots = row_echelon(
            full_basis_rows + nearby_97_witness_rows, names)
        nearby_97_direct_coverage += int(row_in_span(
            full_augmented_pivots, correction_rows[target], names))
    need(nearby_97_direct_coverage == 104,
         "nearby 97-row witness misses an exact pooled-span correction")
    nearby_96_candidates = []
    for removed in nearby_97_witness_indices:
        candidate_omissions = nearby_97_witness_omissions | {removed}
        nearby_96_candidates.append((
            candidate_omissions,
            correction_basis_omission_coverage(candidate_omissions)))
    nearby_96_best_coverage = max(
        len(covered) for _, covered in nearby_96_candidates)
    nearby_96_witness_omissions = next(
        (omissions for omissions, covered in nearby_96_candidates
         if len(covered) == 104), None)
    nearby_96_witness_indices = (
        sorted(set(range(104)) - nearby_96_witness_omissions)
        if nearby_96_witness_omissions is not None else [])
    nearby_96_direct_coverage = 0
    if nearby_96_witness_indices:
        nearby_96_witness_rows = [correction_rows[index]
                                  for index in nearby_96_witness_indices]
        need(len(row_echelon(nearby_96_witness_rows, names)) == 96,
             "nearby 96-row correction witness is not independent")
        for target in range(104):
            full_basis_rows = [
                {names[column]: value for column, value in row.items()}
                for row in pooled_pivots_by_target[target].values()
            ]
            full_augmented_pivots = row_echelon(
                full_basis_rows + nearby_96_witness_rows, names)
            nearby_96_direct_coverage += int(row_in_span(
                full_augmented_pivots, correction_rows[target], names))
        need(nearby_96_direct_coverage == 104,
             "nearby 96-row witness misses an exact pooled-span correction")

    # Screen whether a small shared space spanned by actual correction rows
    # can cover the target-specific correction cosets.
    coverage_by_correction = [set() for _ in range(104)]
    correction_residuals = []
    for target, pivots in enumerate(pooled_pivots_by_target):
        correction_residuals.append(
            residual_mod_span(pivots, correction_rows[target], names))
    for target, pivots in enumerate(pooled_pivots_by_target):
        for candidate, row in enumerate(correction_rows):
            candidate_residual = residual_mod_span(pivots, row, names)
            if proportional(correction_residuals[target], candidate_residual):
                coverage_by_correction[candidate].add(target)
    need(all(coverage_by_correction[target] == {target}
             for target in range(104)),
         "a correction-row direction became reusable across targets")

    coverage_by_boundary_coordinate = [set() for _ in names]
    for target, pivots in enumerate(pooled_pivots_by_target):
        target_residual = correction_residuals[target]
        for coordinate, name in enumerate(names):
            residual = residual_mod_span(pivots, {name: Q(1)}, names)
            if proportional(target_residual, residual):
                coverage_by_boundary_coordinate[coordinate].add(target)

    # Test a small natural family of two-dimensional X-space additions. This
    # is an exploratory candidate screen, not a lower bound on arbitrary H.
    candidate_directions: dict[str, dict[str, Q]] = {
        f"root_coordinate_{axis}": {
            f"X{source}": Q(ports[source][axis])
            for source in range(104) if ports[source][axis]
        }
        for axis in range(8)
    }
    candidate_directions.update({
        "all_ones": {f"X{source}": Q(1) for source in range(104)},
        "linear_index": {f"X{source}": Q(source + 1)
                         for source in range(104)},
        "alternating": {f"X{source}": Q(1 if source % 2 == 0 else -1)
                        for source in range(104)},
        "quadratic_index": {f"X{source}": Q((source + 1)**2)
                            for source in range(104)},
    })
    candidate_names = sorted(candidate_directions)
    candidate_pair_coverage = {
        pair: set() for pair in itertools.combinations(candidate_names, 2)
    }
    for target, pivots in enumerate(pooled_pivots_by_target):
        correction_residual = correction_residuals[target]
        projected = {
            name: residual_mod_span(pivots, row, names)
            for name, row in candidate_directions.items()
        }
        correction_vector = {
            names[column]: value for column, value in correction_residual.items()
        }
        for pair in candidate_pair_coverage:
            pair_rows = [
                {names[column]: value
                 for column, value in projected[name].items()}
                for name in pair
            ]
            if in_span_of_two(pair_rows, correction_vector, names):
                candidate_pair_coverage[pair].add(target)
    best_pair = min(candidate_pair_coverage,
                    key=lambda pair: (-len(candidate_pair_coverage[pair]), pair))
    best_pair_coverage = len(candidate_pair_coverage[best_pair])

    # Exhaust all two-direction spaces generated by the 104 actual correction
    # rows. Modular quotient ranks cheaply reject almost all pairs; candidates
    # surviving that necessary test are confirmed over Q.
    correction_pair_coverage = {
        pair: set() for pair in itertools.combinations(range(104), 2)
    }
    mixed_pair_coverage = {
        (source, direction): set()
        for source in range(104) for direction in candidate_names
    }
    correction_residual_grid = [
        [residual_mod_span(pooled_pivots_by_target[target],
                           correction_rows[source], names)
         for source in range(104)]
        for target in range(104)
    ]
    natural_residual_grid = [
        {name: residual_mod_span(pooled_pivots_by_target[target], row, names)
         for name, row in candidate_directions.items()}
        for target in range(104)
    ]
    primes = (1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051)
    pair_prime = next((prime for prime in primes if all(
        value.denominator % prime
        for target_rows in correction_residual_grid
        for row in target_rows for value in row.values()) and all(
        value.denominator % prime
        for target_rows in natural_residual_grid
        for row in target_rows.values() for value in row.values())), None)
    need(pair_prime is not None,
         "no screen prime is invertible on the correction quotient data")
    for target, target_rows in enumerate(correction_residual_grid):
        target_vector = reduce_mod_prime(target_rows[target], pair_prime)
        modular_rows = [reduce_mod_prime(row, pair_prime)
                        for row in target_rows]
        modular_natural = {
            name: reduce_mod_prime(row, pair_prime)
            for name, row in natural_residual_grid[target].items()
        }
        for first in range(103):
            pair_basis = row_echelon_mod(
                [target_vector, modular_rows[first]], pair_prime)
            for second in range(first + 1, 104):
                if not row_in_span_mod(pair_basis, modular_rows[second],
                                       pair_prime):
                    continue
                pair = (first, second)
                if in_span_of_two(
                        [{names[column]: value
                          for column, value in target_rows[index].items()}
                         for index in pair],
                        {names[column]: value for column, value in
                         correction_residuals[target].items()}, names):
                    correction_pair_coverage[pair].add(target)
        for source in range(104):
            pair_basis = row_echelon_mod(
                [target_vector, modular_rows[source]], pair_prime)
            for direction in candidate_names:
                if not row_in_span_mod(pair_basis, modular_natural[direction],
                                       pair_prime):
                    continue
                if in_span_of_two(
                        [{names[column]: value
                          for column, value in row.items()}
                         for row in (target_rows[source],
                                     natural_residual_grid[target][direction])],
                        {names[column]: value for column, value in
                         correction_residuals[target].items()}, names):
                    mixed_pair_coverage[source, direction].add(target)
    best_correction_pair = min(
        correction_pair_coverage,
        key=lambda pair: (-len(correction_pair_coverage[pair]), pair))
    best_correction_pair_coverage = len(
        correction_pair_coverage[best_correction_pair])
    best_mixed_pair = min(
        mixed_pair_coverage,
        key=lambda pair: (-len(mixed_pair_coverage[pair]), pair))
    best_mixed_pair_coverage = len(mixed_pair_coverage[best_mixed_pair])

    uncovered = set(range(104))
    chosen_corrections = []
    while uncovered:
        candidate = max(range(104),
                        key=lambda index: (len(coverage_by_correction[index] &
                                              uncovered), -index))
        newly_covered = coverage_by_correction[candidate] & uncovered
        need(newly_covered, "correction-row directions do not cover all targets")
        chosen_corrections.append(candidate)
        uncovered -= newly_covered
    chosen_rows = [correction_rows[index] for index in chosen_corrections]
    chosen_row_rank = len(row_echelon(chosen_rows, names))
    for target in range(104):
        rows = (list(available[f"Y{target}"].values()) +
                list(target_available[f"Y{target}"].values()) + chosen_rows)
        need(row_in_span(row_echelon(rows, names), correction_rows[target], names),
             f"greedy correction-row directions miss C_{target}")

    # Turn each exact-chart representation of C_t using helper snapshots plus
    # X_t into chronological scalar additions. Route the terminal Y transport
    # through X_t's frame to make the final X_t addition legal.
    scheduled: dict[int, list[tuple[int, str, Q, tuple[int, ...], dict[str, Q]]]] = \
        defaultdict(list)
    source_unit_coefficients = {}
    helper_snapshot_add_count = 0
    terminal_detour_rank_mass = 0
    correction_word_records = []
    for target in range(104):
        exact_rows = exact_snapshot_rows_by_target[target]
        exact_meta = exact_snapshot_meta_by_target[target]
        representation = exact_correction_representations[target]
        unit_coefficient = representation.get(len(exact_rows), Q())
        need(unit_coefficient, f"C_{target} has zero X_t coefficient")
        source_unit_coefficients[str(target)] = str(unit_coefficient)
        target_ops = []
        for snapshot_index, coefficient in representation.items():
            if snapshot_index == len(exact_rows):
                continue
            source, event_index, frame = exact_meta[snapshot_index]
            need(not source.startswith("Y"),
                 "correction representation unexpectedly reads another target")
            need(event_index >= -1 and event_index < len(witness["program"]),
                 "helper snapshot has an invalid chronological cut")
            snapshot_row = exact_rows[snapshot_index]
            scheduled[event_index].append(
                (target, source, coefficient, frame, snapshot_row))
            helper_snapshot_add_count += 1
            target_ops.append({
                "target": target,
                "after_event": event_index,
                "source": source,
                "coefficient": str(coefficient),
                "frame": list(frame),
            })
        correction_word_records.append({
            "target": target,
            "terminal_transport_event": last_y_write[target],
            "source_frame": list(terminal_source_frames[target]),
            "source_unit_coefficient": str(unit_coefficient),
            "helper_snapshot_additions": target_ops,
        })
        terminal_event = witness["program"][last_y_write[target]]
        need(terminal_event[0] == "transport",
             f"Y{target} terminal correction cut is not a transport")
        first_rank = abs(len(terminal_event[2]) -
                         len(terminal_source_frames[target]))
        second_rank = abs(len(terminal_source_frames[target]) -
                          len(terminal_event[3]))
        need(first_rank + second_rank - terminal_event[4] == 2,
             f"Y{target} terminal detour rank increment is not two")
        terminal_detour_rank_mass += first_rank + second_rank - terminal_event[4]

    need(len(terminal_source_frames) == 104,
         "some target has no terminal source frame")
    need(all(len(frame) == 9 for frame in terminal_source_frames.values()),
         "terminal source roles are not in full F9 frames")
    scalar_correction_add_count = helper_snapshot_add_count + 104
    need(scalar_correction_add_count ==
         sum(rank * count for rank, count in exact_representation_support_hist.items())
         == 1352, "unexpected exact snapshot correction addition count")
    need(terminal_detour_rank_mass == 208,
         "unexpected terminal source-frame detour rank mass")
    detour_paid_profile = {int(rank): int(count)
                           for rank, count in channel["paid_profile"].items()}
    for target in range(104):
        event = witness["program"][last_y_write[target]]
        old_rank = int(event[4])
        source_rank = len(terminal_source_frames[target])
        first_rank = abs(len(event[2]) - source_rank)
        second_rank = abs(source_rank - len(event[3]))
        need(first_rank + second_rank - old_rank == 2,
             f"Y{target} corrected profile changed")
        detour_paid_profile[old_rank] -= 1
        detour_paid_profile[first_rank] = detour_paid_profile.get(first_rank, 0) + 1
        detour_paid_profile[second_rank] = detour_paid_profile.get(second_rank, 0) + 1
    detour_paid_profile = {rank: count for rank, count in detour_paid_profile.items()
                           if count}
    corrected_rank_mass = sum(rank * count
                              for rank, count in detour_paid_profile.items())
    channel_add_count = sum(event[0] == "add" for event in witness["program"])
    zero_saving_moment = Q(corrected_rank_mass, 9 * int(channel["columns"]))
    need(corrected_rank_mass == 2576 and max(detour_paid_profile) < 9 and
         zero_saving_moment == Q(46, 45) > 1 and channel_add_count == 2624,
         "snapshot-correction finite invoice changed")

    corrected_state = {name: {name: Q(1)} for name in names}
    corrected_frames = {name: tuple(frame)
                        for name, frame in witness["initial_frames"].items()}

    def apply_scheduled(cut: int) -> None:
        for target, source, coefficient, frame, expected_row in scheduled.get(cut, ()):
            destination = f"Y{target}"
            need(corrected_state[source] == expected_row,
                 f"{source} snapshot differs at inserted cut {cut}")
            need(corrected_frames[destination] == corrected_frames[source] == frame,
                 f"inserted helper add lacks an exact common chart at cut {cut}")
            for name, value in corrected_state[source].items():
                updated = corrected_state[destination].get(name, Q()) + coefficient*value
                if updated:
                    corrected_state[destination][name] = updated
                else:
                    corrected_state[destination].pop(name, None)

    apply_scheduled(-1)
    for index, event in enumerate(witness["program"]):
        op = event[0]
        target = next((t for t in range(104) if last_y_write[t] == index), None)
        if target is not None:
            _, register, old_frame, new_frame, _ = event
            need(op == "transport" and register == f"Y{target}",
                 "correction cut is not a terminal target transport")
            source_frame = terminal_source_frames[target]
            need(frame_span(corrected_frames[register]) == frame_span(tuple(old_frame)) and
                 corrected_frames[f"X{target}"] == source_frame,
                 f"{register} source-frame detour is unavailable")
            corrected_frames[register] = source_frame
            coefficient = Q(source_unit_coefficients[str(target)])
            for name, value in corrected_state[f"X{target}"].items():
                updated = corrected_state[register].get(name, Q()) + coefficient*value
                if updated:
                    corrected_state[register][name] = updated
                else:
                    corrected_state[register].pop(name, None)
            corrected_frames[register] = tuple(new_frame)
        elif op == "transport":
            _, register, old_frame, new_frame, _ = event
            need(frame_span(corrected_frames[register]) == frame_span(tuple(old_frame)),
                 f"transport entry mismatch at event {index}")
            corrected_frames[register] = tuple(new_frame)
        elif op == "zero":
            _, register, frame = event
            corrected_state[register] = {}
            corrected_frames[register] = tuple(frame)
        elif op == "erase":
            _, register, frame = event
            need(frame_span(corrected_frames[register]) == frame_span(tuple(frame)),
                 f"erase frame mismatch at event {index}")
            corrected_state.pop(register)
            corrected_frames.pop(register)
        elif op == "copy":
            _, register, source, frame = event
            need(frame_span(corrected_frames[register]) ==
                 frame_span(corrected_frames[source]) == frame_span(tuple(frame)),
                 f"copy chart mismatch at event {index}")
            corrected_state[register] = dict(corrected_state[source])
            corrected_frames[register] = tuple(frame)
        else:
            need(op == "add", "unknown scalar event")
            _, register, source, coefficient, frame = event
            need(frame_span(corrected_frames[register]) ==
                 frame_span(corrected_frames[source]) == frame_span(tuple(frame)),
                 f"native scalar chart mismatch at event {index}")
            coefficient = Q(coefficient)
            for name, value in corrected_state[source].items():
                updated = corrected_state[register].get(name, Q()) + coefficient*value
                if updated:
                    corrected_state[register][name] = updated
                else:
                    corrected_state[register].pop(name, None)
        apply_scheduled(index)

    need(set(corrected_state) == set(names),
         "snapshot correction did not restore private storage")
    for name in names:
        expected = {name: Q(1)}
        if name.startswith("Y"):
            target = int(name[1:])
            expected[f"X{target}"] = Q(1)
        need(corrected_state[name] == expected,
             f"snapshot correction output row mismatch at {name}")
        need(frame_span(corrected_frames[name]) ==
             frame_span(tuple(witness["final_frames"][name])),
             f"snapshot correction endpoint frame mismatch at {name}")

    correction_word = {
        "schema": "p104-snapshot-side-correction/1",
        "target_count": 104,
        "exact_helper_snapshot_additions": helper_snapshot_add_count,
        "source_unit_additions": 104,
        "total_scalar_additions": scalar_correction_add_count,
        "row_support_histogram": {
            str(k): count for k, count in sorted(exact_representation_support_hist.items())
        },
        "terminal_frame_detour_added_rank_mass": terminal_detour_rank_mass,
        "channel_rank_mass": int(channel["rank_mass"]),
        "channel_plus_correction_rank_mass": corrected_rank_mass,
        "paid_profile": {str(rank): count
                          for rank, count in sorted(detour_paid_profile.items())},
        "channel_scalar_additions": channel_add_count,
        "channel_plus_correction_scalar_additions": (
            channel_add_count + scalar_correction_add_count),
        "fixed_interface_zero_saving_moment": str(zero_saving_moment),
        "fixed_interface_conclusion": "moment exceeds one for every nonnegative saving before hosting or idle charges",
        "arbitrary_dirty_helper_restoration": True,
        "chronological_helper_additions": [operation
            for record in correction_word_records
            for operation in record["helper_snapshot_additions"]],
        "per_target_source_frame_terms": correction_word_records,
    }
    (ROOT / "SNAPSHOT-CORRECTION.json").write_text(
        json.dumps(correction_word, indent=2) + "\n")

    result = {
        "schema": "p104-existing-delivery-span/1",
        "status": "PASS_NO_FIXED_TRAJECTORY_SIDE_CORRECTION_DELIVERY",
        "witness_sha256": WITNESS_SHA256,
        "fixture_sha256": FIXTURE_SHA256,
        "independent_columns": len(names),
        "target_count": 104,
        "available_source_register_kinds": sorted({
            name[0] for name in names if not name.startswith("Y")
        }),
        "same_subspace_helper_snapshots_per_target_histogram": {
            str(k): count for k, count in sorted(Counter(
                len(rows) for rows in available.values()).items())
        },
        "target_reads_by_other_registers": 0,
        "delivery_rows_per_target_histogram": {
            str(k): row_count_hist[k] for k in sorted(row_count_hist)
        },
        "delivery_source_span_rank_histogram": {
            str(k): rank_hist[k] for k in sorted(rank_hist)
        },
        "same_subspace_other_target_snapshots_per_target_histogram": {
            str(k): count for k, count in sorted(Counter(
                len(rows) for rows in target_available.values()).items())
        },
        "helper_plus_target_carrier_span_rank_histogram": {
            str(k): count for k, count in sorted(expanded_rank_hist.items())
        },
        "projected_pooled_span_rank_in_X_histogram": {
            str(k): count for k, count in sorted(projected_span_rank_hist.items())
        },
        "pooled_span_intersection_with_X_rank_histogram": {
            str(k): count for k, count in sorted(
                x_intersection_dimension_hist.items())
        },
        "side_correction_outside_pooled_span_intersect_X_count":
            x_intersection_correction_outside,
        "one_common_added_X_space_direction_can_cover_all_targets":
            bool(x_common_direction) and not x_common_blocking_targets,
        "common_X_space_correction_extension_intersection_dimension":
            x_common_direction_dimension,
        "common_X_space_correction_extension_constraint_rank":
            x_common_constraint_rank,
        "common_X_space_correction_extension_blocking_targets":
            x_common_blocking_targets,
        "projected_coset_independence_lower_bound":
            len(projected_lower_bound_targets),
        "projected_coset_independence_target_subset":
            projected_lower_bound_targets,
        "projected_fixed_span_union_rank_for_subset":
            projected_lower_bound_span_rank,
        "projected_fixed_span_plus_corrections_rank_for_subset":
            projected_lower_bound_joint_rank,
        "projected_lower_bound_correction_basis_H_rank":
            projected_basis_H_rank,
        "projected_lower_bound_correction_basis_H_coverage":
            projected_basis_H_coverage,
        "initial_full_span_correction_basis_H_coverage":
            initial_full_basis_H_coverage,
        "optimized_full_span_correction_basis_H_indices":
            optimized_correction_basis_indices,
        "optimized_full_span_correction_basis_H_rank": full_basis_H_rank,
        "optimized_full_span_correction_basis_H_coverage_targets":
            optimized_coverage_targets,
        "full_span_correction_basis_H_coverage": full_basis_H_coverage,
        "full_span_correction_basis_H_uncovered_targets":
            full_basis_H_uncovered,
        "constructed_shared_correction_space_rank": constructive_H_rank,
        "constructed_shared_correction_space_row_indices":
            constructive_H_indices,
        "constructed_shared_correction_space_coverage":
            direct_constructive_H_coverage,
        "constructed_shared_correction_space_search_scope": (
            "Selected from spans of subsets of the 104 natural C_j basis rows; "
            "the exact rank-minimality search is only within this basis subset "
            "family, not arbitrary H."),
        "nearby_97_correction_basis_search_count": len(nearby_97_candidates),
        "nearby_97_correction_basis_best_coverage": nearby_97_best_coverage,
        "nearby_97_correction_basis_full_witness_count": nearby_97_witness_count,
        "nearby_97_correction_basis_witness_row_indices":
            nearby_97_witness_indices,
        "nearby_97_correction_basis_witness_direct_coverage":
            nearby_97_direct_coverage,
        "nearby_96_correction_basis_search_count": len(nearby_96_candidates),
        "nearby_96_correction_basis_best_coverage": nearby_96_best_coverage,
        "nearby_96_correction_basis_witness_row_indices":
            nearby_96_witness_indices,
        "nearby_96_correction_basis_witness_direct_coverage":
            nearby_96_direct_coverage,
        "nearby_96_correction_basis_search_scope": (
            "All 96-row subsets obtained by deleting one row from the recorded "
            "97-row witness; failure to find a witness here does not rule out "
            "other 96-row correction bases or arbitrary 96-dimensional spaces."),
        "nearby_97_correction_basis_search_scope": (
            "All 97-row subsets obtained from the constructed 98-row witness "
            "by one deletion or one deletion plus one exchange with an omitted "
            "natural C_j row; this local search does not rule out other basis "
            "subsets or arbitrary 97-dimensional spaces."),
        "unit_source_row_outside_helper_and_target_carrier_spans": target_failures,
        "side_correction_row_in_helper_span_count": correction_in_helper_span,
        "side_correction_row_in_helper_plus_X_t_span_count": correction_in_helper_plus_target_unit,
        "side_correction_row_in_exact_chart_helper_plus_X_t_span_count": correction_in_exact_helper_plus_target_unit,
        "helper_snapshot_plus_X_t_representation_support_histogram": {
            str(k): count for k, count in sorted(representation_support_hist.items())
        },
        "maximum_helper_snapshot_plus_X_t_additions_per_target": max(
            representation_support_hist),
        "exact_chart_helper_snapshot_plus_X_t_representation_support_histogram": {
            str(k): count for k, count in sorted(exact_representation_support_hist.items())
        },
        "exact_snapshot_correction_scalar_additions": scalar_correction_add_count,
        "exact_snapshot_correction_helper_additions": helper_snapshot_add_count,
        "terminal_source_frame_detour_rank_mass": terminal_detour_rank_mass,
        "side_correction_row_in_pooled_helper_target_span_count": correction_in_pooled_span,
        "side_correction_row_outside_pooled_span_count": correction_outside_pooled_span,
        "one_common_added_direction_can_cover_all_targets_in_relaxed_span_model": False,
        "common_direction_intersection_dimension": common_direction_dimension,
        "common_direction_constraint_rank": common_constraint_rank,
        "common_direction_example_support_size": len(common_direction),
        "common_direction_blocking_targets": common_blocking_targets,
        "minimum_shared_added_directions_lower_bound": 2,
        "greedy_shared_space_from_correction_rows_dimension": chosen_row_rank,
        "greedy_shared_space_from_correction_rows_selected_targets": chosen_corrections,
        "single_correction_row_direction_coverage_histogram": {
            str(k): count for k, count in sorted(Counter(
                len(targets) for targets in coverage_by_correction).items())
        },
        "single_boundary_coordinate_direction_coverage_histogram": {
            str(k): count for k, count in sorted(Counter(
                len(targets) for targets in coverage_by_boundary_coordinate).items())
        },
        "single_boundary_coordinate_direction_cover_map": {
            names[index]: sorted(targets)
            for index, targets in enumerate(coverage_by_boundary_coordinate)
            if targets
        },
        "best_single_boundary_coordinate_target_coverage": max(
            len(targets) for targets in coverage_by_boundary_coordinate),
        "natural_two_direction_family": candidate_names,
        "tested_natural_two_direction_pairs": len(candidate_pair_coverage),
        "best_natural_two_direction_pair": list(best_pair),
        "best_natural_two_direction_target_coverage": best_pair_coverage,
        "natural_two_direction_screen_scope": (
            "The eight root-coordinate rows and four constant/linear/"
            "alternating/quadratic index-pattern X-space rows only; this is "
            "a finite candidate screen, not a lower bound for arbitrary H."),
        "tested_actual_correction_row_pairs": len(correction_pair_coverage),
        "best_actual_correction_row_pair": list(best_correction_pair),
        "best_actual_correction_row_pair_target_coverage":
            best_correction_pair_coverage,
        "actual_correction_pair_screen_prime": pair_prime,
        "actual_correction_pair_exact_confirmations": sum(
            len(targets) for targets in correction_pair_coverage.values()),
        "tested_correction_plus_natural_direction_pairs":
            len(mixed_pair_coverage),
        "best_correction_plus_natural_direction_pair": [
            best_mixed_pair[0], best_mixed_pair[1]],
        "best_correction_plus_natural_direction_target_coverage":
            best_mixed_pair_coverage,
        "correction_plus_natural_pair_exact_confirmations": sum(
            len(targets) for targets in mixed_pair_coverage.values()),
        "unit_source_row_outside_span_count": target_failures,
        "scope": "For each target, exact rational spans are computed over every non-target helper snapshot and every other Y snapshot ever available in the same underlying F2 frame subspace along the fixed native trajectories. Basis conversion within that subspace is treated as free, enlarging the available source set. The unit source row X_t and actual side-correction row C_t = X_t - sum_s G[t,s] X_s/2 lie outside the pooled span for all 104 targets. The intersection of S_t + span(C_t) over all targets has dimension 72 and is contained in every S_t, so no one shared new row direction can supplement any target's fixed span enough to supply C_t, even with target-specific coefficients. Thus at least two shared added row directions are necessary. Screens over correction rows, twelve natural X-space directions and their mixed pairs show no two-direction space in those finite families supplies corrections for multiple targets; this is not a lower bound for arbitrary H. Changed helper trajectories and transports to other subspaces remain outside the screen; no general fusion impossibility is claimed.",
    }
    (ROOT / "EXISTING-DELIVERY-SPAN.json").write_text(
        json.dumps(result, indent=2) + "\n")
    package_result_path = ROOT / "RESULT.json"
    package_result = json.loads(package_result_path.read_text())
    package_result["existing_delivery_source_span_obstruction"] = result
    package_result["snapshot_correction_finite_invoice"] = {
        "correction_scalar_additions": scalar_correction_add_count,
        "helper_snapshot_additions": helper_snapshot_add_count,
        "source_unit_additions": 104,
        "correction_rank_mass": terminal_detour_rank_mass,
        "channel_plus_correction_scalar_additions": (
            channel_add_count + scalar_correction_add_count),
        "channel_plus_correction_rank_mass": corrected_rank_mass,
        "paid_profile": {str(rank): count
                          for rank, count in sorted(detour_paid_profile.items())},
        "fixed_interface_zero_saving_moment": str(zero_saving_moment),
        "scope": "Exact arbitrary-input correction word generated from same-chart fixed helper snapshots plus one source-unit direction per target; the source-unit additions are made through terminal F9 detours whose complete Clifford edges are independently checked by verify_transports.py. This improves the scalar-addition count but retains the noncontracting fixed-interface rank profile and excludes global hosting.",
    }
    package_result_path.write_text(json.dumps(package_result, indent=2) + "\n")
    print("PASS_P104_NO_FIXED_TRAJECTORY_SIDE_CORRECTION_DELIVERY",
          "targets=104", "y_reads=0",
          "span_ranks={74:12,75:24,76:32,77:24,78:12}",
          "target_carrier_span_ranks=" + str(dict(sorted(expanded_rank_hist.items()))),
          "correction_rows_in_pooled_span=" + str(correction_in_pooled_span),
          f"snapshot_word_adds={scalar_correction_add_count}",
          f"corrected_rank_mass={corrected_rank_mass}",
          "unit_rows_outside_spans=104")


if __name__ == "__main__":
    main()
