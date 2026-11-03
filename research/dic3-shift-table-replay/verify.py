#!/usr/bin/env python3
"""Check all prepared permutations, source rejection, and the complete replay."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import statistics
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import replay


def literal_shift(mask: int, g: int) -> int:
    k, ell = g % 6, g // 6
    out = 0
    for i in range(12):
        if (mask >> i) & 1:
            j, bit = i % 6, i // 6
            power = (j + (k if bit == 0 else -k) + 3 * bit * ell) % 6
            out ^= 1 << (power + 6 * ((bit + ell) % 2))
    return out


def check_tables(search, tables) -> dict:
    original = search.right_monomial_shift
    count = 0
    for g in range(12):
        for mask in range(4096):
            expected = literal_shift(mask, g)
            replay.require(tables[g][mask] == expected == original(mask, g),
                           "prepared shift changed a coefficient")
            replay.require(expected.bit_count() == mask.bit_count(),
                           "permutation changed support cardinality")
            count += 1
    composition = 0
    for g in range(12):
        for h in range(12):
            for mask in range(4096):
                replay.require(tables[h][tables[g][mask]] == tables[search.GROUP_TABLE[g][h]][mask],
                               "right-action composition changed")
                composition += 1
    return {"coefficient_cases": count, "composition_cases": composition}


def expect_rejection(action, label: str) -> None:
    try:
        action()
    except (ValueError, OSError, KeyError, json.JSONDecodeError):
        return
    raise ValueError("control did not reject: " + label)


def controls(search, tables) -> list[str]:
    labels = []
    for name, group in (("missing group row", search.GROUP_TABLE[:-1]),
                        ("short group row", ((),) + search.GROUP_TABLE[1:]),
                        ("nonpermutation", tuple((0,) * 12 for _ in range(12)))):
        expect_rejection(lambda: replay.shift_tables(group), name)
        labels.append(name)
    left_tables = replay.shift_tables(tuple(zip(*search.GROUP_TABLE)))
    expect_rejection(lambda: check_tables(search, left_tables), "left multiplication")
    labels.append("left versus right multiplication")
    changed = list(tables[1])
    changed[1 << 6] ^= 1
    mutant = (tables[0], tuple(changed)) + tables[2:]
    expect_rejection(lambda: check_tables(search, mutant), "coefficient mutation")
    labels.append("coefficient mutation")
    payloads = replay.source_bytes()
    with tempfile.TemporaryDirectory(prefix="dic3-source-controls-") as directory:
        root = Path(directory)
        for name, payload in payloads.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
        replay.source_bytes(root)
        for name, payload in payloads.items():
            target = root / name
            target.write_bytes(payload + b"\n")
            expect_rejection(lambda: replay.source_bytes(root), name)
            labels.append("changed " + name)
            target.write_bytes(payload)
        target = root / replay.INPUTS[0]
        target.unlink()
        expect_rejection(lambda: replay.source_bytes(root), "missing source")
        labels.append("missing source")
    return labels


def check_measurement() -> None:
    result = json.loads((PACKAGE / "MEASUREMENTS.json").read_text())
    replay.require(len(result["samples"]) == 10 and result["errors"] == 0,
                   "incomplete timing evidence")
    for index, row in enumerate(result["samples"]):
        replay.require(row["baseline"] == (index % 2 == 0), "timing order changed")
        replay.require(row["returncode"] == row["stderr_bytes"] == 0,
                       "timed execution failed")
        replay.require(row["stdout_sha256"] == hashlib.sha256(result["stdout"].encode()).hexdigest(),
                       "timed complete output changed")
    for name, digest in result["source_hashes"].items():
        replay.require(hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest() == digest,
                       "timing implementation changed: " + name)
    for side, name in ((True, "baseline"), (False, "prepared")):
        values = [r["elapsed_ns"] for r in result["samples"] if r["baseline"] == side]
        replay.require(all(0 < value < 120_000_000_000 for value in values),
                       "timing exceeded its declared domain")
        expected = {"median_ns": statistics.median(values), "min_ns": min(values),
                    "max_ns": max(values)}
        replay.require(result[name] == expected, "timing summary changed")
    reduction = 1 - result["prepared"]["median_ns"] / result["baseline"]["median_ns"]
    replay.require(result["reduction_fraction"] == reduction > 0,
                   "recorded timing reduction changed")


def main() -> None:
    check_measurement()
    search, checker = replay.load_sources()
    tables = replay.shift_tables(search.GROUP_TABLE)
    counts = check_tables(search, tables)
    rejected = controls(search, tables)
    installed = replay.install(search)
    replay.require(installed == tables, "installed table changed")
    checker.main()
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(PACKAGE.iterdir()) if p.is_file()}
    print(json.dumps({"status": "PASS_DIC3_SHIFT_TABLE_REPLAY", **counts,
                      "controls": rejected, "package_sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
