#!/usr/bin/env python3
"""Separate the #1042 status link from the live selected record.

The historical section states the #1042 kappa and links to the live record.
The matching checkpoint is reached through the selected record's historical
previous_record chain (currently via frontier1094).
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
STATUS = ROOT / "docs/research/current-status.md"
MARKER = "PASS_HISTORICAL_1042_LINK kappas_differ=true no_new_kappa"
HREF = "../../certificates/selected-result.json"
CHECKPOINT = "certificates/checkpoints/frontier1042.json"
INTERMEDIATE = "certificates/checkpoints/frontier1094.json"
SHOWN = "0.001672188119205421"


def fail(message):
    raise SystemExit("FAIL_HISTORICAL_1042_LINK " + message)


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
    expected = {
        "docs/research/current-status.md",
        "certificates/selected-result.json",
        "certificates/checkpoints/frontier1042.json",
        "certificates/checkpoints/frontier1094.json",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def historical_section(text):
    start = text.index("# Historical status through #1042")
    end = text.index("# Historical status through #942")
    return text[start:end]


def evaluate():
    authenticate()
    text = STATUS.read_text(encoding="utf-8")
    section = historical_section(text)
    live = json.loads((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
    old = json.loads((ROOT / CHECKPOINT).read_text(encoding="utf-8"))
    require(HREF in section, "the historical section lost the live-record link")
    require(SHOWN in section, "the historical kappa sentence moved")
    require(Fraction(SHOWN) == Fraction(old["kappa"]), "the checkpoint kappa left the printed decimal")
    require(live["previous_record"] == INTERMEDIATE, "the live previous-record pointer moved")
    intermediate = json.loads((ROOT / INTERMEDIATE).read_text(encoding="utf-8"))
    require(intermediate["previous_record"] == CHECKPOINT, "the checkpoint ancestry link moved")
    require(Fraction(live["kappa"]) != Fraction(old["kappa"]), "the live and historical kappas agree")
    require(text.index(HREF) < text.index("# Historical status through #1042"), "the live section lost its record link")
    return {
        "historical_href": HREF,
        "checkpoint": CHECKPOINT,
        "intermediate_checkpoint": INTERMEDIATE,
        "historical_kappa": old["kappa"],
        "live_kappa": live["kappa"],
        "same_href": True,
        "kappas_differ": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
