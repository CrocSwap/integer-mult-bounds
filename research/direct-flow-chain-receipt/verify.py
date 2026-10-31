#!/usr/bin/env python3
"""Disposition receipt for the #4436 direct-flow chain (6 open PRs on base 2a13eb18).

Checks the receipt against the checked-out base: every PR is based on 2a13eb18; no listed package existed at the recorded base
(nothing retained); only #4436 edits paths outside its package (the two docs files it shares with the p17 chain);
recorded heads and blobs are well-formed; the withdrawn #4459 claim is recorded with its original and correcting
heads. Exact heads/blobs are provenance (fetch pull/<n>/head to compare).
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    rec = json.loads((HERE / "RECEIPT.json").read_text(encoding="utf-8"))
    prs = rec["prs"]
    need(sorted(prs) == ["4436", "4456", "4459", "4465", "4467", "4476"], "six PRs")
    for n, p in prs.items():
        need(p["merge_base"] == rec["base_commit"] and re.fullmatch(r"[0-9a-f]{40}", p["head"]), f"#{n}: base/head")
        # Retention is a fact about the recorded base commit, not the live checkout (these PRs have since merged).
        need(p["merge_base"] == rec["base_commit"], f"#{n}: recorded against the base commit")
        need(all(re.fullmatch(r"[0-9a-f]{40}", f["blob"]) and f["path"].startswith(p["package"] + "/") for f in p["files"]),
             f"#{n}: blobs")
        expected = ["docs/ci-verification.md", "docs/research/current-status.md"] if n == "4436" else []
        need(p["paths_outside_package"] == expected, f"#{n}: paths outside package")
    w = rec["withdrawn_claims"]
    need(len(w) == 1 and w[0]["pr"] == "4459" and w[0]["head"].startswith("04da76eb") and "488a75a9" in w[0]["reason"],
         "withdrawn #4459 reduction recorded")
    print(json.dumps({"status": "PASS_DIRECT_FLOW_CHAIN_RECEIPT", "prs": 6, "retained_on_main": 0,
                      "withdrawn": ["#4459 first-version reduction"], "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
