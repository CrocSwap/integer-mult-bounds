#!/usr/bin/env python3
"""Navigation receipt for pinterbanget's 37 open PRs of 2026-10-22 (03:03-11:03 UTC), #4513-#4591.

Checks internal consistency of the recorded facts only (no working-tree or network checks, so it replays after any
of these PRs merges): every head is a full SHA, PR numbers are distinct, every PR has at least one research package
and packages are distinct across PRs, types come from a fixed vocabulary, every internal edge joins listed PRs and the
internal "controls reproduce" relation is acyclic, and the recorded #4554 coverage set is exactly the listed #4554 group.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
TYPES = {"check", "extension", "rank", "negative", "receipt", "repair"}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    rec = json.loads((HERE / "RECEIPT.json").read_text(encoding="utf-8"))
    rows = rec["prs"]
    nums = [r["pr"] for r in rows]
    need(len(rows) == 37 and len(set(nums)) == 37 and min(nums) == 4513 and max(nums) == 4591, "37 distinct PRs")
    seen = set()
    for r in rows:
        need(re.fullmatch(r"[0-9a-f]{40}", r["head"]), f"#{r['pr']}: head")
        need(r["packages"] and not (set(r["packages"]) & seen), f"#{r['pr']}: distinct packages")
        seen |= set(r["packages"])
        need(r["type"] in TYPES and r["group"] and r["what"], f"#{r['pr']}: type and description")
    listed = set(nums)
    for e in rec["edges"]:
        need(e["from"] in listed and e["to"] in listed, "internal edge endpoints")
    reproduce = {(e["from"], e["to"]) for e in rec["edges"] if e["kind"] == "controls reproduce"}
    order = {4563: 0, 4564: 1, 4565: 2}
    need(all(order[a] > order[b] for a, b in reproduce), "controls-reproduce edges point back in the rank chain")
    cover = next(x["covered_by"] for x in rec["external_edges"] if x.get("external") == 4554)
    group = sorted(r["pr"] for r in rows if r["group"].startswith("#4554"))
    need(sorted(cover) == group, "#4554 coverage set equals its group")
    counts = {t: sum(1 for r in rows if r["type"] == t) for t in sorted(TYPES)}
    print(json.dumps({"status": "PASS_SESSION_RECEIPT", "prs": len(rows), "packages": len(seen), "types": counts,
                      "groups": len({r["group"] for r in rows}), "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
