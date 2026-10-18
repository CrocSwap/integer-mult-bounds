#!/usr/bin/env python3
"""Replay the encoded arithmetic-to-payload boundary and its exact receipt."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def receipt(result):
    rings = result["binary_words"]["rings"]
    return {
        "schema_version": 1,
        "full_result_sha256": sha256(canonical(result).encode()).hexdigest(),
        "ring_moduli": [row["modulus"] for row in rings],
        "ring_pairs": sum(row["pairs"] for row in rings),
        "inverses_and_nonunits": sum(row["inverses_and_nonunits"] for row in rings),
        "division_cases": result["binary_words"]["division"]["division_cases"],
        "carry_borrow_cases": result["binary_words"]["carry"]["carry_borrow_cases"],
        "counter_ranges": result["binary_counters"]["complete_ranges"],
        "source_checkpoints": result["source_checkpoints"],
        "projector_entries": sum(row["projector_entries"] for row in result["matrix_preparation"]),
        "table_entries": sum(row["table_entries"] for row in result["matrix_preparation"]),
        "callbacks": [{key: row[key] for key in ("kind", "variant", "width", "root_size", "weights", "offset")}
                      for row in result["callbacks"]],
        "payload_bits": result["complete_payload_site"]["records"]*16,
        "payload_sha256": result["complete_payload_site"]["payload_sha256"],
        "rejection_controls": sorted(result["rejection_controls"]),
        "large_source_codes": result["large_source_codes"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true", help="emit the complete deterministic result")
    parser.add_argument("--emit-receipt", action="store_true", help="emit the compact receipt without comparison")
    args = parser.parse_args()
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for item in sources["files"]:
        if item["usage"] == "input" and sha256((ROOT / item["path"]).read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("pinned source bytes changed: " + item["path"])
    # Authenticate retained source bytes before importing their reader.
    import checks
    result = checks.run()
    observed = receipt(result)
    if not (args.emit or args.emit_receipt):
        expected = json.loads((HERE / "RESULT.json").read_text())
        if canonical(observed) != canonical(expected):
            raise ValueError("retained exact receipt differs from replay")
        print("PASS_SELECTED_BINARY_CONTROL")
    print(json.dumps(result if args.emit else observed, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
