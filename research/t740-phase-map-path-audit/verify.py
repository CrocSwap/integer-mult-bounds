#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent signed-path audit of the exact PR3297 phase-map certificate."""

import argparse
import hashlib
import json
from pathlib import Path

from inverse import certify
from paths import collect, expand
from source import HERE, gates_from_inputs, load_inputs, require


def expected_export(path: Path = HERE / "inputs/PR3297-RESULT.json") -> dict:
    export = json.loads((HERE / "EXPORT.json").read_bytes())
    require(path.stat().st_size <= 100_000 and not path.is_symlink(), "export size/type")
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == export["sha256"], "predecessor export SHA256")
    blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
    require(hashlib.sha1(blob, usedforsecurity=False).hexdigest() == export["git_blob"],
            "predecessor export Git blob")
    return json.loads(raw)


def build() -> dict:
    expected = expected_export()
    data = load_inputs()
    gates, ranks = gates_from_inputs(data)
    streams, peak, final = expand(gates)
    q = data["phases"]["recipes"][0]["q"]
    terms = collect(streams, q)
    require(terms == expected["polynomial_matrix"], "full predecessor matrix mismatch")
    require([[i, rank] for i, rank in enumerate(ranks)] == expected["residual_ranks"],
            "source residual rank mismatch")
    require(expected["sites"] == list(range(20)) and q == 11, "predecessor domain")
    certificate = certify(terms)
    return {"schema_version": 1, "owner": 0, "port": 0, "ambient_bits": 73,
            "primitive_gates": len(gates), "uncancelled_path_peak": peak,
            "uncancelled_final_paths": final, "matrix_terms": len(terms),
            "full_matrix_matches_predecessor": True, "residual_ranks": ranks,
            "inverse_certificate": certificate}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print the freshly computed receipt")
    args = parser.parse_args()
    receipt = build()
    if args.emit:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        require(receipt == json.loads((HERE / "RESULT.json").read_bytes()), "audit receipt mismatch")
        print("PASS_T740_PHASE_PATH_AUDIT paths=1174 terms=72 coordinates=20 unit_divisions=21")


if __name__ == "__main__":
    main()
