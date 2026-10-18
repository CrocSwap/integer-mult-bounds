#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Portable exact replay. Default operation is read-only; no third-party packages."""
import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASE = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
SOURCE = "research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json"
SOURCE_SHA = "327d2a868043e846381aa58a33053c24425e8cad522ff401b10ec8af1d649a3f"
EXTRACT_SHA = "09e9586025b25dbbffa4b038d2183b986792f452c20daa6d5f74e6af9f876c22"
MANIFEST_SHA = "f809da068e59e118b8d2fde83ace036653de8d054351e44a2c35ec7484fc9a43"

def require(ok, message):
    if not ok:
        raise ValueError(message)

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)

def checked_json(path, digest=None):
    raw = Path(path).read_bytes()
    if digest is not None:
        require(hashlib.sha256(raw).hexdigest() == digest, "source digest mismatch: " + Path(path).name)
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, "duplicate JSON key")
            out[key] = value
        return out
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda v: (_ for _ in ()).throw(ValueError("nonfinite JSON")))

def validate_source(src):
    require(type(src) is dict and set(src) == {"root_lines", "binary_ports"}, "source fields")
    roots, labels = src["root_lines"], src["binary_ports"]
    require(type(roots) is list and len(roots) == 120, "root count")
    require(all(type(r) is list and len(r) == 8 and
                all(type(x) is int and -2 <= x <= 2 for x in r) and
                sum(x*x for x in r) == 4 for r in roots), "root numeric domain")
    require(type(labels) is list and len(labels) == 120 and
            all(type(x) is int and 0 < x < 512 for x in labels) and
            len(set(labels)) == 120, "label numeric domain")

def load_source(here=HERE):
    manifest = checked_json(here / "SOURCES.json", MANIFEST_SHA)
    require(manifest["base_commit"] == BASE, "base binding")
    src = checked_json(here / "ROOTS.json", EXTRACT_SHA)
    validate_source(src)
    # An exported package is self-contained. If the upstream input is present,
    # authenticate all its bytes as well as equality of the retained fields.
    original = here.parents[1] / SOURCE
    if original.exists():
        full = checked_json(original, SOURCE_SHA)
        require(canonical({key: full[key] for key in src}) == canonical(src), "source extraction mismatch")
    return src

def validate_witness(witness):
    require(type(witness) is dict and set(witness) == {"M", "N", "ranks"}, "witness fields")
    mats = []
    for name in ("M", "N"):
        mat = witness[name]
        require(type(mat) is list and len(mat) == 9 and all(type(row) is list and len(row) == 9 for row in mat), "witness shape")
        require(all(type(x) is str and str(Fraction(x)) == x for row in mat for x in row), "canonical rational domain")
        mats.append([[Fraction(x) for x in row] for row in mat])
    ranks = witness["ranks"]
    require(type(ranks) is list and len(ranks) == 9 and all(type(x) is int and 0 <= x <= 9 for x in ranks), "COPY numeric domain")
    m, n = mats
    require(all(sum(m[i][k]*n[j][k] for k in range(9)) == int(i == j) for i in range(9) for j in range(9)), "coefficient compensation / ordinary duality")

def compare(actual, expected, label):
    require(canonical(actual) == canonical(expected), label + " mismatch")

def model():
    spec = importlib.util.spec_from_file_location("copy_optimum_model", HERE / "model.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, metavar="NEW_FILE", help="write a new deterministic certificate; refuse existing paths")
    args = parser.parse_args()
    if args.write is not None:
        require(not args.write.exists(), "--write refuses existing paths")
    src = load_source()
    witness = checked_json(HERE / "WITNESS.json")
    validate_witness(witness)
    receipt = model().compute(src)
    compare(receipt["witness"], witness, "attaining witness")
    if args.write is None:
        compare(receipt, checked_json(HERE / "CERTIFICATE.json"), "complete finite certificate")
    else:
        with args.write.open("x", encoding="utf-8") as out:
            out.write(json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print("PASS: 1022 exact character kernels; COPY65 control; COPY64 attainer; all-entry ordinary/nonreal controls")
    print("Finite premises verified for PROOF.md: min sum rho**q = 7*8**q + 7**q + 1 (0<q<=1)")

if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, ZeroDivisionError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        sys.exit(1)
