#!/usr/bin/env python3
"""Read-only, exact replay for the scoped QQ16 shear transcript floor.

Apache-2.0. Prepared with substantial OpenAI Codex assistance.
No predecessor checker is imported, and no native supplier replay is claimed.
"""

import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
MANIFEST = "research/community-frontier1094-audit/SELECTED-SOURCE.json"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=unique_object)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    # Unlike Python dict equality, JSON equality distinguishes true from 1.
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def compare_receipt(expected, actual):
    need(canonical(expected) == canonical(actual),
         "RESULT.json differs from deterministic replay")


def verify_sources(root=ROOT, package=HERE):
    sources = read_json(package / "SOURCES.json")
    declaration = read_json(package / "VERIFY.json")
    need(sources["base_commit"] == BASE, "scientific base changed")
    paths = [entry["path"] for entry in sources["files"]]
    need(len(paths) == len(set(paths)), "duplicate source path")
    inputs = {}
    for entry in sources["files"]:
        path = PurePosixPath(entry["path"])
        need(not path.is_absolute() and ".." not in path.parts and
             str(path) == entry["path"], "noncanonical source path")
        need(entry["usage"] in ("input", "provenance"), "unknown source usage")
        if entry["usage"] == "provenance":
            continue  # The repository package launcher checks historical Git provenance.
        raw = (root / path).read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
        need(sha == entry["sha256"], "source SHA256 mismatch: " + str(path))
        need(blob == entry["git_blob"], "source Git blob mismatch: " + str(path))
        inputs[str(path)] = sha
    need(sorted(declaration["inputs"]) == sorted(inputs),
         "VERIFY.json inputs differ from pinned mathematical inputs")
    selected = read_json(root / MANIFEST)["files"]
    bound = [
        "research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json",
        "research/direct-delivery504-global/inputs/data-base/work/complex-nine-native/DATA-PHASES.json",
        "research/gauge44-slots-t16/construction/leaver/cgx_leaver.py",
        "research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2/code/hpe_audit_and_transport.py",
    ]
    for path in bound:
        need(selected[path] == inputs[path], "selected-manifest binding failed: " + path)
    return {"live_input_sha256": inputs, "selected_manifest_members_checked": bound,
            "full_selected_inventory_replay": "NOT RUN"}


def module(name):
    spec = importlib.util.spec_from_file_location("qq16_shear_" + name, HERE / (name + ".py"))
    need(spec is not None and spec.loader is not None, "cannot load checker: " + name)
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


def compute():
    sources = verify_sources()
    moments = module("source_moments").run(ROOT)
    algebra = module("algebra").verify()
    tail = module("tail").verify(ROOT)
    rank = Fraction(moments["trace_certificate"]["rank_lower_bound_per_owner"])
    floor = rank - 8
    need(floor == Fraction(77, 5), "joint selected capacity bound")
    need(floor - 8 == Fraction(37, 5), "one-query deficit")
    need(floor - 15 == Fraction(2, 5), "fifteen-coordinate deficit")
    checked_files = ["PROOF.md", "SOURCES.json", "verify.py", "source_moments.py",
                     "algebra.py", "tail.py", "test_verify.py"]
    return {
        "schema_version": 1,
        "status": "PASS_SCOPED_QQ16_SHEAR_TRANSCRIPT_FLOOR",
        "base_commit": BASE,
        "arithmetic": "exact integers and fractions; no assertion-dependent acceptance",
        "package_sha256": {name: digest(HERE / name) for name in checked_files},
        "sources": sources,
        "source_moments": moments,
        "ordered_algebra_fixtures": algebra,
        "retained_tail": tail,
        "rank_consequences": {
            "triple_query_rank_per_owner_at_least": str(rank),
            "joint_selected_deficit_before_counted_record_per_owner_at_least": str(floor),
            "one_eight_coordinate_record_deficit_per_owner_at_least": str(floor - 8),
            "fifteen_coordinate_record_deficit_per_owner_at_least": str(floor - 15),
            "necessary_uniform_scalar_records_per_owner": 16,
            "integer_rounding": "ceil(77*N/5)-d for total record rank d",
            "sufficiency": "NOT CLAIMED",
        },
        "scope": "Written conditional regular-cover proof plus finite source and algebra checks; no complete native packet, supplier, tariff or kappa claim",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-result", type=Path, metavar="NEW_PATH",
                        help="explicitly write a new receipt; never overwrite")
    args = parser.parse_args()
    result = compute()
    if args.emit_result:
        with args.emit_result.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, sort_keys=True, indent=2) + "\n")
        print("WROTE_SCOPED_QQ16_RECEIPT", args.emit_result)
    else:
        compare_receipt(read_json(HERE / "RESULT.json"), result)
        print(result["status"])


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print("FAIL_QQ16_SHEAR:", error, file=sys.stderr)
        raise SystemExit(1) from error
