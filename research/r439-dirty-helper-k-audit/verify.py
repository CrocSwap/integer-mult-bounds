#!/usr/bin/env python3
"""Independent finite witness for a dirty helper-bit mismatch in the R439 K interface."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def xor_sources(values, sources):
    out = 0
    for source in sources:
        out ^= values[source]
    return out


def replay_gates(values, gates):
    for _, target, sources in gates:
        values[target] ^= xor_sources(values, sources)


def result():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    live = [row for row in manifest["files"] if row["usage"] == "input"]
    need(live, "no live source pins")
    for row in live:
        path = ROOT / row["path"]
        need(path.is_file(), "missing pinned input: " + row["path"])
        need(digest(path.read_bytes()) == row["sha256"], "source hash mismatch: " + row["path"])

    cert_path = ROOT / "research/r439-helper-stars-seed19/CERTIFICATE.json"
    cert = json.loads(cert_path.read_text(encoding="utf-8"))
    packed = (ROOT / "research/r439-helper-stars-seed19/candidate.json.gz").read_bytes()
    word = json.loads(gzip.decompress(packed))
    v, helpers = word["v"], word["R"]
    n = 2 * v + helpers
    need((v, helpers) == (111, 439), "candidate dimensions changed")
    need(cert["helper_edges"] == 221, "helper-star count changed")
    d_gates = word["D"]
    target_index = 1
    target = v + target_index
    edge_index = 0
    read_index = cert["helper_edges"] + 306 + target_index
    restore_index = len(d_gates) - 1
    first = d_gates[edge_index]
    center = first[1]
    leaf = first[2][0]
    need(first == [0, 280, [260]], "first helper-star edge changed")
    need(read_index == 528 and restore_index == 1164, "pinned gate indices changed")
    read = d_gates[read_index]
    restore = d_gates[restore_index]
    need(read[0] == 0 and read[1] == target, "target read gate moved")
    need(center in read[2] and leaf not in read[2], "target source list changed")
    need(restore == first, "center restoration gate changed")

    # The literal K mask XORs source-register labels at every D write to this target.
    literal_k = [0] * v
    for _, d, sources in d_gates:
        if v <= d < 2 * v:
            for source in sources:
                literal_k[d - v] ^= 1 << source

    # Independently replay the raw A/scatter/B map on identity columns.
    raw = [1 << r for r in range(n)]
    replay_gates(raw, word["A"])
    copied = [raw[r] for r in word["ret"]]
    for t, row in enumerate(word["scatter"]):
        for k in row:
            raw[v + t] ^= copied[k]
    replay_gates(raw, word["B"])

    helper_mask = ((1 << helpers) - 1) << (2 * v)
    raw_target = raw[target] & helper_mask
    k_target = literal_k[target_index] & helper_mask
    raw_leaf = (raw_target >> leaf) & 1
    k_leaf = (k_target >> leaf) & 1
    raw_center = (raw_target >> center) & 1
    k_center = (k_target >> center) & 1
    need((raw_leaf, k_leaf) == (1, 0), "dirty leaf coefficient is not a counterexample")
    need((raw_center, k_center) == (1, 1), "center-helper positive control failed")

    # Scalar replay on the dirty basis input records the three relevant cuts.
    dirty = [int(r == leaf) for r in range(n)]
    read_before_center = read_before_target = read_after_target = None
    for i, (_, d, sources) in enumerate(d_gates):
        if i == read_index:
            read_before_center = dirty[center]
            read_before_target = dirty[target]
        dirty[d] ^= xor_sources(dirty, sources)
        if i == read_index:
            read_after_target = dirty[target]
    need(read_before_center == 1, "dirty leaf did not reach the center at the read cut")
    need(read_before_target ^ read_after_target == 1, "the target read did not transfer the dirty leaf")
    need(dirty[center] == 0 and dirty[leaf] == 1, "center was not restored at D exit")

    observed = {
        "status": "PASS_R439_DIRTY_HELPER_K_COUNTEREXAMPLE",
        "source_sha256": digest(packed),
        "dimensions": {"v": v, "helpers": helpers, "registers": n},
        "target_index": target_index,
        "target_register": target,
        "dirty_helper_register": leaf,
        "center_helper_register": center,
        "gate_indices": {
            "helper_edge": edge_index,
            "target_read": read_index,
            "helper_restoration": restore_index,
        },
        "raw_dirty_coefficient": raw_leaf,
        "literal_k_dirty_coefficient": k_leaf,
        "raw_helper_support_size": raw_target.bit_count(),
        "literal_k_helper_support_size": k_target.bit_count(),
        "symmetric_difference_size": (raw_target ^ k_target).bit_count(),
        "center_positive_control_matches": raw_center == k_center == 1,
        "center_has_dirty_value_at_read": read_before_center == 1,
        "target_toggled_at_read": (read_before_target ^ read_after_target) == 1,
        "center_restored_at_d_exit": dirty[center] == 0,
        "no_new_kappa": True,
    }
    return observed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    observed = result()
    receipt = PACKAGE / "RESULT.json"
    if args.write_result:
        receipt.write_text(json.dumps(observed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        need(receipt.is_file(), "missing RESULT.json; run with --write-result once")
        expected = json.loads(receipt.read_text(encoding="utf-8"))
        need(observed == expected, "RESULT.json differs from the replay")
    print("PASS_R439_DIRTY_HELPER_K_COUNTEREXAMPLE target=112 dirty_helper=260 actual=1 literal_K=0 center=280 restored=true")


if __name__ == "__main__":
    main()
