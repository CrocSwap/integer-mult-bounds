#!/usr/bin/env python3
"""Run the unchanged Dic3 checker with one prepared coefficient permutation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import types


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = "research/bit-dicyclic-diagonal-seed620ca/"
INPUTS = tuple(SOURCE + name for name in ("search.py", "verify.py", "EXPECTED.json"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def source_bytes(root: Path = ROOT) -> dict[str, bytes]:
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    require({row["path"] for row in rows} == set(INPUTS), "source inventory changed")
    require(len(rows) == 3, "duplicate source pin")
    payloads = {}
    for row in rows:
        path = root / row["path"]
        require(path.is_file() and not path.is_symlink(), "missing regular input")
        require(path.stat().st_size <= 65536, "source size exceeds bound")
        payload = path.read_bytes()
        require(hashlib.sha256(payload).hexdigest() == row["sha256"],
                "source digest mismatch: " + row["path"])
        payloads[row["path"]] = payload
    return payloads


def load_sources(root: Path = ROOT) -> tuple[types.ModuleType, types.ModuleType]:
    payloads = source_bytes(root)
    search = types.ModuleType("dic3_pinned_search")
    search.__file__ = str(root / (SOURCE + "search.py"))
    exec(compile(payloads[SOURCE + "search.py"], search.__file__, "exec"),
         search.__dict__)
    checker = types.ModuleType("dic3_pinned_checker")
    checker.__file__ = str(root / (SOURCE + "verify.py"))
    previous = sys.modules.get("search")
    sys.modules["search"] = search
    try:
        exec(compile(payloads[SOURCE + "verify.py"], checker.__file__, "exec"),
             checker.__dict__)
    finally:
        if previous is None:
            del sys.modules["search"]
        else:
            sys.modules["search"] = previous
    require(checker.search is search, "checker did not bind the pinned search")
    return search, checker


def shift_tables(group: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    require(len(group) == 12 and all(len(row) == 12 for row in group),
            "expected twelve group elements")
    require(all(sorted(row[g] for row in group) == list(range(12))
                for g in range(12)), "right translation is not a permutation")
    tables = []
    for g in range(12):
        row = [0] * 4096
        images = tuple(1 << group[i][g] for i in range(12))
        for mask in range(1, 4096):
            bit = mask & -mask
            row[mask] = row[mask ^ bit] ^ images[bit.bit_length() - 1]
        tables.append(tuple(row))
    return tuple(tables)


def install(search: types.ModuleType) -> tuple[tuple[int, ...], ...]:
    tables = shift_tables(search.GROUP_TABLE)

    def prepared_shift(mask: int, g: int) -> int:
        # The authenticated caller supplies 0<=mask<4096 and 0<=g<12.
        return tables[g][mask]

    search.right_monomial_shift = prepared_shift
    return tables


def run(baseline: bool = False) -> None:
    search, checker = load_sources()
    if not baseline:
        install(search)
    checker.main()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", action="store_true")
    args = parser.parse_args()
    run(args.baseline)


if __name__ == "__main__":
    main()
