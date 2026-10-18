#!/usr/bin/env python3
"""Certify the fixed-space common-deletion span theorem using exact arithmetic."""

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path

from geometry import dot, echelon, label, normal, orthogonality_systems, require, roots

PACKAGE = Path(__file__).resolve().parent


def binary_rank(values: list[int]) -> int:
    assert len(values) <= 120 and all(0 <= x < 512 for x in values)
    basis = [0] * 9
    for value in values:
        for bit in range(8, -1, -1):
            if not value >> bit & 1:
                continue
            if basis[bit]:
                value ^= basis[bit]
            else:
                basis[bit] = value
                break
    return sum(bool(x) for x in basis)


def binary_span(basis: list[int]) -> set[int]:
    assert len(basis) <= 120 and all(0 <= x < 512 for x in basis)
    result = {0}
    for value in basis:
        result |= {x ^ value for x in result}
    assert len(result) <= 512
    return result


def bounded_bytes(path: Path) -> bytes:
    with path.open("rb") as stream:
        raw = stream.read(1024 * 1024 + 1)
    require(len(raw) <= 1024 * 1024, "JSON exceeds one MiB")
    return raw


def read_json(path: Path) -> dict:
    value = json.loads(bounded_bytes(path))
    require(isinstance(value, dict), "JSON must be an object")
    return value


def fixture_geometry(fixture: dict) -> tuple[tuple, list[int], int, int]:
    lines = roots()
    require(fixture.get("schema") == "p112-common-deletion/v1", "wrong fixture schema")
    frame = fixture.get("omitted_frame")
    require(isinstance(frame, list) and len(frame) == 8, "frame needs eight roots")
    require(
        all(isinstance(row, list) and len(row) == 8 for row in frame), "bad root shape"
    )
    require(all(type(x) is int for row in frame for x in row), "root is not integral")
    frame = {tuple(row) for row in frame}
    require(len(frame) == 8 and frame <= set(lines), "invalid frame roots")
    require(
        all(dot(a, b) == 0 for a, b in combinations(frame, 2)), "frame not orthogonal"
    )
    live = sum(1 << i for i, row in enumerate(lines) if row not in frame)
    labels = [label(row) for row in lines]
    require(len(set(labels)) == 120, "root labels collide")
    covered = 0
    sizes = []
    for key in ("V1_basis", "V2_basis"):
        basis = fixture.get(key)
        require(isinstance(basis, list) and len(basis) == 6, "basis needs six entries")
        require(
            all(type(x) is int and 0 < x < 512 for x in basis), "invalid basis entry"
        )
        require(binary_rank(basis) == 6, "basis not independent")
        span = binary_span(basis)
        part = sum(1 << i for i, x in enumerate(labels) if x in span) & live
        covered |= part
        sizes.append(part.bit_count())
    require(sizes == [20, 16] and covered.bit_count() == 32, "fixed spaces changed")
    return lines, labels, live, covered


def character_masks(labels: list[int], live: int) -> list[int]:
    assert len(labels) == 120 and 0 <= live < 1 << 120
    return [
        sum(1 << i for i, x in enumerate(labels) if (x & c).bit_count() % 2) & live
        for c in range(512)
    ]


def seven_flat_cap(characters: list[int], live: int) -> dict:
    assert len(characters) == 512
    histogram = {}
    count = 0
    for a, b in combinations(range(1, 512), 2):
        if b >= a ^ b:
            continue
        size = (live & ~(characters[a] | characters[b])).bit_count()
        histogram[size] = histogram.get(size, 0) + 1
        count += 1
    require(count == 43435, "incomplete codimension-two flat enumeration")
    require(max(histogram) == 36, "rank-seven label cardinality cap changed")
    return {"flats": count, "maximum_lines": max(histogram)}


def deletion_cuts(residual: int, rank: int, characters: list[int]) -> list[int]:
    """All inclusion-minimal cuts of size at most four leaving rank at most seven."""
    assert 0 <= rank <= 9 and len(characters) == 512
    if rank <= 7:
        return [0]
    small = sorted(
        {c & residual for c in characters if 0 < (c & residual).bit_count() <= 4}
    )
    if rank == 8:
        candidates = small
    else:
        candidates = sorted(
            {a | b for a, b in combinations(small, 2) if (a | b).bit_count() <= 4}
        )
    minimal = []
    for cut in sorted(candidates, key=lambda x: (x.bit_count(), x)):
        if not any(old & ~cut == 0 for old in minimal):
            minimal.append(cut)
    require(
        len(minimal) <= 511 * 511, "cut inventory exceeded finite character-pair bound"
    )
    return minimal


def qualified_directions(
    lines: tuple, labels: list[int], live: int, covered: int
) -> tuple:
    characters = character_masks(labels, live)
    cap = seven_flat_cap(characters, live)
    systems, orbits = orthogonality_systems(lines, live)
    qualified = []
    rank_histogram = {}
    for orthogonal in systems:
        residual = live & ~(orthogonal | covered)
        rank = binary_rank([x for i, x in enumerate(labels) if residual >> i & 1])
        rank_histogram[rank] = rank_histogram.get(rank, 0) + 1
        cuts = deletion_cuts(residual, rank, characters)
        if cuts:
            qualified.append(
                {"vector": normal(lines, orthogonal), "cuts": cuts, "rank": rank}
            )
    require(len(qualified) <= 32, "qualified-direction inventory exceeded capacity")
    qualified.sort(key=lambda row: row["vector"])
    return qualified, {
        "seven_flat_cap": cap,
        "parabolic_orbits": orbits,
        "orthogonality_systems_with_at_least_40_live_roots": len(systems),
        "residual_rank_histogram": {
            str(k): rank_histogram[k] for k in sorted(rank_histogram)
        },
    }


def common_states(qualified: list[dict]) -> list[int]:
    assert len(qualified) <= 32
    states = {0}
    for row in qualified:
        additions = {
            state | cut
            for state in states
            for cut in row["cuts"]
            if (state | cut).bit_count() <= 4
        }
        require(
            len(states | additions) <= 65536, "common-state inventory exceeded capacity"
        )
        states |= additions
    return sorted(states, key=lambda state: (state.bit_count(), state))


def report_states(qualified: list[dict], labels: list[int]) -> list[dict]:
    reports = []
    for state in common_states(qualified):
        indices = [
            j
            for j, row in enumerate(qualified)
            if any(cut & ~state == 0 for cut in row["cuts"])
        ]
        rank = len(echelon([qualified[j]["vector"] for j in indices]))
        reports.append(
            {
                "deleted_labels": sorted(
                    x for i, x in enumerate(labels) if state >> i & 1
                ),
                "direction_indices": indices,
                "rational_span": rank,
            }
        )
    return reports


def prove(fixture: dict) -> dict:
    lines, labels, live, covered = fixture_geometry(fixture)
    qualified, geometry = qualified_directions(lines, labels, live, covered)
    states = report_states(qualified, labels)
    separate = len(echelon([row["vector"] for row in qualified]))
    common = max(row["rational_span"] for row in states)
    require(
        len(qualified) == 10 and len(states) == 6, "fixed-space classification changed"
    )
    require(separate == 5 and common == 3, "sharp span claims failed")
    directions = [
        {
            "vector": list(row["vector"]),
            "rank_before": row["rank"],
            "minimal_deletions": [
                sorted(x for i, x in enumerate(labels) if cut >> i & 1)
                for cut in row["cuts"]
            ],
        }
        for row in qualified
    ]
    return {
        "status": "PASS_P112_COMMON_DELETION_SPAN",
        "geometry": geometry,
        "covered_lines": covered.bit_count(),
        "shared_deletion_budget": 4,
        "all_real_direction_count": len(directions),
        "separate_deletion_span": separate,
        "maximum_common_deletion_span": common,
        "directions": directions,
        "complete_common_states": states,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, help="write a receipt outside the checkout"
    )
    args = parser.parse_args()
    fixture_path = PACKAGE / "FIXTURE.json"
    source = read_json(PACKAGE / "SOURCES.json")
    require(
        hashlib.sha256(bounded_bytes(fixture_path)).hexdigest()
        == source["fixture_sha256"],
        "fixture pin mismatch",
    )
    report = prove(read_json(fixture_path))
    expected = read_json(PACKAGE / "RESULT.json")
    require(report == expected, "recomputed result differs from the committed receipt")
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        "PASS_P112_COMMON_DELETION_SPAN real_directions=10 "
        "separate_span=5 common_span=3 states=6"
    )


if __name__ == "__main__":
    main()
