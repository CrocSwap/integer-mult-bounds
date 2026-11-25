#!/usr/bin/env python3
"""Exact one-block coefficient audit and omitted-helper corruption control."""

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
GEOMETRY = ROOT / "research/p112-tetrad-local-decoder/verify.py"
GEOMETRY_SHA256 = "0654723f43e4c8876b76127715909bdb575122d406e4698c2574e234f8ed41f0"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def coefficient_matrix(terms, outputs, inputs):
    result = [[0] * inputs for _ in range(outputs)]
    for d, t in terms:
        need(len(d) == outputs and len(t) == inputs, "term dimension")
        for i, di in enumerate(d):
            if di:
                for j, tj in enumerate(t):
                    if tj:
                        result[i][j] += di * tj
    return result


def load_geometry():
    raw = GEOMETRY.read_bytes()
    need(sha256(raw) == GEOMETRY_SHA256, "pinned predecessor checker changed")
    spec = importlib.util.spec_from_file_location("p112_tetrad_pinned_geometry", GEOMETRY)
    need(spec is not None and spec.loader is not None, "cannot load pinned geometry source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    pins = json.loads((PACKAGE / "REMOTE-PINS.json").read_text(encoding="utf-8"))
    pr = pins["pr3566"]
    mapping = pr["root_to_port"]
    need(len(mapping) == 112 and sorted(mapping) == list(range(112)),
         "PR 3566 map is not a permutation")
    map_hash = sha256(json.dumps(mapping, separators=(",", ":")).encode("ascii"))
    need(map_hash == pr["map_sha256"], "transcribed port map differs from PR receipt digest")

    geom = load_geometry()
    roots, frame = geom.roots_and_frame()
    live = sorted(set(roots) - set(frame))
    need(len(live) == 112, "P112 live root count")
    signs = [[geom.dot(root, f) // 4 for f in frame] for root in live]

    blocks = {}
    for i, row in enumerate(signs):
        coords = tuple(j for j, value in enumerate(row) if value)
        need(len(coords) == 4 and all(row[j] in (-1, 1) for j in coords),
             "tetrad-coordinate row")
        blocks.setdefault(coords, []).append(i)
    need(len(blocks) == 14 and all(len(rows) == 8 for rows in blocks.values()),
         "tetrad partition")

    coords, indices = sorted(blocks.items())[0]
    selected = pr["selected_block"]
    need(list(coords) == selected["frame_coordinate_indices"], "selected tetrad changed")
    need(indices == selected["root_indices"], "selected root block changed")
    mapped = sorted(mapping[i] for i in indices)
    need(mapped == selected["port_indices"] == selected["receipt_group"],
         "first mapped tetrad differs from PR 3566 result")

    terms = []
    index_set = set(indices)
    for coordinate in coords:
        d = [signs[i][coordinate] if i in index_set else 0 for i in range(112)]
        terms.append((d, d[:]))

    gram = [[geom.dot(live[i], live[j]) // 4 for j in range(112)]
            for i in range(112)]
    frame_matrix = [[signs[i][coordinate] for coordinate in coords]
                    for i in indices]
    observed = coefficient_matrix(terms, 112, 112)
    expected = [[0] * 112 for _ in range(112)]
    for i in indices:
        for j in indices:
            expected[i][j] = 2 * gram[i][j]
    need(observed == expected, "one-block coefficient identity")

    inside = sum(observed[i][j] == 2 * gram[i][j]
                 for i in indices for j in indices)
    external_inputs = sum(observed[i][j] == 0
                          for i in indices for j in range(112) if j not in indices)
    external_outputs = sum(observed[i][j] == 0
                           for i in range(112) if i not in indices for j in range(112))
    need((inside, external_inputs, external_outputs) == (64, 832, 11648),
         "formal 112-port coefficient coverage")

    # The original port map has no helper variable. Extend its input by h and
    # inject h into one term: all port coefficients stay unchanged, while the
    # h coefficient becomes that term's nonzero output vector.
    baseline_extended = [(d, t + [0]) for d, t in terms]
    corrupted_extended = [(d[:], t[:] + [0]) for d, t in terms]
    corrupted_extended[0][1][-1] = 1
    baseline = coefficient_matrix(baseline_extended, 112, 113)
    corrupted = coefficient_matrix(corrupted_extended, 112, 113)
    need([row[:112] for row in baseline] == observed,
         "zero-helper extension changed selected-port coefficients")
    need([row[:112] for row in corrupted] == observed,
         "helper corruption changed selected-port projection")
    helper_column = [row[112] for row in corrupted]
    expected_helper_column = corrupted_extended[0][0]
    need(helper_column == expected_helper_column and any(helper_column),
         "corruption control failed to expose helper dependence")

    result = {
        "status": "PASS_P112_TETRAD_DIRTY_COEFFICIENT_AUDIT",
        "base_port_identity": "exact for all 112 formal port inputs",
        "selected_tetrad": {
            "root_indices": indices,
            "port_indices": mapped,
            "frame_coordinate_indices": list(coords),
            "terms": 4,
            "signed_coordinate_matrix": frame_matrix,
            "exact_target_coefficients": [[2 * gram[i][j] for j in indices]
                                           for i in indices],
            "coefficients_checked": 12544,
            "within_block_coefficients": inside,
            "zero_coefficients_from_other_port_inputs": external_inputs,
            "zero_coefficients_to_other_outputs": external_outputs,
        },
        "external_helper_contract": "not represented in the PR 3566 port matrix",
        "corruption_control": {
            "selected_port_projection_unchanged": True,
            "one_appended_helper_coefficient_nonzero": True,
            "nonzero_helper_outputs": sum(value != 0 for value in helper_column),
            "helper_values_quantified": "symbolically, by the full coefficient column",
        },
        "interpretation": "No defect in the port-only identity. Dirty helper independence is an unproved physical interface obligation, as PR 3566 already states.",
        "no_new_kappa": True,
        "no_supplier_claim": True,
    }
    result_path = PACKAGE / "RESULT.json"
    if "--write" in sys.argv:
        result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                               encoding="utf-8")
    else:
        need(result_path.is_file(), "RESULT.json is absent; run verify.py --write once")
        need(json.loads(result_path.read_text(encoding="utf-8")) == result,
             "recomputed result differs from RESULT.json")
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS_P112_TETRAD_DIRTY_COEFFICIENT_AUDIT coefficients=12544 helper_corruption_detected=true no_new_kappa")


if __name__ == "__main__":
    main()
