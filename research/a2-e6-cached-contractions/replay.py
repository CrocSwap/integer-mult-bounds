#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Complete PR2061 primary replay with invocation-local fixed contractions."""

import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/a2-e6-nine-normal-floor"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(root=ROOT):
    """Check every live dependency before the predecessor imports any code."""
    pins = json.loads((HERE / "SOURCES.json").read_text())
    live = [row for row in pins["files"] if row["usage"] == "input"]
    require(len(live) == 9, "live dependency inventory")
    for row in live:
        path = root / row["path"]
        require(path.is_file() and path.stat().st_size <= 2**20, "source size")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
                "source mismatch: " + row["path"])


def load_original():
    authenticate()
    spec = importlib.util.spec_from_file_location("a2_e6_original", ROOT / SOURCE / "verify.py")
    require(spec is not None and spec.loader is not None, "source loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cached_identity(E, frame, indices, rows, counts=None):
    """Factor the j,k-only contraction out of the all-pairs i,j test."""
    indices = tuple(indices)
    require(len(indices) <= 120 and len(frame.F) == 9, "bounded identity domain")
    coefficients = {
        j: tuple(sum(Q(a) * b for a, b in zip(E.LINES[j], normal)) / 4
                 for normal in frame.F)
        for j in indices
    }
    visited = 0
    valid = True
    for i in indices:
        for j in indices:
            visited += 1
            value = sum(rows[i][k] * coefficients[j][k] for k in range(9))
            if value != 2 * E.G[i][j]:
                valid = False
                break
        if not valid:
            break
    if counts is not None:
        counts.append({"entries": visited,
                       "original_contractions": 9 * visited,
                       "cached_contractions": 9 * len(indices), "valid": valid})
    return valid


def replay(mode):
    require(mode in ("original", "cached"), "replay mode")
    module = load_original()
    counts = []
    if mode == "cached":
        def identity(E, frame, indices, rows):
            return cached_identity(E, frame, indices, rows, counts)
        module.exact_identity = identity
    result = json.loads(json.dumps(module.run()))
    expected = json.loads((ROOT / SOURCE / "RESULT.json").read_text())
    require(result == expected, "complete predecessor certificate mismatch")
    return result, counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("original", "cached"), default="cached")
    args = parser.parse_args()
    replay(args.mode)
    print("PASS_A2_E6_NINE_NORMAL_FLOOR copy=69 active=9 variable=17 fixed=52 entries=12544 controls=4")


if __name__ == "__main__":
    main()
