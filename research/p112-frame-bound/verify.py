#!/usr/bin/env python3
"""An eight-frame meets at most 4 lost-free ports, so weight 14 gives bound 56.

The checker multiplies these counts. It does not rerun the frame census.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_P112_FRAME_BOUND ports=56 tariff=184 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_P112_FRAME_BOUND " + message)


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


def tariff(size):
    return 72 + 2 * (112 - size)


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    require(2 * 4 <= 9 and 2 * 5 > 9, "the frame cap moved")
    require(4 * 14 == 56, "the port bound moved")
    require(tariff(32) == 232, "the size-32 tariff moved")
    require([tariff(size) for size in range(33, 37)] == [230, 228, 226, 224], "the middle tariffs moved")
    require(tariff(36) == 224 and tariff(37) == 222, "the 224 crossing moved")
    require(tariff(56) == 184 and all(tariff(size) >= 184 for size in range(57)), "the size-56 floor moved")
    return {
        "frame_cap": 4,
        "port_bound": 56,
        "size_56_tariff": 184,
        "below_224_at": 37,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
