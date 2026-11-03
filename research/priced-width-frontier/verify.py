#!/usr/bin/env python3
"""Offline research replay. SHIN09-git with OpenAI Codex assistance. Apache-2.0."""
import hashlib
import json
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from checks import (check_examples, check_families, check_onset_family, intersection_grid, invalid_inputs,
                    large_period, menu_grid, require)
from execution import run_schedules
from rank12 import check_rank12
from recursive_dispatch import check_recursive


SOURCE_PINS = {
    "source/6658-README.md": "4c0a17a159cf2d04f1333393933e833f5af39b4974890a0e3ff3b36b0ad6b3b3",
    "source/6658-PROOF.md": "5b682aa1a79baa9d18d751c76764a48781aadbf3568b141aa347db16bca41c7c",
    "source/LICENSE": "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
    "source/4507-batches.py": "73e7ab4a1925ee7d412d0f2b5d28b70f3a9e43e427c2ec6f6d89f193b84655ef",
    "source/4507-RESULT.json": "2750ea29f5d9d40aac5d97f1c4aa6482b5315003a9b50d1a21afae81b86d739a",
}


def load_json(name):
    return json.loads((PACKAGE / name).read_text(encoding="utf-8"))


def build():
    sources = load_json("SOURCES.json")["files"]
    for name, expected in SOURCE_PINS.items():
        actual = hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
        rows = [r for r in sources if r.get("vendored_as") == name]
        require(len(rows) == 1 and expected == actual == rows[0]["sha256"], "retained source hash")
    cases = load_json("CASES.json")
    examples = check_examples(cases)
    result = {"examples": examples, "menu_grid": menu_grid(), "intersections": intersection_grid(),
              "fixed_fee_families": check_families(), "executed_schedules": run_schedules(cases, examples),
              "onset_family": check_onset_family(), "large_period": large_period(),
              "rejected_invalid_inputs": invalid_inputs()}
    rank12 = check_rank12(PACKAGE, load_json("source/4507-RESULT.json"))
    result.update(rank12=rank12, recursive_dispatch=check_recursive(PACKAGE, rank12))
    return result


def main():
    result = build()
    # The JSON archive uses arrays for the schedule tuples.
    require(json.loads(json.dumps(result)) == load_json("RESULT.json"), "stored research result differs")
    print(json.dumps({"status": "PASS_PRICED_WIDTH_FRONTIER", "result": result}, sort_keys=True))


if __name__ == "__main__":
    main()
