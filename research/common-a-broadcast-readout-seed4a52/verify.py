#!/usr/bin/env python3
"""Verify a charged common-A broadcast readout for the five-source boundary."""

from __future__ import annotations

import copy
import hashlib
import json
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
SOURCE = ROOT / "research/universal-connector-boundary/CERTIFICATE.json"
SOURCE_SHA256 = "e733746ba3e5151c829b4e8728bfff5ae3ed24d8d203eb77c735d20758e8266a"
CERTIFICATE_PATH = PACKAGE / "CERTIFICATE.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def prefix_states(source_word: list[int]) -> list[int]:
    states = [0]
    for source in source_word:
        states.append(states[-1] ^ (1 << source))
    return states


def derive(source_word: list[int], rows: list[int], slots: list[list[int]]) -> dict:
    require(len(rows) == len(slots), "one slot list is required for each output mask")
    states = prefix_states(source_word)
    counts = [source_word.count(j) for j in range(5)]
    require(counts == [2, 2, 2, 2, 2], "each dirty source must be toggled twice")
    require(states[-1] == 0, "the source path must restore the connector")
    require(len(set(states[:-1])) == 10, "the witness must have ten distinct visited states")
    require(rows == list(range(1, 32)), "the five-source target set must be masks 1 through 31")

    grouped: dict[int, list[int]] = {}
    row_counts: dict[int, int] = {}
    for mask, positions in zip(rows, slots):
        require(len(positions) in (2, 4), f"mask {mask} needs two or four readouts")
        require(all(0 <= p < len(states) for p in positions), f"mask {mask} has an invalid boundary")
        selected_states = [states[p] for p in positions]
        require(len(set(selected_states)) == len(selected_states), f"mask {mask} repeats a readout state")
        total = 0
        for state in selected_states:
            total ^= state
            grouped.setdefault(state, []).append(mask)
        require(total == mask, f"mask {mask} has wrong prefix difference {total}")
        row_counts[mask] = len(selected_states)

    visit_order: list[int] = []
    for state in states[:-1]:
        if state in grouped and state not in visit_order:
            visit_order.append(state)
    require(set(visit_order) == set(grouped), "every broadcast target set must have a visited state")
    events = [
        {
            "state": state,
            "prefix_id": visit_order.index(state),
            "targets": sorted(grouped[state]),
        }
        for state in visit_order
    ]
    writes = sum(len(event["targets"]) for event in events)
    require(writes == sum(row_counts.values()) == 64, "the broadcast events must preserve all 64 target writes")
    require(all(len(event["targets"]) == len(set(event["targets"])) for event in events),
            "one target may be updated at most once by a state")
    require(sum(count == 4 for count in row_counts.values()) == 1
            and row_counts[21] == 4
            and all(row_counts[m] == 2 for m in rows if m != 21),
            "the ten-toggle witness must use its four-readout repair only for mask 21")

    return {
        "source_word": source_word,
        "prefix_states": states,
        "unique_prefix_states": visit_order,
        "rows": rows,
        "readout_slots": slots,
        "row_readout_counts": {str(m): row_counts[m] for m in rows},
        "events": events,
        "counts": {
            "sources": 5,
            "output_masks": 31,
            "source_calls": len(source_word),
            "distinct_broadcast_evaluations": len(events),
            "ordinary_readouts_on_same_path": writes,
            "target_row_updates": writes,
            "A_evaluation_saving": writes - len(events),
        },
            "cost_model": {
                "common_setup": "P",
                "unicast": "P + 2*sum(b_j) + 64*(a+w) + D_u",
                "broadcast": "P + 2*sum(b_j) + 10*a + 64*w + D_b",
                "saving": "54*a + D_u - D_b",
                "break_even": "D_b - D_u < 54*a",
                "target_update_saving_coefficient": 0,
                "source_toggle_saving_coefficient": 0,
                "normalized_example": {
                    "a": "1/2",
                    "w": "1/2",
                    "D_u_minus_D_b": "0",
                    "saving": "27",
                },
            },
    }


def load_source_schedule() -> dict:
    raw = SOURCE.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == SOURCE_SHA256, f"pinned predecessor certificate changed: {digest}")
    parent = json.loads(raw)
    require(parent["scope"] == "Exact binary query model; no new kappa or supplier integration",
            "unexpected predecessor scope")
    return parent["schedules"]["five_extra_output"]


def make_certificate(schedule: dict) -> dict:
    result = derive(schedule["source_word"], schedule["rows"], schedule["readout_slots"])
    result.update(
        {
            "schema": "common-a-broadcast-readout-v1",
            "assignment_seed": "4a52e71a301f7115ab632ed556f62fad",
            "priority_revision": 3,
            "base_commit": "0b1cccf86e2f5132ed286a26ef0a681a495740ea",
            "selected_record_sha256": "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
            "predecessor": {
                "pr": 943,
                "source_certificate": "research/universal-connector-boundary/CERTIFICATE.json",
                "schedule": "five_extra_output",
            },
            "operation": "R_S(z): y_m += A z for every mask m in S, using one common A evaluation",
            "tariff": "one full A evaluation plus one full target-row addition per listed mask, plus declared routing and dispatch",
            "program_encoding_bits": {
                "ordinary": 10 * (1 + 3) + 64 * (1 + 4 + 5),
                "broadcast": 10 * (1 + 3) + 10 * (1 + 4 + 4) + 64 * 5,
                "saving": 10 * (1 + 3) + 64 * (1 + 4 + 5)
                - (10 * (1 + 3) + 10 * (1 + 4 + 4) + 64 * 5),
                "field_widths": {
                    "opcode": 1,
                    "source_id": 3,
                    "ordinary_boundary_id": 4,
                    "broadcast_state_id": 4,
                    "broadcast_target_count": 4,
                    "target_id": 5,
                },
            },
            "dense_reference": {
                "data_rows": 37,
                "coefficient_matrices": 6,
                "coefficient_storage_bits": "6*L^2",
                "data_storage_bits": "37*L",
                "extra_full_length_rows": 0,
                "scalar_accumulators": 1,
                "source_B_evaluations": 10,
                "A_evaluations_ordinary": 64,
                "A_evaluations_broadcast": 10,
                "target_updates_either_schedule": "64*L",
                "per_A_evaluation": {
                    "coefficient_reads": "L^2",
                    "connector_reads": "L^2",
                    "binary_products": "L^2",
                    "accumulator_xors": "L^2",
                    "scalar_zeroes": "L",
                },
                "per_B_evaluation": {
                    "coefficient_reads": "L^2",
                    "source_reads": "L^2",
                    "binary_products": "L^2",
                    "accumulator_xors": "L^2",
                    "scalar_zeroes": "L",
                    "connector_xors": "L",
                },
            },
        }
    )
    return result


def verify_certificate_file(schedule: dict, write: bool = False) -> dict:
    expected = make_certificate(schedule)
    encoded = json.dumps(expected, indent=2, sort_keys=True) + "\n"
    if write:
        CERTIFICATE_PATH.write_text(encoded, encoding="utf-8")
        return expected
    actual = json.loads(CERTIFICATE_PATH.read_text(encoding="utf-8"))
    require(actual == expected, "CERTIFICATE.json does not match the pinned source schedule")
    return actual


def small_fixture() -> tuple[list[int], list[int], list[list[int]]]:
    word = [0, 1, 0, 1]
    rows = [1, 2, 3]
    slots = [[0, 1], [1, 2], [0, 2]]
    states = prefix_states(word)
    require(states == [0, 1, 3, 2, 0], "small positive-control prefix path changed")
    return word, rows, slots


def groups_for(word: list[int], rows: list[int], slots: list[list[int]]) -> dict[int, list[int]]:
    states = prefix_states(word)
    grouped: dict[int, list[int]] = {}
    for mask, positions in zip(rows, slots):
        total = 0
        chosen = [states[p] for p in positions]
        require(len(chosen) == len(set(chosen)), f"mask {mask} uses a duplicate state")
        for state in chosen:
            total ^= state
            grouped.setdefault(state, []).append(mask)
        require(total == mask, f"mask {mask} has incorrect source contribution")
    return {state: sorted(masks) for state, masks in grouped.items()}


def matvec(matrix: list[int], vector: int) -> int:
    result = 0
    for row_id, row in enumerate(matrix):
        if ((row & vector).bit_count() & 1) != 0:
            result |= 1 << row_id
    return result


def matrices(n_sources: int, width: int) -> tuple[list[int], list[list[int]]]:
    mask = (1 << width) - 1
    common_a = []
    for r in range(width):
        common_a.append((((r + 1) * 5) ^ ((r + 2) << 1) ^ 0b101) & mask)
    source_maps = []
    for j in range(n_sources):
        rows = []
        for r in range(width):
            rows.append((((j + 3) * (r + 1) * 7) ^ ((r + j + 1) << (j % width)) ^ (1 << r)) & mask)
        source_maps.append(rows)
    return common_a, source_maps


def run_schedule(
    word: list[int],
    rows: list[int],
    slots: list[list[int]],
    common_a: list[int],
    source_maps: list[list[int]],
    sources: list[int],
    connector: int,
    targets: dict[int, int],
) -> tuple[list[int], int, dict[int, int]]:
    grouped = groups_for(word, rows, slots)
    seen: set[int] = set()
    q = 0
    for boundary in range(len(word) + 1):
        if q in grouped and q not in seen:
            value = matvec(common_a, connector)
            for mask in grouped[q]:
                targets[mask] ^= value
            seen.add(q)
        if boundary < len(word):
            j = word[boundary]
            connector ^= matvec(source_maps[j], sources[j])
            q ^= 1 << j
    require(seen == set(grouped), "some broadcast event was not executed")
    return sources, connector, targets


def expected_outputs(
    rows: list[int],
    common_a: list[int],
    source_maps: list[list[int]],
    sources: list[int],
    targets: dict[int, int],
) -> dict[int, int]:
    result = dict(targets)
    for mask in rows:
        signal = 0
        for j, source in enumerate(sources):
            if (mask >> j) & 1:
                signal ^= matvec(source_maps[j], source)
        result[mask] ^= matvec(common_a, signal)
    return result


def verify_dense_instance(
    word: list[int],
    rows: list[int],
    slots: list[list[int]],
    width: int,
    random_cases: int,
    seed: int,
) -> int:
    n_sources = max(word) + 1
    common_a, source_maps = matrices(n_sources, width)
    total_rows = n_sources + 1 + len(rows)
    basis_count = total_rows * width
    for bit in range(basis_count):
        vectors = [0] * total_rows
        vectors[bit // width] = 1 << (bit % width)
        sources = vectors[:n_sources]
        connector = vectors[n_sources]
        old_targets = {mask: vectors[n_sources + 1 + i] for i, mask in enumerate(rows)}
        expected = expected_outputs(rows, common_a, source_maps, sources, old_targets)
        got_sources, got_connector, got_targets = run_schedule(
            word, rows, slots, common_a, source_maps, list(sources), connector, dict(old_targets)
        )
        require(got_sources == sources, "a source row changed in dense replay")
        require(got_connector == connector, "dirty connector was not restored in dense replay")
        require(got_targets == expected, f"dense basis column {bit} has an incorrect target")

    rng = random.Random(seed)
    for case in range(random_cases):
        sources = [rng.getrandbits(width) for _ in range(n_sources)]
        connector = rng.getrandbits(width)
        old_targets = {mask: rng.getrandbits(width) for mask in rows}
        expected = expected_outputs(rows, common_a, source_maps, sources, old_targets)
        got_sources, got_connector, got_targets = run_schedule(
            word, rows, slots, common_a, source_maps, list(sources), connector, dict(old_targets)
        )
        require(got_sources == sources, f"random case {case} changed a source")
        require(got_connector == connector, f"random case {case} changed connector dirt")
        require(got_targets == expected, f"random case {case} has an incorrect target")
    return basis_count


def expect_rejected(label: str, operation) -> None:
    try:
        operation()
    except (ValueError, KeyError, IndexError):
        return
    raise ValueError(f"negative control was not rejected: {label}")


def verify_controls(schedule: dict) -> None:
    bad_word = schedule["source_word"][:-1]
    expect_rejected(
        "omitted source restoration",
        lambda: derive(bad_word, schedule["rows"], schedule["readout_slots"]),
    )

    bad_slots = copy.deepcopy(schedule["readout_slots"])
    bad_slots[0] = [bad_slots[0][0], bad_slots[0][0]]
    expect_rejected(
        "wrong target prefix difference",
        lambda: derive(schedule["source_word"], schedule["rows"], bad_slots),
    )

    broken = derive(schedule["source_word"], schedule["rows"], schedule["readout_slots"])
    broken["events"][0]["targets"].pop()
    expected = derive(schedule["source_word"], schedule["rows"], schedule["readout_slots"])
    expect_rejected(
        "missing target update",
        lambda: require(broken["events"] == expected["events"], "target event mismatch"),
    )


def main() -> None:
    source_schedule = load_source_schedule()
    write_certificate = len(sys.argv) == 2 and sys.argv[1] == "--write-certificate"
    require(len(sys.argv) == 1 or write_certificate, "usage: verify.py [--write-certificate]")
    certificate = verify_certificate_file(source_schedule, write=write_certificate)
    if write_certificate:
        print("WROTE_CERTIFICATE")
        return

    small_word, small_rows, small_slots = small_fixture()
    small_events = groups_for(small_word, small_rows, small_slots)
    require(len(small_events) == 3 and sum(map(len, small_events.values())) == 6,
            "two-source fixture must use three evaluations and six target writes")
    small_basis = verify_dense_instance(
        small_word, small_rows, small_slots, width=3, random_cases=32, seed=0x2A
    )

    verify_controls(source_schedule)
    main_basis = verify_dense_instance(
        source_schedule["source_word"],
        source_schedule["rows"],
        source_schedule["readout_slots"],
        width=3,
        random_cases=64,
        seed=0x4A52,
    )
    counts = certificate["counts"]
    require(counts["source_calls"] == 10, "unexpected source-call count")
    require(counts["distinct_broadcast_evaluations"] == 10, "unexpected broadcast count")
    require(counts["ordinary_readouts_on_same_path"] == 64, "unexpected old readout count")
    require(counts["target_row_updates"] == 64, "target writes were not fully charged")
    require(certificate["program_encoding_bits"]["ordinary"] == 680, "ordinary program bill changed")
    require(certificate["program_encoding_bits"]["broadcast"] == 450, "broadcast program bill changed")
    require(certificate["program_encoding_bits"]["saving"] == 230, "descriptor saving changed")

    print(
        "PASS_COMMON_A_BROADCAST "
        f"small_basis_columns={small_basis} "
        f"masks=31 source_calls=10 distinct_states=10 "
        f"A_evaluations=10 ordinary_A_calls=64 target_writes=64 "
        f"descriptor_bits=680->450 dense_basis_columns={main_basis} "
        "random_dirty_cases=96 negative_controls=3"
    )


if __name__ == "__main__":
    main()
