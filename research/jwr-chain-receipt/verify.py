#!/usr/bin/env python3
"""Disposition receipt for jwr404's halo-absorption PR chain (13 open PRs, #4508-#4531, recorded at main f626db5c).

Checks internal consistency of the recorded facts only (no working-tree checks, so the receipt still replays after any
of these PRs merges): every head and merge base is a full SHA, each PR is a single-package addition whose recorded
files lie inside its package, no package was present at its merge base, answer edges point to the merged predecessor
#4506, to #4517, or to earlier PRs in the set, and the factor-9 pair refines the factor-10 pair it answers.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
SHA = re.compile(r"[0-9a-f]{40}")


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    rec = json.loads((HERE / "RECEIPT.json").read_text(encoding="utf-8"))
    prs = {int(n): r for n, r in rec["prs"].items()}
    need(sorted(prs) == [4508, 4509, 4511, 4512, 4515, 4520, 4523, 4524, 4526, 4527, 4528, 4530, 4531], "the 13 PRs")
    need(SHA.fullmatch(rec["recorded_against_main"]), "main SHA")
    known = set(prs) | {rec["predecessor_merged"]["pr"]} | {int(n) for n in rec["outside_author"]}
    packages = set()
    for n, r in prs.items():
        need(SHA.fullmatch(r["head"]) and SHA.fullmatch(r["merge_base"]), f"#{n}: head and base")
        need(r["package_at_base"] is False, f"#{n}: package not retained at its base")
        need(r["paths_outside_package"] == [], f"#{n}: single-package addition")
        need(len(r["files"]) >= 5 and all(SHA.fullmatch(b) for b in r["files"].values()), f"#{n}: blobs")
        need(all(p.startswith(r["package"] + "/") for p in r["files"]), f"#{n}: files inside the package")
        need(r["package"] not in packages, f"#{n}: distinct package")
        packages.add(r["package"])
        a = r["answers_open_question_of"]
        need(a is None or (a in known and a < n), f"#{n}: answer edge")
    # The factor-9 pair branches from the factor-10 tip #4528: #4530 answers it, #4531 answers #4530.
    sup = {int(n): s["refines"] for n, s in rec["supersession"].items()}
    need(sup == {4530: 4527, 4531: 4528}, "factor-9 pair refines the factor-10 pair")
    need(prs[4530]["answers_open_question_of"] == 4528 and prs[4531]["answers_open_question_of"] == 4530, "branch edges")
    roots = [n for n, r in prs.items() if r["answers_open_question_of"] is None]
    print(json.dumps({"status": "PASS_JWR_CHAIN_RECEIPT", "prs": len(prs), "retained_at_base": 0,
                      "chain_roots": roots, "factor9_refines": {k: v["refines"] for k, v in rec["supersession"].items()},
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
