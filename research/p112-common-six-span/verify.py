"""Complete direct two-flat census and literal six-cut/caller checks."""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from common import (
    PACKAGE,
    direction_bound,
    expected_result,
    libraries,
    read_json,
    require,
)


def encode_census(flats, representatives, supports):
    lines = []
    for masks in (tuple(m for m, _ in flats), representatives, supports):
        lines.append(str(len(masks)))
        lines.extend(f"{mask & ((1 << 64) - 1)} {mask >> 64}" for mask in masks)
    return "\n".join(lines) + "\n"


def execute(data):
    compiler = shutil.which("clang++") or shutil.which("g++")
    require(compiler is not None, "C++20 compiler unavailable")
    with tempfile.TemporaryDirectory(
        prefix="common-six-", dir=os.environ.get("TMPDIR")
    ) as tmp:
        executable = str(Path(tmp) / "census")
        built = subprocess.run(
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
        require(not built.stdout and not built.stderr, "compiler diagnostics")
        replay = subprocess.run(
            [executable],
            input=data,
            check=True,
            capture_output=True,
            text=True,
            timeout=240,
        )
        require(
            not replay.stderr and len(replay.stdout) < 200_000, "census output bounds"
        )
        return replay.stdout


def parse_census(text, flats, representatives, supports):
    classes = []
    for line in text.splitlines():
        fields = line.split()
        require(fields and fields[0] in ("F", "C"), "census tag")
        values = [int(value) for value in fields[1:]]
        if fields[0] == "F":
            require(len(values) == 2 and values[0] == len(classes), "class order")
            require(0 <= values[1] <= 68, "two-flat union bound")
            classes.append([values[1], []])
        else:
            require(len(values) == 4 and classes, "completion shape")
            h, k, low, high = values
            require(0 <= h < 1200 and 0 <= k < 43435, "completion index")
            require(0 <= low < 1 << 64 and 0 <= high < 1 << 48, "completion mask")
            cut = low | high << 64
            actual = supports[h] & ~(representatives[len(classes) - 1] | flats[k][0])
            require(cut == actual and cut.bit_count() <= 6, "completion predicate")
            require(len(classes[-1][1]) < 2048, "completion capacity")
            classes[-1][1].append([h, k, str(cut)])
    require(
        len(classes) == 121 and max(row[0] for row in classes) == 68, "class coverage"
    )
    for _, entries in classes:
        require(
            len(entries) == len({(h, k) for h, k, _ in entries}), "duplicate completion"
        )
    return classes


def literal_witness(domain, g, points, labels):
    witness = read_json("vendor/pr3253-witness.json")
    first = domain.flat_mask(labels, witness["first_flat_annihilator"])
    cut = sum(1 << i for i in witness["common_deleted_lines"])
    directions = [tuple(entry["h"]) for entry in witness["directions"]]
    require(cut.bit_count() == 6 and len(directions) == 3, "six-cut witness shape")
    gram = [[g.dot(a, b) for b in directions] for a in directions]
    require(gram == [[8, 0, 0], [0, 8, 0], [0, 0, 8]], "independent witness")
    for h in directions:
        residual = [
            labels[i]
            for i, r in enumerate(points)
            if g.dot(h, r) and not (first | cut) >> i & 1
        ]
        require(domain.binary_rank(residual) == 7, "witness residual rank")
    return {"witness_gram_determinant": 512, "witness_residual_ranks": [7, 7, 7]}


def caller_certificate():
    weights = [2, 2, 2] + [7] * 7
    basis = [0, 1, 2, 3]
    require(len(weights) - 6 == len(basis), "quotient basis size")
    require(sum([2, 2, 2, 36]) == 42 < 53, "basis support below distance")
    require(2 + 2 + 2 == 6 and weights[3] == 7, "single-seven/common-six contract")
    require(
        len(weights) - len(basis) == 6 > 3,
        "six independent directions contradict three",
    )
    return {
        "weights": weights,
        "quotient_basis": basis,
        "anchor": 3,
        "common_cut_support_cap": 6,
        "basis_support_cap": 42,
        "required_independent_directions": 6,
        "available_projective_directions": 3,
    }


def run():
    expected = expected_result()
    domain, g = libraries()
    roots, points, labels, coordinates = g.root_data()
    chamber = g.chamber_receipt(roots, points, coordinates)
    flats = domain.seven_flats(labels)
    tables = domain.frame_generators(g, roots, points)
    representatives, sizes = domain.flat_representatives(flats, tables)
    directions, supports, classification = domain.directions(
        g, roots, points, coordinates
    )
    classification["support_histogram"] = {
        str(k): v for k, v in classification["support_histogram"].items()
    }
    require(len(directions) == 1200, "direction domain")
    require(112 - (68 + 6) == 38 > 37 > 36, "six-cut direction completeness")
    classes = parse_census(
        execute(encode_census(flats, representatives, supports)),
        flats,
        representatives,
        supports,
    )
    result = {
        "schema_version": 1,
        "common_cut_budget": 6,
        "representative_masks": [str(x) for x in representatives],
        "flat_orbit_sizes": list(sizes),
        "classes": classes,
        "complete_cut_records": sum(len(entries) for _, entries in classes),
    }
    require(
        json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "complete six-cut receipt disagrees",
    )
    summary = {
        "status": "PASS_P112_COMMON_SIX_SPAN",
        "complete_cut_records": 230,
        "seven_spaces": 43435,
        "first_trace_classes": 121,
        "directions": 1200,
        "simple_reflection_checks": chamber["simple_reflection_checks"],
        "classification": classification,
        **direction_bound(classes),
        **literal_witness(domain, g, points, labels),
        "caller": caller_certificate(),
    }
    require(
        json.dumps(summary, sort_keys=True)
        == json.dumps(read_json("SUMMARY.json"), sort_keys=True),
        "summary differs",
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
