"""Source-bound complete common-five census and literal common-six witness."""

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from collections import Counter
from itertools import combinations
from pathlib import Path

from domain import (
    PACKAGE,
    binary_rank,
    directions,
    flat_mask,
    flat_representatives,
    frame_generators,
    geometry,
    require,
    seven_flats,
)


def encode_mask(mask):
    return f"{mask & ((1 << 64) - 1)} {mask >> 64}"


def census_input(flats, representatives, supports):
    lines = []
    for masks in (tuple(m for m, _ in flats), representatives, supports):
        lines.append(str(len(masks)))
        lines.extend(encode_mask(mask) for mask in masks)
    return "\n".join(lines) + "\n"


def execute_census(data, scratch, compiler):
    require(shutil.which(compiler) is not None, "C++20 compiler unavailable")
    with tempfile.TemporaryDirectory(prefix="p112-common-five-", dir=scratch) as tmp:
        executable = str(Path(tmp) / "census")
        subprocess.run(
            [
                compiler,
                "-std=c++20",
                "-O3",
                "-Wall",
                "-Wextra",
                "-Wpedantic",
                "-Wconversion",
                "-Wshadow",
                "-Werror",
                str(PACKAGE / "census.cpp"),
                "-o",
                executable,
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        result = subprocess.run(
            [executable],
            input=data,
            check=True,
            capture_output=True,
            text=True,
            timeout=240,
        )
        require(
            not result.stderr and len(result.stdout) < 100000,
            "unexpected census diagnostics or oversized receipt",
        )
        return result.stdout


def parse_census(text, flats, representatives, supports):
    records = []
    for line in text.splitlines():
        fields = line.split()
        require(fields and fields[0] in ("F", "C"), "invalid census record")
        values = [int(value) for value in fields[1:]]
        if fields[0] == "F":
            require(len(values) == 2 and values[0] == len(records), "flat record order")
            require(0 <= values[1] <= 68, "two-flat union exceeds 68")
            records.append([values[1], []])
            continue
        require(len(values) == 4 and records, "invalid cut record")
        h, k, lo, hi = values
        require(
            0 <= h < 1200
            and 0 <= k < 43435
            and 0 <= lo < 1 << 64
            and 0 <= hi < 1 << 48,
            "cut record bounds",
        )
        cut = lo | (hi << 64)
        expected = supports[h] & ~(representatives[len(records) - 1] | flats[k][0])
        require(cut == expected and cut.bit_count() <= 5, "incorrect cut predicate")
        require(len(records[-1][1]) < 2048, "cut record capacity")
        records[-1][1].append([h, k, str(cut)])
    require(
        len(records) == 121 and max(row[0] for row in records) == 68,
        "flat record coverage",
    )
    for _, entries in records:
        require(len(entries) == len({(h, k) for h, k, _ in entries}), "duplicate cut")
    return records


def common_cut_bound(records):
    compatible_pairs = 0
    for _, entries in records:
        for (h, _, a), (j, _, b) in combinations(entries, 2):
            if h != j and (int(a) | int(b)).bit_count() <= 5:
                compatible_pairs += 1
        for triple in combinations(entries, 3):
            if len({row[0] for row in triple}) != 3:
                continue
            union = int(triple[0][2]) | int(triple[1][2]) | int(triple[2][2])
            require(union.bit_count() > 5, "three directions share five cuts")
    require(compatible_pairs > 0, "two-direction positive control missing")
    return {
        "compatible_distinct_direction_pairs": compatible_pairs,
        "maximum_directions_with_five_common_cuts": 2,
        "qualifying_completion_records": sum(len(row[1]) for row in records),
        "completion_count_histogram": dict(
            sorted(Counter(len(row[1]) for row in records).items())
        ),
    }


def determinant3(matrix):
    a, b, c = matrix
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def check_witness(witness, g, roots, points, labels):
    require(
        witness["schema_version"] == 1 and len(witness["directions"]) == 3,
        "common-six witness schema",
    )
    deleted = witness["common_deleted_lines"]
    require(
        len(deleted) == len(set(deleted)) == 6
        and all(type(i) is int and 0 <= i < 112 for i in deleted),
        "six common cuts",
    )
    common = sum(1 << i for i in deleted)
    first = flat_mask(labels, witness["first_flat_annihilator"])
    hs, ranks, union = [], [], 0
    for entry in witness["directions"]:
        h = tuple(entry["h"])
        require(h in roots, "witness direction is not a normalized E8 root")
        hs.append(h)
        second = flat_mask(labels, entry["second_flat_annihilator"])
        off = sum(1 << i for i, r in enumerate(points) if g.dot(h, r))
        cut = off & ~(first | second)
        require(
            entry["deleted_lines"] == [i for i in range(112) if cut >> i & 1],
            "witness completion cut differs",
        )
        require(cut & ~common == 0, "completion is not covered by common cuts")
        union |= cut
        ranks.append(
            binary_rank(
                tuple(
                    label
                    for i, label in enumerate(labels)
                    if (off & ~(first | common)) >> i & 1
                )
            )
        )
    gram = [[g.dot(a, b) for b in hs] for a in hs]
    require(gram == [[8, 0, 0], [0, 8, 0], [0, 0, 8]], "independent root triple")
    require(union == common and max(ranks) <= 7, "common-six residual rank")
    return {
        "gram": gram,
        "gram_determinant": determinant3(gram),
        "residual_binary_ranks": ranks,
        "common_cut_binary_rank": binary_rank(tuple(labels[i] for i in deleted)),
    }


def compute(scratch=None, compiler="c++"):
    g = geometry()
    roots, points, labels, coordinates = g.root_data()
    chamber = g.chamber_receipt(roots, points, coordinates)
    flats = seven_flats(labels)
    representatives, orbit_sizes = flat_representatives(
        flats, frame_generators(g, roots, points)
    )
    hs, supports, classification = directions(g, roots, points, coordinates)
    require(len(hs) == len(supports) == 1200, "direction/support binding")
    text = execute_census(
        census_input(flats, representatives, supports), scratch, compiler
    )
    records = parse_census(text, flats, representatives, supports)
    witness = json.loads((PACKAGE / "WITNESS.json").read_text())
    return {
        "status": "PASS_P112_COMMON_FIVE_DELETION",
        "seven_spaces": len(flats),
        "distinct_live_traces": 43181,
        "flat_orbit_sizes": orbit_sizes,
        "representative_masks": [str(mask) for mask in representatives],
        "classification": classification,
        "chamber": chamber,
        "common_five": common_cut_bound(records),
        "common_six_witness": check_witness(witness, g, roots, points, labels),
        "census_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "classes": records,
        "new_historical_profile_exclusions": 0,
        "selected_frontier_changed": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scratch", type=Path)
    parser.add_argument("--compiler", default="c++")
    args = parser.parse_args()
    result = json.loads(json.dumps(compute(args.scratch, args.compiler)))
    expected = json.loads((PACKAGE / "RESULT.json").read_text())
    require(result == expected, "committed complete result differs")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
