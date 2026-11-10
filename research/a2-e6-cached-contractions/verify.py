#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Verify the new contraction adapter and its complete retained workload."""

import hashlib
import json
import sys
import tempfile
from fractions import Fraction as Q
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from replay import ROOT, authenticate, cached_identity, load_original, replay, require  # noqa: E402


def controls():
    original = load_original().exact_identity
    E = SimpleNamespace(LINES=[(Q(i), Q(1 - i)) for i in range(4)])
    frame = SimpleNamespace(F=[(Q(k, 3), Q(2 - k, 5)) for k in range(9)])
    rows = {i: [Q((i + 1) * (k - 3), 7) for k in range(9)] for i in range(4)}
    E.G = [[sum(rows[i][k] * sum(a * b for a, b in zip(E.LINES[j], frame.F[k])) / 8
                for k in range(9)) for j in range(4)] for i in range(4)]
    cases = 0
    for length in range(5):
        indices = list(range(length))
        require(original(E, frame, indices, rows) is True, "rational positive fixture")
        require(cached_identity(E, frame, indices, rows) is True, "cached positive fixture")
        cases += 1
        for i in indices:
            for j in indices:
                E.G[i][j] += Q(1, 11)
                require(original(E, frame, indices, rows) is False, "original mutation")
                require(cached_identity(E, frame, indices, rows) is False, "cached mutation")
                E.G[i][j] -= Q(1, 11)
                cases += 1
    # One fresh invocation must see changed source coefficients and Gram entries.
    frame.F[0] = (Q(101), Q(-37))
    require(original(E, frame, list(range(4)), rows) is False, "changed normals original")
    require(cached_identity(E, frame, list(range(4)), rows) is False, "no cross-call cache")
    E.G[0][0] += 1
    require(cached_identity(E, frame, [0], rows) is False, "changed Gram matrix")
    return cases + 2


def source_controls():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    live = [row for row in pins["files"] if row["usage"] == "input"]
    with tempfile.TemporaryDirectory(prefix="a2-e6-source-controls-") as name:
        root = Path(name)
        for row in live:
            path = root / row["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / row["path"]).read_bytes())
        authenticate(root)
        for row in live:
            path = root / row["path"]
            data = path.read_bytes()
            path.write_bytes(data + b"\n")
            try:
                authenticate(root)
            except ValueError as error:
                require(str(error).startswith("source mismatch:"), "hash rejection reason")
            else:
                raise ValueError("source corruption accepted")
            path.write_bytes(data)
        path.unlink()
        try:
            authenticate(root)
        except ValueError as error:
            require(str(error) == "source size", "missing source rejection reason")
        else:
            raise ValueError("missing source accepted")
    return len(live) + 1


def main():
    control_count = controls()
    source_count = source_controls()
    result, counts = replay("cached")
    require(len(counts) == 2, "both original identity invocations retained")
    require(counts[0]["entries"] == 12544 and counts[0]["valid"], "all-pairs coverage")
    require(counts[1]["entries"] == 4817 and not counts[1]["valid"],
            "original changed-coefficient rejection")
    original = sum(row["original_contractions"] for row in counts)
    cached = sum(row["cached_contractions"] for row in counts)
    require((original, cached) == (156249, 2016), "exact operation improvement")
    files = sorted(path for path in HERE.iterdir() if path.is_file())
    require(len(files) <= 16 and all(p.stat().st_size <= 2**20 for p in files), "package bounds")
    receipt = {"status": "PASS_A2_E6_CACHED_CONTRACTIONS", "controls": control_count,
               "source_controls": source_count,
               "calls": counts, "removed_contractions": original - cached,
               "removed_rational_products": 8 * (original - cached),
               "result_sha256": hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest(),
               "package_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
