#!/usr/bin/env python3
"""Independent finite cap-16 partition oracle; standard library only.

This module does not import the primary checker or any predecessor constructor.
It expands every legal first-block choice, retaining all reachable sorted mass
vectors and their exact presentation counts.  Default operation consumes fixed
INDEPENDENT.json.  --json prints the recomputed record; it never writes evidence.

The checked object is a zero-additional-charge chronological packing relaxation.
No circuit identity, dirty-state restoration, precision bound or supplier adoption
is established by this combinatorial calculation.
"""
from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBER = "candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz"
MEMBER_SHA256 = "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"
CAP = 16
RUN_CENSUS = {
    (2,): 362,
    (3,): 123,
    (2, 2): 16,
    (3, 2): 5,
    (3, 3): 124,
    (2, 2, 2): 3,
    (2, 2, 2, 2): 1,
    (3,) * 4: 3,
    (2, 2) + (3,) * 4: 1,
    (3,) * 8: 1,
    (2, 2) + (3,) * 8: 1,
    (2, 2) + (3,) * 24: 1,
}
EXPECTED_CLIMBS = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82}
EXPECTED_PROFILE = {
    1: 2412, 2: 362, 3: 123, 4: 158, 5: 87,
    6: 127, 8: 9, 9: 1, 12: 4, 15: 5, 16: 3,
}


class Rejected(ValueError):
    """A named contract failed; controls must see their intended name."""

    def __init__(self, tag: str, detail: str):
        self.tag = tag
        super().__init__(f"{tag}: {detail}")


def require(condition: bool, tag: str, detail: str) -> None:
    if not condition:
        raise Rejected(tag, detail)


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, "duplicate-json-key", key)
        result[key] = value
    return result


def decode_json(raw: bytes | str) -> Any:
    return json.loads(raw, object_pairs_hook=unique_object)


def load_source() -> dict[str, list[list[Any]]]:
    path = ROOT / ARCHIVE
    require(path.is_file(), "source-missing", str(path))
    archive_bytes = path.read_bytes()
    require(hashlib.sha256(archive_bytes).hexdigest() == ARCHIVE_SHA256,
            "archive-sha256", ARCHIVE)
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        matches = [member for member in archive.getmembers() if member.name == MEMBER]
        require(len(matches) == 1, "member-unique", MEMBER)
        require(matches[0].isfile(), "member-file", MEMBER)
        stream = archive.extractfile(matches[0])
        require(stream is not None, "member-stream", MEMBER)
        compressed = stream.read()
    require(hashlib.sha256(compressed).hexdigest() == MEMBER_SHA256,
            "member-sha256", MEMBER)
    result = decode_json(gzip.decompress(compressed))
    require(isinstance(result, dict) and set(result) == {"forward", "backward"},
            "orientations", "exactly forward and backward required")
    return result


def eligible_runs(events: list[list[Any]]) -> list[tuple[int, ...]]:
    """Erase phase markers; all other ineligible events terminate a run."""
    require(isinstance(events, list), "trace-type", "event list required")
    result: list[tuple[int, ...]] = []
    pending: list[int] = []
    for event in events:
        require(isinstance(event, list) and len(event) > 0 and isinstance(event[0], str),
                "event-shape", repr(event))
        kind = event[0]
        if kind == "phase":
            continue
        if kind == "climb":
            require(len(event) == 6 and type(event[5]) is int and event[5] > 0,
                    "climb-shape", repr(event))
        if kind == "climb" and event[5] in (2, 3):
            pending.append(event[5])
        elif pending:
            result.append(tuple(pending))
            pending = []
    if pending:
        result.append(tuple(pending))
    return result


def check_census(events: list[list[Any]], expected: dict[tuple[int, ...], int]) -> list[tuple[int, ...]]:
    runs = eligible_runs(events)
    require(Counter(runs) == expected, "run-census", "eligible-run multiplicities differ")
    return runs


def ordered_block_lengths(run: tuple[int, ...]) -> tuple[int, ...]:
    """Explicit witnesses for the twelve source-bound run types only."""
    require(run in RUN_CENSUS, "run-domain", repr(run))
    if sum(run) <= CAP:
        return (len(run),)
    if run == (3,) * 8:
        return (5, 3)
    if run == (2, 2) + (3,) * 8:
        return (6, 4)
    require(run == (2, 2) + (3,) * 24, "long-run-domain", repr(run))
    return (6, 5, 5, 5, 5)


def expected_candidate(run: tuple[int, ...]) -> tuple[int, ...]:
    if sum(run) <= CAP:
        return (sum(run),)
    if run == (3,) * 8:
        return (15, 9)
    if run == (2, 2) + (3,) * 8:
        return (16, 12)
    require(run == (2, 2) + (3,) * 24, "candidate-domain", repr(run))
    return (16, 15, 15, 15, 15)


def check_witness(run: tuple[int, ...], lengths: tuple[int, ...],
                  candidate: tuple[int, ...], cap: int = CAP) -> tuple[int, ...]:
    require(all(type(n) is int and n > 0 for n in lengths) and sum(lengths) == len(run),
            "witness-coverage", "blocks must partition every call exactly once")
    start = 0
    masses = []
    for length in lengths:
        mass = sum(run[start:start + length])
        require(mass <= cap, "block-cap", f"block mass {mass} exceeds {cap}")
        masses.append(mass)
        start += length
    result = tuple(sorted(masses, reverse=True))
    require(result == candidate, "witness-masses", "chronological witness has different masses")
    return result


def make_enumerator() -> Callable[[tuple[int, ...]], dict[tuple[int, ...], int]]:
    @lru_cache(maxsize=None)
    def enumerate_vectors(run: tuple[int, ...]) -> dict[tuple[int, ...], int]:
        # The first cut uniquely determines a nonempty prefix, followed by a
        # complete partition of its suffix.  Sorting forgets only block order;
        # integer multiplicities preserve the number of chronological cut sets.
        if not run:
            return {(): 1}
        counts: Counter[tuple[int, ...]] = Counter()
        prefix_mass = 0
        for length, rank in enumerate(run, 1):
            prefix_mass += rank
            if prefix_mass > CAP:
                break
            for suffix_vector, presentations in enumerate_vectors(run[length:]).items():
                combined = tuple(sorted((prefix_mass,) + suffix_vector, reverse=True))
                counts[combined] += presentations
        return dict(counts)
    return enumerate_vectors


def check_majorization(candidate: tuple[int, ...], vector: tuple[int, ...], width: int) -> None:
    require(tuple(sorted(candidate, reverse=True)) == candidate and
            tuple(sorted(vector, reverse=True)) == vector,
            "sorted-vectors", "descending order required")
    require(sum(candidate) == sum(vector), "equal-mass", "majorization requires equal total mass")
    require(max(len(candidate), len(vector)) <= width, "padding-width", "padding width too short")
    candidate_total = 0
    vector_total = 0
    for index in range(width):
        if index < len(candidate):
            candidate_total += candidate[index]
        if index < len(vector):
            vector_total += vector[index]
        require(candidate_total >= vector_total, "prefix-majorization",
                f"prefix {index + 1}: {candidate_total} < {vector_total}")


def expect_rejection(tag: str, action: Callable[[], Any]) -> None:
    try:
        action()
    except Rejected as error:
        require(error.tag == tag, "control-wrong-rejection", f"expected {tag}, got {error.tag}")
        return
    # Unexpected acceptance must not be caught as the expected rejection.
    raise Rejected("control-accepted", tag)


def control_checks() -> list[str]:
    climb2 = ["climb", "fixture", 0, 0, 0, 2]
    climb3 = ["climb", "fixture", 0, 0, 0, 3]
    phase = ["phase", "fixture"]
    scalar = ["scalar", "fixture"]
    check_census([climb2, phase, climb3], {(2, 3): 1})
    for barrier in (scalar, ["adapter"], ["residual_adapter"], ["center"],
                    ["climb", "fixture", 0, 0, 0, 4], ["unknown-event"]):
        check_census([climb2, barrier, climb3], {(2,): 1, (3,): 1})
    # Reversing the two legal blocks is an equivalent positive presentation.
    check_witness((3,) * 8, (3, 5), (15, 9))
    check_majorization((15, 9), (12, 12), 8)
    expect_rejection("witness-masses",
                     lambda: check_witness((3,) * 8, (4, 4), (15, 9)))
    expect_rejection("block-cap",
                     lambda: check_witness((3,) * 8, (6, 2), (18, 6)))
    expect_rejection("run-census",
                     lambda: check_census([climb2, scalar, climb3], {(2, 3): 1}))
    expect_rejection("prefix-majorization",
                     lambda: check_majorization((12, 12), (15, 9), 8))
    expect_rejection("duplicate-json-key", lambda: decode_json('{"x":1,"x":1}'))
    return ["wrong_partition", "infeasible_cap", "changed_trace_boundary",
            "nonmajorizing_candidate", "duplicate_json_key"]


def string_profile(profile: Counter[int] | dict[int, int]) -> dict[str, int]:
    return {str(rank): count for rank, count in sorted(profile.items()) if count}


def compute_record() -> dict[str, Any]:
    source = load_source()
    controls = control_checks()
    enumerate_vectors = make_enumerator()
    run_records = []
    distinct_vector_total = 0
    prefix_total = 0
    partition_total = 0
    global_partition_choices = 1
    for run, multiplicity in sorted(RUN_CENSUS.items(), key=lambda item: (len(item[0]), item[0])):
        lengths = ordered_block_lengths(run)
        candidate = expected_candidate(run)
        check_witness(run, lengths, candidate)
        vectors = enumerate_vectors(run)
        require(candidate in vectors, "candidate-reachable", repr(run))
        for vector in vectors:
            check_majorization(candidate, vector, len(run))
        partition_count = sum(vectors.values())
        distinct_vector_total += len(vectors)
        prefix_total += len(run) * len(vectors)
        partition_total += partition_count
        global_partition_choices *= partition_count ** multiplicity
        run_records.append({
            "run": list(run),
            "multiplicity_per_orientation": multiplicity,
            "ordered_block_lengths": list(lengths),
            "sorted_candidate": list(candidate),
            "distinct_mass_vectors": len(vectors),
            "chronological_partitions": partition_count,
            "candidate_partition_count": vectors[candidate],
        })
    orientations = {}
    for orientation in ("forward", "backward"):
        events = source[orientation]
        runs = check_census(events, RUN_CENSUS)
        climbs: Counter[int] = Counter()
        centers: Counter[int] = Counter()
        for event in events:
            if event[0] == "climb":
                climbs[event[5]] += 1
            elif event[0] == "center":
                require(len(event) == 5 and type(event[4]) is int and event[4] > 0,
                        "center-shape", repr(event))
                centers[event[4]] += 1
        require(climbs == EXPECTED_CLIMBS, "climb-profile", orientation)
        require(centers == {8: 8}, "center-profile", orientation)
        profile = Counter({rank: count for rank, count in climbs.items() if rank not in (2, 3)})
        profile.update(centers)
        nontrivial_blocks = 0
        consolidated_calls = 0
        for run in runs:
            lengths = ordered_block_lengths(run)
            candidate = check_witness(run, lengths, expected_candidate(run))
            profile.update(candidate)
            nontrivial_blocks += sum(length > 1 for length in lengths)
            consolidated_calls += sum(length for length in lengths if length > 1)
        require(profile == EXPECTED_PROFILE, "completed-profile", orientation)
        require(nontrivial_blocks == 162 and consolidated_calls == 365,
                "consolidation-counts", orientation)
        require(sum(rank * count for rank, count in profile.items()) == 5586,
                "completed-mass", orientation)
        orientations[orientation] = {
            "event_count": len(events),
            "event_kinds": dict(sorted(Counter(event[0] for event in events).items())),
            "climb_profile": string_profile(climbs),
            "center_profile": string_profile(centers),
            "run_count": len(runs),
            "eligible_calls": sum(len(run) for run in runs),
            "eligible_mass": sum(sum(run) for run in runs),
            "optimized_profile": string_profile(profile),
            "optimized_children": sum(profile.values()),
            "optimized_mass": sum(rank * count for rank, count in profile.items()),
            "nontrivial_blocks": nontrivial_blocks,
            "consolidated_calls": consolidated_calls,
        }
    return {
        "schema_version": 1,
        "method": "suffix recursion of every sorted block-mass tuple with exact multiplicities",
        "scope": "zero-additional-charge chronological cap-16 relaxation; no physical supplier or new kappa",
        "source_archive": ARCHIVE,
        "source_archive_sha256": ARCHIVE_SHA256,
        "source_member": MEMBER,
        "source_member_sha256": MEMBER_SHA256,
        "cap": CAP,
        "run_type_count": len(run_records),
        "distinct_mass_vectors": distinct_vector_total,
        "sorted_prefix_inequalities": prefix_total,
        "chronological_partitions_across_types": partition_total,
        "chronological_partition_choices_per_orientation": global_partition_choices,
        "suffix_states": enumerate_vectors.cache_info().currsize,
        "run_types": run_records,
        "orientations": orientations,
        "rejecting_controls": controls,
        "positive_controls": ["phase_transparency", "every_ineligible_kind_breaks",
                              "equivalent_block_order", "strict_majorization_example"],
    }


def check_fixed_record(frozen: Any, actual: dict[str, Any]) -> None:
    # JSON types are part of the certificate: true and 1.0 are not integer 1.
    encode = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    require(encode(frozen) == encode(actual), "certificate-mismatch",
            "every frozen field and its JSON type must equal independent replay")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print recomputed record without writing")
    args = parser.parse_args()
    actual = compute_record()
    if args.json:
        print(json.dumps(actual, indent=2, sort_keys=True))
        return
    certificate = HERE / "INDEPENDENT.json"
    require(certificate.is_file(), "certificate-missing", str(certificate))
    frozen = decode_json(certificate.read_bytes())
    check_fixed_record(frozen, actual)
    print("PASS_INDEPENDENT_RANK23_MAJORIZATION "
          f"types={actual['run_type_count']} vectors={actual['distinct_mass_vectors']} "
          f"prefixes={actual['sorted_prefix_inequalities']} "
          f"partitions={actual['chronological_partitions_across_types']} no_new_kappa")


if __name__ == "__main__":
    main()
