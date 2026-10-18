"""Independently replay PR1363's R420 block-4 Boolean map on all 12-bit inputs."""

import gzip
import json
from pathlib import Path
import re
import sys

from importlib.util import module_from_spec, spec_from_file_location


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
PR1363 = "2f80560e741f8255fd8023799bdfedae17a9bc12"
SEED = 0

_spec = spec_from_file_location("seed00_independent", HERE / "independent.py")
if _spec is None or _spec.loader is None:
    raise RuntimeError("could not load independent.py")
independent = module_from_spec(_spec)
_spec.loader.exec_module(independent)


def need(value, message):
    independent.need(value, message)


def load_json(path):
    return json.loads(path.read_bytes())


def compute():
    deps = load_json(HERE / "DEPENDENCIES.json")
    need(deps["schema_version"] == 1 and deps["base_commit"] == BASE,
         "base and dependency schema")
    need(deps["pr1363_head"] == PR1363, "exact predecessor head")
    for rel, expected_sha in deps["vendored_sha256"].items():
        raw = (HERE / rel).read_bytes()
        need(independent.digest(raw) == expected_sha, "vendored SHA-256 " + rel)
        blob_id = __import__("hashlib").sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob_id == deps["source_git_blobs"][rel], "vendored Git blob " + rel)

    source_pins = load_json(HERE / "SOURCES.json")
    selected = load_json(ROOT / "certificates/selected-result.json")
    need(source_pins["selected_result"]["kappa"] == selected["kappa"]
         == "836330098538459/500000000000000000", "selected conditional result unchanged")
    for row in source_pins["selected_result"]["files"]:
        need(independent.digest((ROOT / row["path"]).read_bytes()) == row["sha256"],
             "selected evidence pin " + row["path"])

    base_raw = (ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz").read_bytes()
    base_word = json.loads(gzip.decompress(base_raw))
    predecessor = HERE / "vendor/pr1363"
    cert_raw = (predecessor / "search-certificate.json").read_bytes()
    candidate_raw = (predecessor / "candidate-word.json.gz").read_bytes()
    cert = json.loads(cert_raw)
    candidate_word = json.loads(gzip.decompress(candidate_raw))
    need(cert["base_commit"] == BASE and cert["assignment_seed"] == 4,
         "pinned PR1363 source receipt")
    need(independent.digest(independent.canonical(base_word))
         == cert["baseline"]["canonical_word_sha256"], "source baseline full-word hash")
    need(independent.digest(independent.canonical(candidate_word))
         == cert["candidate"]["canonical_word_sha256"], "candidate full-word canonical hash")

    obj = cert["object"]
    wires = obj["input_wires"]
    n = 12
    start, stop = obj["baseline_B_interval"]
    candidate_stop = start + obj["candidate_operations"]
    need(obj["block_index"] == 4 and obj["frame"] == 546
         and [start, stop] == [313, 371] and stop - start == 58
         and candidate_stop == 364 and obj["candidate_operations"] == 51,
         "exact phase-B frame and slices")
    need(len(wires) == n and len(set(wires)) == n, "12 unique source wires")
    need([len(base_word["B"]), len(candidate_word["B"])] == [837, 830],
         "source and candidate carry their pinned full B schedules")

    baseline_events = base_word["B"][start:stop]
    candidate_events = candidate_word["B"][start:candidate_stop]
    baseline_ops = independent.local_operations(baseline_events, wires, obj["frame"])
    candidate_ops = independent.local_operations(candidate_events, wires, obj["frame"])
    need(len(baseline_ops) == 58 and len(candidate_ops) == 51,
         "literal block gate counts")

    baseline_perm = cert["baseline"]["output_to_wire"]
    candidate_perm = cert["candidate"]["output_to_wire"]
    need(sorted(baseline_perm) == list(range(n)) and sorted(candidate_perm) == list(range(n)),
         "baseline and candidate output placements are permutations")
    source_matrix = independent.linear_rows(baseline_ops, n)
    expected_rows = [source_matrix[wire] for wire in baseline_perm]
    need(expected_rows == cert["baseline"]["target_rows"],
         "baseline certificate rows derived from the frozen source block")
    need(cert["candidate"]["target_rows"] == expected_rows,
         "candidate and source use the same logical target map")
    candidate_matrix = independent.linear_rows(candidate_ops, n)
    need([candidate_matrix[wire] for wire in candidate_perm] == expected_rows,
         "candidate linear rows equal the source-derived target")
    need(independent.positive_cost(baseline_ops, n) == cert["baseline"]["positive_cost"],
         "baseline literal positive-norm control")
    need(independent.positive_cost(candidate_ops, n) == cert["candidate"]["positive_cost"],
         "candidate literal positive-norm replay")

    baseline_table = independent.truth_table(baseline_ops, baseline_perm, expected_rows, n)
    candidate_table = independent.truth_table(candidate_ops, candidate_perm, expected_rows, n)
    need(baseline_table["first_mismatch"] is None and baseline_table["checked_inputs"] == 4096,
         "baseline exhausts all Boolean inputs")
    need(candidate_table["first_mismatch"] is None and candidate_table["checked_inputs"] == 4096,
         "candidate exhausts all Boolean inputs")

    omitted_table = independent.truth_table(candidate_ops[1:], candidate_perm, expected_rows, n)
    reversed_ops = list(candidate_ops)
    first_target, first_source = reversed_ops[0]
    reversed_ops[0] = (first_source, first_target)
    reversed_table = independent.truth_table(reversed_ops, candidate_perm, expected_rows, n)
    need(omitted_table["first_mismatch"] is not None, "omitted-gate negative control rejects")
    need(reversed_table["first_mismatch"] is not None, "reversed-gate negative control rejects")

    return {
        "status": "PASS_R420_BLOCK4_BOOLEAN_AUDIT",
        "assignment_seed": SEED,
        "track": "bit supplier",
        "base_commit": BASE,
        "selected_kappa": selected["kappa"],
        "predecessor": {"pr": 1363, "head": PR1363, "original_seed": cert["assignment_seed"]},
        "object": {"frame": obj["frame"], "baseline_slice": [start, stop],
                   "candidate_slice": [start, candidate_stop], "input_wires": wires,
                   "boolean_input_count": 1 << n},
        "source_target_rows": expected_rows,
        "baseline": {"gates": len(baseline_ops), "all_inputs": baseline_table,
                     "positive_norm_peak": cert["baseline"]["positive_cost"]},
        "candidate": {"gates": len(candidate_ops), "all_inputs": candidate_table,
                      "positive_norm_peak": cert["candidate"]["positive_cost"]},
        "negative_controls": {
            "omitted_first_gate": {"rejected": True, **omitted_table},
            "reversed_first_gate": {"rejected": True, **reversed_table},
        },
        "scope": "Local Boolean-map audit only; no full-word route, hosting, supplier, or kappa claim.",
    }


def main():
    result = compute()
    path = HERE / "CERTIFICATE.json"
    if "--write" in sys.argv:
        need(not path.exists(), "refuse to overwrite receipt")
        path.write_bytes(independent.canonical(result) + b"\n")
    else:
        need(independent.canonical(result) == independent.canonical(load_json(path)),
             "frozen Boolean audit receipt")
    print(result["status"])
    print("baseline gates", result["baseline"]["gates"], "inputs",
          result["baseline"]["all_inputs"]["checked_inputs"], "source_map exact")
    print("candidate gates", result["candidate"]["gates"], "inputs",
          result["candidate"]["all_inputs"]["checked_inputs"], "source_map exact")
    print("controls omitted_first_gate=rejected reversed_first_gate=rejected")


if __name__ == "__main__":
    main()
