#!/usr/bin/env python3
"""Exact agreement check for three separately written annular constructions."""
from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path
import random
from types import ModuleType

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_bytes(name, path):
    source = path.read_bytes()
    module = ModuleType(name)
    module.__file__ = str(path)
    module.__package__ = ""
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


def pair(x):
    return x[:2], x[2:]


def flat(x):
    return x[0] + x[1]


def verify():
    source = json.loads((HERE / "SOURCES.json").read_text())
    hashes = {row["path"]: row["sha256"] for row in source["local_artifacts"]}
    paths = ("proof/verify.py", "proof/PROOF.md", "review/independent/matching.py",
             "review/independent/REVIEW.md", "review/root/check_candidate.py")
    for name in paths:
        require(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == hashes[name],
                "recorded source mismatch: " + name)
    proof = load_bytes("proof_ring_generator", HERE / "proof/verify.py")
    independent = load_bytes("independent_direct_ring", HERE / "review/independent/matching.py")
    root = load_bytes("root_direct_ring", HERE / "review/root/check_candidate.py")
    grid_count = 0
    for z in product(range(-31, 32, 2), repeat=2):
        require(proof.M(z) == independent.match(z) == root.match(z),
                "half-grid construction mismatch")
        grid_count += 1
    cube_count = 0
    for x in product(range(-4, 5), repeat=4):
        y = root.forward(x)
        require(proof.F(x) == flat(independent.forward(pair(x))) == y,
                "Gaussian construction mismatch")
        require(flat(independent.inverse(pair(y))) == root.inverse(y) == x,
                "inverse agreement")
        root.one(x)
        cube_count += 1
    rng = random.Random(2026111304)
    large_count = 0
    for bits in (16, 64, 256, 1024, 4096):
        for _ in range(16):
            x = tuple(rng.getrandbits(bits) * (-1 if rng.randrange(2) else 1)
                      for _ in range(4))
            require(flat(independent.forward(pair(x))) == root.forward(x),
                    "large direct construction mismatch")
            require(flat(independent.inverse(pair(x))) == root.inverse(x),
                    "large direct inverse mismatch")
            root.one(x)
            large_count += 1
    witness = (0, -2, 0, 3)
    image = (3, 1, -3, 0)
    require(root.forward(witness) == flat(independent.forward(pair(witness))) == image,
            "exact attaining witness")
    require((root.n2(witness), root.n2(image)) == (13, 19), "attaining norms")
    real = (1, 0, 0, 0)
    require(root.conjugate(root.forward(root.conjugate(real))) != root.inverse(real),
            "conjugation inverse failure control")
    # A rectangle matching is a complete unit matching of the 36-vertex box,
    # but fails the quarter-equivariance premise needed for the lower proof.
    rectangle = {}
    for y in (-5, -3, -1, 1, 3, 5):
        for a, b in ((-5, -3), (-1, 1), (3, 5)):
            rectangle[a, y] = (b, y)
            rectangle[b, y] = (a, y)
    require(len(rectangle) == 36, "premise-control box")
    require(any(rectangle[root.rot(z)] != root.rot(rectangle[z]) for z in rectangle),
            "non-equivariant matching control")
    return {
        "marker": "PASS_SHARP_ORDER_FOUR_CROSS_IMPLEMENTATIONS",
        "three_model_half_grid_cases": grid_count,
        "three_model_gaussian_cube_cases": cube_count,
        "two_direct_model_large_cases": large_count,
        "largest_component_bits": 4096,
        "seed": 2026111304,
        "attaining_input": witness,
        "attaining_output": image,
        "squared_norms": [13, 19],
        "inverse_conjugation_control": "rejected",
        "quarter_equivariance_premise_control": "rejected",
        "source_hashes": {name: hashes[name] for name in paths},
        "scope": "Exact cross-implementation evidence for shared candidate; universal theorem is the written proof, not finite coverage.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="regenerate finite receipt")
    args = parser.parse_args()
    result = json.loads(json.dumps(verify()))
    destination = HERE / "review/CROSS-CHECK-RESULT.json"
    if args.write:
        destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(json.loads(destination.read_text()) == result, "cross-check receipt drift")
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
