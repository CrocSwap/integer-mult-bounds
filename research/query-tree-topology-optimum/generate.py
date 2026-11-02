#!/usr/bin/env python3
"""Generate the finite integer upper certificate; output only to stdout."""

import json
from pathlib import Path


def main():
    rows = []
    for threshold in range(3, 18):
        optimum = [0] * 18
        for leaves in range(2, 18):
            child_best = max(optimum[left] + optimum[leaves - left] for left in range(1, leaves))
            optimum[leaves] = max(threshold - leaves, 0) + child_best
        rows.append({"threshold": threshold, "upper": optimum[1:]})
    certificate = {"schema": "query-tree-hinge-upper/1", "leaves": 19, "roots": 3, "hinges": rows}
    payload = json.dumps(certificate, indent=2) + "\n"
    existing = Path(__file__).with_name("CERTIFICATE.json")
    if existing.exists() and existing.read_text(encoding="utf-8") != payload:
        raise ValueError("generated certificate differs from committed certificate")
    print(payload, end="")


if __name__ == "__main__":
    main()
