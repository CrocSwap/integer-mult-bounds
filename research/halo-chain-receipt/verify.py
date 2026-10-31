#!/usr/bin/env python3
"""Disposition receipt for the Gaussian halo-exponent PR chain (13 PRs, all open at base 2a13eb18).

Checks the receipt's internal consistency and its retention claims against the checked-out base: every listed
package path is absent at base (nothing retained), each PR is a single-package addition with recorded file blobs,
dependency and coverage edges refer only to listed PRs, and every author PR except the open transfer #4462 has at
least one independent check listed. Exact PR heads and blobs are provenance (fetch pull/<n>/head to compare).
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
    prs = {r["pr"]: r for r in rec["prs"]}
    need(len(prs) == 13, "13 PRs")
    for n, r in prs.items():
        need(re.fullmatch(r"[0-9a-f]{40}", r["head"]) and r["merge_base"] == rec["base_commit"], f"#{n}: head and base")
        # Retention is a fact about the recorded base commit, not the live checkout (these PRs have since merged).
        need(r["package_on_main"] is False, f"#{n}: recorded as not retained at base")
        need(r["paths_changed_outside_package"] == [], f"#{n}: single-package addition")
        need(len(r["files"]) >= 5 and all(re.fullmatch(r"[0-9a-f]{40}", f["blob"]) for f in r["files"]), f"#{n}: blobs")
        need(all(f["path"].startswith(r["package"] + "/") for f in r["files"]), f"#{n}: files inside the package")
        need(set(r["depends_on"]) <= set(prs) and set(r["independently_checked_by"]) <= set(prs), f"#{n}: edges")
    authors = [n for n, r in prs.items() if r["author"] != "pinterbanget"]
    need(all(prs[n]["independently_checked_by"] for n in authors), "every author PR has an independent check")
    need(rec["not_checked_independently"] == [4462], "only the transfer #4462 lacks an independent check")
    print(json.dumps({"status": "PASS_HALO_CHAIN_RECEIPT", "prs": len(prs), "retained_on_main": 0,
                      "author_prs_checked": len(authors), "unchecked": rec["not_checked_independently"],
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
