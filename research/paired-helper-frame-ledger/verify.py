#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read-only replay of the source-pinned finite frame ledger.

Use --details to print every derived paid event as JSON. No predecessor Python,
network, external package, subprocess, or cached output enters the calculation.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("paired_frame_ledger", HERE / "ledger.py")
ledger = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ledger)
INPUTS_SHA256 = "09e49a4edffa3f98b0845289a5041d31ebfa5780e908b70686e6602cec82a9b1"
SOURCE_COMMIT = "224bd5e56041c40078ff6b5fa7393733a215de5c"


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result

    def nonfinite(value):
        raise ValueError("nonfinite JSON number: " + value)

    def finite_float(value):
        result = float(value)
        if not math.isfinite(result):
            nonfinite(value)
        return result

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite,
                      parse_float=finite_float)


def canonical(value):
    # Compare serialized JSON, not Python equality (True == 1 == 1.0).
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def load_inputs(directory=HERE):
    manifest_raw = (directory / "INPUTS.json").read_bytes()
    ledger.require(hashlib.sha256(manifest_raw).hexdigest() == INPUTS_SHA256,
                   "source manifest pin mismatch")
    manifest = strict_json(manifest_raw)
    ledger.require(manifest["source_commit"] == SOURCE_COMMIT, "source commit mismatch")
    names = {"data/" + kind + "-" + variant + ".json.gz"
             for kind in ("PARENT", "WORD") for variant in ("base", "extra")}
    names |= {f"data/TRANSFORM-{helper}.json" for helper in ledger.HELPERS}
    names.add("SOURCE-CREDITS.md")
    rows = manifest["files"]
    ledger.require(len(rows) == len(names) and {row["path"] for row in rows} == names,
                   "source inventory mismatch")
    ledger.require({"data/" + path.name for path in (directory / "data").iterdir()}
                   == names - {"SOURCE-CREDITS.md"}, "unexpected data file")
    result = {}
    for row in rows:
        path = directory / row["path"]
        ledger.require(path.is_file() and not path.is_symlink(), "non-regular source file")
        raw = path.read_bytes()
        ledger.require(len(raw) == row["bytes"]
                       and hashlib.sha256(raw).hexdigest() == row["sha256"],
                       "source bytes changed: " + row["path"])
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        ledger.require(blob == row["git_blob"], "source Git blob mismatch")
        if path.suffix == ".gz":
            result[path.name[:-8]] = strict_json(gzip.decompress(raw))
        elif path.suffix == ".json":
            result[path.stem] = strict_json(raw)
    return result


def replay(directory=HERE, details=False):
    inputs = load_inputs(directory)
    words, chains = {}, {}
    for variant in ("base", "extra"):
        for kind in ("PARENT", "WORD"):
            name = kind + "-" + variant
            receipt = ledger.audit_word(inputs[name])
            if not details:
                receipt = dict(receipt)
                for key in ("charges", "warp_events", "helper_widths", "role_profiles",
                            "restored_helpers", "private_buffers"):
                    value = receipt.pop(key)
                    receipt[key + "_sha256"] = ledger.canonical_hash(value)
                    receipt[key + "_count"] = len(value)
            words[name] = receipt
        transforms = [inputs[f"TRANSFORM-{helper}"] for helper in ledger.HELPERS]
        chains[variant] = ledger.audit_chain(inputs["PARENT-" + variant],
                                             inputs["WORD-" + variant], transforms)
    return {"status": "PASS_PAIRED_HELPER_FRAME_LEDGER", "source_commit": SOURCE_COMMIT,
            "inputs_sha256": INPUTS_SHA256, "words": words, "chains": chains,
            "scope": "Finite frame/rank/cleanup-syntax audit only; no new kappa, operator endpoint, zero-buffer, native, allocation or full supplier certification."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--details", action="store_true", help="print derived event ledgers to stdout")
    args = parser.parse_args()
    result = replay()
    expected = strict_json((HERE / "RESULT.json").read_bytes())
    ledger.require(canonical(result) == canonical(expected), "frozen RESULT differs from replay")
    if args.details:
        print(json.dumps(replay(details=True), indent=2, sort_keys=True))
    else:
        print(result["status"])
        print("2 providers; 4 words; 9 stages/provider; 13 exact frame edits/provider")
        print("rank mass 5179 -> 5170; helper widths 3323 -> 3314; buffers 73 -> 82")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print("FAIL_PAIRED_HELPER_FRAME_LEDGER: " + str(error), file=sys.stderr)
        raise SystemExit(1) from error
