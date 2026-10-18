#!/usr/bin/env python3
"""Source-authenticated bounded replay of the complete residual interface."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE / "vendor"))
sys.path.insert(0, str(HERE))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def receipt(suite, result):
    out = {"full_result_sha256": sha256(canonical(result).encode()).hexdigest()}
    if suite == "source":
        out.update({"selected_cases": len(result["selected"]),
                    "address_columns": sum(row["address_columns"] for row in result["selected"]),
                    "selected_child_invocations": sum(row["events"]["enter"] for row in result["selected"]),
                    "serialized_children": len(result["serialized_children"]),
                    "shared_low_callbacks": result["shared_low_callbacks"],
                    "complete_bit_traces": result["complete_bit_traces"],
                    "fallback_packet": result["fallback_packet"]})
    elif suite == "packet":
        out["result"] = result
    else:
        out.update({"wrong_endpoint_controls": sorted(result["wrong_endpoint_controls"]),
                    "source_rejections": sorted(result["source_rejections"]),
                    "geometry_rejections": sorted(result["geometry_rejections"]),
                    "cardinalities": result["cardinalities"]})
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=("source", "packet", "controls"), required=True)
    parser.add_argument("--emit", action="store_true", help="emit the complete deterministic result")
    parser.add_argument("--emit-receipt", action="store_true", help="emit the compact receipt without comparison")
    args = parser.parse_args()
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for item in sources["files"]:
        if item["usage"] == "input" and sha256((ROOT/item["path"]).read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("pinned main input changed: " + item["path"])
    for item in sources["vendor_files"]:
        if item["unchanged"] and sha256((HERE/"vendor"/item["name"]).read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("unchanged vendor source changed: " + item["name"])
    import checks
    if args.suite == "source":
        result = checks.run_source()
    elif args.suite == "packet":
        import check_packet
        result = check_packet.complete_cube()
    else:
        import control_checks
        result = control_checks.run()
    observed = receipt(args.suite, result)
    if not (args.emit or args.emit_receipt):
        expected = json.loads((HERE/"RESULT.json").read_text())[args.suite]
        if canonical(observed) != canonical(expected):
            raise ValueError("retained exact receipt differs: " + args.suite)
        print("PASS_SELECTED_COMPLETE_RESIDUAL " + args.suite)
    print(json.dumps(result if args.emit else observed, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
