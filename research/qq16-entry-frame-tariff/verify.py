#!/usr/bin/env python3
"""Exact, per-field terminal frame tariffs. Standard library; no source imports."""

import argparse
from collections import Counter
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
import tarfile


HERE = Path(__file__).resolve().parent
DIM = 17
PORTS = 112
MEMBER = "t16/global/base/work/complex-nine-native/DATA-PHASES.json"
MEMBER_SHA256 = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
INPUTS = (ARCHIVE, "research/joint-query/evidence/BRIDGE-REVIEW.md",
          "research/joint-query/evidence/CONSERVED-QQ16.md")
COORDINATES = tuple(1 << i for i in range(DIM))
EXTERNAL = COORDINATES[9:]
POINTS = (0,) + COORDINATES + tuple(
    COORDINATES[i] ^ COORDINATES[j]
    for i in range(DIM) for j in range(i + 1, DIM)
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bounded(path, limit):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, "input size limit: " + str(path))
    return raw


def source_data(repo):
    """Authenticate before interpreting the bounded archive and endpoint proof."""
    pins = json.loads(read_bounded(HERE / "SOURCES.json", 16384))
    require(len(pins["files"]) <= 8, "source metadata size")
    live = [row for row in pins["files"] if row["usage"] == "input"]
    require(sorted(row["path"] for row in live) == sorted(INPUTS), "live source set")
    for row in live:
        if row["path"] != ARCHIVE:
            raw = read_bounded(repo / row["path"], 2**20)
            require(sha256(raw).hexdigest() == row["sha256"], "live source pin")
    archive_pin = next(row for row in pins["files"] if row["path"] == ARCHIVE)
    raw = read_bounded(repo / ARCHIVE, 20 * 1024 * 1024)
    require(sha256(raw).hexdigest() == archive_pin["sha256"], "archive pin")
    with tarfile.open(fileobj=BytesIO(raw), mode="r:gz") as archive:
        member = archive.getmember(MEMBER)
        require(member.isfile() and member.size < 2**20, "chart member size/type")
        stream = archive.extractfile(member)
        require(stream is not None, "chart member missing")
        with stream:
            charts_raw = stream.read(2**20)
    require(sha256(charts_raw).hexdigest() == MEMBER_SHA256, "chart member pin")
    predecessors = json.loads(read_bounded(HERE / "PREDECESSORS.json", 16384))
    require(predecessors["head"] == "630d557af5088f66b45c447969cee9576600e50b",
            "decoder source head")
    require(len(predecessors["files"]) == 1, "one retained source")
    for row in predecessors["files"]:
        require(row["local_path"] == "sources/PR2540-PROOF.md", "source path")
        raw = read_bounded(HERE / row["local_path"], 2**20)
        require(sha256(raw).hexdigest() == row["sha256"], "decoder source pin")
    proof = raw.decode("utf-8")
    require("original x_p,y_p in the common physical frame F_U1" in proof,
            "decoder endpoint")
    rows = re.findall(r"^\| ([^|]+) \| ([\d,]+) \|$", proof, re.MULTILINE)
    invoice = {label: int(number.replace(",", "")) for label, number in rows}
    charts = json.loads(charts_raw)
    require(charts["m"] == 73 and charts["ports"] == PORTS, "source dimensions")
    require(len(charts["recipes"]) == PORTS, "source recipe count")
    return charts["recipes"], invoice


def parity(value):
    return value.bit_count() % 2


def xor_axes(axes):
    result = 0
    for axis in axes:
        result ^= axis
    return result


def phase(terms, translation, point):
    return (sum(sign * parity(axis & point) for axis, sign in terms)
            + 2 * parity(translation & point)) % 4


def polarization(terms):
    """Rows of B with p(u+v)-p(u)-p(v) = 2 u^T B v, modulo four."""
    rows = [0] * DIM
    for axis, sign in terms:
        require(0 < axis < 2**DIM and sign in (-1, 1), "phase term")
        for i in range(DIM):
            if axis & (1 << i):
                rows[i] ^= axis
    return rows


def binary_rank(rows):
    pivots = [0] * DIM
    for row in rows:
        require(0 <= row < 2**DIM, "binary row range")
        for bit in range(DIM - 1, -1, -1):
            if row & (1 << bit):
                if pivots[bit]:
                    row ^= pivots[bit]
                else:
                    pivots[bit] = row
                    break
    return sum(bool(row) for row in pivots)


def check_adapter(target, axes, translation, rank):
    require(1 <= len(axes) <= DIM and len(axes) == rank, "child rank invoice")
    require(0 <= translation < 2**DIM, "translation range")
    for i, axis in enumerate(axes):
        require(0 < axis < 2**DIM, "axis range")
        for j, other in enumerate(axes):
            require(parity(axis & other) == int(i == j), "orthonormal child axes")
    require(binary_rank(polarization(target)) == rank, "polarization rank bound")
    positive = tuple((axis, 1) for axis in axes)
    for point in POINTS:
        require(phase(target, 0, point) == phase(positive, translation, point),
                "exact phase mismatch")
    return len(POINTS)


def port_adapters(recipe):
    q = recipe["q"]
    require(type(q) is int and 0 < q < 512 and parity(q), "odd local port label")
    child = recipe["idle_children"][0]
    axes = tuple(child["orthogonal_axes"])
    require(child["rank"] == 16 and len(axes) == 16, "source hole rank")
    shift = child["translation_after"]
    require(type(shift) is int and 0 <= shift < 512, "source hole translation")
    # The source's positive hole frame is F_U1 C_q^-1.
    hole = tuple((axis, 1) for axis in COORDINATES) + ((q, -1),)
    check_adapter(hole, axes, shift, 16)
    negative_full = tuple((axis, -1) for axis in COORDINATES)
    negative_external = tuple((axis, -1) for axis in EXTERNAL)
    return {
        "entry_X": (((q, 1),) + negative_full, axes,
                    shift ^ xor_axes(axes)),
        "entry_Y": (negative_full, COORDINATES, xor_axes(COORDINATES)),
        "F0_X": (negative_external, EXTERNAL, xor_axes(EXTERNAL)),
        "F0_Y": (((q, -1),) + negative_external, (q,) + EXTERNAL,
                 q ^ xor_axes(EXTERNAL)),
    }


def wrapper_columns(axes, recipe):
    """Extend the chosen axes to an explicit orthogonal 17-coordinate chart."""
    source_axes = tuple(recipe["idle_children"][0]["orthogonal_axes"])
    candidates = (recipe["q"],) + source_axes
    columns = list(axes)
    for candidate in candidates:
        if all(parity(candidate & axis) == 0 for axis in axes):
            columns.append(candidate)
    require(len(columns) == DIM, "wrapper completion length")
    for i, column in enumerate(columns):
        for j, other in enumerate(columns):
            require(parity(column & other) == int(i == j), "orthogonal wrapper")
    return columns


def compute(recipes, invoice):
    require(sorted(row["port"] for row in recipes) == list(range(PORTS)),
            "complete, nonduplicated source ports")
    histograms = {"entry": Counter(), "F0": Counter()}
    words = []
    evaluations = 0
    for recipe in recipes:
        adapters = port_adapters(recipe)
        for name, (target, axes, translation) in adapters.items():
            rank = len(axes)
            evaluations += check_adapter(target, axes, translation, rank)
            histograms[name.split("_")[0]][rank] += 1
            words.append({"port": recipe["port"], "boundary_field": name,
                          "positive_child_axes": list(axes), "rank": rank,
                          "translation_after": translation,
                          "active_wrapper_columns": wrapper_columns(axes, recipe)})
    entry = histograms["entry"]
    require(entry == {16: 112, 17: 112}, "entry profile")
    require(histograms["F0"] == {8: 112, 9: 112}, "F0 profile")
    require(invoice["Positive rank-one children"] == 224
            and invoice["Positive rank-eight children"] == 16
            and invoice["Native rank mass"] == 352, "source native invoice")
    combined = entry + Counter({1: invoice["Positive rank-one children"],
                                8: invoice["Positive rank-eight children"]})
    return {
        "status": "PASS_QQ16_ENTRY_FRAME_TARIFF",
        "model": "separate single-field convolution kernels and affine payload maps",
        "ports": PORTS, "active_axes": DIM, "payload_dimension": 73,
        "entry_adapter_histogram": dict(sorted(entry.items())),
        "entry_adapter_rank_mass": sum(r * n for r, n in entry.items()),
        "F0_adapter_histogram": dict(sorted(histograms["F0"].items())),
        "F0_adapter_rank_mass": 1904,
        "common_F_L_adapter_histogram": {8: 224},
        "common_F_L_adapter_rank_mass": 1792,
        "decoder_plus_entry_histogram": dict(sorted(combined.items())),
        "decoder_plus_entry_rank_mass": sum(r * n for r, n in combined.items()),
        "adapter_phase_evaluations": evaluations,
        "source_hole_phase_evaluations": PORTS * len(POINTS),
        "adapters": words,
    }


def controls(recipes):
    """Faults whose rank can agree while the required native operator differs."""
    target, axes, shift = port_adapters(recipes[0])["entry_X"]
    cases = (
        (target, axes, shift ^ 1, len(axes), "missing translation bit"),
        (target, axes[:-1], shift, len(axes) - 1, "omitted child axis"),
        (target, axes, shift, 15, "underpriced child"),
        (target, axes[:-1] + (recipes[0]["q"],), shift, 16,
         "equal-rank wrong subspace"),
        (tuple((a, -s) for a, s in target), axes, shift, 16, "inverse sign"),
        (target, axes[:-1] + (axes[0],), shift, 16, "duplicate axis"),
    )
    rejected = []
    for target, axes, shift, rank, label in cases:
        try:
            check_adapter(target, axes, shift, rank)
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError("negative control accepted: " + label)
    # Translation is invisible to B, so rank alone cannot certify the endpoint.
    require(polarization(((1, 1),)) == polarization(((1, -1),)),
            "same-rank sign control")
    require(phase(((1, 1),), 0, 1) != phase(((1, -1),), 0, 1),
            "positive/negative phase distinction")
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=HERE.parents[1])
    parser.add_argument("--write", action="store_true", help="write new RESULT.json only")
    args = parser.parse_args()
    recipes, invoice = source_data(args.repo)
    result = compute(recipes, invoice)
    result["rejected_controls"] = controls(recipes)
    result_path = HERE / "RESULT.json"
    if args.write:
        with result_path.open("x", encoding="utf-8") as stream:
            stream.write(format_result(result))
    else:
        expected = json.loads(read_bounded(result_path, 2**20))
        require(json.loads(json.dumps(result)) == expected, "committed result differs")
    print("PASS_QQ16_ENTRY_FRAME_TARIFF ports=112 entry_mass=3696 F0_mass=1904 "
          "decoder_plus_entry_mass=4048 controls=6 no_new_kappa")


def format_result(result):
    """Keep each literal adapter on one line for a reviewable generated diff."""
    summary = {key: value for key, value in result.items() if key != "adapters"}
    header = json.dumps(summary, indent=2, sort_keys=True)[:-2]
    words = ",\n".join("    " + json.dumps(word, sort_keys=True)
                        for word in result["adapters"])
    return header + ',\n  "adapters": [\n' + words + "\n  ]\n}\n"


if __name__ == "__main__":
    main()
