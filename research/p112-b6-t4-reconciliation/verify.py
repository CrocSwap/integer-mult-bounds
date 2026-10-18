"""Replay the exact caller reconciliation without Git or network."""

import contextlib
import io
import json

from binding import ROOT, authenticate, read_json, require
from model import CAP, RULES, classify, historical, universe


def source_filter(domain):
    authenticate()
    # The unchanged source prints its historical table during import.
    with contextlib.redirect_stdout(io.StringIO()):
        from vendor import bk2b
    results = []
    for weights in domain:
        accepted = (
            sum(w - 2 for w in weights) < 36
            and bk2b.feasible(weights, 6)
            and not bk2b.killed(weights, 6)
        )
        results.append(accepted)
    return results


def compute():
    hashes = authenticate()
    domain = universe()
    require(len(domain) == 7546, "wrong finite domain")
    original = source_filter(domain)
    own = [historical(weights) for weights in domain]
    require(original == own, "full-domain filter disagreement")
    survivors = [w for w, accepted in zip(domain, own, strict=True) if accepted]
    require(len(survivors) == 69, "wrong historical cell")
    rows = [classify(weights) for weights in survivors]
    primary = {rule: sum(row["primary"] == rule for row in rows) for rule in RULES}
    unresolved = [row["weights"] for row in rows if row["primary"] is None]
    require(sum(primary.values()) + len(unresolved) == 69, "incomplete partition")
    return {
        "schema": "p112-b6-t4-reconciliation/v1",
        "cell": [6, 4],
        "domain_multisets": len(domain),
        "historical_survivors": 69,
        "source_hashes": hashes,
        "support_caps": list(CAP[2:]),
        "primary_rule_counts": primary,
        "certified": 69 - len(unresolved),
        "uncertified": unresolved,
        "scope": "Conditional composition of six fixed pinned theorem contracts; "
        "uncertified is relative to this inventory, not all public work.",
        "rows": rows,
    }


def main():
    actual = json.loads(json.dumps(compute()))
    require(actual == read_json(ROOT / "RESULT.json"), "committed receipt disagrees")
    print(
        "PASS_P112_B6_T4_RECONCILIATION",
        actual["domain_multisets"],
        actual["historical_survivors"],
        actual["certified"],
        len(actual["uncertified"]),
    )


if __name__ == "__main__":
    main()
