#!/usr/bin/env python3
"""Check the convolution against source sums and literal matrices.

Ali Romman with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from math import comb, prod
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from count import joint_count, require


def load(path, name):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for item in manifest["files"]:
        if item["usage"] == "input":
            require(sha256((ROOT / item["path"]).read_bytes()).hexdigest()
                    == item["sha256"], "source hash mismatch")
    frozen = manifest["discussion"]
    require(sha256((HERE / frozen["path"]).read_bytes()).hexdigest()
            == frozen["sha256"], "Discussion hash mismatch")
    return load(ROOT / "research/schur-rank-pair-law/verify.py", "pair_source")


def simplex(t, remaining):
    if t == 0:
        yield ()
    else:
        for k in range(remaining + 1):
            for tail in simplex(t - 1, remaining - k):
                yield (k,) + tail


def direct(q, n, a, old, omit_lifts=False, wrong_sign=False):
    """Use the Discussion formula with only feasible dimension tuples."""
    if sum(a) > n:
        return 0
    result = 0
    for extra in simplex(len(a), n - sum(a)):
        taken, moment, weight = 0, 1, 1
        for x, u in zip(a, extra):
            k = x + u
            moment *= old.gaussian(n - taken, k, q)
            if not omit_lifts:
                moment *= q**(taken * k)
            taken += k
            weight *= old.gaussian(k, x, q) * q**(u * (u - 1) // 2)
            if not wrong_sign:
                weight *= (-1)**u
        result += moment * weight * q**(n * (n - taken))
    return result


def replay():
    old = source()
    comparisons = 0
    for q in (2, 3, 4, 5, 7):
        for n in range(7):
            for t in range(min(q, 4) + 1):
                for a in simplex(t, n):
                    require(joint_count(q, n, a) == direct(q, n, a, old),
                            "simplex disagreement")
                    if t == 2:
                        require(joint_count(q, n, a) == old.joint_count(n, *a, q),
                                "two-shift disagreement")
                    comparisons += 1
    contexts = [(2, n, 2) for n in range(4)] + [(3, n, 3) for n in range(4)]
    contexts += [(4, 2, 4), (5, 2, 3), (5, 2, 5)]
    matrices = bins = 0
    for q, n, t in contexts:
        histogram = Counter()
        for entries in product(range(q), repeat=n * n):
            nullities = []
            for shift in range(t):
                negative = shift if q == 4 else -shift
                shifted = tuple(old.add(entries[n * i + j], negative if i == j else 0, q)
                                for i in range(n) for j in range(n))
                nullities.append(n - old.rank(shifted, n, q))
            histogram[tuple(nullities)] += 1
            matrices += 1
        for a in product(range(n + 1), repeat=t):
            require(joint_count(q, n, a) == histogram[a], "matrix census disagreement")
            bins += 1
        require(sum(histogram.values()) == q**(n * n), "census total")
    for q, n, t in ((3, 5, 3), (5, 6, 4), (7, 5, 7)):
        values = {a: joint_count(q, n, a) for a in simplex(t, n)}
        require(sum(values.values()) == q**(n * n), "distribution total")
        for a, value in values.items():
            require(value == joint_count(q, n, tuple(reversed(a))), "shift symmetry")
        for a in simplex(t - 1, n):
            require(sum(values[a + (b,)] for b in range(n - sum(a) + 1))
                    == joint_count(q, n, a), "marginal consistency")
    require(joint_count(3, 2, (0, 0, 0)) == 18, "quadratic calibration")
    require(joint_count(3, 3, (1, 1, 1)) == 1404, "split calibration")
    require(joint_count(3, 3, (0, 0, 0)) == 3456, "cubic calibration")
    require(joint_count(2, 2, (1, 1)) != direct(2, 2, (1, 1), old, omit_lifts=True),
            "lift control")
    require(joint_count(3, 2, (0, 0, 0)) != direct(3, 2, (0, 0, 0), old, wrong_sign=True),
            "sign control")
    require(joint_count(2, 2, (0, 0)) * 16 != joint_count(2, 2, (0,))**2,
            "independence control")
    rejected = 0
    for args in ((6, 2, (0,)), (1, 2, (0,)), (True, 2, (0,)),
                 (2, -1, (0,)), (2, True, (0,)), (2, 2, (-1,)),
                 (2, 2, (True,)), (2, 2, (0, 0, 0))):
        try:
            joint_count(*args)
        except ValueError:
            rejected += 1
    require(rejected == 8, "invalid input accepted")
    large = joint_count(17, 24, (0,) * 17)
    return {"status": "PASS_MULTISHIFT_CONVOLUTION_NO_NEW_KAPPA",
            "direct_comparisons": comparisons, "matrix_contexts": len(contexts),
            "matrices": matrices, "bins": bins, "consistency_contexts": 3,
            "negative_controls": 11,
            "large_count": str(large), "large_direct_summands": comb(41, 17),
            "large_convolution_products": 17 * 25 * 26 // 2}


if __name__ == "__main__":
    result = replay()
    receipt = HERE / "RESULT.json"
    if "--record" in sys.argv:
        receipt.write_text(json.dumps(result, indent=2) + "\n")
    else:
        require(result == json.loads(receipt.read_text()), "receipt mismatch")
    print(json.dumps(result, sort_keys=True))
