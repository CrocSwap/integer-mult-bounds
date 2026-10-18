#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Recompute the complete finite restore-frame optimum from pinned source words."""

import argparse
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

from frames import census, need, problem

PACKAGE = Path(__file__).resolve().parent
EXPECTED_PROFILE = {1: 2433, 2: 712, 3: 232, 4: 108, 5: 18, 8: 8}
EXPECTED_DISTRIBUTION = [32, 1056, 12936, 79408, 274560,
                         558000, 661824, 430272, 130248, 11664]


def load_words(package=PACKAGE):
    sources = json.loads((package / "SOURCES.json").read_text(encoding="utf-8"))
    exports = sources["exports"]
    need([row["local"] for row in exports] == ["inputs/base.json.gz", "inputs/extra.json.gz"],
         "exact two input exports")
    words = {}
    for row in exports:
        raw = (package / row["local"]).read_bytes()
        need(len(raw) < 100000 and hashlib.sha256(raw).hexdigest() == row["sha256"],
             "pinned exported input bytes")
        decoded = gzip.decompress(raw)
        need(len(decoded) < 700000, "decoded source bound")
        words[Path(row["local"]).name.split(".")[0]] = json.loads(decoded)
    return words


def distribution(result):
    """Convolve exact component multiplicities, retaining every legal schedule."""
    counts = Counter({0: 1})
    for component in result["components"]:
        local = Counter()
        for row in component["deltas"]:
            delta = row["profile"]
            units = -delta.get(2, 0)
            need(units >= 0 and delta == ({1: 2 * units, 2: -units} if units else {}),
                 "every component delta is a nonnegative multiple of 2H1-H2")
            local[units] += row["count"]
        combined = Counter()
        need(len(counts) <= 10 and len(local) <= 3, "convolution support bound")
        for a, n in counts.items():
            for b, m in local.items():
                combined[a + b] += n * m
        counts = combined
    return dict(sorted(counts.items()))


def classify_ties(result):
    changed = []
    for component in result["components"]:
        choices = component["equal_profile_changes"]
        need([] in choices and len(choices) in (1, 2), "source and at most one neutral change")
        for changes in choices:
            need(len(changes) <= 1, "one independent neutral scale per component")
            for change in changes:
                need(change["operation"] == "scale" and change["endpoint"] != "interior",
                     "every neutral change is a scale at an interval endpoint")
                changed.append(change)
    need([(x["gate"], x["rank"]) for x in changed] ==
         [(12, 6), (67, 6), (98, 7), (101, 7), (210, 9)], "five neutral scale choices")
    return changed


def run():
    results = {}
    for name, word in load_words().items():
        traces, profile, widths = problem(word)
        need(profile == EXPECTED_PROFILE, "source six-skip local profile")
        result = census(word["restore"], traces)
        counts = distribution(result)
        need(result["gates"] == 212 and result["forced"] == 185
             and result["variables"] == 27 and result["edges"] == 531, "exact frame domain")
        need(result["component_attempts"] == 542 and len(result["components"]) == 9,
             "exact component coverage")
        need(result["global_legal"] == sum(counts.values()) == 2160000,
             "complete global coverage")
        need(list(counts.values()) == EXPECTED_DISTRIBUTION, "exact profile multiplicities")
        need(len(word["helper_final"]) == 91, "91 retained private returns")
        result.update(profile=profile, widths=widths, private_returns=91,
                      delta_units=counts, optimum_assignments=counts[0],
                      neutral_scales=classify_ties(result))
        results[name] = result
    need(results["base"] == results["extra"], "both provider restore problems agree")
    return {"status": "PASS_RESTORE_FRAME_OPTIMUM", "providers": results,
            "claim": "No legal fixed-order restore-frame reassignment improves the local bill for b>0.",
            "scope": "Fixed prefix, scalar operations, live registers and endpoints; no supplier admission."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    if args.output:
        rendered = json.dumps(result, sort_keys=True, indent=2) + "\n"
        need(args.output.write_text(rendered, encoding="utf-8") == len(rendered), "complete result write")
    print("PASS_RESTORE_FRAME_OPTIMUM providers=2 legal_each=2160000 optimal_each=32 "
          "component_attempts_each=542 no_new_kappa")


if __name__ == "__main__":
    main()
