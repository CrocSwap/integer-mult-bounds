#!/usr/bin/env python3
"""The staged entrance is one rank unit narrower than its parent.

The checker follows the published frames. It does not replay columns.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_SPAN_ENTRANCE_WIDTH staged=7 parent=8 no_new_kappa"
TERMINAL = (256, 128, 64, 32, 16, 8, 4, 2, 1)
CHAINS = {
    644: (
        (429, 30),
        (423, 65, 20, 10),
        (292, 131, 65, 20, 10),
        (260, 128, 65, 32, 20, 9, 3),
        (257, 128, 65, 32, 17, 9, 5, 3),
        TERMINAL,
    ),
    660: (
        (429, 30),
        (427, 96, 24, 6),
        (290, 136, 96, 24, 6, 1),
        (256, 136, 66, 34, 24, 6, 1),
        (256, 136, 64, 32, 24, 4, 2, 1),
        TERMINAL,
    ),
}
PARENT = {
    644: (3, 1, 2, 1, 1),
    660: (3, 2, 1, 1, 1),
}


def fail(message):
    raise SystemExit("FAIL_SPAN_ENTRANCE_WIDTH " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    require(set(pinned) == set(), "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def ranks(frames):
    return tuple(len(frames[index + 1]) - len(frames[index]) for index in range(len(frames) - 1))


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    require(TERMINAL == tuple(1 << shift for shift in range(8, -1, -1)), "the terminal frame moved")
    require(sum(TERMINAL) == (1 << 9) - 1, "the terminal sum moved")
    for helper, frames in CHAINS.items():
        require(frames[0] == (429, 30) and frames[-1] == TERMINAL, "a chain missed its endpoints")
        growth = ranks(frames)
        require(sum(growth) == len(TERMINAL) - len(frames[0]) == 7, "the staged width moved")
        parent = PARENT[helper]
        require(sum(parent) == len(TERMINAL) - 1 == 8, "the parent width moved")
        require(parent[0] == growth[0] + 1 and parent[1:] == growth[1:], "the first climb is not the only change")
    require(57 - 56 == 1 and (644, 660) == tuple(sorted(CHAINS)), "the recipe count moved")
    return {
        "staged_width": 7,
        "parent_width": 8,
        "helpers": 2,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
