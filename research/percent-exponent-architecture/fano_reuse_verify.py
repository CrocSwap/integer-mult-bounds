#!/usr/bin/env python3
"""Replay the whole finite stub-reuse screen without a solver or C++.

The complete negative statements below apply only to reuse topologies that
preserve the original three-demand routing obstruction. The other topologies
are recorded as outside this particular selection, not proved impossible.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "discovery"))
from fano_reuse import topologies
from balanced_fano import existence


def verify():
    if sys.flags.optimize:
        raise ValueError("Run without -O")
    cases = list(topologies())
    accepted = [c for c in cases if not c["routing"]["routable"]]
    if len(cases) != 87 or len(accepted) != 16:
        raise ValueError("The exhaustively specified topology family changed")
    certificates = []
    for i, c in enumerate(accepted):
        result = existence(c["W"], c["pairs"], c["prescribed"])
        if result["exists"] or not result["exhaustive_negative"]:
            raise ValueError("A scalar completion needs further investigation")
        if result["prefix_assignments"] != 6**7 or result["suffix_assignments"] != 6**7:
            raise ValueError("The complete halves were not enumerated")
        certificates.append({"topology": c, "scalar_exhaustion": result})
        print(f"PASS {i+1}/{len(accepted)}: case {c['id']}, W={c['W']}, all 6^14 assignments excluded", flush=True)
    return {"status": "NO SCALAR COMPLETION IN THE SPECIFIED OBSTRUCTION-PRESERVING REUSE FAMILY",
            "topologies_enumerated": len(cases), "obstruction_preserving_topologies": len(accepted),
            "other_topologies": len(cases) - len(accepted),
            "width_counts": dict(sorted(Counter(c["W"] for c in accepted).items())),
            "cases": certificates,
            "scope": "Chronological pairings of distinct auxiliary output/input stubs of the balanced Fano DAG, retaining the original three-demand obstruction; GL(2,F2) at each of 14 vertices; all other inputs independent with a free output permutation. Other topologies, larger local blocks and different coding graphs are not excluded."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    output = json.dumps(verify(), sort_keys=True, indent=2) + "\n"
    path = HERE / "fano-reuse-certificate.json"
    if args.write:
        path.write_text(output)
    elif path.read_text() != output:
        raise ValueError("Exact Fano reuse certificate changed")


if __name__ == "__main__":
    main()
