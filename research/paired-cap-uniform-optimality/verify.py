#!/usr/bin/env python3
"""Authenticate frozen inputs and replay the uniform packing certificate.

ToikY, with substantial OpenAI Codex assistance. Apache-2.0.
Predecessor Python files are documentary inputs and never executed.
"""
import argparse
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from uniform import verify_certificate

MANIFEST_SHA256 = "ccdb04ba9f326bc450558529d02aa745bac6e1f767619f3d899ab44baa09dffa"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def reject_float(value):
    raise ValueError("non-integer JSON number: " + value)


def read_json(raw):
    return json.loads(raw, object_pairs_hook=unique_object,
                      parse_float=reject_float, parse_constant=reject_float)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def authenticate(package=HERE):
    manifest_path = package / "INPUTS.json"
    need(manifest_path.is_file() and not manifest_path.is_symlink(), "regular input manifest")
    raw = manifest_path.read_bytes()
    need(sha256(raw).hexdigest() == MANIFEST_SHA256, "input manifest changed")
    manifest = read_json(raw)
    expected = {row["path"] for row in manifest["files"]}
    actual = set()
    need((package / "inputs").is_dir() and not (package / "inputs").is_symlink(),
         "regular input directory")
    for path in (package / "inputs").rglob("*"):
        need(not path.is_symlink(), "input symlink")
        if path.is_file():
            actual.add(path.relative_to(package).as_posix())
        else:
            need(path.is_dir(), "nonregular input")
    need(actual == expected, "input inventory changed")
    for row in manifest["files"]:
        raw = (package / row["path"]).read_bytes()
        need(len(raw) == row["bytes"], "input length changed: " + row["path"])
        need(sha256(raw).hexdigest() == row["sha256"], "input bytes changed: " + row["path"])
        blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == row["git_blob"], "input Git blob changed: " + row["path"])
    return manifest


def replay(package=HERE):
    manifest = authenticate(package)
    result = verify_certificate(read_json((package / "inputs/RELAX-CAP.json").read_bytes()),
                                read_json((package / "inputs/PROFILE.json").read_bytes()))
    return {
        "schema_version": 1,
        "source_commit": manifest["source_commit"],
        "input_manifest_sha256": MANIFEST_SHA256,
        "scope": "Uniform fixed-inventory packing optimum; no physical realization, supplier admission or new kappa.",
        "certificate": result,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true", help="explicitly regenerate RESULT.json")
    parser.add_argument("--emit", action="store_true", help="print the complete recomputed receipt")
    args = parser.parse_args()
    result = replay()
    if args.write_result:
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        expected = read_json((HERE / "RESULT.json").read_bytes())
        need(canonical(result) == canonical(expected), "complete typed receipt differs")
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS_PAIRED_CAP_UNIFORM_OPTIMALITY receipt_sha256=" + sha256(canonical(result)).hexdigest())


if __name__ == "__main__":
    main()
