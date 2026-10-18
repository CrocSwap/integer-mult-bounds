#!/usr/bin/env python3
"""Code-disjoint local matrix replay of the pinned R439 frame-509 splice."""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
PRIOR = "inputs/PR973-CANDIDATE.json"
CANDIDATE = "inputs/PR1221-CANDIDATE.json"
WIRES = [17, 22, 33, 38, 50, 60, 67, 77, 87, 92, 468]
FRAME = 509
SLICE = (283, 314)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def strict_pairs(items):
    out = {}
    for key, value in items:
        need(key not in out, "duplicate JSON key: " + key)
        out[key] = value
    return out


def load_json(path: Path):
    return json.loads(path.read_text(), object_pairs_hook=strict_pairs,
                      parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))


def load_word(path: Path):
    return json.loads(gzip.decompress(path.read_bytes()), object_pairs_hook=strict_pairs,
                      parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def verify_source_pins():
    manifest = load_json(HERE / "SOURCES.json")
    need(manifest["base_commit"] == "bce54fb3f895cbe5cd4c0eb477c3afeed100190f", "base commit pin")
    for rel, expected in manifest["files"].items():
        raw = (ROOT / rel).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == expected["sha256"], "source SHA-256: " + rel)
        need(git_blob(raw) == expected["git_blob"], "source Git blob: " + rel)
    return manifest


def local_map(gates, wires, characteristic_two: bool):
    """Replay CNOT-style row additions on the declared 11 local coordinates."""
    index = {wire: i for i, wire in enumerate(wires)}
    n = len(wires)
    if characteristic_two:
        rows = [1 << i for i in range(n)]
        for gate in gates:
            need(type(gate) is list and len(gate) == 3, "gate shape")
            frame, dst, srcs = gate
            need(frame == FRAME and len(srcs) == 1, "gate frame/source shape")
            src = srcs[0]
            need(dst in index and src in index and dst != src, "gate outside local coordinates")
            rows[index[dst]] ^= rows[index[src]]
        return tuple(rows)

    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    for gate in gates:
        need(type(gate) is list and len(gate) == 3, "gate shape")
        frame, dst, srcs = gate
        need(frame == FRAME and len(srcs) == 1, "gate frame/source shape")
        src = srcs[0]
        need(dst in index and src in index and dst != src, "gate outside local coordinates")
        target, source = rows[index[dst]], rows[index[src]]
        rows[index[dst]] = [a + b for a, b in zip(target, source)]
    return tuple(tuple(row) for row in rows)


def rebuild_cleanup(word):
    v = word["v"]
    word["C"] = [[1, dst, list(srcs)] for _, dst, srcs in
                  reversed(word["A"] + word["B"])
                  if not v <= dst < 2 * v]
    return word


def splice(base, gates):
    word = copy.deepcopy(base)
    start, end = SLICE
    need(len(word["B"][start:end]) == 31, "selected frame-509 source slice length")
    need(all(g[0] == FRAME for g in word["B"][start:end]), "selected source frame")
    word["B"][start:end] = copy.deepcopy(gates)
    return rebuild_cleanup(word)


def frame_paths(word):
    paths = [[frame] for frame in word["start"]]
    for phase in "DABC":
        for frame, dst, srcs in word[phase]:
            for register in [dst, *srcs]:
                if paths[register][-1] != frame:
                    paths[register].append(frame)
    for register, frame in enumerate(word["final"]):
        if paths[register][-1] != frame:
            paths[register].append(frame)
    return paths


def add_count(word):
    phase_adds = sum(len(srcs) for phase in "DABC" for _, _, srcs in word[phase])
    scatter_adds = sum(len(readers) for readers in word["scatter"])
    return phase_adds + scatter_adds


def audit():
    manifest = verify_source_pins()
    prior = load_json(HERE / PRIOR)
    candidate = load_json(HERE / CANDIDATE)
    for recipe in (prior, candidate):
        need(recipe["frame"] == FRAME and recipe["slice"] == list(SLICE), "recipe frame/slice")
        need(recipe["registers"] == WIRES, "recipe registers")
        need(all(g[0] == FRAME and g[1] in WIRES and g[2][0] in WIRES
                 for g in recipe["gates"]), "recipe gate domain")
    need(prior["format"] == "r439-frame509-seed08/1" and len(prior["gates"]) == 21,
         "pinned PR973 recipe")
    need(candidate["format"] == "r439-b509-boolean/1" and len(candidate["gates"]) == 20,
         "pinned PR1221 recipe")
    need(prior["source_sha256"] == manifest["files"][BASE_WORD]["sha256"], "predecessor source binding")

    old_f2 = local_map(prior["gates"], WIRES, True)
    new_f2 = local_map(candidate["gates"], WIRES, True)
    need(old_f2 == new_f2, "local GF(2) maps differ")
    old_z = local_map(prior["gates"], WIRES, False)
    new_z = local_map(candidate["gates"], WIRES, False)
    delta = []
    for row, (old_row, new_row) in enumerate(zip(old_z, new_z)):
        for col, (old_value, new_value) in enumerate(zip(old_row, new_row)):
            if old_value != new_value:
                delta.append({"destination": WIRES[row], "source": WIRES[col],
                              "prior_minus_candidate": old_value - new_value})
    expected_delta = [{"destination": 468, "source": 33, "prior_minus_candidate": 2}]
    need(delta == expected_delta, "integer local map difference")

    base = load_word(ROOT / BASE_WORD)
    prior_word = splice(base, prior["gates"])
    candidate_word = splice(base, candidate["gates"])
    for word in (prior_word, candidate_word):
        for key in base:
            if key not in ("B", "C"):
                need(word[key] == base[key], "non-splice field changed: " + key)
    paths = frame_paths(base)
    need(len(paths) == 661 and frame_paths(prior_word) == paths
         and frame_paths(candidate_word) == paths, "ordered frame paths changed")
    invoices = [add_count(word) for word in (base, prior_word, candidate_word)]
    need(invoices == [24305, 24285, 24283], "whole-word ADD invoice")

    return {
        "status": "PASS_R439_B509_MATRIX_AUDIT",
        "base_commit": manifest["base_commit"],
        "candidate_pr": manifest["candidate_pr"],
        "candidate_head": manifest["candidate_head"],
        "predecessor_pr": manifest["predecessor_pr"],
        "predecessor_head": manifest["predecessor_head"],
        "local_registers": WIRES,
        "local_adds": {"predecessor": len(prior["gates"]), "candidate": len(candidate["gates"])},
        "local_f2_basis_columns_equal": len(WIRES),
        "integer_delta_prior_minus_candidate": delta,
        "whole_word_ADD_invoice": {"selected": invoices[0], "predecessor": invoices[1],
                                   "candidate": invoices[2]},
        "ordered_frame_paths_equal": len(paths),
        "non_splice_fields_unchanged": True,
        "new_kappa_claimed": False
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = audit()
    receipt = HERE / "RESULT.json"
    if args.write_result:
        receipt.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    else:
        need(receipt.is_file() and load_json(receipt) == result, "result receipt mismatch")
    print("PASS_R439_B509_MATRIX_AUDIT local_f2_inputs=11 integer_delta=2*e468e33 "
          "frame_paths=661 ADDs=24305/24285/24283 no_new_kappa")


if __name__ == "__main__":
    main()
