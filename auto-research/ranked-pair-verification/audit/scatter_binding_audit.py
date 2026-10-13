#!/usr/bin/env python3
"""Bind every serialized scatter XOR to a charged output record.

This independent check supplements the inherited scalar replay. It does not
establish an all-size tape transfer or a multiplication bound.
"""
import argparse
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_scatter(d):
    h, v, roles = d["h"], d["v"], d["R"]
    require(type(h) is int and h in (23, 25), "Unsupported axis")
    triples = list(combinations(range(h), 3))
    require(type(v) is int and len(triples) == v, "Wrong source dimension")
    require(type(roles) is int and roles >= v, "Wrong physical role count")
    require(set(d["sources"]) == {str(i) for i in range(v)}, "Incomplete source keys")
    require(all(type(s) is int and 0 <= s < roles for s in d["sources"].values()), "Source domain")
    require(len(set(d["sources"].values())) == v, "Aliased source slots")
    expected, seen, central = [], set(), 0
    for slot, frame, common, triple in d["outputs"]:
        require(type(slot) is int and 0 <= slot < roles and slot not in seen, "Output slot domain or alias")
        seen.add(slot)
        require(type(frame) is int and 0 <= frame < len(d["frames"]), "Output frame domain")
        require(type(common) is int and 0 <= common < h, "Output common point")
        if len(triple) == 1:
            require(triple == [common], "Invalid retained center")
            central += 1
            destinations = [i for i, t in enumerate(triples) if common in t]
        else:
            require(len(triple) == 3 and triple == sorted(triple) and common in triple,
                    "Invalid side-output triple")
            require(tuple(triple) in triples, "Output triple domain")
            destinations = [triples.index(tuple(triple))]
        expected.extend([v + i, 2 * v + slot] for i in destinations)
    require(central == h, "Missing retained centers")
    for target, source in d["scatter"]:
        require(type(target) is int and type(source) is int and
                v <= target < 2 * v and 2 * v <= source < 2 * v + roles, "Scatter domain")
    require(d["scatter"] == expected,
            "Serialized scatter differs from complete output-derived literal operation list")
    return {"scatter_xors": len(expected), "central_outputs": central,
            "output_records": len(d["outputs"]), "literal_binding": True,
            "sequence_sha256": sha256(json.dumps(expected, separators=(",", ":")).encode()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("word", type=Path)
    args = parser.parse_args()
    raw = args.word.read_bytes()
    if args.word.suffix == ".gz":
        raw = gzip.decompress(raw)
    print(json.dumps(verify_scatter(json.loads(raw)), indent=2))


if __name__ == "__main__":
    main()
