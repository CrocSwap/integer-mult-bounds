#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with substantial OpenAI Codex assistance.
"""Authenticate and run the complete unchanged canonical Fano verifier.

Only its relation_census callable is adapted. Canonical and compact modes use
the original multiplication and packing; optional row-table modes use the
separately authenticated key engine. Every mode retains the complete source
checks, Fano searches and controls, and must match the original receipt bytes.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys
from types import ModuleType

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REFERENCE = "research/centre-seven-owner-fano-independent"
ROWTABLE_SHA256 = "decc8e6a4331ffd28460056d49f06758c6fad721e0638ade90a7ee723c367458"
MODES = ("baseline", "compact", "rowtables", "rowtables-compact")
sys.path.insert(0, str(HERE))
import kernel


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(root=ROOT):
    data = {}
    for row in json.loads((HERE / "SOURCES.json").read_bytes())["files"]:
        if row["usage"] != "input":
            continue
        path = row["path"]
        require(not Path(path).is_absolute() and ".." not in Path(path).parts, "relative source path")
        body = (Path(root) / path).read_bytes()
        require(hashlib.sha256(body).hexdigest() == row["sha256"], "source hash: " + path)
        data[path] = body
    return data


def load_reference(root=ROOT):
    """Return a fresh authenticated module and its pinned complete receipt bytes."""
    data = authenticate(root)
    source = REFERENCE + "/verify.py"
    module = ModuleType("retained_fano_verifier")
    module.__file__ = str(Path(root) / source)
    exec(compile(data[source], module.__file__, "exec"), module.__dict__)
    return module, data[REFERENCE + "/RESULT.json"]


def load_rowtables(path=HERE / "inputs/pr3219-kernel.py"):
    """Optional comparison only: authenticate exact PR3219 source before execution."""
    raw = Path(path).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == ROWTABLE_SHA256, "optional row-table source hash")
    module = ModuleType("retained_rowtable_comparison")
    module.__file__ = str(path)
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    return module


def rowtable_compact(matrices, tables):
    """Unchanged PR3219 products and keys, with only class storage replaced."""
    indexed, actions, _ = tables.prepare(matrices)
    n = len(matrices)
    classes = kernel.CompactClasses(n)
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            rows = indexed[a, b]
            prefix = (a * n + b) * n
            for c in range(n):
                if c != b:
                    classes.add(tables.product_key(rows, actions[c]), prefix + c)
    return classes.finish()


def full_build(reference, expected, census):
    """Run every retained check, also fingerprinting the complete census result."""
    calls = []
    original = reference.relation_census

    def capture(matrices):
        total, sizes, relations = census(matrices)
        payload = [total, sorted(sizes.items()), sorted(relations)]
        body = json.dumps(payload, separators=(",", ":")).encode()
        calls.append(hashlib.sha256(body).hexdigest())
        return total, sizes, relations

    reference.relation_census = capture
    try:
        result = reference.build()
    finally:
        reference.relation_census = original
    require(len(calls) == 1, "one complete retained census")
    actual = reference.canonical(result)
    require(actual == expected, "complete canonical receipt mismatch")
    return {"receipt_sha256": hashlib.sha256(actual).hexdigest(),
            "receipt_bytes": len(actual), "census_sha256": calls[0],
            "reduced_triples": result["reduced_triples"],
            "class_size_histogram": result["class_size_histogram"],
            "relation_words": result["cyclic_length6_relation_words_with_symmetry"]}


def run(mode="compact", root=ROOT):
    require(mode in MODES, "unknown census mode")
    reference, expected = load_reference(root)
    if mode == "baseline":
        census = reference.relation_census
    elif mode == "compact":
        census = lambda matrices: kernel.relation_census(matrices, reference.mul, reference.pack)
    else:
        tables = load_rowtables()
        census = (tables.relation_census if mode == "rowtables" else
                  lambda matrices: rowtable_compact(matrices, tables))
    return {"mode": mode, **full_build(reference, expected, census)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=MODES, default="compact")
    args = parser.parse_args()
    print(json.dumps(run(args.mode), sort_keys=True))


if __name__ == "__main__":
    main()
