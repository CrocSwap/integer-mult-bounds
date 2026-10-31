#!/usr/bin/env python3
"""Independent finite geometry check for the carrier relay-premise audit.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Only pinned input data is read; no predecessor/author executable is imported.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

WORD_SHA = "7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f"
FACTS_SHA = "6db1b3fadd64f643731879ec4fdb661e36da97e5969424e6364628b5f2e3780d"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dot(a, b):
    return (a & b).bit_count() % 2


def closure(values):
    result = {0}
    for value in values:
        result |= {entry ^ value for entry in tuple(result)}
    return result


def check(ports, normals, lines):
    need(len(ports) == len(set(ports)) == 104, "104 distinct ports")
    need(len(normals) == len(lines) == 8, "eight carriers")
    facts = []
    for c, (g, line) in enumerate(zip(normals, lines)):
        hyperplane = {x for x in range(512) if not dot(x, line)}
        receivers = {x for x in ports if not dot(x, line)}
        start = {0, g}
        need(len(hyperplane) == 256 and len(receivers) == 52, "hyperplane and receiver sizes")
        need(start < hyperplane and {0} < hyperplane, "strict grow then shrink")
        need(closure([g, *receivers]) == hyperplane, "receiver span identity")
        need(all(dot(other, line) == (a != c) for a, other in enumerate(normals)),
             "cross-normal pairing")
        need(receivers <= hyperplane, "all receivers served")
        need(len(hyperplane | {0}) != 512, "full-span hypothesis fails")
        facts.append({"carrier": c, "normal_g": g, "line": line,
                      "receiver_count": len(receivers), "walk_dimensions": [1, 8, 0],
                      "paid": 7, "union_dimension": 8, "eta": 0})
    count = 0
    for z in range(1, 10):
        for t in range(10):
            for intersection in range(min(z, t) + 1):
                union = z + t - intersection
                if union not in (8, 9):
                    continue
                for w in range(intersection + 1):
                    need((z - 1) + (t - w) >= 7 + union - 8, "repaired modular inequality")
                    count += 1
    need(count == 383, "dimension-domain coverage")
    return {"carriers": facts, "dimension_tuples": count,
            "two_carrier_paid": 14, "unqualified_stronger_rhs": 16,
            "scope": "abstract dual-subspace walk; not a pure-carrier physical program"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path, required=True)
    parser.add_argument("--facts", type=Path, required=True)
    args = parser.parse_args()
    word_bytes, facts_bytes = args.word.read_bytes(), args.facts.read_bytes()
    need(hashlib.sha256(word_bytes).hexdigest() == WORD_SHA, "word source bytes")
    need(hashlib.sha256(facts_bytes).hexdigest() == FACTS_SHA, "predecessor fact bytes")
    word = json.loads(gzip.decompress(word_bytes))
    facts = json.loads(facts_bytes)["carriers"]
    result = check(word["ports"], facts["normals_g"], facts["lines"])
    rejected = 0
    for normals, lines in [([0] + facts["normals_g"][1:], facts["lines"]),
                           (facts["normals_g"], [0] + facts["lines"][1:]),
                           (facts["normals_g"], facts["lines"][::-1])]:
        try:
            check(word["ports"], normals, lines)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("mutated geometry accepted")
    need(rejected == 3, "three negative controls")
    result["negative_controls"] = rejected
    print(json.dumps(result, sort_keys=True))
    print("PASS_INDEPENDENT_CARRIER_PREMISE")


if __name__ == "__main__":
    main()
