#!/usr/bin/env python3
"""Zero-saving bills of the direct odd-stage frame schedule.

The checker applies the pinned idle rules. It does not replay bridge columns.
"""

import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_DIRECT_FRAME_STAGE_BILLS excess=3552 bills=145/144,513/512,781/780 no_new_kappa"
RECIPE = "research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py"
CONFIG = "research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r740-replica32/code/config.py"
PORTS = "research/e8-bit-p111-tuned/README.md"
STAGES = (5, 9, 11)


def fail(message):
    raise SystemExit("FAIL_DIRECT_FRAME_STAGE_BILLS " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def idle_ranks(half):
    ranks = []
    for stage in range(2 * half + 1):
        if stage % 2 == 1 and stage <= 2 * half - 3:
            ranks.append(7 * (stage + 1))
        elif stage % 2 == 0 and 2 <= stage <= 2 * half - 2:
            ranks.append(7)
        elif stage == 2 * half:
            for pair in range(half):
                ranks.append(7 * (2 * half - (2 * pair + 2)))
    return ranks


def bills(ports, replicas):
    rows = []
    for stages in STAGES:
        half = (stages - 1) // 2
        require(2 * half + 1 == stages, "the stage count is not odd")
        width = 1 + 7 * stages
        live = 2 * half * ports * replicas
        histogram = Counter({7: stages * replicas * ports, 8: stages * replicas * ports})
        for rank in idle_ranks(half):
            if rank:
                histogram[rank] += 2 * ports * replicas
        paid = sum(rank * count for rank, count in histogram.items())
        capacity = width * live
        require(capacity - paid == -ports * replicas, "the capacity gap moved")
        rows.append({
            "stages": stages,
            "width": width,
            "live": live,
            "paid": paid,
            "capacity": capacity,
            "bill": str(Fraction(paid, capacity)),
            "histogram": {str(rank): histogram[rank] for rank in sorted(histogram)},
        })
    return rows


def evaluate():
    require(sha256(ROOT / RECIPE) == "6368196a393ac25bb2918880e4c4bd31ed733b762c27b6873ab391cbc0c5c3c8", "recipe drift")
    require(sha256(ROOT / CONFIG) == "283d7fad45155ee91e704d63ec947cf4a60aeff5cc43510bc0e835f7da7d8767", "replica config drift")
    require(sha256(ROOT / PORTS) == "a054ce8453e2936d45c4edd1c3678993903fcf6705ac241b9f1a4c4f9accda2d", "port note drift")
    recipe = (ROOT / RECIPE).read_text(encoding="utf-8")
    for clause in (
        "M=1+7*L",
        "DATA=2*K*V*T",
        "if NOBANK: place,NB=None,None; LIVE=DATA",
        "rank=7*(s+1)",
        "rank=7,source_level=s-1",
        "rank=7*(2*K-oldlevel)",
        "paid[e['rank']]+=2*V*T",
    ):
        require(clause in recipe, "a schedule clause moved")
    require("REPLICAS = 32" in (ROOT / CONFIG).read_text(encoding="utf-8"), "the replica count moved")
    require("v = 111 live ports" in (ROOT / PORTS).read_text(encoding="utf-8"), "the live port count moved")
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    rows = bills(111, 32)
    require([row["bill"] for row in rows] == ["145/144", "513/512", "781/780"], "a bill moved")
    require(all(row["paid"] - row["capacity"] == 3552 for row in rows), "the excess moved")
    return {"ports": 111, "replicas": 32, "excess": 3552, "stages": rows, "no_new_kappa": True}


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
