#!/usr/bin/env python3
"""Rebind a literal stream to the unchanged, hash-pinned PR2139 producer."""
import argparse
import contextlib
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRODUCER_SHA256 = "c948f0d726399b1a4503af3b6468566be270f86229e5d0d29a2b62bf4d4e553a"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def authenticate():
    raw = (HERE / "producer.py").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PRODUCER_SHA256,
         "unchanged PR2139 producer authentication")
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for item in pins["files"]:
        if item["usage"] == "input":
            raw = (ROOT / item["path"]).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == item["sha256"],
                 "source authentication: " + item["path"])


def capture(native):
    """Observe only main's return; never replace an algorithm or its checks."""
    path = HERE / "producer.py"
    spec = importlib.util.spec_from_file_location("p104_precision_producer", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = {}

    def returned(frame, event, unused):
        if event == "return" and frame.f_code is module.main.__code__:
            result.update(frame.f_locals)

    old_argv, old_profile = sys.argv, sys.getprofile()
    sys.argv = [str(path)] + (["--native"] if native else [])
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            sys.setprofile(returned)
            module.main()
    finally:
        sys.setprofile(old_profile)
        sys.argv = old_argv
    report = json.loads(output.getvalue())
    need(report["status"] == "PASS_CANONICAL_P104_DELAYED_SIDE_PROTOTYPE",
         "predecessor endpoint checks")
    need(report["actions"] == 26647 and report["baseline_compensation_adds"] == 7686,
         "complete producer instruction inventory")
    need(all(report["controls"].values()), "predecessor semantic controls")
    if native:
        checked = report["native_new_recipe_check"]
        need(checked == {"status": "PASS_NEW_NATIVE_RECIPES", "distinct_recipes": 241,
                         "paid_occurrences": 421, "global_phase_control": "REJECT"},
             "predecessor new native checks")
    return result


def exported(result):
    compensation = [[t, s, str(q)] for t, s, q in result["compensation"]]
    value = {"schema_version": 1, "total_roles": result["total"],
             "live_ports": result["live"], "frame_bases": result["frame_bases"],
             "initial_frames": result["initial"], "final_frames": result["cur"],
             "compensation": compensation, "actions": result["actions"]}
    need(value["total_roles"] == 844 and len(value["actions"]) == 26647,
         "bounded stream geometry")
    raw = canonical(value)
    need(len(raw) <= 4 * 1024 * 1024, "literal stream size bound")
    return raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path, help="create a new compressed literal stream")
    group.add_argument("--check", action="store_true", help="compare every exported field")
    parser.add_argument("--native", action="store_true", help="also run the predecessor native checks")
    args = parser.parse_args()
    authenticate()
    raw = exported(capture(args.native))
    if args.write:
        with args.write.open("xb") as stream:
            stream.write(gzip.compress(raw, mtime=0))
    else:
        with gzip.open(HERE / "WORD.json.gz", "rb") as stream:
            frozen = stream.read(4 * 1024 * 1024 + 1)
        need(len(frozen) <= 4 * 1024 * 1024, "frozen stream size bound")
        need(raw == frozen, "complete regenerated literal stream")
    print("PASS_P104_DELAYED_WORD_REBIND sha256=" + hashlib.sha256(raw).hexdigest()
          + " new_native=" + str(args.native))


if __name__ == "__main__":
    main()
